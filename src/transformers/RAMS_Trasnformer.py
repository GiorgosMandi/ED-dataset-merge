import re
from .Transformer import Transformer
from tqdm import tqdm
from ..utils import utilities
from ..conf.Constants import Keys
import time
import json


class RamsTransformer(Transformer):

    def __init__(self, rams_path, model, disable_mapping):
        super().__init__(model, disable_mapping)
        self.log.info("Initializing RamsTransformer")
        self.id_base = "RAMS-instance-"
        self.rams_path = rams_path
        self.origin = "RAMS"

    def export_types(self):
        events = set()
        roles = set()
        with open(self.rams_path) as json_file:
            for inline_json in tqdm(json_file):
                instance = json.loads(inline_json)
                for triple in instance['gold_evt_links']:
                    event = instance['evt_triggers'][0][2][0][0]
                    if event not in self.events_mapper.keys():
                        events.add(event)
                    role = re.split("\d", triple[2])[-1]
                    if role not in self.roles_mapper.keys():
                        roles.add(role)
        return events, roles

    # transform dataset to the common schema
    def transform(self, output_path):
        self.log.info("Starts transformation of RAMS")
        start_time = time.monotonic()
        new_instances = []
        i = -1
        with open(self.rams_path) as json_file:
            for inline_json in tqdm(json_file):
                instance = json.loads(inline_json)

                i += 1
                default_list_of_words = [w for sentence in instance['sentences'] for w in sentence]
                new_instance_id = self.id_base + str(i) + "-" + instance['doc_key']
                # parsing sentences
                text_sentences = " ".join([t for s in instance['sentences'] for t in s])
                successfully = True

                all_sentences = ". ".join([' '.join(sentence) for sentence in instance['sentences']])
                try:
                    parsing = self.advanced_parsing(all_sentences)
                except ValueError:
                    break
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

                # process entities
                entities = []
                for j, entity in enumerate(instance['ent_spans']):
                    entity_id = new_instance_id + "-entity-" + str(j)

                    # process text of entity
                    entity_start = entity[0]
                    entity_end = entity[1] + 1
                    entity_text = ' '.join(default_list_of_words[entity_start: entity_end])
                    indices = self.search_text_in_list(entity_start, entity_end, entity_text, words)
                    entity_start = indices[Keys.START.value]
                    entity_end = indices[Keys.END.value]
                    if entity_start is None or entity_end is None:
                        successfully = False
                        self.log.error("\n")
                        self.log.error("Failed to parse, skipping instance")
                        break
                    entity_text = ' '.join(words[entity_start: entity_end])

                    # multiple words may result to multiple types - pick the most frequent type
                    entity_type = utilities.most_frequent(ner[entity_start: entity_end])
                    new_entity = {Keys.START.value: entity_start,
                                  Keys.END.value: entity_end,
                                  Keys.TEXT.value: entity_text,
                                  Keys.ENTITY_ID.value: entity_id,
                                  Keys.ENTITY_TYPE.value: entity_type,
                                  Keys.EXISTING_ENTITY_TYPE.value: ""}
                    entities.append(new_entity)

                if not successfully:
                    continue

                # process trigger
                if len(instance['evt_triggers']) > 1:
                    self.log.error("\n")
                    self.log.error("More triggers than expected")
                    continue

                # process text of trigger
                trigger_start = instance['evt_triggers'][0][0]
                trigger_end = instance['evt_triggers'][0][1] + 1
                trigger_text = ' '.join(default_list_of_words[trigger_start: trigger_end])
                indices = self.search_text_in_list(trigger_start, trigger_end, trigger_text, words)
                trigger_start = indices[Keys.START.value]
                trigger_end = indices[Keys.END.value]
                if trigger_start is None or trigger_end is None:
                    self.log.error("\n")
                    self.log.error("Failed to parse, skipping instance")
                    break
                trigger_text = ' '.join(words[trigger_start: trigger_end])
                trigger = {Keys.START.value: trigger_start,
                           Keys.END.value: trigger_end,
                           Keys.TEXT.value: trigger_text}

                # process events - construct event-triples
                event_type = instance['evt_triggers'][0][2][0][0]
                event_type = self.get_event_type(event_type)
                events_triples = []
                arguments = []
                for triple in instance['gold_evt_links']:
                    # process text of argument
                    arg_start = triple[1][0]
                    arg_end = triple[1][1] + 1
                    arg_text = ' '.join(default_list_of_words[arg_start: arg_end])
                    indices = self.search_text_in_list(arg_start, arg_end, arg_text, words)
                    arg_start = indices[Keys.START.value]
                    arg_end = indices[Keys.END.value]
                    if arg_start is None or arg_end is None:
                        self.log.error("\n")
                        self.log.error("Failed to parse, skipping instance")
                        successfully = False
                        break

                    arg_text = ' '.join(words[arg_start: arg_end])
                    entity_type = utilities.most_frequent(ner[arg_start: arg_end])
                    arg_role = re.split("\d", triple[2])[-1]
                    arg_role = self.roles_mapper[arg_role] if arg_role in self.roles_mapper else arg_role
                    argument = {Keys.START.value: arg_start,
                                Keys.END.value: arg_end,
                                Keys.TEXT.value: arg_text,
                                Keys.ROLE.value: arg_role,
                                Keys.ENTITY_TYPE.value: entity_type,
                                Keys.EXISTING_ENTITY_TYPE.value: ""}
                    arguments.append(argument)

                if not successfully:
                    continue
                events_triples.append({Keys.ARGUMENTS.value: arguments,
                                       Keys.TRIGGER.value: trigger,
                                       Keys.EVENT_TYPE.value: event_type})
                new_instance = {
                    Keys.ORIGIN.value: self.origin,
                    Keys.ID.value: new_instance_id,
                    Keys.NO_SENTENCES.value: no_of_sentences,
                    Keys.SENTENCES.value: sentences,
                    Keys.TEXT.value: text_sentences,
                    Keys.WORDS.value: words,
                    Keys.LEMMA.value: lemma,
                    Keys.POS_TAGS.value: pos_tags,
                    Keys.NER.value: ner,
                    Keys.ENTITIES_MENTIONED.value: entities,
                    Keys.EVENTS_MENTIONED.value: events_triples,
                    Keys.PENN_TREEBANK.value: penn_treebanks,
                    Keys.DEPENDENCY_PARSING.value: dependency_parsing,
                    Keys.CHUNKS.value: chunks
                }
                new_instances.append(new_instance)
                if len(new_instances) == self.batch_size:
                    utilities.write_jsons(new_instances, output_path)
                    new_instances = []
        utilities.write_jsons(new_instances, output_path)
        self.log.info("Transformation of RAMS completed in " + str(round(time.monotonic() - start_time, 3)) + "sec")

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