from .Transformer import Transformer
from tqdm import tqdm
from ..utils import utilities
import time


class AceTransformer(Transformer):

    def __init__(self, ace_path, model):
        super().__init__(model)
        self.log.info("Initializing AceTransformer")
        self.id_base = "ACE-instance-"
        self.path = ace_path
        self.origin = "ACE"

    # process eventTypes to be more lookalike with the ones of rams
    def process_event(self, event_type):
        return event_type.replace(":", ".")

    # accumulate and store all the roles/eventTypes
    def export_types(self, roles_path, event_paths):
        events = set()
        roles = set()
        ace_jsons = utilities.read_json(self.path)
        for instance in tqdm(ace_jsons):
            for event in instance['golden-event-mentions']:
                events.add(self.process_event(event['event_type']))
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
            text_sentence = instance['sentence']

            try:
                parsing = self.advanced_parsing(text_sentence)
            except ValueError:
                continue
            sentences = parsing['sentences']
            words = parsing['words']
            lemma = parsing['lemma']
            pos_tags = parsing['pos-tag']
            entity_types = parsing['ner']

            # sentence centric
            penn_treebanks = parsing['treebank']
            dependency_parsing = parsing['dep-parse']
            chunks = parsing['chunks']
            no_of_sentences = len(sentences)

            # adjust entities
            entities = []
            text_to_entity = {}
            for entity in instance["golden-entity-mentions"]:
                existing_entity_type = entity["entity-type"]
                entity_type = utilities.most_frequent(entity_types[entity['start']: entity['end']])
                text_to_entity[entity['text']] = entity_type
                new_entity = {'start': entity['start'], 'end': entity['end'], 'text': entity['text'],
                              'entity-id': entity['entity_id'], "entity-type": entity_type,
                              "existing-entity-type":  existing_entity_type}
                entities.append(new_entity)

            # adjust events
            for event in instance['golden-event-mentions']:
                event['event-type'] = self.get_event_type(event['event_type'])
                del event['event_type']
                for arg in event['arguments']:
                    arg["existing-entity-type"] = arg["entity-type"]
                    arg["entity-type"] = text_to_entity[arg['text']]
                    role = arg['role']
                    arg["role"] = self.get_role(role)

            new_instance = {
                'origin': self.origin,
                'id': new_instance_id,
                'no-of-sentences': no_of_sentences,
                'sentences': sentences,
                'text': text_sentence,
                'words': words,
                'lemma': lemma,
                'pos-tags': pos_tags,
                'ner': entity_types,
                'golden-entity-mentions': entities,
                'golden-event-mentions': instance['golden-event-mentions'],
                'penn-treebank': penn_treebanks,
                "dependency-parsing": dependency_parsing,
                'chunks': chunks
            }
            new_instances.append(new_instance)
            if len(new_instances) == self.batch_size:
                utilities.write_jsons(new_instances, output_path)
                new_instances = []
        utilities.write_jsons(new_instances, output_path)
        self.log.info("Transformation of ACE completed in " + str(round(time.monotonic() - start_time, 3)) + "sec")

    def get_event_type(self, event_type):
        event_type = self.process_event(event_type)
        return utilities.find_most_similar(event_type, self.events)

    def get_role(self, role):
        return utilities.find_most_similar(role, self.roles)

