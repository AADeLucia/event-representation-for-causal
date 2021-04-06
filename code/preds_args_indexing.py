'''
Indexes (pred, arg) PredPatt pairs with Apache Lucene.

Author: Anton Belyy
'''

import os
import json
import regex
import lucene
import jsonlines
import collections

from tqdm import tqdm
from glob import glob
from java.nio.file import Paths
from argparse import ArgumentParser
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, Field, StoredField, TextField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('input_dir', help='Path to a dir with JSONL files with PredPatt (pred, arg) pairs')
    parser.add_argument('output_dir', type=str, help='Path to a Lucene index dir')
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    # Initialize lucene and the JVM
    lucene.initVM()

    # Get and configure an IndexWriter
    directory = SimpleFSDirectory.open(Paths.get(args.output_dir))
    analyzer = WhitespaceAnalyzer()
    config = IndexWriterConfig(analyzer)
    writer = IndexWriter(directory, config)

    # Index the documents
    escape_pa_regex = regex.compile('[\s_]+')
    num_indexed_docs = 0
    for input_file in tqdm(glob(f'{args.input_dir}/*.jsonl')):
        with jsonlines.open(input_file) as reader:
            for doc in reader:
                filename = doc['filename']
                preds_args = [(escape_pa_regex.sub('', pred), escape_pa_regex.sub('', arg), pos) for pred, arg, pos in doc['preds_args']]
                preds_args_str = ' '.join(f'{pred}_{arg}_{pos}' for pred, arg, pos in preds_args)
                preds_str = ' '.join(pred for pred, _, _ in preds_args)
                args_str = ' '.join(arg for _, arg, _ in preds_args)
                lucene_doc = Document()
                lucene_doc.add(StoredField('filename', filename))
                lucene_doc.add(TextField('preds_args', preds_args_str, Field.Store.YES))
                lucene_doc.add(TextField('preds', preds_str, Field.Store.YES))
                lucene_doc.add(TextField('args', args_str, Field.Store.YES))
                writer.addDocument(lucene_doc)
                num_indexed_docs += 1
                if args.debug:
                    print(filename)
                    print(preds_args_str)
                    print(preds_str)
                    print(args_str)
                    break
        if args.debug:
            break

    writer.close()

    print(f'Indexed {num_indexed_docs} docs')
