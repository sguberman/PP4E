"""
display all images in a directory in popup windows
GIFs work in basic tkinter, but jpeg will be skipped without PIL
"""

import sys
import os
from tkinter import *
from PIL.ImageTk import PhotoImage


imgdir = 'images'
if len(sys.argv) > 1:
    imgdir = sys.argv[1]
imgfiles = os.listdir(imgdir)

main = Tk()
main.title('Viewer')
quit = Button(main, text='Quit all', command=main.quit, font=('courier', 25))
quit.pack()
savephotos = []

for imgfile in imgfiles:
    imgpath = os.path.join(imgdir, imgfile)
    win = Toplevel()
    win.title(imgfile)
    try:
        imgobj = PhotoImage(file=imgpath)
        Label(win, image=imgobj).pack()
        print(imgpath, imgobj.width(), imgobj.height())
        savephotos.append(imgobj)
    except:
        errmsg = 'skipping %s\n%s' % (imgfile, sys.exc_info()[1])
        Label(win, text=errmsg).pack()


main.mainloop()
