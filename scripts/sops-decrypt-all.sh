#!/bin/bash

# Check if a path argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <path>"
    exit 1
fi

# Use the provided path
ROOT_DIR="$1"

# yaml files
find "$ROOT_DIR" -name "*.sops.yaml" -type f -not -path "$ROOT_DIR/.sops.yaml" | while read file; do
  if yq e 'has("sops")' "$file" | grep -q "true"; then
    sops -d -i "$file"
    echo "Decrypted: $file"
  else
    echo "Already decrypted: $file"
  fi
done
 
# env files
find "$ROOT_DIR" -name "*.env" -type f | while read file; do
    if grep -q "^sops_" "$file"; then
    sops -d -i "$file"
    echo "Decrypted: $file"
  else
    echo "Already decrypted: $file"
    fi
done
