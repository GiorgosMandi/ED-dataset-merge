from .Transformer import Transformer
from tqdm import tqdm
from ..utils import utilities

EVENT_TYPE_MAPPER_PATH = "data/ACE/ACE_events_mapping.json"
ROLE_MAPPER_PATH = "data/ACE/ACE_roles_mapping.json"

class AceTransformer(Transformer):

    def __init__(self, ace_path, stanford_core_path):
        super().__init__(stanford_core_path)
        print("ace-transformer intialization")
        self.id_base = "ACE-instance-"
        self.path = ace_path
        self.origin = "ACE"

        self.event_types_mapper = utilities.read_json(EVENT_TYPE_MAPPER_PATH)
        self.roles_mapper = utilities.read_json(ROLE_MAPPER_PATH)

    def process_event(self, event_type):
        return event_type.replace(":", ".").replace("-", "")

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

    def transform(self):
        new_instances = []
        i = -1
        ace_jsons = utilities.read_json(self.path)
        for instance in tqdm(ace_jsons):
            i += 1
            no_of_sentences = 1

            new_instance_id = self.id_base + str(i)
            text_sentence = instance['sentence']
            sentences = [{
                'start': 0,
                'end': len(instance['words']),
                'text': text_sentence
            }]

            parsing = self.simple_parsing(text_sentence)
            lemma = parsing[2]
            words = parsing[0]
            pos_tags = parsing[1]
            conll_head = parsing[3]

            # chunking
            chunks = [self.chunking(words[s['start']: s['end']], pos_tags[s['start']: s['end']]) for s in sentences]

            # zip(*list) unzips a list o tuples
            annotations = list(zip(*[self.coreNLP_annotation(s['text']) for s in sentences]))
            penn_treebanks = annotations[0]
            dependency_parsing = annotations[1]

            entities = []
            for entity in instance["golden-entity-mentions"]:
                entity_type = entity["entity-type"].split(":")
                new_entity = {'start': entity['start'], 'end': entity['end'], 'text': entity['text'],
                              'entity-id': entity['entity_id'], "entity-type": entity_type[0],
                              "detailed-entity-type":  entity_type[1]}
                entities.append(new_entity)

            for event in instance['golden-event-mentions']:
                processed_event = self.process_event(event['event_type'])
                event['event_type'] = self.event_types_mapper[processed_event]
                for arg in event['arguments']:
                    entity_type = arg["entity-type"].split(":")
                    arg["entity-type"] = entity_type[0]
                    arg["detailed-entity-type"] = entity_type[1]
                    role = arg['role']
                    arg["role"] = self.roles_mapper[role]

            new_instance = {
                'origin': self.origin,
                'id': new_instance_id,
                'no-of-sentences': no_of_sentences,
                'sentences': sentences,
                'text': text_sentence,
                'words': words,
                'lemma': lemma,
                'pos-tags': pos_tags,
                'head': conll_head,
                'golden-entity-mentions': entities,
                'golden-event-mentions': instance['golden-event-mentions'],
                'penn-treebank': penn_treebanks,
                "dependency-parsing": dependency_parsing,
                'chunks': chunks
            }
            new_instances.append(new_instance)
        return new_instances
