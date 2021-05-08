#!/bin/sh

# "protests" "election" "arrest"  "disease_outbreak" "plane_crash"
for dir in "disease_outbreak"
do

  DIR="${EVENT_HOME}/results/${dir}"
  INPUT="${DIR}/nyt_comms_train.tar.gz"
  OUTPUT="${DIR}/temporal_relations.jsonl"
  AGG_OUTPUT="${DIR}/temporal_relations_agg.txt"
  VERBS="${DIR}/key_verbs.json"

  rm "${OUTPUT}"
  python "${EVENT_HOME}/code/parse_temporal_relations.py" \
    --input-file "${INPUT}" \
    --output-file "${OUTPUT}" \
    --key-verbs "${VERBS}" \

  status=$?
  if [ $status -ne 0 ]
  then
    echo "Task failed"
    exit 1
  fi

  python "${EVENT_HOME}/code/parse_temporal_relations.py" \
    --input-file "${INPUT}" \
    --output-file "${OUTPUT}" \
    --key-verbs "${VERBS}" \
    --aggregate \
    --aggregation-output-file "${AGG_OUTPUT}"

done

echo "Done"
