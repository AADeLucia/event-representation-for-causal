#!/bin/bash

  INPUT_FILES=("/srv/local1/share/datasets/causalbank/because_mode/caused_by" "/srv/local1/share/datasets/causalbank/because_mode/because")
  OUTPUT="${EVENT_HOME}/results/causalbank_relations.txt"
  VERBS="${EVENT_HOME}/results/schema_verbs.json"

  python "${EVENT_HOME}/code/temporal_relations_causalbank.py" \
    --input-file "${INPUT_FILES[@]}" \
    --output-file "${OUTPUT}" \
    --key-verbs "${VERBS}" \

  status=$?
  if [ $status -ne 0 ]
  then
    echo "Task failed"
    exit 1
  fi

echo "Done."
