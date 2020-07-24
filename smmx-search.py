#!/usr/bin/env python3

# fast-autocomplete is used for search
# pip install fast-autocomplete
# see https://pypi.org/project/fast-autocomplete/

# pip install nltk
# source: https://stackoverflow.com/questions/47839813/python-tkinter-autocomplete-combobox-with-like-search

import os
import tkinter as tk
from fast_autocomplete import AutoComplete
from scanners.smmx import scan

rootdir = 'C:/Users/xxx/Dropbox/SimpleMind'
words, paths = scan(rootdir)
autocomplete = AutoComplete(words=words)
contexts = []

def on_keyrelease(event):
    
    # get text from entry
    value = event.widget.get()
    value = value.strip().lower()
    
    # get data from test_list
    if value == '':
        data = test_list
    else:
        # search using fast-autocomplete
        results = autocomplete.search(word=value, max_cost=3, size=3)
        data = []
        for words in results:
            for word in words:
                # print('Word: {}'.format(word))
                context = autocomplete.words[word]
                # print(context.filenames[0])
                # for path in context.filenames:
                #     filename = os.path.basename(path)
                #     if filename not in data:
                #         data.append(filename)
                data = data + context.getNames()

    # update data in listbox
    listbox_update(data)
    
def listbox_update(data):
    # delete previous data
    listbox.delete(0, 'end')
    
    # sorting data 
    data = sorted(data, key=str.lower)

    # put new data
    for item in data:
        listbox.insert('end', item)


def on_select(event):
    # display element selected on list
    print('(event) previous:', event.widget.get('active'))
    print('(event)  current:', event.widget.get(event.widget.curselection()))
    print('---')


# --- main ---

# test_list = ('apple', 'banana', 'Cranberry', 'dogwood', 'alpha', 'Acorn', 'Anise', 'Strawberry' )
test_list = []#[ os.path.basename(paths[i]) for i in range(0, len(paths) - 1) ]

root = tk.Tk()

entry = tk.Entry(root)
entry.pack()
entry.bind('<KeyRelease>', on_keyrelease)

listbox = tk.Listbox(root)
listbox.pack()
#listbox.bind('<Double-Button-1>', on_select)
listbox.bind('<<ListboxSelect>>', on_select)
listbox_update(test_list)

root.mainloop()