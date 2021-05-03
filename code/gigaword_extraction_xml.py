"""
Filter Gigaword documents to only NYT articles that contain specified keywords.

Keywords are organized into topics. The output is one file per topic.

Author: Alexandra DeLucia
"""
from argparse import ArgumentParser
import gzip
import xml.etree.ElementTree as ET
import os
from tqdm import tqdm
import jsonlines as jl
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--input-files", nargs="+", help="GZIP'd XML files from Gigaword")
    parser.add_argument("--output-dir", type=str, help="Save location")
    parser.add_argument("--topic-keywords", type=str, help="TSV format with <topic>\t<keywords>")
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def get_topic(sentences, topic_keywords):
    return None


if __name__ == "__main__":
    args = parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    # Parse topic keywords into usable dictionary/set
    topic_keywords = None

    for input_file in tqdm(args.input_files):
        documents = []
        # <FILE><DOC><HEADLINE><DATELINE><TEXT><P></P></TEXT><sentences><coreferences></FILE>
        # Skip <coferences> and <sentences>
        # Keep DOC id, headline
        # DOC types are story, advis, and multi
        with gzip.open(input_file, "rt") as f:
            # Parse XML
            root = ET.fromstring(f.read())
            # Save file ID
            file_id = root.attrib.get("id")

            # Iterate through articles in file
            for child in root:
                document = {
                    "doc_id": child.attrib.get("id"),
                    "type": child.attrib.get("type"),
                    "file_id": file_id,
                    "dateline": child.find("DATELINE").text.strip() if child.find("DATELINE") else None,
                    "headline": child.find("HEADLINE").text.strip() if child.find("HEADLINE") else None,
                    "sentences": [s.text.strip() for s in child.find("TEXT")]  # Get sentences
                }
                document["topic"] = get_topic(document["sentences"], topic_keywords)
                documents.append(document)

            # Write out
            output_file = f"{args.output_dir}/{file_id}.jsonl.gz"
            with gzip.open(output_file, "wt") as fo:
                with jl.Writer(fo) as writer:
                    writer.write_all(documents)

        if args.debug:
            break
