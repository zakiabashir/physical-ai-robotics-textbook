#!/bin/bash

# Create Prompt History Record (PHR) Script
# Usage: ./create-phr.sh --title "Title" --stage <stage> [--feature <name>] [--json]

set -e

# Default values
TITLE=""
STAGE=""
FEATURE=""
JSON_OUTPUT=false
PHR_ID=1
DATE=$(date +%Y-%m-%d)
DATETIME=$(date -Iseconds)

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --title)
            TITLE="$2"
            shift 2
            ;;
        --stage)
            STAGE="$2"
            shift 2
            ;;
        --feature)
            FEATURE="$2"
            shift 2
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 --title \"Title\" --stage <stage> [--feature <name>] [--json]"
            echo ""
            echo "Stages: constitution, spec, plan, tasks, red, green, refactor, explainer, misc, general"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$TITLE" || -z "$STAGE" ]]; then
    echo "Error: --title and --stage are required"
    exit 1
fi

# Determine output directory
if [[ "$STAGE" == "constitution" ]]; then
    OUTPUT_DIR="history/prompts/constitution"
elif [[ "$STAGE" == "general" ]]; then
    OUTPUT_DIR="history/prompts/general"
elif [[ -n "$FEATURE" ]]; then
    OUTPUT_DIR="history/prompts/$FEATURE"
else
    OUTPUT_DIR="history/prompts/general"
fi

# Create directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Find next available ID
find_next_id() {
    local dir=$1
    local max_id=0

    for file in "$dir"/*.prompt.md; do
        if [[ -f "$file" ]]; then
            local basename=$(basename "$file" .prompt.md)
            local id=$(echo "$basename" | cut -d'-' -f1)
            if [[ "$id" =~ ^[0-9]+$ ]]; then
                if (( id > max_id )); then
                    max_id=$id
                fi
            fi
        fi
    done

    echo $((max_id + 1))
}

PHR_ID=$(find_next_id "$OUTPUT_DIR")

# Create slug from title
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')

# Output filename
FILENAME="${PHR_ID}-${SLUG}.${STAGE}.prompt.md"
OUTPUT_PATH="$OUTPUT_DIR/$FILENAME"

# Create PHR content
if [[ "$JSON_OUTPUT" == "true" ]]; then
    # Output JSON for agent processing
    cat << EOF
{
  "PHR_ID": "$PHR_ID",
  "TITLE": "$TITLE",
  "STAGE": "$STAGE",
  "DATE_ISO": "$DATE",
  "DATETIME": "$DATETIME",
  "FEATURE": "$FEATURE",
  "OUTPUT_PATH": "$OUTPUT_PATH",
  "FILENAME": "$FILENAME",
  "OUTPUT_DIR": "$OUTPUT_DIR",
  "SLUG": "$SLUG"
}
EOF
else
    # Create basic PHR file
    cat << EOF > "$OUTPUT_PATH"
---
ID: $PHR_ID
TITLE: $TITLE
STAGE: $STAGE
DATE_ISO: $DATE
SURFACE: "agent"
MODEL: "claude-opus-4-5"
FEATURE: "${FEATURE:-none}"
BRANCH: "$(git branch --show-current 2>/dev/null || echo 'unknown')"
USER: "\$USER"
COMMAND: "sp.phr"
LABELS: []
LINKS:
  SPEC: null
  TICKET: null
  ADR: null
  PR: null
FILES_YAML:
TESTS_YAML:
OUTCOME:
  STATUS: "pending"
  EVALUATION: ""
---

# $TITLE - Prompt History Record

## Prompt Text

<!-- Add prompt text here -->

## Response Summary

<!-- Add response summary here -->

---
*Generated: $DATETIME*
EOF

    echo "Created PHR: $OUTPUT_PATH"
fi