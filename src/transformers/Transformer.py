import json
import re
from abc import abstractmethod
import spacy
from ..utils import utilities
from ..utils.chunker import BigramChunker
from stanfordcorenlp import StanfordCoreNLP

ROLES_MAPPER_PATH = "data/roles_mapping.json"
EVENTS_MAPPER_PATH = "data/events_mapping.json"

class Transformer:

    def __init__(self, stanford_core_path):
        print("transformer intialization")
        self.nlp = spacy.load('en_core_web_sm')
        self.snlp = StanfordCoreNLP(stanford_core_path, memory='3g', timeout=10, logging_level="INFO")
        self.chunker = BigramChunker()
        self.roles_mapper = utilities.read_json(ROLES_MAPPER_PATH)
        self.events_mapper = utilities.read_json(EVENTS_MAPPER_PATH)


    def simple_parsing(self, sentence):
        nlp_sentence = self.nlp(sentence)
        lemma = []
        words = []
        pos_tags = []
        conll_head = []
        entity_types = []
        for word in nlp_sentence:
            words.append(word.text)
            lemma.append(word.lemma_)
            pos_tags.append(word.tag_)
            conll_head.append(word.head.i)
            ent_type = word.ent_type_
            if ent_type == 'PERSON':
                ent_type = 'PER'
            entity_types.append(ent_type)

        return words, pos_tags, lemma, conll_head, entity_types

    def coreNLP_annotation(self, sentence):
        snlp_processed_json = self.snlp.annotate(sentence,
                                                 properties={'annotators': 'tokenize,ssplit,pos,lemma,parse'})
        if snlp_processed_json:
            snlp_processed = json.loads(snlp_processed_json)
            treebank = re.sub(r'\n|\s+', ' ', snlp_processed['sentences'][0]['parse'])
            dep_parse = ['{}/dep={}/gov={}'.format(dep['dep'], dep['dependent'] - 1, dep['governor'] - 1)
                         for dep in snlp_processed['sentences'][0]['enhancedPlusPlusDependencies']]
            return treebank, dep_parse
        else:
            return "", []

    def chunking(self, words, tags):
        zipped = list(zip(words, tags))
        s_chunks = self.chunker.parseIOB(zipped)
        return [c[1:] for c in s_chunks]



    @abstractmethod
    def transform(self):
        pass
