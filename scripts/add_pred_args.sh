#!/bin/bash


SCHEMA_DOCS=(
#  "${EVENT_HOME}/results/arrest/nyt_en_arrest.jsonl"
  "${EVENT_HOME}/results/protests/nyt_en_protest.jsonl"
  "${EVENT_HOME}/results/disease_outbreak/nyt_en_disease_outbreak.jsonl"
  "${EVENT_HOME}/results/election/nyt_en_election.jsonl"
  "${EVENT_HOME}/results/plane_crash/nyt_en_plane_crash.jsonl"
)

for docs in "${SCHEMA_DOCS[@]}"
do

  echo "On docs ${docs}"

  python "${EVENT_HOME}/code/add_pred_args_jsonl.py" \
    --schema-related "${docs}" \
    --pred-args-dir "${EVENT_HOME}/data/cgw/preds_args"

  status=$?
  if [ $status -ne 0 ]
  then
    echo "Task failed"
    exit 1
  fi

done

echo "Done"
