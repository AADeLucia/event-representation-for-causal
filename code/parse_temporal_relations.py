"""
Parse raw timeline/predictions from Fine-Grained Temporal
Extraction output

Output is single JSONL with a single entry for each Gigaword document

Author: Alexandra DeLucia
"""
import pandas as pd
import csv
import json
import jsonlines
from tqdm import tqdm
from argparse import ArgumentParser
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--input-files", nargs="+", help="List of JSONL files")
    parser.add_argument("--output-dir", type=str, help="Output folder to save .json")
    parser.add_argument('--debug', action='store_true')
    parser.add_argument("--log-file", help="Path to log")
    return parser.parse_args()


def determine_temporal_relation(event1, event2):
    # 1. Event1 completed before Event2 started
    if event1[1] < event2[0]:
        return "before"
    # 2. Event2 completed before Event1 started
    if event1[0] > event2[1]:
        return "after"
    # 3. There is overlap
    return "overlap"


if __name__ == "__main__":
    args = parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.log_file:
        logger.addHandler(logging.FileHandler(args.log_file))

    counts = {}
    all_relations = {}
    for input_file in tqdm(args.input_files):
        # Save ID
        document_id = input_file.split("/")[-1].split(".")[0]
        all_relations[document_id] = []

        # Columns
        # 'sent_pred_id1', 'sent_pred_id2', 'b1', 'e1', 'b2', 'e2',
        # 'pred1_duration', 'pred2_duration', 'pred1_text', 'pred2_text',
        # 'pred1_dict_idx', 'pred2_dict_idx'
        with open(input_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                event1 = (row['b1'], row['e1'])
                event2 = (row['b2'], row['e2'])
                relationship = determine_temporal_relation(event1, event2)
                all_relations[document_id].append((row['pred1_text'], row['pred2_text'], relationship))
                counts[relationship] = counts.get(relationship, 0) + 1
                logger.debug(f"{event1}\t{event2}\t{relationship}")

    with open(f"{args.output_dir}/temporal_relations.json", "w") as f:
        json.dump(all_relations, f)

    logger.info(counts)
