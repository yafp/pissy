#!/usr/bin/env python
#
#
# ---------------------------------------------------------------------------- #
# NAME:         pissy
# ---------------------------------------------------------------------------- #
# DESCRIPTION:  a simple python based image slideshow script
# ---------------------------------------------------------------------------- #
# USAGE:        ./pissy.py
# ---------------------------------------------------------------------------- #
# PARAMETER:    --source /path/to/image/folder     To set the image source dir
#               --delay 5                          To set image delay to 5 sec
#               --verbose                          To enable verbose output
# ---------------------------------------------------------------------------- #
# AUTHOR:       Florian Poeck
# ---------------------------------------------------------------------------- #
# URL:          https://github.com/yafp/pissy
# ---------------------------------------------------------------------------- #
# LICENSE:      GPLv3
# ---------------------------------------------------------------------------- #
# CREDIT:       https://gist.github.com/terencewu/034e09f0e318c621516b

''' pissy.py - a simple python based image slideshow script '''


# Brainstorming
#       loading animation (splash screen)
#       show lay-over information at launch (i.e. regarding ESC)
#       add image transition (i.e. using Image.blend)
#       add icon to script itself
#       change background color of image window


# ---------------------------------------------------------------------------- #
# IMPORTS
# ---------------------------------------------------------------------------- #
import sys                          # for handling exit
import os                           # for walking dirs
import argparse                     # for parsing arguments
import Tkinter as tk                # for ui stuff
import random                       # for picking random images
import tkMessageBox                 # for dialogs
from PIL import Image, ImageTk      # for image handling


# ---------------------------------------------------------------------------- #
# CONSTANTS
# ---------------------------------------------------------------------------- #
APP_NAME_SHORT = "pissy"
APP_NAME_LONG = "Python Image SlideShow"
APP_VERSION = "0.1.0"


# ---------------------------------------------------------------------------- #
# ON VERBOSE
# ---------------------------------------------------------------------------- #
def on_verbose(message):
    ''' Display verbose output if verbose is set '''
    global verbose
    if(verbose):
        print(message)


# ---------------------------------------------------------------------------- #
# ON ESC
# ---------------------------------------------------------------------------- #
def on_closing(event):
    ''' Ask user if he wants to quit if ESC key was pressed '''
    on_verbose("function: on_closing")
    result = tkMessageBox.askquestion("Close", \
        "Do you really want to quit "+APP_NAME_SHORT+"?", icon='question')
    if result == 'yes':
        on_verbose("\tBye")
        sys.exit()


# ---------------------------------------------------------------------------- #
# ON WINDOW CLOSE
# ---------------------------------------------------------------------------- #
def on_window_close():
    ''' Exit the script if image-window is closed '''
    on_verbose("function: on_window_close")
    on_verbose("\tBye")
    sys.exit()


# ---------------------------------------------------------------------------- #
# HIDDENROOT
# ---------------------------------------------------------------------------- #
class HiddenRoot(tk.Tk):
    ''' HiddenRoot '''
    def __init__(self):
        '''init stuff'''
        on_verbose("init class HiddenRoot")
        tk.Tk.__init__(self)

        # hackish way, essentially makes root window
        # as small as possible but still "focused"
        # enabling us to use the binding on <esc>
        self.wm_geometry("0x0+0+0")

        # hides the hidden main window from window-list
        self.withdraw()

        # TEMP: get amount of displays and the related resolutions
        on_verbose("\tDetecting displays")
        from screeninfo import get_monitors # to detect screens/displays
        for m in get_monitors():
            on_verbose("\t"+str(m)) # output display info

        self.window = MySlideShow(self)
        self.window.start_slideshow()


