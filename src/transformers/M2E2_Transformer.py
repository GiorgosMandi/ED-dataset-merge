
from .Transformer import Transformer


class M2e2Transformer(Transformer):

    def __init__(self, m2e2_path, stanford_core_path):
        super().__init__(stanford_core_path)
        print("rams-transformer intialization")
        self.id_base = "M2E2-instance-"
        self.m2e2_path = m2e2_path
        self.origin = "M2E2"

    def transform(self):
        new_instances = []
        roles = set()
        triggers = set()

        m2e2_jsons = self.read_json(self.m2e2_path)

        for i, instance in enumerate(m2e2_jsons):
            new_instance_id = self.id_base + str(i) + "-" + instance['sentence_id']
            text_sentence = instance['sentence']
            sentences = [{
                'start': instance['sentence_start'],
                'end': instance['sentence_end'],
                'text': text_sentence
            }]

            parsing = self.simple_parsing(text_sentence)
            lemma = parsing[2]
            words = parsing[0]
            pos_tags = parsing[1]
            conll_head = parsing[3]

            # chunking
            chunks = [self.chunking(words[s['start']: s['end']], pos_tags[s['start']: s['end']]) for s in sentences]

            # zip(*list) unzips a list o tuples
            annotations = list(zip(*[self.coreNLP_annotation(s['text']) for s in sentences]))
            penn_treebanks = annotations[0]
            dependency_parsing = annotations[1]


            new_instance = {
                'origin': self.origin,
                'id': new_instance_id,
                'no_of_sentences': 1,
                'sentences': sentences,
                'text': text_sentence,
                'words': words,
                'lemma': lemma,
                'pos-tags': pos_tags,
                'conll_head': conll_head,
                'golden-entity-mentions': instance['golden-entity-mentions'],
                'golden-event-mentions': instance['golden-event-mentions'],
                'penn-treebank': penn_treebanks,
                "stanford-colcc": dependency_parsing,
                'chunks': chunks
            }
            new_instances.append(new_instance)
        return new_instances

