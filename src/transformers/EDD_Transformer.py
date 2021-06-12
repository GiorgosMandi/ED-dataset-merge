from .Transformer import Transformer
from tqdm import tqdm
from ..utils import utilities
import re
import os


class EDDTransformer(Transformer):

    def __init__(self, edd_path, stanford_core_path):
        super().__init__(stanford_core_path)
        print("edd-transformer initialization")
        self.id_base = "EDD-instance-"
        self.path = edd_path
        self.origin = "EDD"

    # accumulate and store all the roles/eventTypes
    def export_types(self, roles_path, event_paths):
        events = set()
        roles = set()

        for file in os.listdir(self.path):
            json_file = self.path + file
            edd_jsons = utilities.read_json(json_file)
            for instance in edd_jsons:
                instance_result = instance['completions'][0]['result']

                for i, result in enumerate(instance_result):
                    value = result['value']
                    if result['from_name'] == "ev_type":
                        event = value['choices'][0]
                        event = re.sub(r"\s+", ".", event.lower())
                        events.add(event)
                    elif value['labels'][0] != 'Event Trigger':
                        role = value['labels'][0]
                        role = re.sub(r"\s+", ".", role.lower())
                        roles.add(role)

        utilities.write_iterable(roles_path, roles)
        utilities.write_iterable(event_paths, events)


    def transform(self):
        new_instances = []
        i = -1
        for file in tqdm(os.listdir(self.path)):
            json_file = self.path + file
            edd_jsons = utilities.read_json(json_file)
            for instance in edd_jsons:
                instance_data = instance['data']

                new_instance_id = self.id_base + "-" + instance_data['filename'] + str(i)
                text_sentence = re.sub(r'(?<!\.)\n', ' . ', instance_data['text']).replace("\n", "")

                sentences = []
                words = []
                lemma = []
                pos_tags = []
                entity_types = []
                chunks = []
                penn_treebanks = []
                dependency_parsing = []
                for sentence in filter(None, text_sentence.strip().split(".", )):
                    parsing = self.advanced_parsing(sentence)
                    words.extend(parsing['words'])
                    pos_tags.extend(parsing['pos-tag'])
                    lemma.extend(parsing['lemma'])
                    # conll_head.extend(parsing['head'])
                    entity_types.extend(parsing['ner'])
                    sentences.extend(parsing['sentences'])
                    penn_treebanks.extend(parsing['treebank'])
                    dependency_parsing.extend(parsing['dep-parse'])
                    chunks.extend([self.chunking(parsing['words'], parsing['pos-tag'])])

                no_of_sentences = len(sentences)

                event_type = ""
                trigger = {}
                arguments = []
                entities = []
                instance_result = instance['completions'][0]['result']
                for i, result in enumerate(instance_result):
                    if result['from_name'] == "ev_type":
                        event_type = result['value']['choices'][0].lower()
                        event_type = self.events_mapper[event_type]
                    else:
                        value = result['value']
                        entity_start = value['start']
                        entity_end = value['end']
                        entity_text = value['text']
                        role = value['labels'][0].lower()
                        if role == 'event trigger':
                            trigger = {'start': entity_start, 'end': entity_end, 'text': entity_text}
                        else:
                            entity_id = new_instance_id + "-" + str(i)
                            types = set(entity_types[entity_start: entity_end])
                            entity_type = ""
                            if len(types) > 0:
                                entity_type = utilities.most_frequent(entity_types[entity_start: entity_end])

                            entity = {'start': entity_start, 'end': entity_end, 'text': entity_text, 'entity-id': entity_id,
                                      'entity-type': entity_type, 'detailed-entity-type': ""}
                            argument = entity.copy()
                            if role in self.roles_mapper:
                                role = self.roles_mapper[role]
                                argument['role'] = role
                                entities.append(entity)
                                arguments.append(argument)
                            else:
                                print(role)

                events_triples = {'arguments': arguments, 'trigger': trigger, 'event-type': event_type}
                new_instance = {
                    'origin': self.origin,
                    'id': new_instance_id,
                    'no-of-sentences': no_of_sentences,
                    'sentences': sentences,
                    'text': text_sentence,
                    'words': words,
                    'lemma': lemma,
                    'pos-tags': pos_tags,
                    # 'head': conll_head,
                    'golden-entity-mentions': entities,
                    'golden-event-mentions': events_triples,
                    'penn-treebank': penn_treebanks,
                    'dependency-parsing': dependency_parsing,
                    'chunks': chunks
                }
                new_instances.append(new_instance)
        return new_instances
