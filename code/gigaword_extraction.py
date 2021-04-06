'''
Extract (pred, arg) pairs from a Concrete Gigaword .tar.gz.

`pred`s are the roots of PredPatt-identified predicates, `arg`s are either `nsubj` or `dobj` subordinates of `pred`s.

Output is written into a JSONL file.

Author: Alexandra DeLucia and Anton Belyy
'''

import os
import json
import spacy
import tarfile
import jsonlines

from glob import glob
from tqdm import tqdm
from nltk.corpus import wordnet
from argparse import ArgumentParser
from nltk.stem import WordNetLemmatizer
from predpatt import PredPatt, load_comm
from concrete.util import CommunicationReader
from predpatt.util.load import get_udparse, get_tags


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('input_file', help='Path to a Concrete Gigaword tar.gz file')
    parser.add_argument('output_file', type=str, help='Path to a JSONL file')
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()


def comm2sents(comm):
    if comm.sectionList:
        for sec in comm.sectionList:
            if sec.sentenceList:
                for sent in sec.sentenceList:
                    yield sent


def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


if __name__ == '__main__':    
    args = parse_args()
    
    lemmatizer = WordNetLemmatizer()

    with tarfile.open(args.input_file) as archive:
        num_comms = sum(1 for comm in archive if comm.isfile())

    with jsonlines.open(args.output_file, mode='w') as writer:
        for comm, filename in tqdm(CommunicationReader(args.input_file), total=num_comms):
            preds_args = []
            for sent in comm2sents(comm):
                tokens = [x.text for x in sent.tokenization.tokenList.tokenList]
                pos_tags = get_tags(sent.tokenization, 'POS')
                udparse = get_udparse(sent, tool='Stanford CoreNLP basic')
                ppatt = PredPatt(udparse)
                assert len(tokens) == len(pos_tags)
                lemmas = [lemmatizer.lemmatize(x, pos=get_wordnet_pos(y)) for x, y in zip(tokens, pos_tags)]
                for event in ppatt.events:
                    for triple in event.root.dependents:
                         # TODO: extend to other rels?
                        pred_lemma = lemmas[triple.gov.position]
                        arg_lemma = lemmas[triple.dep.position]
                        if triple.rel == 'nsubj':
                            pred_arg = (arg_lemma, pred_lemma, 1)
                        elif triple.rel == 'dobj':
                            pred_arg = (pred_lemma, arg_lemma, 0)
                        else:
                            continue
                        preds_args.append(pred_arg)
            out_jsonl = {'filename': filename, 'preds_args': preds_args}
            writer.write(out_jsonl)

            if args.debug:
                # print(ppatt.pprint(color=True))
                print(out_jsonl)
                break
