from .Transformer import Transformer
from tqdm import tqdm
from ..utils import utilities
import re


class EDDTransformer(Transformer):

    def __init__(self, edd_path, stanford_core_path):
        super().__init__(stanford_core_path)
        print("edd-transformer initialization")
        self.id_base = "EDD-instance-"
        self.path = edd_path
        self.origin = "EDD"

    def transform(self):
        new_instances = []
        i = -1
        edd_jsons = utilities.read_json(self.path)
        for instance in tqdm(edd_jsons):
            instance_data = instance['data']
            new_instance_id = self.id_base + "-" + instance_data['filename'] + str(i)
            text_sentence = instance_data['text']
            text_sentence = re.sub(r'(?<!\.)\n', ' . ', instance_data['text']).replace("\n", "")

            sentences = []
            words = []
            lemma = []
            pos_tags = []
            conll_head = []
            entity_types = []
            chunks = []
            next_start = 0
            for sentence in text_sentence.split("."):
                parsing = self.simple_parsing(sentence)
                s_words = parsing[0]
                s_tags = parsing[1]
                words.extend(s_words)
                pos_tags.extend(s_tags)
                lemma.extend(parsing[2])
                conll_head.extend(parsing[3])
                entity_types.extend(parsing[4])

                start = next_start
                end = start + len(parsing[0])
                next_start = end
                sentences.append({'start': start, 'end': end, 'text': sentence, 'words': parsing[0]})

                s_chunks = self.chunking(s_words, s_tags)
                chunks.append(s_chunks)

            no_of_sentences = len(sentences)

            print()
