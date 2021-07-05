from tqdm import tqdm
from .Transformer import Transformer
from ..utils import utilities
from ..conf.Constants import Keys
import time
import re


class M2e2Transformer(Transformer):

    def __init__(self, m2e2_path, model):
        super().__init__(model)
        self.log.info("Initializing M2e2Transformer")
        self.id_base = "M2E2-instance-"
        self.m2e2_path = m2e2_path
        self.origin = "M2E2"

    # transform dataset to the common schema
    # WARNING: Dataset contains errors and inconsistency:
    #   - in its word list, contains characters that do not exist in the actual sentence
    #   - sometimes the '-' separated words are treated as one word and other times as two
    def transform(self, output_path):
        self.log.info("Starts transformation of M2E2")
        start_time = time.monotonic()

        new_instances = []
        i = -1
        m2e2_jsons = utilities.read_json(self.m2e2_path)
        for instance in tqdm(m2e2_jsons):
            i += 1
            new_instance_id = self.id_base + str(i) + "-" + instance['sentence_id']
            text_sentence = instance['sentence']
            try:
                parsing = self.advanced_parsing(text_sentence)
            except ValueError:
                continue
            words = parsing[Keys.WORDS.value]
            lemma = parsing[Keys.LEMMA.value]
            pos_tags = parsing[Keys.POS_TAGS.value]
            ner = parsing[Keys.NER.value]
            sentences = parsing[Keys.SENTENCES.value]

            # sentence centric
            penn_treebanks = parsing[Keys.PENN_TREEBANK.value]
            dependency_parsing = parsing[Keys.PENN_TREEBANK.value]
            chunks = parsing[Keys.CHUNKS.value]
            no_of_sentences = len(sentences)

            # adjust entities
            text_to_entity = {}
            entities = []
            successfully = True
            for j, entity in enumerate(instance['golden-entity-mentions']):
                entity_id = new_instance_id + "-entity-" + str(j)
                existing_ner = entity['entity-type']

                entity_text = ' '.join(instance['words'][entity['start']:entity['end']])
                indices = self.search_text_in_list(entity['start'], entity['end'], entity_text, words)
                entity_start = indices[Keys.START.value]
                entity_end = indices[Keys.END.value]
                if entity_start is None or entity_end is None:
                    successfully = False
                    continue
                entity_text = ' '.join(words[entity_start: entity_end])
                new_ner = utilities.most_frequent(ner[entity_start: entity_end])
                new_entity = {Keys.ENTITY_ID.value: entity_id,
                              Keys.START.value: entity_start,
                              Keys.END.value: entity_end,
                              Keys.TEXT.value: entity_text,
                              Keys.ENTITY_TYPE.value: new_ner,
                              Keys.EXISTING_ENTITY_TYPE.value: existing_ner
                              }
                entities.append(new_entity)
                text_in_dataset = ' '.join(instance['words'][entity['start']: entity['end']])
                text_to_entity[text_in_dataset] = new_entity

            if not successfully:
                self.log.error("\n")
                self.log.error("Failed to parse, skipping instance")
                continue

            # adjust events
            events = []
            if len(instance['golden-event-mentions']) > 0:
                for event in instance['golden-event-mentions']:
                    event_type = self.events_mapper[event['event_type']]
                    event['event_type'] = event_type
                    arguments = []
                    for arg in event['arguments']:
                        role = arg['role'].lower()
                        role = self.roles_mapper[role] if role in self.roles_mapper else role

                        # there are also inconsistencies between arguments' text and entities' text
                        text_in_dataset = ' '.join(instance['words'][arg['start']: arg['end']])
                        corresponding_entity = text_to_entity[text_in_dataset]
                        arguments.append({Keys.START.value: corresponding_entity[Keys.START.value],
                                          Keys.END.value: corresponding_entity[Keys.END.value],
                                          Keys.TEXT.value: corresponding_entity[Keys.TEXT.value],
                                          Keys.ROLE.value: role,
                                          Keys.ENTITY_TYPE.value: corresponding_entity[Keys.ENTITY_TYPE.value],
                                          Keys.EXISTING_ENTITY_TYPE.value: corresponding_entity[Keys.EXISTING_ENTITY_TYPE.value]
                                          })

                    trigger_text = ' '.join(instance['words'][event['trigger']['start']:event['trigger']['end']])
                    indices = self.search_text_in_list(event['trigger']['start'], event['trigger']['end'], trigger_text, words)
                    trigger_start = indices[Keys.START.value]
                    trigger_end = indices[Keys.END.value]
                    if trigger_start is None or trigger_end is None:
                        successfully = False
                        continue
                    trigger_text = ' '.join(words[trigger_start: trigger_end])
                    trigger = {
                        Keys.TEXT.value: trigger_text,
                        Keys.START.value: trigger_start,
                        Keys.END.value: trigger_end
                    }

                    events.append({Keys.ARGUMENTS.value: arguments,
                                   Keys.TRIGGER.value: trigger,
                                   Keys.EVENT_TYPE.value: event_type})
            if not successfully:
                self.log.error("\n")
                self.log.error("Failed to parse trigger, skipping instance")
                continue

            new_instance = {
                Keys.ORIGIN.value: self.origin,
                Keys.ID.value: new_instance_id,
                Keys.NO_SENTENCES.value: no_of_sentences,
                Keys.SENTENCES.value: sentences,
                Keys.TEXT.value: text_sentence,
                Keys.WORDS.value: words,
                Keys.LEMMA.value: lemma,
                Keys.POS_TAGS.value: pos_tags,
                Keys.NER.value: ner,
                Keys.ENTITIES_MENTIONED.value: entities,
                Keys.EVENTS_MENTIONED.value: events,
                Keys.PENN_TREEBANK.value: penn_treebanks,
                Keys.DEPENDENCY_PARSING.value: dependency_parsing,
                Keys.CHUNKS.value: chunks
            }
            new_instances.append(new_instance)
            if len(new_instances) == self.batch_size:
                utilities.write_jsons(new_instances, output_path)
                new_instances = []
        utilities.write_jsons(new_instances, output_path)
        self.log.info("Transformation of M2E2 completed in " + str(round(time.monotonic() - start_time, 3)) + "sec")

    def search_text_in_list(self, initial_start, initial_end, text, parsed_words):

        # to tackle the inconsistencies in the list of words of the dataset,
        # we find the text to the words of our list and make pointers to
        try:
            new_parsed_words = []
            for i, pw in enumerate(parsed_words):
                pw = re.sub(r"-|\'", " ", pw).strip(",. \n\'\"-")
                splits = pw.split()
                for spw in splits:
                    new_parsed_words.append(spw)
                initial_start -= len(splits)
                initial_end += len(splits)
            parsed_words = new_parsed_words

            text_ = re.sub(r"-|\.|\'|\"|‘|’|\[|\]", " ", text).replace("(", " LRB ").replace(")", " RRB ")
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