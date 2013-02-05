from collections import Counter, defaultdict
from operator import itemgetter
import cPickle
import re
import math

class Classifier(object):
    _training_items = Counter() 
    _data = defaultdict(dict) 

    def __init__(self):
        pass
    
    def _words(self, source):
        #return [filter(str.isalpha, s) for s in source.split()]
        return re.findall('\w+', source)

    def train(self, text, identifier):
        self._training_items[identifier] += 1
        if identifier not in self._data:
            self._data[identifier] = defaultdict(int)

        for w in self._words(text):
            self._data[identifier][w] += 1

        return self._training_items, self._data
    
    def identify(self, text):
        probabilities = dict()
        ws = self._words(text)

        for language in self._training_items:
            # Calculate probabilities for each language

            matches = 0
            for w in ws:
                occurences = self._data[language][w] 
                matches += math.log(self._data[language][w]) if occurences else 0

            probabilities[language] = math.log(self._training_items[language]) + matches
       
        return max(probabilities.iteritems(), key=itemgetter(1))[0]
   
    def export(self, fp):
        cPickle.dump(self, fp, 2)
    
    @classmethod
    def from_data(cls, fp):
        return cPickle.load(fp) 

    def __getstate__(self):
        return {
            'training_items': self._training_items,
            'data': self._data
        }
    
    def __setstate__(self, state):
        self._training_items = state['training_items']
        self._data = state['data']
