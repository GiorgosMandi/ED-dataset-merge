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

    def advanced_parsing(self, text):
        text = re.sub("-", " - ", text)
        snlp_processed_json = self.snlp.annotate(text, properties={'annotators': 'tokenize,ssplit,pos,lemma,parse,ner',
                                                                   'timeout': '50000',
                                                                    'ner.applyFineGrained': 'false'})
        words = []
        lemma = []
        pos_tags = []
        entity_types = []
        penn_treebanks = []
        dependency_parsing = []
        sentences = []
        texts = []
        if snlp_processed_json:
            snlp_processed = json.loads(snlp_processed_json)
            next_start = 0
            for parsed in snlp_processed['sentences']:

                penn_treebanks.append(re.sub(r'\n|\s+', ' ', parsed['parse']))
                dependency_parsing.append(['{}/dep={}/gov={}'.format(dep['dep'], dep['dependent']-1, dep['governor']-1)
                             for dep in parsed['enhancedPlusPlusDependencies']])
                sentence_words = [token['word'] for token in parsed['tokens']]
                words.extend(sentence_words)
                pos_tags.extend([token['pos'] for token in parsed['tokens']])
                lemma.extend([token['lemma'] for token in parsed['tokens']])

                # applying IOB to named entities
                current_type = "O"
                ner = []
                for token in parsed['tokens']:
                    token_ner = token['ner']
                    if token_ner != "O":
                        if current_type != "O" and current_type == token_ner:
                            ner.append("I-" + current_type)
                        else:
                            current_type = token_ner
                            ner.append("B-" + current_type)
                    else:
                        current_type = "O"
                        ner.append("O")

                entity_types.extend(ner)
                start = next_start
                end = start + len(sentence_words)
                next_start = end
                text = ' '.join(sentence_words)
                texts.append(text)
                sentences.append({'start': start, 'end': end, 'text': text})

                # nlp_sentence = self.nlp(text)
                # head.extend([word.head.i for word in nlp_sentence if word.text != '\''])

        return {'sentences': sentences, 'text': ' '.join(texts), 'words': words, 'pos-tag': pos_tags, 'lemma': lemma,
                'ner': entity_types, 'treebank': penn_treebanks, 'dep-parse': dependency_parsing}

    def chunking(self, words, tags):
        zipped = list(zip(words, tags))
        s_chunks = self.chunker.parseIOB(zipped)
        return [c[1:] for c in s_chunks]

    @abstractmethod
    def transform(self):
        pass
