
from nltk.corpus import conll2000
import nltk

nltk.download('conll2000')


class BigramChunker(nltk.ChunkParserI):

    def __init__(self):
        train_sents = conll2000.chunked_sents('train.txt', chunk_types=['NP'])
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

    def evaluateChunker(self):
        test_sents = conll2000.chunked_sents('test.txt', chunk_types=['NP'])
        return self.evaluate(test_sents)


# chunker = BigramChunker()
# print(chunker.evaluateChunker())



