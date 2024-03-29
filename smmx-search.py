#!/usr/bin/env python3

import os
import tkinter as tk
from fast_autocomplete import AutoComplete
from scanners.smmx import scan
from pathlib import Path
import subprocess
import platform
from pynput import keyboard
import threading
import copy

rootdir = 'C:/Users/xxx/Dropbox/SimpleMind'
words, paths = scan(rootdir)
words_copy = copy.deepcopy(words)

autocomplete = AutoComplete(words=words)
contexts = []
selected = None

def remove_prefix(str, prefix):
    if str.startswith(prefix):
        return str[len(prefix):]
    return str

def on_keyrelease(event):

    # get text from entry
    value = event.widget.get()
    value = value.strip().lower()

    # get data from test_list
    global contexts
    contexts = []
    if value == '':
        data = test_list
    else:
        # search first using partial match (autocomplete may not handle it)
        results = []
        for word in words_copy:
            if value in word.lower():
                results.append([word])
        results_full = [i[0] for i in results]
        results = results + autocomplete.search(word=value, max_cost=3, size=10)
        print('Results:')
        print(results)
        filepaths = []
        data = []
        for words in results:
            for word in words:
                context = words_copy[word]

                for path in context.filenames:
                    if path not in filepaths:
                        filepaths.append(path)
                        filename = os.path.basename(path)
                        if filename not in data:
                            if word in results_full:
                                data.append('[FULL] ' + filename)
                            else:
                                data.append(filename)
                contexts.append(context)

    # update data in listbox
    listbox_update(data)


def listbox_update(data):
    # delete previous data
    listbox.delete(0, 'end')

    # sorting data
    # data = sorted(data, key=str.lower)

    # put new data
    for item in data:
        listbox.insert('end', item)


def on_select(event):
    # display element selected on list
    print('(event) previous:', event.widget.get('active'))
    print('(event) current:', event.widget.get(event.widget.curselection()))
    print('---')
    global selected
    selected = remove_prefix(event.widget.get(event.widget.curselection()), '[FULL] ')

def on_open():
    if selected is None:
        print('Can\'t open - nothing is selected')
        return
    filenames = []
    for context in contexts:
        for filename in context.filenames:
            if selected in filename:
                if not filename in filenames:
                    filenames.append(filename)
    if len(filenames) > 0:
        print('Matched: {}'.format(len(filenames)))
        for filename in filenames:
            print('Openning file: {}'.format(filenames[0]))
            filepath = Path(filename).absolute()
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', filepath))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(filepath)
            else:                                   # linux variants
                subprocess.call(('xdg-open', filepath))
    else:
        print('No matching entries found...')
        print('Context count: {}'.format(len(contexts)))


# --- main ---

test_list = []

root = tk.Tk()
root.minsize(width=300, height=600)

is_opened = True


entry = tk.Entry(root)
entry.pack(fill='x')
entry.bind('<KeyRelease>', on_keyrelease)
entry.focus_set()

listbox = tk.Listbox(root)

# see https://stackoverflow.com/questions/4318103/resize-tkinter-listbox-widget-when-window-resizes
listbox.pack(side='left', fill='both', expand=True)

listbox.bind('<<ListboxSelect>>', on_select)
listbox_update(test_list)

def clear_entry():
    entry.delete(0, tk.END)
    entry.insert(0, "")
    global selected
    selected = None

def close(event):
    clear_entry()
    root.withdraw()

    global is_opened
    is_opened = False
    # root.iconify()


def open():
    root.deiconify()
    entry.focus_set()

    global is_opened
    is_opened = True


def toggle():
    global is_opened

    if is_opened:
        clear_entry()
        root.withdraw()
    else:
        root.deiconify()
        entry.focus_set()

    is_opened = not is_opened

def open(event):
    on_open()
    toggle()

root.bind('<Escape>', close)
root.bind('<Return>', open)
listbox.bind('<Double-Button-1>', open)


def processGlobalHotkeys():
    print('listening...')
    with keyboard.GlobalHotKeys({'<alt>+<shift>+s': toggle}) as h:
        h.join()


thread = threading.Thread(target=processGlobalHotkeys, args=())
thread.daemon = False
thread.start()

close('any')

root.mainloop()
