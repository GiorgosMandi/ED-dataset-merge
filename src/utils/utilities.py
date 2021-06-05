import json


def most_frequent(List):
    return max(set(List), key=List.count)


def read_json(path):
    with open(path) as json_file:
        data = json.loads(json_file.read())
    return data


def read_jsonlines(path):
    with open(path) as json_file:
        data = [json.loads(inline_json) for inline_json in json_file]
    return data


def write_iterable(path, iterable):
    iterable_str = "\n".join(iterable)
    with open(path, "w") as f:
        f.write(iterable_str)