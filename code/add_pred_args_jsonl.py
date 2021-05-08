"""
Author: Alexandra DeLucia
"""
import os
import jsonlines
from tqdm import tqdm
from argparse import ArgumentParser
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--schema-related", help="JSONL of articles related to schema topic")
    parser.add_argument("--pred-args-dir", help="Path to comm files parsed into predicates and arguments")
    parser.add_argument('--debug', action='store_true')
    parser.add_argument("--log-file", help="Path to log")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.log_file:
        logger.addHandler(logging.FileHandler(args.log_file))

    # 1. Aggregate unique IDs
    articles_by_id = {}
    with jsonlines.open(args.schema_related) as reader:
        for obj in reader.iter():
            parent_id = obj['id'].split(".")[0][:-2].lower()
            articles_by_id[parent_id] = articles_by_id.get(parent_id, {})
            articles_by_id[parent_id][obj['id']] = obj

    # 2. For each parent ID, reader through group of pred args
    for pred_args_doc in tqdm(os.listdir(args.pred_args_dir)):
        if not pred_args_doc.endswith(".jsonl"):
            continue
        parent_id = pred_args_doc.split(".")[0]
        if parent_id not in articles_by_id:
            continue

        with jsonlines.open(f"{args.pred_args_dir}/{pred_args_doc}") as reader:
            for obj in reader.iter():
                # Match document to the one in articles_by_id
                doc_id = obj['filename'][:-5]  # remove ".comm"
                if doc_id in articles_by_id[parent_id]:
                    # Add the pred_args
                    articles_by_id[parent_id][doc_id]["pred_args"] = obj["preds_args"]

    # Write out
    output_file = f"{args.schema_related}.predargs"
    logger.info(f"Writing out to {output_file}")
    with jsonlines.open(output_file, "w") as writer:
        for parent_id, docs in articles_by_id.items():
            for doc_id, obj in docs.items():
                writer.write(obj)
