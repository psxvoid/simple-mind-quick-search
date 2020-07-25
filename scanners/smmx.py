#!python3

from xml.etree import ElementTree as et
import glob
import os
import pathlib
import string
import collections
import copy
import inspect
import shlex
import zipfile
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

class SearchModelContext(collections.MutableMapping):
    def __init__(self, filenames = None):
        super(SearchModelContext, self).__init__()
        if filenames != None:
            self.filenames = filenames
            self.length = 1
            self.count = 1

    def merge(self, other):
        self.filenames = self.filenames + other.filenames
    
    def getNames(self):
        names = []
        for path in self.filenames:
            filename = os.path.basename(path)
            if filename not in names:
                names.append(filename)
        return names

    def copy(self):
        self_copy = SearchModelContext()
        for k, v in inspect.getmembers(self):
            if k != '__weakref__':
                setattr(self_copy, k, v)
        return self_copy

    def __getitem__(self, key):
        return getattr(self, key)
            
    def __setitem__(self, key, value):
        if not hasattr(self, key):
            self.length = self.length + 1
            self.count = self.count + 1
        setattr(self, key, value)

    def __delitem__(self, key):
        delattr(self, key)
        self.length = self.length - 1
        self.count = self.count - 1

    def __iter__(self):
        return self.__dict__.items()

    def __len__(self):
        return self.length

    def __keytransform__(self, key):
        return key


def read_smmx_as_words(filename):
    try:
        with zipfile.ZipFile(filename, mode='r') as smmx:
            with smmx.open('document/mindmap.xml', mode='r') as document:
                try:
                    etree = et.fromstring(document.read())
                    notags = et.tostring(etree, encoding='utf8', method='text')
                    word_list = notags.split()
                    words = {word_list[i].decode("utf-8").lower(): SearchModelContext(
                        [filename]) for i in range(0, len(word_list))}
                    return words
                except:
                    print("ERRROR!!! Invalid XML!!!")
                    print(filename)
                    return {}
    except:
        print("ERRROR!!! Invalid ZIP!!!")
        print(filename)
        return {}

def scan(rootdir):
    words = {}
    paths = []
    for filename in glob.iglob(rootdir + '/**', recursive=True):
        if os.path.isfile(filename):  # filter dirs
            if pathlib.Path(filename).suffix == '.smmx':
                paths.append(filename)
                file_words = read_smmx_as_words(filename)
                for word in file_words:
                    if (word not in words):
                        words[word] = file_words[word]
                    else:
                        words[word].merge(file_words[word])

    return words, paths
