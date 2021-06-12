import re
from .Transformer import Transformer
from tqdm import tqdm
from ..utils import utilities


class RamsTransformer(Transformer):

    def __init__(self, rams_path, stanford_core_path):
        super().__init__(stanford_core_path)
        print("rams-transformer intialization")
        self.id_base = "RAMS-instance-"
        self.rams_path = rams_path
        self.origin = "RAMS"

    # transform dataset to the common schema
    def transform(self):
        new_instances = []
        i = -1
        rams_jsons = utilities.read_jsonlines(self.rams_path)
        for instance in tqdm(rams_jsons):
            i += 1
            new_instance_id = self.id_base + str(i) + "-" + instance['doc_key']
            # parsing sentences
            all_sentences = " ".join([t for s in instance['sentences'] for t in s])

            parsing = self.advanced_parsing(all_sentences)
            words = parsing['words']
            lemma = parsing['lemma']
            pos_tags = parsing['pos-tag']
            head = parsing['head']
            entity_types = parsing['ner']
            sentences = parsing['sentences']
            text_sentence = parsing['text']

            # sentence centric
            penn_treebanks = parsing['treebank']
            dependency_parsing = parsing['dep-parse']
            chunks = self.chunking(parsing['words'], parsing['pos-tag'])
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
                new_entity = {'start': start, 'end': end, 'text': text, 'entity-id': entity_id,
                              'entity-type': entity_type, 'detailed-entity-type': ""}
                entities.append(new_entity)

            # process trigger
            if len(instance['evt_triggers']) > 1:
                print("ERROR: More triggers than expected")

            trigger_start = instance['evt_triggers'][0][0]
            trigger_end = instance['evt_triggers'][0][1] + 1
            trigger_text = ' '.join(words[trigger_start: trigger_end]).lower()
            trigger = {'start': trigger_start, 'end': trigger_end, 'text': trigger_text}

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
                arg_role = self.roles_mapper[arg_role]
                argument = {'start': arg_start, 'end': arg_end, 'text': text, 'role': arg_role,
                            'entity-type': entity_type, 'detailed-entity-type': ""}
                arguments.append(argument)

            events_triples.append({'arguments': arguments, 'trigger': trigger, 'event-type': event_type})

            new_instance = {
                'origin': self.origin,
                'id': new_instance_id,
                'no-of-sentences': no_of_sentences,
                'sentences': sentences,
                'text': text_sentence,
                'words': words,
                'lemma': lemma,
                'pos-tags': pos_tags,
                'head': head,
                'golden-entity-mentions': entities,
                'golden-event-mentions': events_triples,
                'penn-treebank': penn_treebanks,
                "dependency-parsing": dependency_parsing,
                'chunks': chunks
            }
            new_instances.append(new_instance)
        return new_instances

