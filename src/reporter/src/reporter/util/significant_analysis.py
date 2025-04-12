import json
import re

from llama_index.core import Document, Settings
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

# configure llm and embedding model
Settings.llm = GoogleGenAI(model_name="models/gemini-2.0-flash-latest")
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/embedding-001")


class SignificantAnalysis:
    """Analyzes a contract diff summary focusing on significant changes and suggestions, outputting JSON."""

    def __init__(self, summary_text):
        self.summary_text = summary_text
        self.document = Document(text=self.summary_text)
        self.llm = Settings.llm

    def _build_prompt(self):
        """Builds the prompt for the LLM analysis, requesting JSON output."""
        return f"""
        Analyze the following contract diff summary, which includes changes between two versions of a contract.
        Focus ONLY on the following aspects:

        1.  **Significant Changes:** Identify the most impactful changes based *only* on the provided summary (consider financial impact, scope changes, liability shifts). Describe each significant change as a **brief, factual statement only**. **DO NOT include explanations, implications, or the (CHANGE #) markers in your descriptions.** Just state what changed.
        2.  **Overall Impression:** Briefly describe the overall nature of the changes based on the details observed (e.g., major overhaul, minor updates, primarily risk adjustment, etc.).
        3.  **Suggestions for Investigation:** Based on the significant changes and overall impression, provide a list of specific points or areas that a reviewer should investigate further to fully understand the implications of the contract modifications.

        **Output Format:** Structure your entire response as a single JSON object with the following exact keys:
        - `significant_changes`: A list of concise strings, where each string states one significant change factually.
        - `overall_impression`: A single string containing the overall impression.
        - `suggestions_for_investigation`: A list of strings, where each string is a suggestion.

        **Example JSON Structure:**
        ```json
        {{
          "significant_changes": [
            "Effective date changed from 2023 to 2024.",
            "Governing law changed from Florida to Georgia.",
            "First layer retention increased from $10M to $25M."
          ],
          "overall_impression": "Overall assessment of the changes...",
          "suggestions_for_investigation": [
            "Suggestion 1 for further review.",
            "Suggestion 2 for further review."
          ]
        }}
        ```

        Ensure the output is valid JSON. Analyze the summary provided below:
        ------------------------------------------------------------
        {self.summary_text}
        ------------------------------------------------------------
        JSON Analysis:
        """

    def run_analysis(self):
        """Runs the LLM analysis and returns the structured JSON result."""
        prompt = self._build_prompt()
        print("Analyzing summary content for significant changes (JSON output)...")
        response = self.llm.complete(prompt)
        response_text = response.text.strip()

        # Attempt to clean and parse the JSON output from the LLM
        try:
            # Find the start and end of the JSON block
            json_match = re.search(r"```json\n(.*?)\n```", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # Fallback if ```json``` markers are missing, assume the whole response is JSON
                json_str = response_text

            # Basic cleaning (sometimes LLMs add trailing commas)
            json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)

            parsed_json = json.loads(json_str)
            # Validate expected keys
            required_keys = {
                "significant_changes",
                "overall_impression",
                "suggestions_for_investigation",
            }
            if not required_keys.issubset(parsed_json.keys()):
                raise ValueError(
                    f"LLM JSON output missing required keys. Found: {parsed_json.keys()}"
                )
            if not isinstance(parsed_json["significant_changes"], list):
                raise ValueError("`significant_changes` should be a list.")
            if not isinstance(parsed_json["overall_impression"], str):
                raise ValueError("`overall_impression` should be a string.")
            if not isinstance(parsed_json["suggestions_for_investigation"], list):
                raise ValueError("`suggestions_for_investigation` should be a list.")

            return parsed_json
        except json.JSONDecodeError as e:
            print(f"Error decoding LLM JSON response: {e}")
            print("Raw LLM Response:\n", response_text)
            # Return an error structure or raise the exception
            return {
                "error": "Failed to parse LLM JSON response",
                "raw_output": response_text,
            }
        except ValueError as e:
            print(f"Error validating LLM JSON structure: {e}")
            print("Raw LLM Response:\n", response_text)
            return {
                "error": f"LLM JSON structure validation failed: {e}",
                "raw_output": response_text,
            }
        except Exception as e:
            print(f"An unexpected error occurred during JSON processing: {e}")
            print("Raw LLM Response:\n", response_text)
            return {
                "error": f"Unexpected error processing JSON: {e}",
                "raw_output": response_text,
            }
