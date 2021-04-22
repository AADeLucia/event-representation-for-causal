#!/bin/bash

# Input and output must be folder names
# Program only checks folders for .comm files
# Writes to <file>_updated.comm
INPUT=(${EVENT_HOME}/data/cgw/schema_related/pos/*.jsonl)
OUTPUT="${EVENT_HOME}/test"
mkdir -p "${OUTPUT}"

python "${EVENT_HOME}/code/jsonl_to_text.py" \
  --input-files "${INPUT[@]}" \
  --output-dir "${OUTPUT}" \
