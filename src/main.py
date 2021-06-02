from .transformers.RAMS_Trasnformer import RamsTransformer

rams_path = '../data/rams_100.jsonlines'
core_nlp_path = '../model/stanford-corenlp-full-2018-10-05'
transformer = RamsTransformer(rams_path, core_nlp_path)
instances = transformer.transform()
print("done")
