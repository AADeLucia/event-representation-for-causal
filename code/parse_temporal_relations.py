"""
Parse raw timeline/predictions from LOME temporal output (Concrete .tar.gz)

Output is single JSONL with a single entry for each Gigaword document of form

{"filename": filename, "relations": [(kind, arg0, arg1), (kind, arg0, arg1)]}

where "kind" is one of before/after/contained/container and arg0/arg1 are verbs.

Author: Alexandra DeLucia
"""
import pandas as pd
import jsonlines
from tqdm import tqdm
from argparse import ArgumentParser
import pickle
import logging
import tarfile

from concrete.communication.ttypes import Communication
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--input-file", nargs="+", help="Tarball of Concrete Gigaword files processed through LOME.")
    parser.add_argument("--output-file", type=str, help="Path to save .jsonl")
    parser.add_argument('--debug', action='store_true')
    parser.add_argument("--log-file", help="Path to log")
    return parser.parse_args()


def get_temporal_relations(comm: Communication):
    """
    Get before/after/contained/container temporal relations from text
    """
    # 1. Store spans by ID for easy lookup
    spans_by_id = dict(map(lambda x: (x.uuid.uuidString, x.text), comm.situationMentionSetList[0].mentionList))
    # logger.debug(f"{span.situationType=} {span.text=} {span.situationKind=} {span.argumentList}")

    # 2. Get temporal relations
    # sm.confidence was always None so I took it out
    # situationKind is one of "after", "before", "contained", "container"
    def extract_relation(sm):
        return (sm.situationKind,
                # sm.argumentList[0].role,  # always ARG0
                # sm.argumentList[1].role,
                spans_by_id.get(sm.argumentList[0].situationMentionId.uuidString),
                spans_by_id.get(sm.argumentList[1].situationMentionId.uuidString)
                )
    relations = map(extract_relation, comm.situationMentionSetList[1].mentionList)
    return relations


if __name__ == "__main__":
    args = parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.log_file:
        logger.addHandler(logging.FileHandler(args.log_file))

    with tarfile.open(args.input_file) as archive:
        num_comms = sum(1 for comm in archive if comm.isfile())

    writer = jsonlines.open(args.output_file, "w")
    for comm, filename in tqdm(CommunicationReader(input_file, total=num_comms)):
        rel = {
            "filename": filename,
            "relations": list(get_temporal_relations(comm))
        }
        writer.write(rel)

    writer.close()
    logger.info("Done")
