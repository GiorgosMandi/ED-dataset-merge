from .utils import utilities
from .conf.Constants import Keys
import argparse
import logging


class ValidateTransformation:
    def __init__(self):
        self.log = logging.getLogger()
        self.log.setLevel(logging.NOTSET)

    def test_pointers(self, text, start, end, words):
        try:
            new_text = ' '.join(words[start:end])
            if utilities.string_similarity(new_text, text) < 0.9:
                return False
            return True
        except IndexError:
            self.log.error("Index ERROR: Text'" + text + "' not found in the list of words")
            return False

    def validate_parsing(self, parsing_dict):

        # test all fields exists
        assert(Keys.SENTENCES.value in parsing_dict and
               Keys.TEXT.value in parsing_dict and
               Keys.WORDS.value in parsing_dict and
               Keys.LEMMA.value in parsing_dict and
               Keys.POS_TAGS.value in parsing_dict and
               Keys.NER.value in parsing_dict and
               Keys.PENN_TREEBANK.value in parsing_dict and
               Keys.DEPENDENCY_PARSING.value in parsing_dict and
               Keys.CHUNKS.value in parsing_dict)

        # test word-centric features
        assert(len(parsing_dict[Keys.WORDS.value]) == len(parsing_dict[Keys.LEMMA.value]) and
               len(parsing_dict[Keys.WORDS.value]) == len(parsing_dict[Keys.POS_TAGS.value]) and
               len(parsing_dict[Keys.WORDS.value]) == len(parsing_dict[Keys.NER.value]))

        # test sentences-centric features
        assert (parsing_dict[Keys.NO_SENTENCES.value] == len(parsing_dict[Keys.SENTENCES.value]) and
                parsing_dict[Keys.NO_SENTENCES.value] == len(parsing_dict[Keys.PENN_TREEBANK.value]) and
                parsing_dict[Keys.NO_SENTENCES.value] == len(parsing_dict[Keys.CHUNKS.value]) and
                parsing_dict[Keys.NO_SENTENCES.value] == len(parsing_dict[Keys.DEPENDENCY_PARSING.value]))

        # test chunks
        assert(len(parsing_dict[Keys.WORDS.value]) == len([c for ch in parsing_dict[Keys.CHUNKS.value] for c in ch]))

        words = parsing_dict[Keys.WORDS.value]

        # test sentences
        for sentence in parsing_dict[Keys.SENTENCES.value]:
            assert (self.test_pointers(sentence[Keys.TEXT.value],
                                       sentence[Keys.START.value],
                                       sentence[Keys.END.value],
                                       words))

        # test entities
        for entity in parsing_dict[Keys.ENTITIES_MENTIONED.value]:
            assert(self.test_pointers(entity[Keys.TEXT.value],
                                      entity[Keys.START.value],
                                      entity[Keys.END.value],
                                      words))

        # test events
        for event in parsing_dict[Keys.EVENTS_MENTIONED.value]:
            # test trigger
            assert(self.test_pointers(event[Keys.TRIGGER.value][Keys.TEXT.value],
                                      event[Keys.TRIGGER.value][Keys.START.value],
                                      event[Keys.TRIGGER.value][Keys.END.value],
                                      words))
            # test arguments
            for arg in event[Keys.ARGUMENTS.value]:
                assert(self.test_pointers(arg[Keys.TEXT.value],
                                          arg[Keys.START.value],
                                          arg[Keys.END.value],
                                          words))
        self.log.info("Parsing completed Successfully")
        self.log.info("Document is correct")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Give arguments")
    parser.add_argument('-input', metavar='input', type=str, help='Path to the json to validate', required=True)
    args = parser.parse_args()
    jsons = utilities.read_jsonlines(args.input)
    validator = ValidateTransformation()
    for json in jsons:
        validator.validate_parsing(json)