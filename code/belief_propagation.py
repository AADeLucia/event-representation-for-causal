"""
Belief Propagation inference on the Bayesian graph

Author: Alexandra DeLucia
"""
from argparse import ArgumentParser
from tqdm import tqdm
import logging

from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import BeliefPropagation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument("--log-file", help="Path to log")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.log_file:
        logger.addHandler(logging.FileHandler(args.log_file))

    G = BayesianModel([('diff', 'grade'), ('intel', 'grade'),
                       ('intel', 'SAT'), ('grade', 'letter')])
    diff_cpd = TabularCPD('diff', 2, [[0.2], [0.8]])
    intel_cpd = TabularCPD('intel', 3, [[0.5], [0.3], [0.2]])
    grade_cpd = TabularCPD('grade', 3,
                           [[0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                            [0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                            [0.8, 0.8, 0.8, 0.8, 0.8, 0.8]],
                           evidence=['diff', 'intel'],
                           evidence_card=[2, 3])
    sat_cpd = TabularCPD('SAT', 2,
                         [[0.1, 0.2, 0.7],
                          [0.9, 0.8, 0.3]],
                         evidence=['intel'], evidence_card=[3])
    letter_cpd = TabularCPD('letter', 2,
                            [[0.1, 0.4, 0.8],
                             [0.9, 0.6, 0.2]],
                            evidence=['grade'], evidence_card=[3])
    G.add_cpds(diff_cpd, intel_cpd, grade_cpd, sat_cpd, letter_cpd)
    bp = BeliefPropagation(G)
    bp.calibrate()

    print(bp.get_clique_beliefs())

