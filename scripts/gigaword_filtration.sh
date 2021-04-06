#/bin/sh

for f in ../data/cgw/raw/*.tar.gz; do
    g=`basename ${f%.tar.gz}`
    echo $g
    nohup /usr/bin/time -v python gigaword_extraction.py "$f" "../data/cgw/preds_args/$g.jsonl" >"../logs/cgw/preds_args/$g.log" 2>&1 &
done
