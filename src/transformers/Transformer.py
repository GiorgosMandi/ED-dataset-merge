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
        """
        extract text-based features using coreNLP based on the input text
        :param text:  input text
        :return: a dictionary of features
        """
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

        # big texts lead to error - so we split text into senteces
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

            # failed to parse text, try to increase memory
            except json.decoder.JSONDecodeError:
                self.log.error("")
                self.log.error("CoreNLP could not parse the input text. Try increasing timeout and heap memory")
                raise ValueError("CoreNLP could not parse the input text. Try increasing timeout and heap memory")

        return {Keys.SENTENCES.value: sentences, Keys.TEXT.value: ' '.join(texts), Keys.WORDS.value: words,
                Keys.POS_TAGS.value: pos_tags, Keys.LEMMA.value: lemma, Keys.NER.value: ner,
                Keys.PENN_TREEBANK.value: penn_treebanks, Keys.DEPENDENCY_PARSING.value: dependency_parsing,
                Keys.CHUNKS.value: chunks}

    def chunking(self, words, tags):
        """
        Produce the chunks of the list of words
        :param words: list of words
        :param tags:  list of part of speech of each word
        :return:
        """
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

    def search_text_in_list(self, initial_start, initial_end, text, parsed_words):
        """
                This function finds the pointers of text inside the parsed list of words.
                    - First we clean the text, as it is expected in the words
                    - we get its first an last word and we seek it in the list of words
                    - to tackle inconsistencies, we use spacy parser to parse the text

                :param initial_start:       first index - pointer in the initial list of words (different)
                :param initial_end:         last index - - pointer in the initial list of words (different)
                :param text:                the text we seek to find its pointers in our word list
                :param parsed_words:        our list of words
                :return:                    a dictionary with the starting and the ending indices -
                                            None in case we don't find them
                """
        try:
            new_parsed_words = []
            for i, pw in enumerate(parsed_words):
                pw = re.sub(r"-|\'|/", " ", pw).strip(",. \n\'\"-“”/")
                splits = pw.split()
                for spw in splits:
                    new_parsed_words.append(spw)
                initial_start -= len(splits)
                initial_end += len(splits)
            parsed_words = new_parsed_words

            text_ = re.sub(r"-|\.|\'|\"|‘|’|\[|\]|“|”|/", " ", text).replace("(", " LRB ").replace(")", " RRB ")
            text_ = re.sub(r"(\d\d)pm", r"\1 pm", text_)
            text_ = re.sub(r"(\d\d)am", r"\1 pm", text_)
            parsed = list(filter(lambda name: name.strip(",. \n\'\"-"), [token.text for token in self.nlp(text_)]))

            entity_first_word = parsed[0]
            initial_start = initial_start - 2 if initial_start > 2 else 0
            start = parsed_words[initial_start:].index(entity_first_word) + initial_start

            entity_last_word = parsed[-1]
            initial_end = initial_end + 2 if initial_end > len(parsed_words) - 3 else len(parsed_words) - 1
            end = parsed_words[initial_start:initial_end].index(entity_last_word) + initial_start

            return {Keys.START.value: start, Keys.END.value: end+1}
        except ValueError:
            self.log.error("\n")
            self.log.error("Not able to find '"+text+"' in list of words")
            return {Keys.START.value: None, Keys.END.value: None}