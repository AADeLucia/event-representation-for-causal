#!/bin/bash
ALGORITHM=fges
JAVA15=/srv/local1/share/pkgs/jdk-15.0.1/bin/java

for SCHEMA_NAME in ce_001_protest ce_005_disease_outbreak ce_040_arrest election plane_crash; do
    $JAVA15 -jar 3rdparty/causal-cmd-1.2.2/causal-cmd-1.2.2-jar-with-dependencies.jar --skip-latest --delimiter comma --resamplingWithReplacement --numberResampling 50 --resamplingEnsemble 1 --addOriginalDataset --json-graph --algorithm $ALGORITHM --data-type discrete --score bdeu-score --dataset "data/cgw/schema_related/pos/${SCHEMA_NAME}_binary_10.csv" --knowledge "data/cgw/temporal/causal-cmd/${SCHEMA_NAME}.txt" --out data/cgw/causal --prefix "${SCHEMA_NAME}_out"
    # $JAVA15 -jar 3rdparty/causal-cmd-1.2.2/causal-cmd-1.2.2-jar-with-dependencies.jar --skip-latest --delimiter comma --resamplingWithReplacement --numberResampling 50 --resamplingEnsemble 0 --addOriginalDataset --json-graph --algorithm $ALGORITHM --data-type discrete --score bdeu-score --dataset "data/cgw/schema_related/pos/${SCHEMA_NAME}_binary_10.csv" --out data/cgw/causal/non-restr --prefix "${SCHEMA_NAME}_out"
done

