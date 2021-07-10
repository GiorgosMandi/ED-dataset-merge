from .utils import utilities
from .conf.Constants import Keys
from .conf.Configuration import events
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
        self.gold = []
        self.predictions = []

    def evaluate(self, gt, pred):
        events_gt = gt[Keys.EVENTS_MENTIONED.value]
        golden_events = {}
        self.total_gold_events += len(events_gt)

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
            self.gold.append(event_type)

        events_pred = pred[Keys.EVENTS_MENTIONED.value]
        self.total_predicted_events += len(events_pred)
        for event in events_pred:
            event_type = event[Keys.EVENT_TYPE.value]
            if event_type in golden_events.keys():
                if golden_events[event_type][Keys.COUNTER.value] > 0:
                    self.event_types_tp += 1
                    golden_events[event_type][Keys.COUNTER.value] -= 1

                predicted_trigger = event[Keys.TRIGGER.value][Keys.TEXT.value]
                for trigger in golden_events[event_type][Keys.TRIGGER.value]:
                    if utilities.string_similarity(predicted_trigger, trigger) > 0.8:
                        self.trigger_tp += 1
            self.predictions.append(event_type)

    def get_classification_score(self):
        precision = 100.0 * self.event_types_tp / self.total_predicted_events if self.total_predicted_events > 0 else 0
        recall = 100.0 * self.event_types_tp / self.total_gold_events if self.total_gold_events > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
        acc = 100.0 * accuracy_score(self.gold, self.predictions)
        return precision, recall, f1, acc

    def get_identification_score(self):
        precision = 100.0 * self.trigger_tp / self.total_predicted_events if self.total_predicted_events > 0 else 0
        recall = 100.0 * self.trigger_tp / self.total_gold_events if self.total_gold_events > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
        return precision, recall, f1

    def get_confusion_matrix(self, cmPath=None):
        fig, ax = plt.subplots(1, 1, figsize=(25, 25))
        cfm = confusion_matrix(self.gold, self.predictions, labels=events)
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
    with open(args.predictions) as predictions_jsonfile,  open(args.groundTruth) as groundTruth_jsonfile:
        for prediction_json, groundTruth_json in tqdm(zip(predictions_jsonfile, groundTruth_jsonfile)):
            prediction = json.loads(prediction_json)
            groundTruth = json.loads(groundTruth_json)
            evaluator.evaluate(groundTruth, prediction)

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


