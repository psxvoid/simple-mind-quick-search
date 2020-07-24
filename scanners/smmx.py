#!python3
from xml.etree import ElementTree as et

# imports for createGuid start

import glob
import os
import pathlib
import string
import collections
import copy

# converts string into words
# see: https://stackoverflow.com/questions/743806/how-to-split-a-string-into-a-list
#import nltk
# nltk.download()
import shlex


# zip flie imports start

import zipfile
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

# zip file imports end


class SearchModelContext(collections.MutableMapping):
    def __init__(self, filenames):
        super(SearchModelContext, self).__init__()
        self.filenames = filenames
        self.length = 1
        self.count = 1
        #print(args)
        #print(kwardgs)
        # self.store = dict()
        # self.update(dict(*args, **kwargs))  # use the free update to set keys
    # def __init__(self, filenames):
    #     self.filenames = filenames
    #     self.length = 1

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
        # print(getattr(self, 'original_key'))
        return self
        # return copy.deepcopy(self)

    def __getitem__(self, key):
        return getattr(self, key)
        # if hasattr(self, key):
        #     return getattr(self, key)
        # else:
        #     return None
            
    def __setitem__(self, key, value):
        #print('SET ITEM!!! : {} {}'.format(key, value))
        if not hasattr(self, key):
            self.length = self.length + 1
            self.count = self.count + 1
        setattr(self, key, value)
        # if key == 'original_key':
        #     print('SET ITEM!!! : {} {}'.format(key, value))
        #     print(getattr(self, 'original_key'))

        # self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        delattr(self, key)
        self.length = self.length - 1
        self.count = self.count - 1
        # del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return self.__dict__.items()
        # return iter(self.store)

    def __len__(self):
        return self.length
        # return len(self.store)

    def __keytransform__(self, key):
        return key


def read_smmx_as_words(filename):
    modes = {
        zipfile.ZIP_DEFLATED: 'deflated',
        zipfile.ZIP_STORED:   'stored',
    }

    try:
        with zipfile.ZipFile(filename, mode='r') as smmx:
            with smmx.open('document/mindmap.xml', mode='r') as document:
                try:
                    etree = et.fromstring(document.read())
                    notags = et.tostring(etree, encoding='utf8', method='text')
                    # word_list = nltk.word_tokenize(notags)
                    # word_list = shlex.split(notags)
                    word_list = notags.split()
                    # words = { word_list[i]: SearchModelContext([filename]) for i in range(0, len(word_list)) }
                    words = {word_list[i].decode("utf-8"): SearchModelContext(
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

# iterate directories start
# source: https://stackoverflow.com/questions/19587118/iterating-through-directories-with-python


# rootdir = 'C:/Users/sapeh/Dropbox/SimpleMind'
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
# iterate directories end
