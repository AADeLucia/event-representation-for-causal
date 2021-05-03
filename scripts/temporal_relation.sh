#!/bin/sh

INPUT="${EVENT_HOME}/test/NYT_comms.tar.gz"
OUTPUT="${EVENT_HOME}/test/temporal_relations.jsonl"

python "${EVENT_HOME}/code/parse_temporal_relations.py" \
  --input-files "${INPUT}" \
  --output-dir "${OUTPUT}" \
