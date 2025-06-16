#!/bin/bash

# --- Configuration ---
# An optional first argument to the script can specify the directory to scan.
# e.g., ./generate_context.sh backend
# If no argument is given, it scans the current directory '.'
TARGET_DIR=${1:-.}

# --- MODIFICATION START ---
# Configuration for the tree command
TREE_LEVEL=5
# An extensive ignore pattern for the 'tree' command, mirroring the 'find' exclusions.
TREE_IGNORE_PATTERN="node_modules|.venv|venv|env|.git|__pycache__|.pytest_cache|dist|build|target|instance|uploads|unprocessed|data"
# --- MODIFICATION END ---

# Determine the output file name based on the target directory
if [[ "$TARGET_DIR" == "." ]]; then
    OUTPUT_FILE="llm_project_context.txt"
else
    # Sanitize target dir name for the filename (e.g., mushi-frontend -> frontend)
    PREFIX=$(basename "$TARGET_DIR")
    OUTPUT_FILE="${PREFIX}_context.txt"
fi

# --- Main Script ---
echo "--- LLM Context Generator ---"
echo "Scanning directory: $TARGET_DIR"
echo "Output file:        $OUTPUT_FILE"
echo ""

# --- MODIFICATION START ---
# Clear output file and add the project tree structure first
> "$OUTPUT_FILE" # This empties the file

# Check if 'tree' command exists and add the directory structure to the output
if command -v tree &> /dev/null; then
    echo "Generating project tree structure (up to level $TREE_LEVEL)..."
    echo "--- PROJECT STRUCTURE ---" >> "$OUTPUT_FILE"
    tree -L $TREE_LEVEL -I "$TREE_IGNORE_PATTERN" "$TARGET_DIR" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "--- END PROJECT STRUCTURE ---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
else
    echo "Warning: 'tree' command not found. Skipping project structure generation."
    echo "         (To install: 'sudo apt-get install tree' or 'brew install tree')"
fi
# --- MODIFICATION END ---

echo "Finding files (excluding common build, dependency, and data folders)..."

# Use a temporary file for the list of files to process
TEMP_FILE="/tmp/file_list_$$"

# Find files that DON'T contain certain path segments or match certain names.
# This properly excludes nested directories.
find "$TARGET_DIR" -type f \
    ! -path "*/node_modules/*" \
    ! -path "*/.venv/*" \
    ! -path "*/venv/*" \
    ! -path "*/env/*" \
    ! -path "*/.git/*" \
    ! -path "*/__pycache__/*" \
    ! -path "*/.pytest_cache/*" \
    ! -path "*/dist/*" \
    ! -path "*/build/*" \
    ! -path "*/target/*" \
    ! -path "*/instance/*" \
    ! -path "*/uploads/*" \
    ! -path "*/unprocessed/*" \
    ! -path "*/backend/data/*" \
    ! -name "*.pyc" \
    ! -name "*.db" \
    ! -name "*.sqlite*" \
    ! -name "*.lockb" \
    ! -name "*.tsbuildinfo" \
    ! -name "*.svg" \
    ! -name "*.jpg" \
    ! -name "*.jpeg" \
    ! -name "*.png" \
    ! -name "*.gif" \
    ! -name "*.ico" \
    ! -name "*.bin" \
    ! -name "*.log" \
    ! -name "*.zip" \
    ! -name "*.tar*" \
    ! -name "*.gz" \
    ! -name "package-lock.json" \
    ! -name "yarn.lock" \
    ! -name "pnpm-lock.yaml" \
    ! -name ".DS_Store" \
    ! -name "*.min.js" \
    ! -name "*.min.css" \
    ! -name "crawler.sh" \
    > "$TEMP_FILE" 2>/dev/null

# Get script name for exclusion (this script shouldn't include itself)
SCRIPT_NAME=$(basename "$0")

# Count files
total_files=$(wc -l < "$TEMP_FILE")
echo "Found $total_files files to process"

# Quick sanity check
if [[ $total_files -eq 0 ]]; then
    echo "No files found matching the criteria. Exiting."
    rm -f "$TEMP_FILE"
    exit 0
fi
if [[ $total_files -gt 1000 ]]; then
    echo "WARNING: Still found $total_files files - this might include unwanted files"
    echo "First 10 files found:"
    head -10 "$TEMP_FILE"
    echo ""
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        rm -f "$TEMP_FILE"
        echo "Aborted."
        exit 1
    fi
fi

echo ""

# Process files
file_count=0
while IFS= read -r file; do
    # Skip empty lines
    [[ -z "$file" ]] && continue

    # Get the basename of the file for checks
    file_basename=$(basename "$file")

    # Skip script itself and output file
    [[ "$file_basename" == "$SCRIPT_NAME" ]] && continue
    [[ "$file_basename" == "$OUTPUT_FILE" ]] && continue

    # Check if file exists and is readable
    if [[ ! -f "$file" ]] || [[ ! -r "$file" ]]; then
        continue
    fi

    # Quick size check - skip files larger than 1MB
    size=$(wc -c < "$file" 2>/dev/null || echo 0)
    if [[ $size -gt 1048576 ]]; then
        echo "Skipping large file: $file ($((size/1024)) KB)"
        continue
    fi

    ((file_count++))
    echo "[$file_count/$total_files] Adding $file"

    # Add to context file
    echo "--- FILE_START: $file ---" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE" 2>/dev/null || echo "[Error reading file]" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "--- FILE_END: $file ---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

done < "$TEMP_FILE"

# Clean up
rm -f "$TEMP_FILE"

echo ""
echo "--- Complete ---"
echo "Processed: $file_count files"

if [[ -f "$OUTPUT_FILE" ]] && [[ -s "$OUTPUT_FILE" ]]; then
    size_info=$(du -h "$OUTPUT_FILE" | cut -f1)
    line_count=$(wc -l < "$OUTPUT_FILE")

    echo "Output size: $size_info"
    echo "Total lines: $line_count"
    echo ""
    echo "File types processed:"
    grep "^--- FILE_START:" "$OUTPUT_FILE" | sed 's/.*\.//' | sort | uniq -c | sort -nr
    echo ""
    echo "✓ Context file ready: $OUTPUT_FILE"
else
    echo "❌ No files were processed or the output file is empty."
fi
