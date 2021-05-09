'''
Extract FrameNet frames and args from a Concrete Gigaword JSONL file.

Frames are idenfified using spanfinder.

Output is written into a JSONL file.

Author: Anton Belyy
'''

import os
import time
import json
import spacy
import tarfile
import jsonlines
import collections

from glob import glob
from tqdm import tqdm
from sftp import SpanPredictor
from nltk.corpus import wordnet
from spacy.lang.en import English
from argparse import ArgumentParser
from nltk.stem import WordNetLemmatizer
from predpatt import PredPatt, load_comm
from concrete.util import CommunicationReader
from predpatt.util.load import get_udparse, get_tags


SFTP_MODEL_PATH = '/srv/local1/gqin2/release/sftp/0.0.2/framenet/model.tar.gz'


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('input_file', help='Path to a Concrete Gigaword JSONL file')
    parser.add_argument('output_file', type=str, help='Path to an output JSONL file with frames')
    parser.add_argument('--input_ids_file', type=str, help='Path to a TXT file specifying a subset of IDs that need to be processed')
    parser.add_argument('--cuda_device', type=int, default=-1, help='CUDA device for spanfinder')
    return parser.parse_args()


if __name__ == '__main__':    
    args = parse_args()
    
    # Load spacy and sftp
    nlp = English()
    tokenizer = nlp.tokenizer
    span_predictor = SpanPredictor.from_path(SFTP_MODEL_PATH, cuda_device=args.cuda_device)
    span_predictor.economize(max_recursion_depth=1)
    
    # Count number of lines in input
    with open(args.input_file) as fin:
        num_docs = sum(1 for _ in fin)

    if args.input_ids_file is None:
        subset_input_ids = None
    else:
        with open(args.input_ids_file) as fin:
            subset_input_ids = {line.strip() for line in fin}

    sftp_input = []
    sftp_metas = []
    with jsonlines.open(args.input_file) as reader:
        for doc in tqdm(reader, total=num_docs):
            if subset_input_ids is None or doc['id'] in subset_input_ids:
                sents = doc['text']
                for sent_id, sent in enumerate(sents):
                    sftp_metas.append({'doc_id': doc['id'], 'sent_id': sent_id})
                    sftp_input.append([str(x) for x in tokenizer(sent)])
#     # !!! TODO: remove !!!
#     sftp_input = sftp_input[:10]
#     sftp_metas = sftp_metas[:10]

    # Run SFTP parser
    sftp_start_time = time.time()
    sftp_output = span_predictor.predict_batch_sentences(sftp_input, max_tokens=1024, progress=True)
    sftp_end_time = time.time()
    print(f'SFTP time: {sftp_end_time - sftp_start_time:.1f} seconds')
    
    # Gather SFTP outputs to form JSONL outputs
    assert len(sftp_input) == len(sftp_metas) == len(sftp_output)
    docs_sents_frames = collections.defaultdict(list)
    for meta, out in zip(sftp_metas, sftp_output):
        doc_id = meta['doc_id']
        sent_frames = [span.label for span in out.span]
        docs_sents_frames[doc_id].append(sent_frames)
    
    with jsonlines.open(args.output_file, mode='w') as writer:
        for doc_id, sents_frames in docs_sents_frames.items():
            out_json = {'id': doc_id, 'frames': sents_frames}
            writer.write(out_json)
