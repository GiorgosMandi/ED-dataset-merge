from .transformers.RAMS_Trasnformer import RamsTransformer
from .transformers.M2E2_Transformer import M2e2Transformer
from .transformers.ACE_Transformer import AceTransformer
from .transformers.EMM_Transformer import EmmTransformer
from stanfordcorenlp import StanfordCoreNLP

import argparse
import os
import logging
import sys

# TODO:
#  1. TICK adjust everything based on Keys ENUM
#  2. TICK complete schema validator
#  3. TICK fix mentioned bugs
#  4. TICK add argument for mapping
#  5. evaluate script
#  6. TICK empty event types of EMM

log = logging.getLogger("TRANSFORMER")
log.setLevel(logging.DEBUG)
consoleOUT = logging.StreamHandler(sys.stdout)
consoleOUT.setLevel(logging.DEBUG)
formatter = logging.Formatter('\n%(asctime)s - %(name)s - %(levelname)s - %(message)s')
consoleOUT.setFormatter(formatter)
consoleOUT.terminator = ""
log.addHandler(consoleOUT)

log_root = logging.getLogger()
consoleER = logging.StreamHandler(sys.stdout)
consoleER.setLevel(logging.FATAL)
consoleER.setFormatter(formatter)
consoleER.terminator = ""
log_root.addHandler(consoleER)


parser = argparse.ArgumentParser(description="Give arguments")
parser.add_argument('-coreNLP', metavar='coreNLP_path', type=str, help='Path to the pretrained coreNLP model', required=True)
parser.add_argument('-memory', metavar='memory', default="3", type=str, help='CoreNLP memory in GB, default value is 3 GB')
parser.add_argument('-timeout', metavar='timeout', default="10", type=str, help='CoreNLP timeout, default value is 10 sec')

parser.add_argument('-out', metavar='out', type=str, help='Output path', required=True)

parser.add_argument('-emm', metavar='emm_path', type=str, help='Path to the EMM dataset, can be a json file or a folder of jsons')
parser.add_argument('-rams', metavar='rams_path', type=str, help='Path to the RAMS dataset')
parser.add_argument('-m2e2', metavar='m2e2_path', type=str, help='Path to the M2E2 dataset')
parser.add_argument('-ace', metavar='ace_path', type=str, help='Path to the pre-processed ACE dataset')

parser.add_argument('-disableMapping', action='store_true', help='Disable event type mapping matching ')

args = parser.parse_args()
disable_mapping = args.disableMapping
if not os.path.exists(args.coreNLP):
    log.error("CoreNLP path does not exist")
    exit(1)

if not os.path.exists(os.path.dirname(args.out)):
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

if disable_mapping:
    log.info("Disable Mapping event types")

output_path = args.out
log.info("Results will be stored in '" + output_path + "'")

coreNLP = StanfordCoreNLP(args.coreNLP, memory=args.memory + 'g', timeout=int(args.timeout), logging_level=logging.WARNING)
log.info("Initialized Core NLP with " + str(args.memory) + "GB of memory and " + args.timeout + " seconds")

if args.rams:
    if os.path.exists(args.rams):
        log.info("Starting the transformation of RAMS ")
        log.info("RAMS source: '" + args.rams + "'")
        transformer = RamsTransformer(args.rams, coreNLP, disable_mapping)
        transformer.transform(output_path)
    else:
        log.error("RAMS path '" + args.rams + "' does not exist")

if args.emm:
    if os.path.exists(args.emm):
        log.info("Starting the transformation of EMM ")
        log.info("EMM source: '" + args.emm + "'")
        transformer = EmmTransformer(args.emm, coreNLP, disable_mapping)
        transformer.transform(output_path)
    else:
        log.error("EMM path '" + args.emm + "' does not exist")

if args.m2e2:
    if os.path.exists(args.m2e2):
        log.info("Starting the transformation of M2E2 ")
        log.info("M2E2 source: '" + args.m2e2 + "'")
        transformer = M2e2Transformer(args.m2e2, coreNLP, disable_mapping)
        transformer.transform(output_path)
    else:
        log.error("M2E2 path '" + args.m2e2 + "' does not exist")

if args.ace:
    if os.path.exists(args.ace):
        log.info("Starting the transformation of pre-processed ACE ")
        log.info("Ace source: '" + args.ace + "'")
        transformer = AceTransformer(args.ace, coreNLP, disable_mapping)
        transformer.transform(output_path)
    else:
        log.error("ACE path '" + args.ace + "' does not exist")

log.info("Transformation Completed")
print()
