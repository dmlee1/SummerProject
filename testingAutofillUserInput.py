import os, openpyxl, re
from translationLists import *
import pandas as pd
import numpy as np
import tkinter as tk



def searchVariables():

    def checkKey(event):
        value = event.widget.get()

        # get data from dict_keys
        if value == '':
            data = dict_keys
        else:
            valueList = value.split()
            combString = ["(?=.*" + str(x) + ")" for x in valueList]
            reParm = ''.join(combString) + ".*"
            data = [key for key in dict_keys if re.search(re.compile(reParm, flags=re.IGNORECASE), key)]

        update(data)


    def update(data):
        # clear previous data
        lb.delete(0, 'end')

        # put new data
        for item in data:
            lb.insert('end', item)

    def setTrans(transText):
        translatedVar.set(transText)

    def itemSelect(evt):
        value = lb.get(lb.curselection())
        setTrans(rosterListForSearch.get(value))

    # Driver code
    dict_keys = rosterListForSearch.keys()

    # Get width of longest humod variable name and then pad on each side
    label_width = max([len(key) for key in rosterListForSearch.values()])


    root = tk.Tk()
    root.title("Search Variables")

    # creating text box
    e = tk.Entry(root)
    e.pack()
    e.bind('<KeyRelease>', checkKey)

    # creating list box
    lb = tk.Listbox(root)
    lb.config(width=0, height=25)
    lb.pack(side='left')

    # Creating scrollbar for list of common name variables and binding it to listbox
    sb = tk.Scrollbar(root, orient='vertical')
    sb.pack(side='left', fill="y")
    lb.configure(yscrollcommand=sb.set)
    sb.config(command=lb.yview)

    # Creating right side that displays corresponding humod variable
    translatedVar = tk.StringVar()
    transLabel = tk.Entry(root, textvariable=translatedVar, justify='center', width=label_width+(2*2), state="readonly", bd=0)
    transLabel.pack(side='right')


    # Setting mouse double click as well as pressing the ENTER button as item selection
    lb.bind('<Double-1>', itemSelect)
    lb.bind('<Return>', itemSelect)

    update(dict_keys)
    root.mainloop()

searchVariables()

