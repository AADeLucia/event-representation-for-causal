"""
Output sentences from Gigaword JSONL files as input to Fine-Grained Temporal
Extraction code

Author: Alexandra DeLucia
"""
import jsonlines
from tqdm import tqdm
from argparse import ArgumentParser
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--input-files", nargs="+", help="List of JSONL files")
    parser.add_argument("--output-dir", type=str, help="Output folder to save .txt")
    parser.add_argument('--debug', action='store_true')
    parser.add_argument("--log-file", help="Path to log")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.log_file:
        logger.addHandler(logging.FileHandler(args.log_file))

    for input_file in tqdm(args.input_files):
        with jsonlines.open(input_file) as reader:
            for obj in reader:
                # Name file with ID
                output_file = f"{args.output_dir}/{obj['id']}.txt"
                with open(output_file, "w") as f:
                    f.write("\n".join(obj['text']))
