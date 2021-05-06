"""

Author: Alexandra DeLucia
"""
import jsonlines
from tqdm import tqdm
from argparse import ArgumentParser
import logging
from collections import Counter
import re
import json
import nltk
import itertools

# import spacy
# spacy.require_gpu()
# nlp = spacy.load("en_core_web_sm")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

lemmatizer = nltk.stem.WordNetLemmatizer()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--input-files", nargs="+", help="Text files from CausalBank")
    parser.add_argument("--output-file", type=str, help="Path to save causation counts")
    parser.add_argument("--aggregate", action="store_true", help="Aggregate counts from outputted .jsonl. Uses --output-file as input")
    parser.add_argument("--aggregation-output-file", type=str, help="Text file with arg0, arg1, kind, counts separated by tabs")
    parser.add_argument("--key-verbs", type=str, help="JSON file with important PredPatt verbs to limit relations")
    parser.add_argument('--debug', action='store_true')
    parser.add_argument("--log-file", help="Path to log")
    return parser.parse_args()


def get_verb_spacy(sentence, key_verbs):
    doc = nlp(sentence)
    verbs = []
    for token in doc:
        if token.pos_ == "VERB" and token.lemma_ in key_verbs:
            verbs.append(token.lemma_)
    return set(verbs)


def get_verb(sentence, key_verbs):
    sentence = nltk.word_tokenize(sentence)
    verbs = []
    for (token, pos) in nltk.pos_tag(sentence):
        if pos == "VB" and lemmatizer.lemmatize(token, pos="v") in key_verbs:
            verbs.append(lemmatizer.lemmatize(token, pos="v"))
    return set(verbs)


if __name__ == "__main__":
    args = parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.log_file:
        logger.addHandler(logging.FileHandler(args.log_file))

    key_verbs = None
    if args.key_verbs:
        with open(args.key_verbs, "r") as f:
            key_verbs = json.load(f)
        for schema in key_verbs:
            key_verbs[schema] = set(key_verbs[schema])

    causations = {schema: Counter() for schema in key_verbs}
    for input_file in args.input_files:
        logger.info(f"On {input_file}")
        with open(input_file) as f:
            for line in tqdm(f.readlines()):
                # "because" pattern where the effect is followed by the cause
                separator, effect, cause = line.split("\t")

                for schema, verbs in key_verbs.items():
                    # Get cause and effect verbs
                    # Skip sentence if there is no verb in cause part
                    cause_verbs = get_verb(cause, verbs)
                    if not cause_verbs:
                        continue
                    effect_verbs = get_verb(effect, verbs)
                    if not effect_verbs:
                        continue

                    # Get all combinations of cause verbs to effect verbs
                    combos = [i for i in itertools.product(cause_verbs, effect_verbs)]
                    logger.debug(f"{combos=}")
                    causations[schema].update(combos)

        if args.debug:
            break

        # Write out checkpoints after each file
        for schema in causations:
            with open(f"{args.output_file}_{schema}", "w") as f:
                for (ce, count) in causations[schema].items():
                    f.write(f"{ce[0]}\t{ce[1]}\t{count}\n")
