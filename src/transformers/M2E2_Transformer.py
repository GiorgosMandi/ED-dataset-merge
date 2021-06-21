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
    # WARNING: This dataset contains many errors and there is no consistency:
    #   - in its word list, contains characters that  do not exist in the actual sentence
    #   - sometimes the '-' separated words are treated as one word and other times as two
    def transform(self, output_path):
        new_instances = []
        i = -1
        m2e2_jsons = utilities.read_json(self.m2e2_path)
        for instance in tqdm(m2e2_jsons):
            i += 1
            new_instance_id = self.id_base + str(i) + "-" + instance['sentence_id']
            text_sentence = instance['sentence']

            parsing = self.advanced_parsing(text_sentence)
            words = parsing['words']
            lemma = parsing['lemma']
            pos_tags = parsing['pos-tag']
            entity_types = parsing['ner']
            sentences = parsing['sentences']

            # sentence centric
            penn_treebanks = parsing['treebank']
            dependency_parsing = parsing['dep-parse']
            chunks = parsing['chunks']
            no_of_sentences = len(sentences)

            # adjust entities
            text_to_entity = {}
            entities = []
            for j, entity in enumerate(instance['golden-entity-mentions']):
                entity_id = new_instance_id + "-entity-" + str(j)
                existing_ner = entity['entity-type']

                # to tackle the inconsistencies in the list of words of the dataset,
                # we find the text to the words of our list and make pointers to thees
                entity_first_word = instance['words'][entity['start']]
                entity_first_word = entity_first_word.split("-")[0] if "-" in entity_first_word else entity_first_word
                entity_first_word = self.adjust_to_parsed(entity_first_word)

                entity_last_word = instance['words'][entity['end']-1]
                entity_last_word = entity_last_word.split("-")[-1] if "-" in entity_last_word else entity_last_word
                entity_last_word = self.adjust_to_parsed(entity_last_word)

                # the first word after start that matches
                start = words[entity['start']:].index(entity_first_word) + entity['start']
                end = words[start:].index(entity_last_word) + start + 1
                text = ' '.join(words[start: end])
                new_ner = utilities.most_frequent(entity_types[start: end])
                new_entity = {'entity-id': entity_id,
                              'start': start,
                              'end': end,
                              'text': text,
                              'entity-type': new_ner,
                              'existing-entity-type': existing_ner
                              }
                entities.append(new_entity)
                text_in_dataset = ' '.join(instance['words'][entity['start']: entity['end']])
                text_to_entity[text_in_dataset] = new_entity

            # adjust events
            events = []
            if len(instance['golden-event-mentions']) > 0:
                for event in instance['golden-event-mentions']:
                    event_type = self.events_mapper[event['event_type']]
                    event['event_type'] = event_type
                    arguments = []
                    for arg in event['arguments']:
                        role = arg['role'].lower()
                        role = self.roles_mapper[role]

                        # there are also inconsistencies between arguments' text and entities' text
                        text_in_dataset = ' '.join(instance['words'][arg['start']: arg['end']])
                        corresponding_entity = text_to_entity[text_in_dataset]
                        arguments.append({'start': corresponding_entity['start'],
                                          'end': corresponding_entity['end'],
                                          'text': corresponding_entity['text'],
                                          'role': role,
                                          'entity-type': corresponding_entity['entity-type'],
                                          'existing-entity-type': corresponding_entity['existing-entity-type']
                                          })
                    events.append({'arguments': arguments, 'trigger': event['trigger'], 'event-type': event_type})

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
                'golden-event-mentions': events,
                'penn-treebank': penn_treebanks,
                "dependency-parsing": dependency_parsing,
                'chunks': chunks
            }
            new_instances.append(new_instance)
            if len(new_instances) == self.batch_size:
                utilities.write_json(new_instances, output_path)
                new_instances = []
        utilities.write_json(new_instances, output_path)

    def adjust_to_parsed(self, token):
        return token.replace('’', r"'").replace('‘', "'").replace("(", "-LRB-").replace(")", "-RRB-")
