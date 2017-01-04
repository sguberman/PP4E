"""
display all images in a directory as thumbmail image buttons that display
the full image when clicked; requires PIL for jpegs and thumbnail image
creation; to do: add scrolling if too many thumbs for window
"""

import math
import os
import sys
from tkinter import *
from PIL import Image
from PIL.ImageTk import PhotoImage


def make_thumbs(imgdir, size=(100, 100), subdir='thumbs'):
    """
    get thumbnail images for all images in a directory; for each image,
    create and save a new thumb or load and return an existing thumb;
    makes thumb dir if needed; return a list of (image filename, thumb
    image object); caller can also run listdir on thumb dir to load;
    on bad file types may raise IOError, or other; caveat: could also
    check file timestamps;

    :param imgdir: directory to make thumbnails for
    :param size: size of thumbnails to create
    :param subdir: directory to store created thumbs in
    :return: list of (image filename, thumb image object) tuples
    """
    thumbdir = os.path.join(imgdir, subdir)
    if not os.path.exists(thumbdir):
        os.mkdir(thumbdir)

    thumbs = []
    for imgfile in os.listdir(imgdir):
        thumbpath = os.path.join(thumbdir, imgfile)
        if os.path.exists(thumbpath):
            thumbobj = Image.open(thumbpath)
            thumbs.append((imgfile, thumbobj))
        else:
            print('making', thumbpath)
            imgpath = os.path.join(imgdir, imgfile)
            try:
                imgobj = Image.open(imgpath)
                imgobj.thumbnail(size, Image.ANTIALIAS)
                imgobj.save(thumbpath)
                thumbs.append((imgfile, imgobj))
            except:
                print('Skipping: ', imgpath)

    return thumbs


class ViewOne(Toplevel):
    """
    open a single image in a popup window when created; photoimage
    object must be saved: images are erased if object is reclaimed
    """
    def __init__(self, imgdir, imgfile):
        Toplevel.__init__(self)
        self.title(imgfile)
        imgpath = os.path.join(imgdir, imgfile)
        imgobj = PhotoImage(file=imgpath)
        Label(self, image=imgobj).pack()
        print(imgpath, imgobj.width(), imgobj.height())
        self.savephoto = imgobj


def viewer(imgdir, kind=Toplevel, cols=None):
    """
    make thumb links window for an image directory: one thumb button
    per image; use kind=Tk to show in main app window, or Frame container
    (pack); imgfile differs per loop: must save with a default; photoimage
    objs must be saved: erased if reclaimed, packed row frames (versus
    grids, fixed-sizes, canvas);

    :param imgdir: directory to make thumbnails for
    :param kind: what kind of window
    :param cols:
    :return:
    """
    win = kind()
    win.title('Viewer: ' + imgdir)
    quit = Button(win, text='Quit', command=win.quit, bg='beige')
    quit.pack(fill=X, side=BOTTOM)
    thumbs = make_thumbs(imgdir)
    if not cols:
        cols = int(math.ceil(math.sqrt(len(thumbs))))

    savephotos = []
    while thumbs:
        thumbsrow, thumbs = thumbs[:cols], thumbs[cols:]
        row = Frame(win)
        row.pack(fill=BOTH)
        for (imgfile, imgobj) in thumbsrow:
            photo = PhotoImage(imgobj)
            link = Button(row, image=photo)
            handler = lambda savefile=imgfile: ViewOne(imgdir, savefile)
            link.config(command=handler)
            link.pack(side=LEFT, expand=YES)
            savephotos.append(photo)

    return win, savephotos


if __name__ == '__main__':
    imgdir = (len(sys.argv) > 1 and sys.argv[1]) or 'images'
    main, save = viewer(imgdir, kind=Tk)
    main.mainloop()
