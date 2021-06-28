import json
import re
from abc import abstractmethod
import spacy
from . import Configuration
from ..utils.chunker import BigramChunker

import logging


class Transformer:

    def __init__(self, model):
        self.log = logging.getLogger()
        self.log.setLevel(logging.INFO)
        self.log.info("Initializing Transformer")
        self.nlp = spacy.load('en_core_web_sm')
        self.coreNLP = model

        self.log.info("Initializing Chunker")
        self.chunker = BigramChunker()
        self.roles_mapper = Configuration.roles_mapping
        self.roles = Configuration.roles
        self.events_mapper = Configuration.events_mapping
        self.events = Configuration.events
        self.batch_size = 50

    def advanced_parsing(self, text):
        text = re.sub("-", " - ", text)
        processed_json = self.coreNLP.annotate(text, properties={'annotators': 'tokenize,ssplit,pos,lemma,parse,ner',
                                                                   'timeout': '50000'})
        words = []
        lemma = []
        pos_tags = []
        entity_types = []
        penn_treebanks = []
        chunks = []
        dependency_parsing = []
        sentences = []
        texts = []
        if processed_json:
            try:
                processed_json = json.loads(processed_json)
                next_start = 0
                for parsed in processed_json['sentences']:

                    sentence_words = [token['word'] for token in parsed['tokens']]
                    sentence_pos_tags = [token['pos'] for token in parsed['tokens']]
                    words.extend(sentence_words)
                    pos_tags.extend(sentence_pos_tags)
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

                    chunks.append(self.chunking(sentence_words, sentence_pos_tags))
                    penn_treebanks.append(re.sub(r'\n|\s+', ' ', parsed['parse']))
                    dependency_parsing.append(
                        ['{}/dep={}/gov={}'.format(dep['dep'], dep['dependent'] - 1, dep['governor'] - 1)
                         for dep in parsed['enhancedPlusPlusDependencies']])

            except json.decoder.JSONDecodeError:
                self.log.error("Exception reading CoreNLP's results\n CoreNLP -> resulted JSON: \n" + processed_json)

        return {'sentences': sentences, 'text': ' '.join(texts), 'words': words, 'pos-tag': pos_tags, 'lemma': lemma,
                'ner': entity_types, 'treebank': penn_treebanks, 'dep-parse': dependency_parsing, 'chunks': chunks}

    def chunking(self, words, tags):
        zipped = list(zip(words, tags))
        s_chunks = self.chunker.parseIOB(zipped)
        return [c[1:] for c in s_chunks]

    @abstractmethod
    def transform(self, output_path):
        pass
