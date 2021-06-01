import json
import spacy
import re

from spacy.matcher import Matcher
from stanfordcorenlp import StanfordCoreNLP

stanford_core_path = "../model/stanford-corenlp-full-2018-10-05"
nlp = spacy.load('en_core_web_sm')
snlp = StanfordCoreNLP(stanford_core_path, memory='8g', timeout=60000)

verb_phrases_patterns = [
    {'POS': 'VERB', 'OP': '?'},
    {'POS': 'ADV', 'OP': '*'},
    {'POS': 'AUX', 'OP': '*'},
    {'POS': 'VERB', 'OP': '+'}]
matcher = Matcher(nlp.vocab)
matcher.add("verb-phrases", None, verb_phrases_patterns)

# rams_path = 'data/train.jsonlines'
rams_path = '../data/rams_100.jsonlines'
with open(rams_path) as f:
    rams_jsons = [json.loads(inline_json) for inline_json in f]

id_base = "RAMS-instance-"
new_instances = []
roles = set()
triggers = set()
for i, instance in enumerate(rams_jsons):

    # TODO add:
    #  - penn-treebank
    #  - stanford-colcc
    #  - conll-head
    #  - chunk
    new_instance_id = id_base + str(i) + "-" + instance['doc_key']
    no_of_sentences = len(instance['sentences'])
    words = [words for sentence in instance['sentences'] for words in sentence]
    sentence = ' '.join(words)

    nlp_sentence = nlp(sentence)
    tst = snlp.annotate(sentence,  properties={'annotators': 'tokenize,ssplit,pos,lemma,parse'})

    lemma = []
    words = []
    pos_tags = []
    conll_head = []
    for word in nlp_sentence:
        words.append(word.text)
        lemma.append(word.lemma_)
        pos_tags.append(word.tag_)
        conll_head.append(word.head.i)

    chunks = ["O"]*len(words)
    for chunk in nlp_sentence.noun_chunks:
        start = chunk.start
        end = chunk.end
        inside_times = end - start
        chunks[start] = "B-" + chunk.label_
        chunks[start+1:end+1] = ["I-"+chunk.label_]*inside_times

    matches = matcher(nlp_sentence)


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

    events = []
    events_triples = {}
    arguments = []

    for triple in instance['gold_evt_links']:
        arg_start = triple[1][0]
        arg_end = triple[1][1] + 1
        arg_role = re.split("\d", triple[2])[-1]
        roles.add(arg_role)
        argument = {'start': arg_start, 'end': arg_end, 'role': arg_role}
        arguments.append(argument)

    events.append({'arguments': arguments, 'trigger': trigger, 'event_type': event_type})

    new_instance = {
        'id': new_instance_id,
        'no_of_sentences': no_of_sentences,
        'sentence': sentence,
        'words': words,
        'lemma': lemma,
        'pos-tags': pos_tags,
        'golden-entity-mentions': entities,
        'golden-event-mentions': events
    }
    new_instances.append(new_instance)

with open("../data/RAMS-triggers", "w") as triggers_file:
    triggers_file.write("\n".join(triggers))

with open("../data/RAMS-roles", "w") as roles_file:
    roles_file.write("\n".join(roles))
print()
