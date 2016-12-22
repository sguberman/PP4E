import sys
from tkinter import *


widget = Button(None,
                text='Hello event world',
                command=(lambda: print('Hello lambda') or sys.exit()))

widget.pack()
widget.mainloop()
