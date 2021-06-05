from .transformers.RAMS_Trasnformer import RamsTransformer
from .transformers.M2E2_Transformer import M2e2Transformer
from .transformers.ACE_Transformer import AceTransformer
import argparse

import os

parser = argparse.ArgumentParser(description="Give arguments")
parser.add_argument('-base', metavar='base_path', type=str, help='Path of working folder')
parser.add_argument('-dt', metavar='base_path', type=str, help='witch dataset to transform')

args = parser.parse_args()
os.chdir(args.base)

core_nlp_path = 'model/stanford-corenlp-full-2018-10-05'
rams_path = 'data/rams_100.jsonlines'
m2e2_path = 'data/article_0816_filter.json'
ace_path = 'data/ace.json'

if args.dt == "rams":
    transformer = RamsTransformer(rams_path, core_nlp_path)
    instances = transformer.transform()

elif args.dt == "m2e2":
    transformer = M2e2Transformer(m2e2_path, core_nlp_path)
    instances = transformer.transform()

elif args.dt == "ace":
    transformer = AceTransformer(ace_path, core_nlp_path)
    instances = transformer.transform()

elif args.dt == "all":
    rams_transformer = RamsTransformer(rams_path, core_nlp_path)
    rams_instances = rams_transformer.transform()

    m2e2_transformer = M2e2Transformer(m2e2_path, core_nlp_path)
    m2e2_instances = m2e2_transformer.transform()


print("done")
