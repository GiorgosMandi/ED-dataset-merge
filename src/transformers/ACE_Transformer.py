from .Transformer import Transformer
from tqdm import tqdm
from ..utils import utilities
from ..conf.Constants import Keys

import time


class AceTransformer(Transformer):

    def __init__(self, ace_path, model):
        super().__init__(model)
        self.log.info("Initializing AceTransformer")
        self.id_base = "ACE-instance-"
        self.path = ace_path
        self.origin = "ACE"

    # accumulate and store all the roles/eventTypes
    def export_types(self, roles_path, event_paths):
        events = set()
        roles = set()
        ace_jsons = utilities.read_json(self.path)
        for instance in tqdm(ace_jsons):
            for event in instance['golden-event-mentions']:
                events.add(event['event_type'].replace(":", "."))
                for arg in event['arguments']:
                    roles.add(arg["role"])

        utilities.write_iterable(roles_path, roles)
        utilities.write_iterable(event_paths, events)

    # transform dataset to the common schema
    def transform(self, output_path):
        start_time = time.monotonic()

        self.log.info("Starts transformation of ACE")
        new_instances = []
        i = -1
        ace_jsons = utilities.read_json(self.path)
        for instance in tqdm(ace_jsons):
            i += 1

            new_instance_id = self.id_base + str(i)

            try:
                parsing = self.advanced_parsing(instance['sentence'])
            except ValueError:
                continue
            text_sentence = parsing[Keys.TEXT.value]
            sentences = parsing[Keys.SENTENCES.value]
            words = parsing[Keys.WORDS.value]
            lemma = parsing[Keys.LEMMA.value]
            pos_tags = parsing[Keys.POS_TAGS.value]
            ner = parsing[Keys.NER.value]

            # sentence centric
            penn_treebanks = parsing[Keys.PENN_TREEBANK.value]
            dependency_parsing = parsing[Keys.DEPENDENCY_PARSING.value]
            chunks = parsing[Keys.CHUNKS.value]
            no_of_sentences = len(sentences)

            # adjust entities
            entities = []
            text_to_entity = {}
            for entity in instance["golden-entity-mentions"]:
                existing_entity_type = entity["entity-type"]
                entity_type = utilities.most_frequent(ner[entity['start']: entity['end']])
                text_to_entity[entity['text']] = entity_type
                new_entity = {Keys.START.value: entity['start'],
                              Keys.END.value: entity['end'],
                              Keys.TEXT.value: entity['text'],
                              Keys.ENTITY_ID.value: entity['entity_id'],
                              Keys.ENTITY_TYPE.value: entity_type,
                              Keys.EXISTING_ENTITY_TYPE.value:  existing_entity_type}
                entities.append(new_entity)

            # adjust events
            events = []
            for event in instance['golden-event-mentions']:
                arguments = []
                for arg in event['arguments']:
                    new_arg = {
                        Keys.START.value: arg['start'],
                        Keys.END.value: arg['end'],
                        Keys.TEXT.value: arg['text'],
                        Keys.EXISTING_ENTITY_TYPE.value: arg["entity-type"],
                        Keys.ENTITY_TYPE.value: text_to_entity[arg['text']],
                        Keys.ROLE.value: self.get_role(arg['role'])
                    }
                    arguments.append(new_arg)
                events.append({
                    Keys.ARGUMENTS.value: arguments,
                    Keys.EVENT_TYPE.value: self.get_event_type(event['event_type']),
                    Keys.TRIGGER.value: event['trigger']
                })

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
        self.log.info("Transformation of ACE completed in " + str(round(time.monotonic() - start_time, 3)) + "sec")

    def get_event_type(self, event_type):
        event_type = event_type.replace(":", ".")
        return utilities.find_most_similar(event_type, self.events)

    def get_role(self, role):
        return utilities.find_most_similar(role, self.roles)
