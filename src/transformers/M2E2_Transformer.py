from tqdm import tqdm
from .Transformer import Transformer
from ..utils import utilities


class M2e2Transformer(Transformer):

    def __init__(self, m2e2_path, stanford_core_path):
        super().__init__(stanford_core_path)
        print("m2e2-transformer intialization")
        self.id_base = "M2E2-instance-"
        self.m2e2_path = m2e2_path
        self.origin = "M2E2"

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

            parsing = self.advanced_parsing(text_sentence)
            words = parsing['words']
            lemma = parsing['lemma']
            pos_tags = parsing['pos-tag']
            # head = parsing['head']

            # sentence centric
            penn_treebanks = [parsing['treebank']]
            dependency_parsing = [parsing['dep-parse']]
            chunks = [self.chunking(parsing['words'], parsing['pos-tag'])]
            no_of_sentences = len(sentences)

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
                    event['event_type'] = self.events_mapper[event_type]
                    for arg in event['arguments']:
                        role = arg['role'].lower()
                        arg['role'] = self.roles_mapper[role]
                        arg['entity-type'] = entity_types[arg['text']]
                        arg['detailed-entity-type'] = ""

            new_instance = {
                'origin': self.origin,
                'id': new_instance_id,
                'no-of-sentences': no_of_sentences,
                'sentences': sentences,
                'text': text_sentence,
                'words': words,
                'lemma': lemma,
                'pos-tags': pos_tags,
                # 'head': head,
                'golden-entity-mentions': instance['golden-entity-mentions'],
                'golden-event-mentions': instance['golden-event-mentions'],
                'penn-treebank': penn_treebanks,
                "dependency-parsing": dependency_parsing,
                'chunks': chunks
            }
            new_instances.append(new_instance)
        return new_instances

