from collections import Iterable

from nltk import conlltags2tree
from nltk.corpus import conll2000
import nltk
from nltk.chunk.api import ChunkParserI
from nltk.tag.sequential import ClassifierBasedPOSTagger, ClassifierBasedTagger

nltk.download('conll2000')

class BigramChunker(nltk.ChunkParserI):
    def __init__(self, train_sents):
        train_data = [[(t,c) for w,t,c in nltk.chunk.tree2conlltags(sent)]
                      for sent in train_sents]
        self.tagger = nltk.BigramTagger(train_data)

    def parse(self, sentence):
        pos_tags = [pos for (word,pos) in sentence]
        tagged_pos_tags = self.tagger.tag(pos_tags)
        chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags]
        conlltags = [(word, pos, chunktag) for ((word,pos),chunktag)
                     in zip(sentence, chunktags)]
        return nltk.chunk.conlltags2tree(conlltags)

    def parseIOB(self, sentence):
        return nltk.chunk.tree2conlltags(self.parse(sentence))



class NamedEntityChunker(ChunkParserI):
    def __init__(self, train_sents, feature_detector=None, **kwargs):
        assert isinstance(train_sents, Iterable)
        tagged_sents = [[((w,t),c) for (w,t,c) in
                         nltk.tree2conlltags(sent)]
                        for sent in train_sents]

        self.tagger = ClassifierBasedTagger(train=train_sents, feature_detector=feature_detector, **kwargs)

    def parse(self, tagged_sent):
        chunks = self.tagger.tag(tagged_sent)
        iob_triplets = [(w, t, c) for ((w, t), c) in chunks]

        # Transform the list of triplets to nltk.Tree format
        return conlltags2tree(iob_triplets)

test_sents = conll2000.chunked_sents('test.txt', chunk_types=['NP'])
train_sents = conll2000.chunked_sents('train.txt', chunk_types=['NP'])

chunker = BigramChunker(train_sents)
print(chunker.evaluate(test_sents))


sentence = [("John", "NNP"), ("thinks", "VBZ"), ("Mary", "NN"),  ("saw", "VBD"), ("the", "DT"), ("cat", "NN"),
            ("sit", "VB"), ("on", "IN"), ("the", "DT"), ("mat", "NN")]

res = chunker.parseIOB(sentence)
print(res)
