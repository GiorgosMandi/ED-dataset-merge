import json
import re
from abc import abstractmethod
from ..conf import Configuration
from ..utils.chunker import BigramChunker
from ..conf.Constants import Keys
import logging
import spacy


def iob_format(iterable):
    current_type = "O"
    iob_format_tokens = []
    for token in iterable:
        if token != "O":
            if current_type != "O" and current_type == token:
                iob_format_tokens.append("I-" + current_type)
            else:
                current_type = token
                iob_format_tokens.append("B-" + current_type)
        else:
            current_type = "O"
            iob_format_tokens.append("O")
    return iob_format_tokens


class Transformer:

    def __init__(self, model, disable_mapping):
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
        self.disable_mapping = disable_mapping

    def advanced_parsing(self, text):
        words = []
        lemma = []
        pos_tags = []
        ner = []
        penn_treebanks = []
        chunks = []
        dependency_parsing = []
        sentences = []
        texts = []
        next_start = 0
        text = re.sub("-", " - ", text)
        unparsed_sentences = filter(None, text.strip().split(".", ))
        for sentence in unparsed_sentences:
            processed_json = self.coreNLP.annotate(sentence+".", properties={'annotators': 'tokenize,ssplit,pos,'
                                                                                           'lemma,parse,ner',
                                                                             'timeout': '50000'})
            try:
                processed_json = json.loads(processed_json)
                for parsed in processed_json['sentences']:
                    sentence_words = [token['word'] for token in parsed['tokens']]
                    sentence_pos_tags = [token['pos'] for token in parsed['tokens']]
                    sentence_lemma = [token['lemma'] for token in parsed['tokens']]
                    sentence_ner = [token['ner'] for token in parsed['tokens']]
                    words.extend(sentence_words)
                    pos_tags.extend(sentence_pos_tags)
                    lemma.extend(sentence_lemma)
                    ner.extend(iob_format(sentence_ner))

                    start = next_start
                    end = start + len(sentence_words)
                    next_start = end
                    text = ' '.join(sentence_words)
                    texts.append(text)
                    sentences.append({Keys.START.value: start, Keys.END.value: end, Keys.TEXT.value: text})

                    chunks.append(self.chunking(sentence_words, sentence_pos_tags))
                    penn_treebanks.append(re.sub(r'\n|\s+', ' ', parsed['parse']))
                    dependency_parsing.append(
                        ['{}/dep={}/gov={}'.format(dep['dep'], dep['dependent'] - 1, dep['governor'] - 1)
                         for dep in parsed['enhancedPlusPlusDependencies']])

            except json.decoder.JSONDecodeError:
                self.log.error("")
                self.log.error("CoreNLP could not parse the input text. Try increasing timeout and heap memory")
                raise ValueError("CoreNLP could not parse the input text. Try increasing timeout and heap memory")

        return {Keys.SENTENCES.value: sentences, Keys.TEXT.value: ' '.join(texts), Keys.WORDS.value: words,
                Keys.POS_TAGS.value: pos_tags, Keys.LEMMA.value: lemma, Keys.NER.value: ner,
                Keys.PENN_TREEBANK.value: penn_treebanks, Keys.DEPENDENCY_PARSING.value: dependency_parsing,
                Keys.CHUNKS.value: chunks}

    def chunking(self, words, tags):
        zipped = list(zip(words, tags))
        s_chunks = self.chunker.parseIOB(zipped)
        return [c[1:] for c in s_chunks]

    @abstractmethod
    def transform(self, output_path):
        pass

    def get_event_type(self, event_type):
        if self.disable_mapping:
            return event_type
        else:
            return self.events_mapper[event_type]
