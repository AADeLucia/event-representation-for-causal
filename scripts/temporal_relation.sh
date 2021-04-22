#!/bin/sh

INPUT=(${EVENT_HOME}/test/*.output_predictions.csv)
OUTPUT="${EVENT_HOME}/test"
mkdir -p "${OUTPUT}"

python "${EVENT_HOME}/code/parse_temporal_relations.py" \
  --input-files "${INPUT[@]}" \
  --output-dir "${OUTPUT}" \
  --debug
