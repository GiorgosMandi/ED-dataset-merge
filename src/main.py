from .transformers.RAMS_Trasnformer import RamsTransformer
from .transformers.M2E2_Transformer import M2e2Transformer

rams_path = '../data/rams_100.jsonlines'
core_nlp_path = '../model/stanford-corenlp-full-2018-10-05'
# transformer = RamsTransformer(rams_path, core_nlp_path)

m2e2_path = '../data/M2E2_tmp.json'
transformer = M2e2Transformer(m2e2_path, core_nlp_path)

instances = transformer.transform()
print("done")
