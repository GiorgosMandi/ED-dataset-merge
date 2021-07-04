import re
from .Transformer import Transformer
from tqdm import tqdm
from ..utils import utilities
from ..conf.Constants import Keys
import time
import json


class RamsTransformer(Transformer):

    def __init__(self, rams_path, model):
        super().__init__(model)
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
                new_instance_id = self.id_base + str(i) + "-" + instance['doc_key']
                # parsing sentences
                text_sentences = " ".join([t for s in instance['sentences'] for t in s])
                sentences = []
                words = []
                lemma = []
                pos_tags = []
                entity_types = []
                chunks = []
                penn_treebanks = []
                dependency_parsing = []
                successfully = True

                for sentence in instance['sentences']:
                    sentence = ' '.join(sentence)
                    try:
                        parsing = self.advanced_parsing(sentence)
                    except ValueError:
                        successfully = False
                        break
                    words.extend(parsing[Keys.WORDS.value])
                    lemma.extend(parsing[Keys.LEMMA.value])
                    pos_tags.extend(parsing[Keys.POS_TAGS.value])
                    entity_types.extend(parsing[Keys.NER.value])
                    sentences.extend(parsing[Keys.SENTENCES.value])

                    # sentence centric
                    penn_treebanks.extend(parsing[Keys.PENN_TREEBANK.value])
                    dependency_parsing.extend(parsing[Keys.DEPENDENCY_PARSING.value])
                    chunks.extend(parsing[Keys.CHUNKS.value])

                if not successfully:
                    continue
                no_of_sentences = len(sentences)

                # process entities
                entities = []
                for j, entity in enumerate(instance['ent_spans']):
                    start = entity[0]
                    end = entity[1] + 1
                    text = ' '.join(words[start: end])
                    entity_id = new_instance_id + "-entity-" + str(j)

                    # multiple words may result to multiple types - pick the most frequent type
                    entity_type = utilities.most_frequent(entity_types[start: end])
                    new_entity = {Keys.START.value: start,
                                  Keys.END.value: end,
                                  Keys.TEXT.value: text,
                                  Keys.ENTITY_ID.value: entity_id,
                                  Keys.ENTITY_TYPE.value: entity_type,
                                  Keys.EXISTING_ENTITY_TYPE.value: ""}
                    entities.append(new_entity)

                # process trigger
                if len(instance['evt_triggers']) > 1:
                    self.log.error("\n")
                    self.log.error("ERROR: More triggers than expected")

                trigger_start = instance['evt_triggers'][0][0]
                trigger_end = instance['evt_triggers'][0][1] + 1
                trigger_text = ' '.join(words[trigger_start: trigger_end]).lower()
                trigger = {Keys.START.value: trigger_start,
                           Keys.END.value: trigger_end,
                           Keys.TEXT.value: trigger_text}

                # process events - construct event-triples
                event_type = instance['evt_triggers'][0][2][0][0]
                event_type = self.events_mapper[event_type]
                events_triples = []
                arguments = []
                for triple in instance['gold_evt_links']:
                    arg_start = triple[1][0]
                    arg_end = triple[1][1] + 1
                    text = ' '.join(words[arg_start: arg_end])
                    entity_type = utilities.most_frequent(entity_types[arg_start: arg_end])
                    arg_role = re.split("\d", triple[2])[-1]
                    arg_role = self.roles_mapper[arg_role] if arg_role in self.roles_mapper else arg_role
                    argument = {Keys.START.value: arg_start,
                                Keys.END.value: arg_end,
                                Keys.TEXT.value: text,
                                Keys.ROLE.value: arg_role,
                                Keys.ENTITY_TYPE.value: entity_type,
                                Keys.EXISTING_ENTITY_TYPE.value: ""}
                    arguments.append(argument)

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
                    Keys.NER.value: entity_types,
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
