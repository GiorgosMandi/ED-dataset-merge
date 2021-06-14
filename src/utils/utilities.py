import json
import difflib
import numpy as np


def most_frequent(List):
    return max(set(List), key=List.count)


def read_json(path):
    with open(path) as json_file:
        data = json.loads(json_file.read())
    return data


def write_json(mappings, path):
    with open(path, 'w+') as json_file:
        for mapping in mappings:
            json.dump(mapping, json_file)
            json_file.write('\n')


def read_jsonlines(path):
    with open(path) as json_file:
        data = [json.loads(inline_json) for inline_json in json_file]
    return data


def write_iterable(path, iterable):
    iterable_str = "\n".join(iterable)
    with open(path, "w") as f:
        f.write(iterable_str)


def string_similarity(str1, str2):
    return difflib.SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def find_most_similar(entity, entities):
    sim_scores = np.array([string_similarity(entity, e) for e in entities])
    return entities[np.argmax(sim_scores)]


def match_entities(path1, path2):
    mapping = {}
    with open(path2) as target:
        target_entities = target.readlines()
    target_entities = [x.replace('\n', '') for x in target_entities]

    with open(path1) as source:
        source_entities = source.readlines()
    source_entities = [x.replace('\n', '') for x in source_entities]

    for source_entity in source_entities:
        most_similar_target_entity = find_most_similar(source_entity, target_entities)
        mapping[source_entity] = most_similar_target_entity
    return mapping
