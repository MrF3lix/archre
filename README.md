# SwissHacks - 2025

## Project Structure

```
.
├── infra/                   # Infrastructure configuration
├── webapp/                  # Frontend
├── reporter/                # Report Generator
└── taskfile.yaml            # Task automation definitions
```

## Prerequisites

### Installing Task

Task is a task runner/build tool that aims to be simpler and easier to use than
GNU Make. You'll need to install it before you can run any of the development
tasks.

```bash
brew install go-task/tap/go-task
```

## Development Setup

### Development Environment

To set up the development environment, run:

```bash
task devel:env
```

This command will install all necessary dependencies and configure your local
development environment.

### SOPS Encryption

To work with encrypted files in this project, you'll need to generate an `Age`
key and add it to the `sops` recipients list:

```bash
task devel:sops
```

This will generate a new Age key if you don't already have one and add your
public key to the `.sops.yaml` file as a recipient.

After running this task, you'll need to:

- Commit the changes to `.sops.yaml` in a new branch
- Create a pull request
- Notify Martin that you've added a new key so he can update the SOPS files with your key included

> [!NOTE]  
> Until Martin updates the encrypted files, you won't be able to decrypt them with your key.

