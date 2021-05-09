'''
Query and filter the docs most salient to a schema using the (pred, arg) Predpatt representation.

Author: Anton Belyy
'''

import json
import lucene

from tqdm import tqdm
from argparse import ArgumentParser

from typing import List
from java.nio.file import Paths
from org.apache.lucene.index import Term
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import Query, BoostQuery, BooleanQuery, BooleanClause, TermQuery
from org.apache.lucene.index import DirectoryReader


def get_query(field: str, tokens: List[str]) -> Query:
    query_builder = BooleanQuery.Builder()
    for token in tokens:
        query_builder.add(TermQuery(Term(field, token)), BooleanClause.Occur.SHOULD)
    return query_builder.build()


def get_combined_query(fields: List[str], tokens_list: List[List[str]], weights: List[float]) -> Query:
    assert len(fields) == len(tokens_list) == len(weights)
    query_builder = BooleanQuery.Builder()
    for field, tokens, weight in zip(fields, tokens_list, weights):
        query_builder.add(BoostQuery(get_query(field, tokens), weight), BooleanClause.Occur.MUST) # TODO: or SHOULD?
    return query_builder.build()

# This is a debugging helper function
def get_documents(filenames):
    pass

def main():
    parser = ArgumentParser()
    parser.add_argument('index_dir', type=str, help='Path to a folder with a (pred, arg) lucene index')
    parser.add_argument('schema_path', type=str, help='Path to an input TXT file with a query schema')
    parser.add_argument('--k', type=int, default=100, help='top-k parameter')
    parser.add_argument('--p_w', type=float, default=1.0, help='pred weight')
    parser.add_argument('--a_w', type=float, default=1.0, help='arg weight')
    parser.add_argument('--pa_w', type=float, default=1.0, help='(pred, arg) weight')
    args = parser.parse_args()

    # Initialize lucene and the JVM
    lucene.initVM()
    directory = SimpleFSDirectory.open(Paths.get(args.index_dir))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    
    # Read the schema
    combined_tokens = [[], # preds
                       [], # args
                       [], # preds_args
                      ]
    with open(args.schema_path) as fin:
        for line in fin:
            arg0, arg1, pred_idx = line.strip().split()
            pred_idx = int(pred_idx)
            assert pred_idx in range(2)
            # Wikidata refs are ignored for now
            arg0 = arg0.split(':')[0]
            arg1 = arg1.split(':')[0]
            pred = [arg0, arg1][pred_idx]
            arg = [arg0, arg1][1 - pred_idx]
            combined_tokens[0].append(pred)
            combined_tokens[1].append(arg)
            combined_tokens[2].append(f'{arg0}_{arg1}_{pred_idx}')

    # Query the docs
    query = get_combined_query(['preds', 'args', 'preds_args'], combined_tokens, [args.p_w, args.a_w, args.pa_w])
    results = [searcher.doc(d.doc).get('filename') for d in searcher.search(query, args.k).scoreDocs]

    print(searcher.count(query))
    print(results)
    import pdb; pdb.set_trace()


if __name__ == '__main__':
    main()
