"""
Parse temporal relations from LOME temporal output (Concrete .tar.gz)

Output is single JSONL with a single entry for each Gigaword document of form

{"filename": filename, "relations": [(kind, arg0, arg1), (kind, arg0, arg1)]}

where "kind" is one of before/after/contained/container and arg0/arg1 are text spans.

Author: Alexandra DeLucia
"""
import pandas as pd
import jsonlines
from tqdm import tqdm
from argparse import ArgumentParser
import pickle
import logging
import tarfile
from collections import Counter
import re
import json
import nltk

from concrete.util import CommunicationReader
from concrete.communication.ttypes import Communication
from typing import Dict, Iterable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

lemmatizer = nltk.stem.WordNetLemmatizer()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--input-file", type=str,
                        help="Tarball of Concrete Gigaword files processed through LOME.")
    parser.add_argument("--output-file", type=str, help="Path to save .jsonl")
    parser.add_argument("--aggregate", action="store_true", help="Aggregate counts from outputted .jsonl. Uses --output-file as input")
    parser.add_argument("--aggregation-output-file", type=str, help="Text file with arg0, arg1, kind, counts separated by tabs")
    parser.add_argument("--key-verbs", type=str, help="JSON file with important PredPatt verbs to limit relations")
    parser.add_argument('--debug', action='store_true')
    parser.add_argument("--log-file", help="Path to log")
    return parser.parse_args()


def aggregate_relations(input_file, output_file):
    punct = re.compile("[.,!?'`;()]")
    argument_counter = Counter()
    with jsonlines.open(input_file) as reader:
        for obj in reader.iter(skip_invalid=True):
            for (kind, arg0, arg1) in obj["relations"]:
                # Store in alphabetical order
                arg0 = punct.sub("", arg0)
                arg1 = punct.sub("", arg1)
                if arg0 < arg1:
                    rel = (arg0, arg1, kind)
                else:
                    rel = (arg1, arg0, kind)
                argument_counter.update([rel])

    with open(output_file, "w") as f:
        for (rel, count) in argument_counter.most_common():
            a = f.write(f"{rel[0]}\t{rel[1]}\t{rel[2]}\t{count}\n")


def get_temporal_relations(comm: Communication, key_verbs: Iterable = None):
    """
    Get before/after/contained/container temporal relations from text
    """
    # 1. Store spans by ID for easy lookup
    spans_by_id = dict(map(lambda x: (x.uuid.uuidString, x.text), comm.situationMentionSetList[0].mentionList))
    # logger.debug(f"{span.situationType=} {span.text=} {span.situationKind=} {span.argumentList}")

    # 2. Get temporal relations
    def extract_relation(sm):
        """
        sm.confidence was always None so I took it out
        situationKind is one of "after", "before", "contained", "container"
        Do not save sm.argumentList[0].role or sm.argumentList[1].role
           because it is always ARG0/ARG1
        """
        kind = sm.situationKind
        arg0 = spans_by_id.get(sm.argumentList[0].situationMentionId.uuidString)
        arg1 = spans_by_id.get(sm.argumentList[1].situationMentionId.uuidString)
        # arg0 = lemmatizer.lemmatize(arg0, pos="v")
        # arg1 = lemmatizer.lemmatize(arg1, pos="v")
        rel = (kind, arg0, arg1)
        # Skip contained/container
        if kind not in {"before", "after"}:
            return
        # Skip tokens not in key verbs
        if key_verbs:
            if arg0 in key_verbs and arg1 in key_verbs:
                return rel
            else:
                return

    try:
        relations = map(extract_relation, comm.situationMentionSetList[1].mentionList)
    except IndexError as err:
        logger.error(f"Error encountered. Returning [] relations.\n{err}")
        return []
    return [r for r in relations if r is not None]


if __name__ == "__main__":
    args = parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.log_file:
        logger.addHandler(logging.FileHandler(args.log_file))

    if args.aggregate:
        logger.info(f"In aggregation mode. Writing to {args.aggregation_output_file}")
        aggregate_relations(args.output_file, args.aggregation_output_file)
        logger.info("Done")
        exit(0)

    with tarfile.open(args.input_file) as archive:
        num_comms = sum(1 for comm in archive if comm.isfile())
        logger.debug(f"{num_comms:,} Communications in {args.input_file}")

    key_verbs = None
    if args.key_verbs:
        try:
            with open(args.key_verbs, "r") as f:
                key_verbs = json.load(f)
                key_verbs = set([lemmatizer.lemmatize(v, pos="v") for v in key_verbs['predpatt']])
                logger.debug(f"{key_verbs=}")
        except json.decoder.JSONDecodeError as err:
            logger.error(f"Issue reading {args.key_verbs}:\n{err}")

    writer = jsonlines.open(args.output_file, "a")
    for comm, filename in tqdm(CommunicationReader(args.input_file), total=num_comms):
        rel = {
            "filename": filename,
            "relations": get_temporal_relations(comm, key_verbs)
        }
        writer.write(rel)
        if args.debug:
            break

    writer.close()
    logger.info("Done")
