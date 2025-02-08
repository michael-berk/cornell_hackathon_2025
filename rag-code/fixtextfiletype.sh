#!/bin/bash

# Directory containing the files (change if needed)
TARGET_DIR="."

# Find and rename files ending with ".txt.txt"
for file in "$TARGET_DIR"/*.txt.txt; do
    # Ensure the file exists before renaming
    if [ -f "$file" ]; then
        new_name="${file%.txt.txt}.txt"
        mv "$file" "$new_name"
        echo "✅ Renamed: $file → $new_name"
    fi
done

echo "🎉 Done! All files renamed."
    