# ---------------------------------------------------------------------------- #
# MYSLIDESHOW
# ---------------------------------------------------------------------------- #
class MySlideShow(tk.Toplevel):
    ''' slideshow '''
    def __init__(self, *args, **kwargs):
        ''' more init stuff '''
        on_verbose("init class MySlideShow")
        tk.Toplevel.__init__(self, *args, **kwargs)

        # remove window decorations
        #self.overrideredirect(True)

        # save reference to photo so that garbage collection
        # does not clear image variable in show_image()
        self.persistent_image = None
        self.imageList = []
        self.pixNum = 0

        # used to display as background image
        self.label = tk.Label(self)
        self.label.pack(side="top", fill="both", expand=True)

        # bind ESC key
        self.bind('<Escape>', on_closing)

        # check source folder
        self.getImages()


    def getImages(self):
        ''' Get image directory from command line or use current directory '''
        on_verbose("function: getImages")
        img_counter = 0

        global curr_dir
        # loop over dir and find all contained images
        for root, dirs, files in os.walk(curr_dir):
            for f in files:
                if f.endswith(('jpg', 'JPG', 'png', 'PNG', 'gif', 'GIF')):
                    img_counter = img_counter +1
                    img_path = os.path.join(root, f)
                    self.imageList.append(img_path)

        # output amount of images
        on_verbose("\tSource:\t\t\t"+curr_dir)
        on_verbose("\tImages:\t\t\t"+str(img_counter))
        if img_counter == 0: # if no img was found to display
            on_verbose("Error - no images found")
            sys.exit()


    def start_slideshow(self): #delay in seconds
        ''' Starting the slideshow '''
        on_verbose("\nfunction: start_slideshow")

        myimage = self.imageList[self.pixNum]
        on_verbose("\tNext image:\t\t"+myimage)

        # logical image order
        #self.pixNum = (self.pixNum + 1) % len(self.imageList)
        # vs random
        self.pixNum = random.randint(0, len(self.imageList)-1)

        self.show_image(myimage)

        # its like a callback function after n seconds (cycle through pics)
        global delay
        self.after(delay*1000, self.start_slideshow)


    def show_image(self, filename):
        ''' Load a single image, get best dimensions and display it '''
        on_verbose("function: show_image")

        image = Image.open(filename)

        # set window title
        self.title(APP_NAME_SHORT+ " - "+ filename)

        # set window icon
        icon = tk.PhotoImage(file='icon.png')
        self.tk.call('wm', 'iconphoto', self._w, icon)

        # set window background (NOT WORKING)
        self.configure(background='red')

        # add close event
        self.protocol("WM_DELETE_WINDOW", on_window_close)

        # get source image size
        img_w, img_h = image.size
        on_verbose("\tImage-size:\t\t"+str(img_w)+" x "+str(img_h))

        # get display size
        scr_w, scr_h = self.winfo_screenwidth(), self.winfo_screenheight()
        on_verbose("\tScreen-size:\t\t"+str(scr_w)+" x "+str(scr_h))

        # get smaller with and height values from image size and display size
        #width, height = min(scr_w, img_w), min(scr_h, img_h)
        #print "\tPicking prefered size:\t\t"+str(width)+" x "+str(height)

        # Wenn Bild > Display -> display size
        if(img_w > scr_w) or (img_h > scr_h): # image -> use display size
            # scale to display size
            width = scr_w * 0.95
            height = scr_h * 0.95
            on_verbose("\tResizing image")
            image.thumbnail((width, height), Image.ANTIALIAS)
        else:   # image < display -> use image size
            width = img_w
            height = img_h
            on_verbose("\tNo resizing needed")

        # set window size after scaling the original image up/down to fit screen
        # removes the border on the image
        scaled_w, scaled_h = image.size
        on_verbose("\tFinal size:\t\t"+str(scaled_w)+" x "+str(scaled_h))

        # set window dimensions
        # 1) window size based on image size
        #self.wm_geometry("{}x{}+{}+{}".format(scaled_w, scaled_h, 0, 0))
        # 2) window size based on display size
        self.wm_geometry("{}x{}+{}+{}".format(scr_w, scr_h, 0, 0))
        on_verbose("\tSet window size")

        # display the new image
        self.persistent_image = ImageTk.PhotoImage(image)
        on_verbose("\tLoad image to window")





        # ---------------------
        # playing with blend
        # --------------------
        #im1 = Image.open("icon2.png")
        #im2 = Image.open("icon3.png")
        #blended = Image.blend(im1, im2, alpha=0.5)
        #blended.save("blended.png")
        #
        #self.persistent_image = ImageTk.PhotoImage(blended)



        # label
        self.label.configure(image=self.persistent_image)


# ---------------------------------------------------------------------------- #
# ARGUMENT PARSING
# ---------------------------------------------------------------------------- #
parser = argparse.ArgumentParser()

# define optional arguments
parser.add_argument("--delay", \
    help="Delay in seconds before next image is loaded", type=int)
parser.add_argument("--verbose", \
    help="increase output verbosity", action="store_true")
parser.add_argument("--source", \
    help="Set image source path", type=str)

args = parser.parse_args()

# parse arguments
if args.verbose: # enabling verbose or not
    verbose = True
    on_verbose(APP_NAME_SHORT +" - "+APP_NAME_LONG+"\n\n")
    on_verbose("\tEnabled verbose mode")
else:
    verbose = False

if args.delay: # configuring the image display time
    on_verbose("\tSet delay to "+str(args.delay)+" seconds")
    delay = args.delay
else:
    on_verbose("\tSet delay to 3 seconds (default)")
    delay = 3

if args.source: # configuring the image source folder
    on_verbose("\tSet image source to "+str(args.source))
    curr_dir = str(args.source)
else:
    curr_dir = '.'


# ---------------------------------------------------------------------------- #
# MAIN
# ---------------------------------------------------------------------------- #
slideshow = HiddenRoot()
slideshow.mainloop()
