from itertools import product
from tkinter import *


for i, j in product(range(5), range(4)):
    lab = Label(text='%d.%d' % (i, j), relief=RIDGE)
    lab.grid(row=i, column=j, sticky=NSEW)

mainloop()
