from tkinter import Tk, Label, Frame, Canvas, Toplevel, messagebox
import time, os, random, io, threading, multiprocessing, winsound
from screeninfo import get_monitors
from threading import Event
from PIL import Image, ImageTk
from tkinter.colorchooser import askcolor
from dat import dat_main as data_main

class DolphinClock():
    def __init__(self, root, ref_num):
        # Tkinter
        self.root = root
        self.ref_num = ref_num
        self.root.title('clock')
        self.root.config(bg='black')
        self.window_width = 128
        self.window_height = 150
        self.root.attributes('-transparentcolor','black')
        self.root.attributes('-topmost', 1)
        self.root.update_idletasks()
        self.root.overrideredirect(True)

        # Get the screen dimensions. self.monitors contains {"monitor name": {"x_rng":[0,1920],"y_rng":[0,1080]}}
        self.monitors = {}
        for count, m in enumerate(get_monitors()):
            self.monitors[count] = {"x_rng":[],"y_rng":[]}
            self.monitors[count]["x_rng"].append(m.x) # Left most pixel starting point
            self.monitors[count]["x_rng"].append(m.x + m.width) # Right most pixel
            self.monitors[count]["y_rng"].append(m.y) # Top most pixel
            self.monitors[count]["y_rng"].append(m.y + m.height) # Bottom most pixel

        # Set positioning
        rand_rng = []
        self.current_monitor = random.randint(0,len(self.monitors)-1)
        for rng in self.monitors.values():
            rand_rng.append(random.randint(rng["x_rng"][0],rng["x_rng"][1]))
        self.x_pos = rand_rng[self.current_monitor]

        rand_rng.clear()
        for rng in self.monitors.values():
            rand_rng.append(random.randint(rng["y_rng"][0],rng["y_rng"][1]))
        self.y_pos = rand_rng[self.current_monitor]

        # Set window starting position and speed       
        self.root.geometry("+"+str(self.x_pos)+"+"+str(self.y_pos))
        self.xspeed = 0
        self.yspeed = 0
        
        # For direction: true = right or down, false = left or up
        self.xdir = bool(random.getrandbits(1))
        self.ydir = bool(random.getrandbits(1))
        # For pic: true = down, false = up
        self.pic = bool(random.getrandbits(1))
        
        # For egg: true = rgb value up, false = rgb value down
        self.eggdirR = bool(random.getrandbits(1))
        self.eggdirG = bool(random.getrandbits(1))
        self.eggdirB = bool(random.getrandbits(1))
        self.egg_on = False
        self.egg_reset = False
        self.egg_main_clock_red = False

        # Define original picture colour
        self.currentColor = (69, 110, 181, 255)
        self.colorHex = "#456EB5"
        self.picFiles = {}

        # Load audio visual data from dat
        self.dat = data_main.Data()

        self.createUI()

    def createUI(self):
        # Load the audio
        self.loadAudio()
        
        # Clock config
        self.clock = Label(self.root,
                           background='black',
                           foreground=self.colorHex,
                           font=('arial', 34, 'bold'))
        self.clock.grid(column=0, row=0)
        self.update_clock()

        # Load and create the images
        self.loadPics()

        self.canvas = Canvas(self.root, bg='black', width=128, height=100, highlightthickness=0)
        self.img_container = self.canvas.create_image(64,50,image=self.picFiles["DolphinRD"])
        self.updatePic()
        self.canvas.grid(column=0, row=1)

        # Bind variables
        self.canvas.bind("<ButtonPress-3>",self.changeColor)
        for item in [self.clock,self.canvas]:
            item.bind("<Double-1>",self.quitcode)
            item.bind("<ButtonPress-1>",self.startDolphinDrag)
            item.bind("<ButtonRelease-1>", self.stopDolphinDrag)
            item.bind("<B1-Motion>", self.doDolphinDrag)

        # Begin animation
        self.moveDolphin()

    def loadPics(self):
        self.picFileImgs = {"DolphinRD":"",
                            "DolphinRU":"",
                            "DolphinLD":"",
                            "DolphinLU":""}
       
        for var in self.picFileImgs.keys():
            # Load bytes
            self.picFileImgs[var] = self.dat.data(var)

        for var, img_data in self.picFileImgs.items():
            # Open image from bytes
            b = bytearray(img_data)
            self.picFileImgs[var] = Image.open(io.BytesIO(b))
            
            # Create tk version of image
            self.picFiles[var] = ImageTk.PhotoImage(image=self.picFileImgs[var])

    def loadAudio(self):
        # Thanks to SM-AML for supply cool dolphin like noises!
        b = self.dat.data("SMdolphin")
        self.noiseSMAML = bytearray(b)

        # Egg sound
        b = self.dat.data("Celebrate")
        self.noiseCelebrate = bytearray(b)

    def quitcode(self,event):
        global dolphins
        dolphins[self.ref_num].root.destroy()
        
    def startDolphinDrag(self,event):
        self.root.x = event.x
        self.root.y = event.y

    def stopDolphinDrag(self,event):
        self.root.x = None
        self.root.y = None
        x = threading.Thread(target=self.playAudio)
        x.start()

    def doDolphinDrag(self,event):
        deltax = event.x - self.root.x
        deltay = event.y - self.root.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.x_pos = x
        self.y_pos = y
        self.root.geometry(f"+{x}+{y}")

    def update_clock(self):
        self.clock.config(text=time.strftime("%H:%M"))
        self.clock.after(1000,self.update_clock)

    def check_new_monitor(self):
        new_monitor = False
        for key, rng in self.monitors.items():
            if (self.x_pos + self.xspeed + self.win_width) in range(self.monitors[key]['x_rng'][0],self.monitors[key]['x_rng'][1]):
                if (self.y_pos + self.yspeed + self.win_height) in range(self.monitors[key]['y_rng'][0],self.monitors[key]['y_rng'][1]):
                    new_monitor = True
                    self.current_monitor = key
        if new_monitor:
            self.continue_in_x()
            self.continue_in_y()
        return new_monitor

    def continue_in_x(self):
        if self.xdir: self.x_pos += self.xspeed
        else: self.x_pos -= self.xspeed

    def continue_in_y(self):
        if self.ydir: self.y_pos += self.yspeed
        else: self.y_pos -= self.yspeed        

    def moveDolphin(self):
        # Increase intended speed a bit
        if self.xspeed < 30: self.xspeed += random.randint(1,4)
        if self.yspeed < 9: self.yspeed += random.randint(1,2)

        # Define win_width and win_height to calculate if the dolphin is moving screens or out of bounds
        if self.xdir: self.win_width = self.window_width -5
        else: self.win_width = int(-self.window_width) + 35
        if self.ydir: self.win_height = self.window_height -5
        else: self.win_height = -20

        # Move x while checking it doesn't go offscreen (flip direction if so)       
        if (self.x_pos + self.xspeed + self.win_width) not in range(self.monitors[self.current_monitor]['x_rng'][0],self.monitors[self.current_monitor]['x_rng'][1]):
            new_monitor = self.check_new_monitor()
            if not new_monitor:
                self.xdir = not(self.xdir)
                self.x_pos -= self.xspeed
                self.xspeed = 0
                self.yspeed = int(self.yspeed/3)
        else:
            self.continue_in_x()

        # Same thing as above for y!
        if (self.y_pos + self.yspeed + self.win_height) not in range(self.monitors[self.current_monitor]['y_rng'][0],self.monitors[self.current_monitor]['y_rng'][1]):
            new_monitor = self.check_new_monitor()
            if not new_monitor:
                self.ydir = not(self.ydir)
                self.y_pos -= self.yspeed
                self.yspeed = 0
        else:
            self.continue_in_y()

        # Insert some randomness to direction
        if random.randint(1,100) == 100:
            self.xdir = not(self.xdir)
            self.xspeed = 0
            self.yspeed = int(self.yspeed/2)

        if random.randint(1,20) == 20:
            self.ydir = not(self.ydir)
            self.yspeed = int(self.yspeed/2)

        # Change picture direction every movement
        if self.pic: self.pic = False
        else: self.pic = True

        self.updatePic()

        # Define the speed of movement update
        self.root.geometry("+"+str(self.x_pos)+"+"+str(self.y_pos))
        if self.egg_on: self.canvas.after(random.randint(50,150),self.moveDolphin)
        elif random.randint(1,6) == 6: self.canvas.after(random.randint(500,2000),self.moveDolphin)
        else: self.canvas.after(random.randint(200,500),self.moveDolphin)

    def updatePic(self):
        if self.xdir and self.pic: self.canvas.itemconfig(self.img_container,image=self.picFiles["DolphinRD"])
        if self.xdir and not self.pic: self.canvas.itemconfig(self.img_container,image=self.picFiles["DolphinRU"])
        if not self.xdir and self.pic: self.canvas.itemconfig(self.img_container,image=self.picFiles["DolphinLD"])
        if not self.xdir and not self.pic: self.canvas.itemconfig(self.img_container,image=self.picFiles["DolphinLU"])

    def egg(self):
        if self.egg_count == 1:
            self.egg_on = True
            # Play sound effect
            threading.Thread(target=self.celebrate).start()
            self.root.after(1500,create_dolphin_clock)

        # Keep changing a random region of pixels to a random colour for a while (14 times)        
        if self.egg_count < 14:
            rgb = (random.randint(0,255),random.randint(0,255),random.randint(0,255),255)
            for var in self.picFileImgs.keys():
                for x in range(random.randint(0,64),random.randint(65,128)):
                    for y in range(random.randint(0,50),random.randint(51,100)):
                        if self.picFileImgs[var].getpixel((x,y))[3] > 200: self.picFileImgs[var].putpixel((x,y),rgb)
                self.picFiles[var] = ImageTk.PhotoImage(image=self.picFileImgs[var])

            # Set clock colours
            self.clock.config(foreground=self.colorHex)
            if self.ref_num == 0:
                self.clock.config(foreground="red")
                self.egg_main_clock_red = True
            self.updatePic()

            # Loop the colour changing
            self.egg_count += 1
            self.root.after(2000,self.egg)

        else:
            self.currentColor = (69, 110, 181, 255)
            self.egg_on = False
            self.egg_reset = True

    def celebrate(self):
        winsound.PlaySound(self.noiseCelebrate,winsound.SND_MEMORY)

    def changeColor(self, event):
        # Get colour. self.color is set as hex value, so use it to store original colour value
        rgb, self.colorHex = askcolor(title="Pick a colour for the dolphin!")

        if rgb == None: return

        # Pure black is transparent, canvas uses (0,0,0) to be transparent so can't distinguish between convas and dolphin
        if rgb == (0,0,0):
            rgb = (1,0,0)
            self.colorHex = "#000001"

        # Define easter egg value
        if rgb == (69,69,69):
            self.egg_count = 1
            self.egg()

        if self.egg_reset:
            self.loadPics()
            self.egg_reset = False

        # Find and replace current colour pixels
        for var in self.picFileImgs.keys():
            for x in range (0,128):
                for y in range(0,100):
                    if self.picFileImgs[var].getpixel((x,y))[0:3] == self.currentColor[0:3]: self.picFileImgs[var].putpixel((x,y),rgb)
            self.picFiles[var] = ImageTk.PhotoImage(image=self.picFileImgs[var])

        # Set clock colours
        self.clock.config(foreground=self.colorHex)

        # Check if main clock has gone through egg (will close all the additional dolphins if removed)
        if self.egg_main_clock_red and self.ref_num == 0:
            self.clock.config(foreground="red")

        # Set current color value (so it knows what to search next time). Need to add 255 for RGBA.
        newColor = list(rgb)
        newColor.append(255)
        self.currentColor = tuple(newColor)
        self.updatePic()

    def playAudio(self):
        winsound.PlaySound(self.noiseSMAML,winsound.SND_MEMORY)



def create_dolphin_clock():
    global count, dolphins, root

    # Use root for first dolphin instance - acts as master off switch if removed.
    if count == 0:
        dolphin_root = root
    else:
        dolphin_root = Toplevel()
    dolphins[count] = DolphinClock(dolphin_root, count)
    
    count += 1


count = 0
dolphins = {}
root = Tk()
create_dolphin_clock()
root.mainloop()
