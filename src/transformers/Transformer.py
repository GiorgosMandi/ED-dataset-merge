import json
import re
from abc import abstractmethod

import spacy
from ..utils.chunker import BigramChunker
from stanfordcorenlp import StanfordCoreNLP


class Transformer:

    def __init__(self, stanford_core_path):
        print("transformer intialization")
        self.nlp = spacy.load('en_core_web_sm')
        self.snlp = StanfordCoreNLP(stanford_core_path, memory='2g', timeout=60)
        self.chunker = BigramChunker()

    def read_json(self, path):
        with open(path) as f:
            file = [json.loads(inline_json) for inline_json in f]
        return file

    def simple_parsing(self, sentence):
        nlp_sentence = self.nlp(sentence)
        lemma = []
        words = []
        pos_tags = []
        conll_head = []
        for word in nlp_sentence:
            words.append(word.text)
            lemma.append(word.lemma_)
            pos_tags.append(word.tag_)
            conll_head.append(word.head.i)

        return words, pos_tags, lemma, conll_head

    def coreNLP_annotation(self, sentence):
        snlp_processed_json = self.snlp.annotate(sentence,
                                                 properties={'annotators': 'tokenize,ssplit,pos,lemma,parse'})
        snlp_processed = json.loads(snlp_processed_json)
        treebank = re.sub(r'\n|\s+', ' ', snlp_processed['sentences'][0]['parse'])
        dep_parse = ['{}/dep={}/gov={}'.format(dep['dep'], dep['dependent'] - 1, dep['governor'] - 1)
                     for dep in snlp_processed['sentences'][0]['enhancedPlusPlusDependencies']]
        return treebank, dep_parse

    def chunking(self, words, tags):
        zipped = list(zip(words, tags))
        s_chunks = self.chunker.parseIOB(zipped)
        return [c[1:] for c in s_chunks]

    @abstractmethod
    def transform(self):
        pass
