from .transformers.RAMS_Trasnformer import RamsTransformer
from .transformers.M2E2_Transformer import M2e2Transformer
from .transformers.ACE_Transformer import AceTransformer
from .transformers.EMM_Transformer import EmmTransformer
from stanfordcorenlp import StanfordCoreNLP

import argparse
import os
import logging


log = logging.getLogger()
log.setLevel(logging.INFO)

parser = argparse.ArgumentParser(description="Give arguments")
parser.add_argument('-coreNLP', metavar='coreNLP_path', type=str, help='Path to the pretrained coreNLP model', required=True)
parser.add_argument('-memory', metavar='memory', default="3", type=str, help='CoreNLP memory in GB, default value is 3 GB')
parser.add_argument('-timeout', metavar='timeout', default="10", type=str, help='CoreNLP timeout, default value is 10 sec')

parser.add_argument('-out', metavar='out', type=str, help='Output path', required=True)

parser.add_argument('-emm', metavar='emm_path', type=str, help='Path to the EMM dataset, can be a json file or a folder of jsons')
parser.add_argument('-rams', metavar='rams_path', type=str, help='Path to the RAMS dataset')
parser.add_argument('-m2e2', metavar='m2e2_path', type=str, help='Path to the M2E2 dataset')
parser.add_argument('-ace', metavar='ace_path', type=str, help='Path to the pre-processed ACE dataset')

args = parser.parse_args()
if not os.path.exists(args.coreNLP):
    log.error("CoreNLP path does not exist")
    exit(1)

if not os.path.exists(args.out):
    log.error("Output path does not exist")
    exit(1)

if not args.emm and not args.ace and not args.m2e2 and not args.rams:
    log.error("No input dataset to transform")
    exit(1)

if not args.memory.isdigit():
    log.error("CoreNLP memory value is not a number")
    exit(1)

if not args.timeout.isdigit():
    log.error("CoreNLP timeout value is not a number")
    exit(1)

coreNLP = StanfordCoreNLP(args.coreNLP, memory=args.memory + 'g', timeout=int(args.timeout), logging_level="INFO")
log.info("Initialized Core NLP with " + str(args.memory) + "GB of memory and " + args.timeout + " seconds")

output_path = args.out
log.info("Results will be stored in '" + output_path + "'")

if args.rams:
    if os.path.exists(args.rams):
        log.info("Starts the transformation of RAMS ")
        log.info("RAMS source: '" + args.rams + "'")
        transformer = RamsTransformer(args.rams, coreNLP)
        transformer.transform(output_path)
    else:
        log.error("RAMS path '" + args.rams + "' does not exist")

if args.emm:
    if os.path.exists(args.emm):
        log.info("Starts the transformation of EMM ")
        log.info("EMM source: '" + args.emm + "'")
        transformer = EmmTransformer(args.emm, coreNLP)
        transformer.transform(output_path)
    else:
        log.error("EMM path '" + args.emm + "' does not exist")

if args.m2e2:
    if os.path.exists(args.m2e2):
        log.info("Starts the transformation of M2E2 ")
        log.info("M2E2 source: '" + args.m2e2 + "'")
        transformer = M2e2Transformer(args.m2e2, coreNLP)
        transformer.transform(output_path)
    else:
        log.error("M2E2 path '" + args.m2e2 + "' does not exist")

if args.ace:
    if os.path.exists(args.ace):
        # TODO adjust ACE roles and event types
        log.info("Starts the transformation of pre-processed ACE ")
        log.info("Ace source: '" + args.ace + "'")
        transformer = AceTransformer(args.ace, coreNLP)
        transformer.transform(output_path)
    else:
        log.error("ACE path '" + args.ace + "' does not exist")

log.info("Transformation Completed")
