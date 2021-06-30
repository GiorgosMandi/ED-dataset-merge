import argparse
import logging
from tqdm import tqdm
import json
from .utils import utilities

log = logging.getLogger()
log.setLevel(logging.INFO)

parser = argparse.ArgumentParser(description="Give arguments")
parser.add_argument('-i', metavar='input', type=str, help='Path to the input instances', required=True)
parser.add_argument('-out', metavar='out', type=str, help='Path to the input instances', required=True)


args = parser.parse_args()
input_paths = args.i
events_per_role = {}
for input_path in input_paths.split(";"):
    with open(input_path) as json_file:
        for inline_json in tqdm(json_file):
            instance = json.loads(inline_json)

            events = instance['golden-event-mentions']
            for event in events:
                event_type = event['event-type']
                if event_type in events_per_role:
                    for arg in event['arguments']:
                        events_per_role[event_type].add(arg['role'])
                else:
                    events_per_role[event_type] = set([arg['role'] for arg in event['arguments']])

for key, value in events_per_role.items():
    events_per_role[key] = list(value)
utilities.write_json(events_per_role, args.out)
