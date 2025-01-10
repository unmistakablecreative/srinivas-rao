#!/bin/bash

# File to clean up
FILE=$1

if [ -z "$FILE" ]; then
  echo "Usage: ./fix_conflicts.sh <file>"
  exit 1
fi

# Ensure the file exists
if [ ! -f "$FILE" ]; then
  echo "Error: File $FILE does not exist."
  exit 1
fi

# Remove all Git conflict markers
sed -i.bak '/<<<<<<< HEAD/d' "$FILE"
sed -i.bak '/=======/d' "$FILE"
sed -i.bak '/>>>>>>>/d' "$FILE"

echo "Conflict markers removed from $FILE. A backup has been created as $FILE.bak."