from tqdm import tqdm
from .Transformer import Transformer
from ..utils import utilities

EVENT_TYPE_MAPPER_PATH = "data/M2E2/M2E2_event_types.json"
ROLE_MAPPER_PATH = "data/M2E2/M2E2_roles.json"


class M2e2Transformer(Transformer):

    def __init__(self, m2e2_path, stanford_core_path):
        super().__init__(stanford_core_path)
        print("m2e2-transformer intialization")
        self.id_base = "M2E2-instance-"
        self.m2e2_path = m2e2_path
        self.origin = "M2E2"

        # mappers that map roles/eventTypes of M2E2 to the ones of RAMS
        self.event_types_mapper = utilities.read_json(EVENT_TYPE_MAPPER_PATH)
        self.roles_mapper = utilities.read_json(ROLE_MAPPER_PATH)

    # transform dataset to the common schema
    def transform(self):
        new_instances = []
        i = -1
        m2e2_jsons = utilities.read_json(self.m2e2_path)
        for instance in tqdm(m2e2_jsons):
            i += 1
            new_instance_id = self.id_base + str(i) + "-" + instance['sentence_id']
            text_sentence = instance['sentence']
            sentences = [{
                'start': instance['sentence_start'],
                'end': instance['sentence_end'],
                'text': text_sentence
            }]

            # simple parsing - acquire words, lemma, pos-tangs and dependency heads
            parsing = self.simple_parsing(text_sentence)
            lemma = parsing[2]
            words = parsing[0]
            pos_tags = parsing[1]
            conll_head = parsing[3]

            # chunking
            chunks = [self.chunking(words[s['start']: s['end']], pos_tags[s['start']: s['end']]) for s in sentences]

            # advanced parsing - acquire treebank and dependency parsing
            # zip(*list) unzips a list o tuples
            annotations = list(zip(*[self.coreNLP_annotation(s['text']) for s in sentences]))
            penn_treebanks = annotations[0]
            dependency_parsing = annotations[1]

            # adjust entities
            entity_types = {}
            for j, entity in enumerate(instance['golden-entity-mentions']):
                entity['entity-id'] = new_instance_id + "-entity-" + str(j)
                entity['detailed-entity-type'] = ""
                entity_types[entity['text']] = entity['entity-type']

            # adjust events
            if len(instance['golden-event-mentions']) > 0:
                for event in instance['golden-event-mentions']:
                    event_type = event['event_type']
                    event['event_type'] = self.event_types_mapper[event_type]
                    for arg in event['arguments']:
                        role = arg['role']
                        arg['role'] = self.roles_mapper[role]
                        arg['entity-type'] = entity_types[arg['text']]
                        arg['detailed-entity-type'] = ""

            new_instance = {
                'origin': self.origin,
                'id': new_instance_id,
                'no-of-sentences': 1,
                'sentences': sentences,
                'text': text_sentence,
                'words': words,
                'lemma': lemma,
                'pos-tags': pos_tags,
                'head': conll_head,
                'golden-entity-mentions': instance['golden-entity-mentions'],
                'golden-event-mentions': instance['golden-event-mentions'],
                'penn-treebank': penn_treebanks,
                "dependency-parsing": dependency_parsing,
                'chunks': chunks
            }
            new_instances.append(new_instance)
        return new_instances

