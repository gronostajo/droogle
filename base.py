from collections import Counter
import gzip
from operator import itemgetter
from os import listdir, path
import re
import cPickle as pickle
import json
from math import log, sqrt

from scipy.sparse import csr_matrix, lil_matrix, coo_matrix
import numpy as np
from sklearn.preprocessing import normalize
import unicodedata

__author__ = 'gronostaj'


def list_dirs(dirpath):
    return [f for f in listdir(dirpath) if path.isdir(path.join(dirpath, f))]


def list_files(dirpath):
    return [f for f in listdir(dirpath) if path.isfile(path.join(dirpath, f))]


class Serializer:

    @staticmethod
    def serialize(obj, serializer, filename, gz=False, **kwargs):
        if gz:
            with gzip.open('%s.gz' % filename, 'wb', 5) as f:
                f.write(serializer.dumps(obj, **kwargs))
        else:
            with open(filename, 'wb') as f:
                f.write(serializer.dumps(obj, **kwargs))

    @staticmethod
    def deserialize(serializer, filename):
        gz = filename.endswith('.gz')
        if gz:
            with gzip.open(filename, 'rb') as f:
                obj = serializer.load(f)
        else:
            with open(filename, 'rb') as f:
                obj = serializer.load(f)
        return obj

    @staticmethod
    def pickle(obj, filename, gz=True):
        Serializer.serialize(obj, pickle, filename, gz)

    @staticmethod
    def unpickle(filename):
        return Serializer.deserialize(pickle, filename)

    @staticmethod
    def to_json(obj, filename, gz=True):
        Serializer.serialize(obj, json, filename, gz, sort_keys=True, indent=4, separators=(',', ': '))

    @staticmethod
    def from_json(filename):
        return Serializer.deserialize(json, filename)


class Droogle:

    SUFFIXES = ('%s.pickle', '%s.pickle.gz', '%s.json', '%s.json.gz')

    _WORDMAP = 'wordmap'
    _MATRIX = 'matrix'
    _CHUNKS = 'chunks'

    def __init__(self, indexdir):
        dbs = {}
        for req in (Droogle._WORDMAP, Droogle._MATRIX, Droogle._CHUNKS):
            satisfying = [
                path.join(indexdir, suffix % req)
                for suffix in Droogle.SUFFIXES
                if path.isfile(path.join(indexdir, suffix % req))
            ]
            if not satisfying:
                raise FileMissingError(req)
            else:
                dbs[req] = satisfying[0]

        self.dbs = {
            k: Serializer.unpickle(f)
            if f.endswith('.pickle') or f.endswith('.pickle.gz')
            else Serializer.from_json(f)
            for k, f in dbs.iteritems()
        }

    @staticmethod
    def _sanitize(str):
        return re.sub(r'[^\x00-\x7F]+', ' ', str.lower())

    @staticmethod
    def _bagofwords(str):
        return Counter(re.findall(r'\w+', str))

    @staticmethod
    def _indexstring(filename, str, separator):
        bags = {}
        chunks = {}
        wordset = set()

        for i, chunk in enumerate(re.split(separator, str)):
            bag = Droogle._bagofwords(Droogle._sanitize(chunk))
            bags['%s_%d' % (filename, i)] = dict(bag)
            chunks['%s_%d' % (filename, i)] = chunk
            wordset = wordset | set(bag.keys())

        return bags, chunks, wordset

    @staticmethod
    def index(dirpath, inputfiles, separator):
        bags = {}
        chunks = {}
        wordset = set()

        for inputfile in inputfiles:
            print("- Parsing file %s" % inputfile)
            with open(path.join(dirpath, inputfile), 'r') as f:
                thisbag, thischunks, thisset = Droogle._indexstring(inputfile, f.read(), separator)
                bags.update(thisbag)
                chunks.update(thischunks)
                wordset = wordset | thisset

        print("- Building matrix")
        wordmap = {w: i for i, w in enumerate(wordset)}
        chunkmap = {c: i for i, c in enumerate(bags.keys())}
        matrix = lil_matrix((len(wordset), len(bags)))
        chunks = {chunkmap[n]: c for n, c in chunks.items()}

        for chunkname, chunkid in chunkmap.iteritems():
            bag = dict(bags[chunkname])
            for word, quantity in bag.iteritems():
                wordid = wordmap[word]
                matrix[wordid, chunkid] = quantity

        matrix = csr_matrix(matrix)

        print("- Optimizing matrix")
        nonzero = np.diff(matrix.indptr)
        idf = lil_matrix(np.array(map(lambda c: log(len(wordset) / c), nonzero)))
        matrix = matrix.transpose().multiply(idf)
        normalize(matrix, copy=False)
        matrix = matrix.transpose()

        print("- Saving files")
        Serializer.to_json(wordmap, path.join(dirpath, "%s.json" % Droogle._WORDMAP))
        Serializer.pickle(matrix, path.join(dirpath, "%s.pickle" % Droogle._MATRIX))
        Serializer.pickle(chunks, path.join(dirpath, "%s.pickle" % Droogle._CHUNKS))

        return len(bags), len(wordset)

    def query(self, string):

        bag = Droogle._bagofwords(Droogle._sanitize(string))
        norm = sqrt(reduce(lambda v, x: v + x ** 2, bag.values()))
        bag = {k: v / norm for k, v in dict(bag).iteritems()}

        bagmap = {
            self.dbs[Droogle._WORDMAP][word]: count
            for word, count in bag.iteritems()
            if word in self.dbs[Droogle._WORDMAP]
        }
        bagmap = zip(*bagmap.items())
        lookup = coo_matrix(
            (bagmap[1], ([0] * len(bagmap[0]), bagmap[0])),
            dtype='double',
            shape=(1, self.dbs[Droogle._MATRIX].shape[0])
        ).dot(self.dbs[Droogle._MATRIX])

        results = [(self.dbs[Droogle._CHUNKS][i], lookup[0, i]) for i in xrange(self.dbs[Droogle._MATRIX].shape[1])]
        return map(itemgetter(0), sorted(results, key=itemgetter(1), reverse=True))


class FileMissingError(Exception):

    def __init__(self, filename):
        self.filename = filename