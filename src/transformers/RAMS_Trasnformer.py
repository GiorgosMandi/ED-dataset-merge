import json
import spacy
import re
from .. utils.chunker import BigramChunker
from spacy.matcher import Matcher
from stanfordcorenlp import StanfordCoreNLP


class RamsTransformer:

    def __init__(self, rams_path, stanford_core_path):
        print("rams-transformer intialization")

        self.nlp = spacy.load('en_core_web_sm')
        self.snlp = StanfordCoreNLP(stanford_core_path, memory='2g', timeout=60)

        verb_phrases_patterns = [
            {'POS': 'VERB', 'OP': '?'},
            {'POS': 'ADV', 'OP': '*'},
            {'POS': 'AUX', 'OP': '*'},
            {'POS': 'VERB', 'OP': '+'}]
        self.matcher = Matcher(self.nlp.vocab)
        self.matcher.add("verb-phrases", None, verb_phrases_patterns)
        self.chunker = BigramChunker()
        self.id_base = "RAMS-instance-"
        self.rams_path = rams_path

    def transform(self):
        new_instances = []
        roles = set()
        triggers = set()

        with open(self.rams_path) as f:
            rams_jsons = [json.loads(inline_json) for inline_json in f]

        for i, instance in enumerate(rams_jsons):

            # TODO add:
            #  - stanford-colcc
            #  - conll-head
            new_instance_id = self.id_base + str(i) + "-" + instance['doc_key']
            no_of_sentences = len(instance['sentences'])

            sentences = []
            next_start = 0
            for s in instance['sentences']:
                start = next_start
                end = start + len(s)
                next_start = end
                text = ' '.join(s)
                sentences.append({'start': start, 'end': end, 'text': text})

            sentence = ' '.join([s['text'] for s in sentences])

            snlp_processed_json = self.snlp.annotate(sentence,  properties={'annotators': 'tokenize,ssplit,pos,lemma,parse'})
            snlp_processed = json.loads(snlp_processed_json)
            penn_treebank = [re.sub(r'\n|\s+', ' ', s['parse']) for s in snlp_processed['sentences']]

            nlp_sentence = self.nlp(sentence)
            lemma = []
            words = []
            pos_tags = []
            conll_head = []
            for word in nlp_sentence:
                words.append(word.text)
                lemma.append(word.lemma_)
                pos_tags.append(word.tag_)
                conll_head.append(word.head.i)

            chunks = []
            for s in sentences:
                s_words = words[s['start']: s['end']]
                s_tags = pos_tags[s['start']: s['end']]
                zipped = list(zip(s_words, s_tags))
                s_chunks = self.chunker.parseIOB(zipped)
                chunks.append(s_chunks)

            entities = []
            for j, entity in enumerate(instance['ent_spans']):
                # TODO: to add
                #  - entity_type
                #  - phrase_type
                start = entity[0]
                end = entity[1] + 1
                text = ' '.join(words[start: end])
                entity_id = new_instance_id + "-" + str(j)
                new_entity = {'start': start, 'end': end, 'text': text, 'entity_id': entity_id}
                entities.append(new_entity)

            if len(instance['evt_triggers']) > 1:
                print("ERROR: More triggers than expected")

            trigger_start = instance['evt_triggers'][0][0]
            trigger_end = instance['evt_triggers'][0][1] + 1
            trigger_text = ' '.join(words[trigger_start: trigger_end]).lower()
            triggers.add(trigger_text)
            trigger = {'start': trigger_start, 'end': trigger_end, 'text': trigger_text}

            event_type = instance['evt_triggers'][0][2][0][0]

            events_triples = []
            arguments = []

            for triple in instance['gold_evt_links']:
                arg_start = triple[1][0]
                arg_end = triple[1][1] + 1
                arg_role = re.split("\d", triple[2])[-1]
                roles.add(arg_role)
                argument = {'start': arg_start, 'end': arg_end, 'role': arg_role}
                arguments.append(argument)

            events_triples.append({'arguments': arguments, 'trigger': trigger, 'event_type': event_type})

            new_instance = {
                'id': new_instance_id,
                'no_of_sentences': no_of_sentences,
                'sentence': sentence,
                'words': words,
                'lemma': lemma,
                'pos-tags': pos_tags,
                'golden-entity-mentions': entities,
                'golden-event-mentions': events_triples,
                'penn-treebank': penn_treebank,
                'chunks': chunks
            }
            new_instances.append(new_instance)
        return new_instances

