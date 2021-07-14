from src.utils import utilities
from src.conf.Constants import Keys
from src.conf.Configuration import events
import argparse
import logging
import sys
from tqdm import tqdm
import json
import os
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from matplotlib import pyplot as plt
from sklearn.metrics import accuracy_score

log = logging.getLogger("EVALUATOR")
log.setLevel(logging.DEBUG)
consoleOUT = logging.StreamHandler(sys.stdout)
consoleOUT.setLevel(logging.DEBUG)
formatter = logging.Formatter('\n%(asctime)s - %(name)s - %(levelname)s - %(message)s')
consoleOUT.setFormatter(formatter)
consoleOUT.terminator = ""
log.addHandler(consoleOUT)

log_root = logging.getLogger()
consoleER = logging.StreamHandler(sys.stdout)
consoleER.setLevel(logging.FATAL)
consoleER.setFormatter(formatter)
consoleER.terminator = ""
log_root.addHandler(consoleER)


class Evaluator:
    def __init__(self):
        self.trigger_tp = 0
        self.event_types_tp = 0
        self.total_gold_events = 0
        self.total_predicted_events = 0
        self.gold_dict = {}
        self.gold_event_trigger = {}
        self.predictions_dict = {}

    def set_GT(self, gt):
        events_gt = gt[Keys.EVENTS_MENTIONED.value]
        self.total_gold_events += len(events_gt)
        # from type to trigger and number of occurrences
        golden_events = {}
        # list containing predictions/golden event types of the current instance
        gold = []
        for event in events_gt:
            event_type = event[Keys.EVENT_TYPE.value]
            if event_type in golden_events.keys():
                golden_events[event_type][Keys.TRIGGER.value].append(event[Keys.TRIGGER.value][Keys.TEXT.value])
                golden_events[event_type][Keys.COUNTER.value] += 1
            else:
                golden_events[event_type] = {
                    Keys.TRIGGER.value: [event[Keys.TRIGGER.value][Keys.TEXT.value]],
                    Keys.COUNTER.value: 1
                }
            gold.append(event_type)

        # store the results of this instance
        key = groundTruth_json[Keys.ID.value].replace("/", "") + ".json"
        self.gold_dict[key] = gold
        self.gold_event_trigger[key] = golden_events

    def set_predictions(self, pred):
        predictions = []
        key = pred['doc_id']
        events_pred = pred['graph']['triggers']
        self.total_predicted_events += len(events_pred)
        for event in events_pred:
            event_type = event[2]
            event_type = event_type.replace(":", ".").upper()

            if event_type in self.gold_event_trigger[key].keys():
                if self.gold_event_trigger[key][event_type][Keys.COUNTER.value] > 0:
                    self.event_types_tp += 1
                    self.gold_event_trigger[key][event_type][Keys.COUNTER.value] -= 1

                predicted_trigger = ' '.join(pred['tokens'][event[0]:event[1]])
                for trigger in self.gold_event_trigger[key][event_type][Keys.TRIGGER.value]:
                    if utilities.string_similarity(predicted_trigger, trigger) > 0.8:
                        self.trigger_tp += 1
            predictions.append(event_type)

        self.predictions_dict[key] = predictions

    def get_ordered_results(self):
        final_gold = []
        final_predictions = []
        for key in self.predictions_dict.keys():
            gold = self.gold_dict[key]
            predictions = self.predictions_dict[key]

            # if they did not find the same number event types, we fill with empty, so we can compute Accuracy and CM
            if len(predictions) > len(gold):
                gold = gold + ["NONE"] * (len(predictions) - len(gold))
            elif len(predictions) < len(gold):
                predictions = predictions + ["NONE"] * (len(gold) - len(predictions))

            # models could make correct predictions but in different order
            # however, order matters for the computation of Accuracy an CM
            # So we order so if it has found the correct types they will be placed in the same positions
            gold.sort()
            predictions.sort()

            final_gold.extend(gold)
            final_predictions.extend(predictions)
        return final_gold, final_predictions



    def get_classification_score(self):
        precision = 100.0 * self.event_types_tp / self.total_predicted_events if self.total_predicted_events > 0 else 0
        recall = 100.0 * self.event_types_tp / self.total_gold_events if self.total_gold_events > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0

        final_gold, final_predictions = self.get_ordered_results()
        assert(len(final_gold) == len(final_predictions))
        acc = 100.0 * accuracy_score(final_gold, final_predictions)
        return precision, recall, f1, acc

    def get_identification_score(self):
        precision = 100.0 * self.trigger_tp / self.total_predicted_events if self.total_predicted_events > 0 else 0
        recall = 100.0 * self.trigger_tp / self.total_gold_events if self.total_gold_events > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
        return precision, recall, f1

    def get_confusion_matrix(self, cmPath=None):
        fig, ax = plt.subplots(1, 1, figsize=(25, 25))
        final_gold, final_predictions = self.get_ordered_results()
        assert(len(final_gold) == len(final_predictions))
        cfm = confusion_matrix(final_gold, final_predictions, labels=events)
        ConfusionMatrixDisplay(cfm, display_labels=events).plot(values_format='d', ax=ax)
        ax.set_title('Confusion Matrix')
        fig.show()
        if cmPath:
            fig.savefig(cmPath)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Give arguments")
    parser.add_argument('-predictions', metavar='--predictions', type=str, help='Path to the json containing the predictions', required=True)
    parser.add_argument('-groundTruth', metavar='--groundTruth', type=str, help='Path to the json containing the ground truth', required=True)
    parser.add_argument('-cmPath', type=str, help='Path to save CM')

    args = parser.parse_args()

    if not os.path.exists(args.predictions):
        log.error("Prediction file '" + args.predictions + "' does not exist")
        exit(1)

    if not os.path.exists(args.groundTruth):
        log.error("Ground truth file '" + args.groundTruth + "' does not exist")
        exit(1)

    if args.cmPath:
        if not os.path.exists(os.path.dirname(args.cmPath)):
            log.error("CM path '" + args.groundTruth + "' does not exist")
            exit(1)

    evaluator = Evaluator()
    gt_jsons = {}
    with open(args.groundTruth) as groundTruth_jsonfile:
        for groundTruth_json in groundTruth_jsonfile:
            groundTruth_json = json.loads(groundTruth_json)
            evaluator.set_GT(groundTruth_json)

    predictions_jsons = []
    if os.path.isdir(args.predictions):
        for file in os.listdir(args.predictions):
            json_file = os.path.join(args.predictions, file)
            with open(json_file) as prediction_jsonfile:
                for prediction_json in prediction_jsonfile:
                    prediction_json = json.loads(prediction_json)
                    if prediction_json['doc_id'] in evaluator.gold_event_trigger.keys():
                        evaluator.set_predictions(prediction_json)

    print()
    precision, recall, f1, acc = evaluator.get_classification_score()
    log.info("Event Classification")
    log.info("Event Type PRECISION:\t" + str(precision))
    log.info("Event Type RECALL:\t\t" + str(recall))
    log.info("Event Type F1-SCORE:\t" + str(f1))
    log.info("Event Type ACCURACY:\t" + str(acc))
    print()

    log.info("Trigger Identification")
    precision, recall, f1 = evaluator.get_identification_score()
    log.info("PRECISION:\t" + str(precision))
    log.info("RECALL:\t" + str(recall))
    log.info("F1-SCORE:\t" + str(f1))

    evaluator.get_confusion_matrix(args.cmPath)
    print()


