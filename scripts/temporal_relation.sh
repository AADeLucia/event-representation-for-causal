#!/bin/sh

for dir in "protests" "election" "arrest" "disease_outbreak" "plane_crash"
do

  DIR="${EVENT_HOME}/results/${dir}"
  INPUT="${DIR}/nyt_comms.tar.gz"
  OUTPUT="${DIR}/temporal_relations.jsonl"
  AGG_OUTPUT="${DIR}/temporal_relations_agg.txt"

  python "${EVENT_HOME}/code/parse_temporal_relations.py" \
    --input-file "${INPUT}" \
    --output-file "${OUTPUT}" \
    --debug

  python "${EVENT_HOME}/code/parse_temporal_relations.py" \
    --input-file "${INPUT}" \
    --output-file "${OUTPUT}" \
    --aggregate \
    --aggregate-output-file "${AGG_OUTPUT}" \
    --debug

done
echo "Done"
