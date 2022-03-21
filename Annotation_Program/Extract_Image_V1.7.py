import cv2
import numpy as np
import os, gc
import tkinter as tk
from tkinter.messagebox import askyesno, showinfo, askyesnocancel
import copy
import pymatting

### Set these up ###
#Desktop
# dir_root = "/home/reeve/Git_Repos/ROSEBUD/Video/ASV_Sugar_Creek_Canoe_9_30_2021" ### Converting a video ###

#laptop
dir_root = "/home/reeve/Git_repos/ROSEBUD/Video/ASV_Sugar_Creek_Canoe_9_30_2021" ### Converting a video ###

#video_file = 'Wabash_River_1_Edit.mp4'
video_file = 'Sugar_Creek_HD-keep.mp4'
#dir_root = "C:\\Users\\Niklas\\Documents\\Research\\Videos\\Edits\\x" ### Uncomment to Reedit a mask ###
#video_file = 'Wabash_River_1_Edit_2762_B.jpg' # here you select a image file. The converter switches to image mode automatically
start_frame = 202316# Zero starts the video with the first frames

perc = (start_frame/237501)*100  # calcualte percentager of video traversed
num_ims = len([name for name in os.listdir(dir_root+"/All")])
print("===============================================================================")
print("percent of video annotated: " + str(perc))
print("Number of images annotated: " + str(num_ims/4))
print("Total images at linear rate: " + str(num_ims/(4*perc/100)))
print("===============================================================================")

class converter():

    Sets = [] #directories to store the finished photos in
    Polygon = [] #stores points for the current polygon 
    Saved = False
    Refresh = 0 #refreshed the imgview when text has to fade out
    Offset = [0,0,0,0] #Offset for text on the left, top, right, bottom
    OffsetMax = [280,100,0,0] #Maximum Offset for each Direction
    State = [-1,-1,-1,-1] #State for text on the left, top, right, bottom
    Display = [0,0,0,0] #Which Text is currently being displayed
    Edits = [] #stores finished Polygons and ZoneIndexes
    boat = [] #store a template to for the boat across multiple frames
    snapH, snapV, snapG = False, False, False #horizontal, vertical, existing Point
    ### Other helper variables
    moving = 0
    Direction = []
    SnapSpin = 0
    ZoneIndex = 1
    Indicator = False
    multiple = True
    AlphaMap = []
    AlphaMapNumber = 0
    AlphaMapClass = 0
    ### Change class names and their color here
    classes = [  "water", "shore/bank","bridge", "boat", "trees","sky",  "log/debree","stone", "Alpha Matting: Background",   "Alpha Matting: unknown"]
    ColorCode = np.array([[0,0,0],  [0,0,1],     [0,1,0], [1,0,0],[1,1,0], [1,0,1],[0,1,1],[0.7,0.7,0.7], [0,0,0], [0.5,0.5,0.5]])

    def __init__(self,dir_root,file_name,start_frame) -> bool:
        self.path = self.preprocess(dir_root)
        self.file = self.preprocess(file_name)
        self.start_frame = start_frame
        self.video = os.path.join(self.preprocess(dir_root),self.preprocess(file_name))
        if os.path.exists(self.path):
            os.chdir(self.path)
            if not os.path.exists(os.path.join(self.path,"data")): #create data directory if it does not yet exist
                os.makedirs(os.path.join(self.path,"data"))
                self.showMessage(0,"Initialized successfully","Root directory has been found. Data directory created.")
            self.Sets = next(os.walk('.'))[1]
            self.Sets.remove('data')
            if len(self.Sets) == 0:
                os.makedirs(os.path.join(self.path,"All"))
                self.Sets.append('All')
        else:
            self.showMessage(0,"Directory does not exist","Check the spelling of the directory path.")

    def preprocess(self,dir):  # To deal with the error when there is [] in the path
        dir.replace('[','[[]')
        dir.replace(']','[]]')
        return dir

    def extract(self):
        if self.file[-3:] == 'jpg': #single photo mode
            self.frame = cv2.imread(self.video)
            self.base_frame = copy.deepcopy(self.frame)
            self.multiple = False
            self.activateEdit()
            return
        # cv2.VideoCapture(cv2.CAP_DSHOW)  # add the direct show driver.
        cap = cv2.VideoCapture(self.video, ) #video mode
        if (cap.isOpened())==False:
            self.showMessage(0,"Reading Failed","Error opening the file.")
            return
        if self.start_frame > 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES,self.start_frame)
        while(cap.isOpened()):
            ret, self.frame = cap.read()
            if ret == True:
                self.frame_number = cap.get(1)
                self.base_frame = copy.deepcopy(self.frame)
                if os.path.exists(os.path.join(self.path,"data",self.file[0:len(self.file)-4]+"_"+str(self.frame_number)[0:len(str(self.frame_number))-2]+"_data.csv")):
                    self.frame = cv2.putText(self.frame,"Previously Edited",(20,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),2)
                self.frame = cv2.putText(self.frame,f"Frame: {self.frame_number:.0f}",(1750,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),2)
                cv2.namedWindow("Preview",cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty("Preview",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                cv2.imshow('Preview',self.frame)
                Key = cv2.waitKey(self.Refresh)
                if Key == ord('q') or Key == 0x1B: #end extractinge
                    root = tk.Tk()
                    root.withdraw()
                    if askyesno("Exit Converter","Do you want to end converting?") == True:
                        self.showMessage(0,"Converter Ended","Stopped at frame: "+str(self.frame_number))
                        break
                    root.destroy()
                elif Key == ord('n'): #next frame
                    cap.set(cv2.CAP_PROP_POS_FRAMES,self.frame_number+9)
                elif Key == ord('m'): #skip forward
                    cap.set(cv2.CAP_PROP_POS_FRAMES,self.frame_number+99)
                elif Key == ord('x'): #last frame
                    cap.set(cv2.CAP_PROP_POS_FRAMES,self.frame_number-11)
                elif Key == ord('z'): #skip backward
                    cap.set(cv2.CAP_PROP_POS_FRAMES,self.frame_number-101)
                elif Key == 0x08: #last frame
                    cap.set(cv2.CAP_PROP_POS_FRAMES,self.frame_number-2)
                elif Key == ord('s'): #save raw frame
                    self.base_frame = self.frame
                    self.save_frame(False)
                elif Key == ord('e'): #start editing frame
                    cv2.destroyWindow("Preview")
                    self.activateEdit()
            else:
                self.showMessage(0,"Video Ended","Video ended at frame: "+str(self.frame_number))
                break
        cap.release()

    def activateEdit(self): #set up variables and produce edge map
        Next = 1
        self.Refresh = 5
        self.State = [1001,1001,1001,1001]
        self.Offset = [0,0,0,0]
        self.Saved = False
        self.Edits = []
        self.AlphaMap = []
        self.AlphaMapNumber = 0
        if not self.file[-3:] == 'jpg': #single photo mode
            if os.path.exists(os.path.join(self.path,"data",self.file[0:len(self.file)-4]+"_"+str(self.frame_number)[0:len(str(self.frame_number))-2]+"_data.csv")):
                os.chdir(os.path.join(self.path,"data"))
                if True:
                    with open(self.file[0:len(self.file)-4]+"_"+str(self.frame_number)[0:len(str(self.frame_number))-2]+"_data.csv") as File:
                        Import = np.loadtxt(File, delimiter=",",dtype=float)
                        File.close()
                    if self.showMessage(1,"Data found","This frame has previously been Edited. Do you want to import this data for the new Edit?"):
                        PolyNr = 0
                        Index = 0
                        AlphaMaps = 0
                        while PolyNr <= Import[-1][3]: #until number of last Polygon
                            Start = Index
                            while Index < len(Import) and Import[Index][3] == PolyNr:
                                Index += 1
                            Poly = [np.array(Import[Start:Index,0:2],dtype=int).tolist(),int(Import[Start][2])]
                            if int(Import[Start][2]) < AlphaMaps:
                                AlphaMaps = int(Import[Start][2])
                            self.Edits.append(Poly)
                            PolyNr += 1
                        if AlphaMaps < 0:
                            if self.showMessage(1,"Alpha Maps found","The data from the previous Edit contains Alpha Maps. Do you want to restore them? This might take longer for many maps. Note that not showing them wont delete them, but will not be visualized in the Editor and saved Maps."):
                                self.importAlphaMaps(-int(AlphaMaps/(len(self.classes)*2))+1)
                # except:
                #    self.showMessage(0,"Loading failed","The previous Edits could not be retrieved. File access might be restricted or it has been modified. Starting from a blank Edit.")
        self.Direction = []
        self.Polygon = []
        self.ZoneDisplay = [0,0,0,0]
        self.redraw(Indicator=self.Indicator)
        while Next == 1:
            Next = self.edit_frame()

    def edit_frame(self):
        cv2.namedWindow("Edit Frame",cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Edit Frame",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Edit Frame",self.frame)
        cv2.setMouseCallback("Edit Frame",self.declare_boundaries)
        Key = cv2.waitKey(abs(self.Refresh))
        if Key == ord('p'): #paste template
            self.Edits = copy.deepcopy(self.boat)
            self.redraw(Indicator=False)
        elif Key == ord('t') and len(self.Edits)>0: #store to template
            self.boat = copy.deepcopy(self.Edits)
            self.activateOverlay(1,1)
        elif Key == ord('r'): #reset the last polygon
            if len(self.Polygon) > 0:
                self.Polygon = []
            elif len(self.Edits) > 0:
                self.Edits.pop(len(self.Edits)-1)
            else:
                self.activateOverlay(1,2)
            self.redraw(Indicator=False)
        elif Key == 0x08: #undo the last action with backspace
            if self.moving == 1:
                self.moving = 0
                self.redraw(Update=True)
            self.Direction = [] #reset Points created by following polygon
            if len(self.Polygon) > 0:
                self.Polygon.pop(len(self.Polygon)-1)
                if len(self.Polygon) > 0:
                    self.redraw(Indicator=True)
                else:
                    self.redraw(Indicator=False)
            elif len(self.Edits) > 0:
                self.Polygon = self.Edits[len(self.Edits)-1][0]
                self.ZoneIndex = self.Edits[len(self.Edits)-1][1]
                self.Edits.pop(len(self.Edits)-1)
                self.redraw(Indicator=True)
            else:
                self.activateOverlay(1,2)
        elif Key == ord('h') or Key == ord('v') or Key == ord('g'):# or Key == ord('f'):
            if Key == ord('h'): #force curser to the edge of the screen horizontally
                self.snapH = not(self.snapH)
                self.snapV = False
                self.snapG = False
            if Key == ord('v'): #force curser to the edge of the screen vertically
                self.snapV = not(self.snapV)
                self.snapH = False
                self.snapG = False
            if Key == ord('g'): #force curser to existing point 
                self.snapG = not(self.snapG)
                self.snapH = False
                self.snapV = False
            self.activateOverlay(0,0)
        elif Key == ord('f'): #check for existing points and follow to the next one
            if len(self.Polygon) > 0 and len(self.Edits) > 0:
                self.followPolygon() #follow to the next point
            else:
                self.activateOverlay(1,3)
        elif Key == 0x09: # Tab key, switch between direction options
            if len(self.Direction) > 1 and len(self.Polygon) > 0:
                self.SnapSpin -= 1
                if self.SnapSpin < 0:
                    self.SnapSpin += len(self.Direction)
                self.Polygon.pop(len(self.Polygon)-1)
                self.Polygon.append(self.Direction[self.SnapSpin])
                self.redraw(Indicator=True)
        elif Key == ord('i'):
            self.Indicator = not(self.Indicator)
            self.redraw(Indicator=self.Indicator)
        elif Key == ord('s'): #exit editor and apply changes to mask
            if self.showMessage(1,"Exit Editor","Do you want to end editing and save the frame?"):
                self.save_frame(True)
        elif Key == ord('m'): # use pymatting approximation
            if self.checkTrimap() == True:
                if self.showMessage(1,"Alpha Matting","Use the current background and unknown Polygons for Alpha matting?"):
                    self.pymatting()
            else:
                self.showMessage(0,"Trimap not defined","To use Alpha mapping a Trimap has to be created. Make sure both background (Key 8) and Unknown (Key 9) have at least one Polygon.")
        elif Key == ord('q') or Key == 0x1B: #exit editor and go to the next frame
            if self.moving == 1:
                self.moving = 0
                self.redraw(Update=True)
            else:
                if self.showMessage(1,"Exit Editor","Do you want to end editing?") == True:
                    cv2.destroyWindow("Edit Frame")
                    self.Saved = True
        elif Key == ord("e"): #enter moving mode
            if len(self.Edits)> 0:
                self.moving = 1 - self.moving
                self.redraw()
        elif Key == ord('n'):
            self.normals()
        elif Key == ord('d'):
            self.EdgeDetection()
        elif Key == ord('b'): #brush mode
            pass # soon
        elif Key >= 48 and Key <= 58: #number key pressed, change polygon index
            if Key-48 != self.ZoneIndex:
                if len(self.Polygon) > 0:
                    answer =  self.showMessage(2,"Change Zone Index","A Zone has already been marked. This zone will be converted to the new index. Do you want to erase the current zone?")
                    if answer == True:
                        self.Polygon = [] #reset Polygon
                        self.ZoneIndex = Key - 48
                        self.activateOverlay(1,0)
                    elif answer == False:
                        self.ZoneIndex = Key - 48 #update ZoneIndex
                        self.activateOverlay(1,0)
                    self.redraw(Indicator=self.Indicator)
                else:
                    self.ZoneIndex = Key - 48 #update ZoneIndex
                    self.activateOverlay(1,0)
        elif Key == -1: #refresh triggerd
            self.OverlayUpdate()
        if not self.Saved:
            return 1
        self.Refresh = 0
        return 0

    def activateOverlay(self,Zone,Text):
        self.Offset[Zone] = self.OffsetMax[Zone]
        self.Refresh = 5
        self.State[Zone] = 0
        self.Display[Zone] = Text
    
    def showMessage(self,Type,Caption,Text):
        root = tk.Tk()
        root.withdraw()
        response = showinfo(Caption,Text) if Type == 0 else askyesno(Caption,Text) if Type == 1 else askyesnocancel(Caption,Text)
        root.destroy()
        return response
        
    def normals(self): #find normals for every point and line in Polygon
        self.normals_back = np.zeros((len(self.Edits[len(self.Edits)-1][0]),2))
        self.normals_point = np.zeros((len(self.Edits[len(self.Edits)-1][0]),2))
        for Index in range(len(self.Edits[len(self.Edits)-1][0])):
            self.normals_back[Index] = [self.Edits[len(self.Edits)-1][0][Index][1]-self.Edits[len(self.Edits)-1][0][Index-1][1],-(self.Edits[len(self.Edits)-1][0][Index][0]-self.Edits[len(self.Edits)-1][0][Index-1][0])]
        self.normals_point = (self.normals_back + np.roll(self.normals_back,-1,0))/2
        self.normals_back = self.normals_back*10 / np.linalg.norm(self.normals_back,ord=2,axis=1,keepdims=True)
        self.normals_point = self.normals_point*10 / np.linalg.norm(self.normals_point,ord=2,axis=1,keepdims=True)
        self.frame = copy.deepcopy(self.base_frame) #take the raw image
        for Polygon, ColorCode in self.Edits: #redraw polygons
            cv2.fillPoly(self.frame,np.array([Polygon],dtype=int),(255*self.ColorCode[ColorCode][0],255*self.ColorCode[ColorCode][1],255*self.ColorCode[ColorCode][2]))
            if Polygon == self.Edits[len(self.Edits)-1][0]:
                for Index, Point in enumerate(Polygon):
                    cv2.line(self.frame,np.array(Point),np.array(Point+self.normals_point[Index],dtype=int),(0,0,0),2)
                    cv2.line(self.frame,np.array(Point),np.array(Point-self.normals_point[Index],dtype=int),(0,0,0),2)
                    mid = np.array([(Point[0] + Polygon[Index-1][0])/2,(Point[1] + Polygon[Index-1][1])/2],dtype=int)
                    cv2.line(self.frame,np.array(mid),np.array(mid+self.normals_back[Index],dtype=int),(255,255,255),2)
                    cv2.line(self.frame,np.array(mid),np.array(mid-self.normals_back[Index],dtype=int),(255,255,255),2)
        self.frame = np.array(cv2.addWeighted(self.base_frame,0.5,self.frame,0.5,0)) #make anything drawn transparent

    def changeMode(self,x,y):
        x,y = self.snap(x,y,True)
        self.moving = 2
        Container, activePolygon = self.find_Polygons(x,y)
        self.SafetyCopy = [copy.deepcopy(self.Edits),Container,activePolygon]
        Key = 0
        while Key != 13 and Key != 0x1B and Key != 'e' and Key != ord('q') and Key != ord('R') and Key != 8: #m, enter, space, backspace, escape
            self.redraw(Update=True,Moving = Container[activePolygon])#+[activePolygon])
            Key = cv2.waitKey(self.Refresh)
            if Key in [ord('w'),ord('W'),ord('a'),ord('A'),ord('s'),ord('S'),ord('d'),ord('D')]: #move point
                for Index in Container:
                    self.Edits[Index[0]][0][Index[1]][1] = self.Edits[Index[0]][0][Index[1]][1] - (1 if Key == ord('w') else 0) - (10 if Key == ord('W') else 0) + (1 if Key == ord('s') else 0) + (10 if Key == ord('S') else 0)
                    self.Edits[Index[0]][0][Index[1]][0] = self.Edits[Index[0]][0][Index[1]][0] - (1 if Key == ord('a') else 0) - (10 if Key == ord('A') else 0) + (1 if Key == ord('d') else 0) + (10 if Key == ord('D') else 0)
            elif Key == ord('X'):
                self.SafetyCopy = [copy.deepcopy(self.Edits),Container,activePolygon]
                for Index in Container:
                    if len(self.Edits[Index[0]][0]) > 2:
                        self.Edits[Index[0]][0].pop(Index[1])
                        Container, activePolygon = self.find_Polygons(self.Edits[Container[activePolygon][0]][0][Container[activePolygon][1]-1][0],self.Edits[Container[activePolygon][0]][0][Container[activePolygon][1]-1][1])
                    else:
                        self.Edits.pop(Index[0])
                        self.moving = 1 if len(self.Edits)> 0 else 0
                        return
            elif Key == ord('n') or Key == ord('l'): #step through one Polygon
                Poly = self.Edits[Container[activePolygon][0]][0]
                if Key == ord('n'):
                    Container[activePolygon][1] = Container[activePolygon][1]+1 if Container[activePolygon][1] < len(self.Edits[Container[activePolygon][0]][0])-1 else Container[activePolygon][1]-len(self.Edits[Container[activePolygon][0]][0])+1
                elif Key == ord('l'):
                    Container[activePolygon][1] = Container[activePolygon][1]-1 if Container[activePolygon][1] > 0 else Container[activePolygon][1]+len(self.Edits[Container[activePolygon][0]][0])-1
                Container,activePolygon = self.find_Polygons(self.Edits[Container[activePolygon][0]][0][Container[activePolygon][1]][0],self.Edits[Container[activePolygon][0]][0][Container[activePolygon][1]][1])
            elif Key == ord('I'):
                for Index in Container:
                    self.Edits[Index[0]][0].insert(Index[1],copy.deepcopy(self.Edits[Index[0]][0][Index[1]])) #duplicate point in array
            elif Key == 0x09:
                activePolygon = activePolygon + (1 if activePolygon < len(Container)-1 else -(len(Container)-1))
                while Container[activePolygon,0] < len(self.Edits)-1: #rotate Polygons to have active one on top
                    self.Edits.insert(0,self.Edits.pop(len(self.Edits)-1))
                    Container[:,0] += 1
                    Container[Container[:,0]>len(self.Edits)-1,0] = 0
            elif Key == 8:
                self.Edits,Container,activePolygon = self.SafetyCopy
            elif Key == -1:
                self.OverlayUpdate()
        self.moving = 1

    def find_Polygons(self,x,y): # finds clostest Point to click, rotates Points to be on top
        Container = []
        for IndexPoly in range(len(self.Edits)):
            for IndexPoint in range(len(self.Edits[IndexPoly][0])):
                if [x,y] == self.Edits[IndexPoly][0][IndexPoint]:
                    Container.append([IndexPoly,IndexPoint])
        Container = np.array(Container)
        while Container[len(Container[:,0])-1][0] < len(self.Edits)-1: #rotate Polygons to have active one on top
            self.Edits.insert(0,self.Edits.pop(len(self.Edits)-1))
            Container[:,0] += 1
            Container[Container[:,0]>len(self.Edits)-1,0] = 0
        for i in range(len(Container[:,0])):
            while Container[i][1] < len(self.Edits[Container[i][0]][0])-1:  #rotate points of each Polygon to have active Point on Top
                self.Edits[Container[i][0]][0].insert(0,self.Edits[Container[i][0]][0].pop(len(self.Edits[Container[i][0]][0])-1))
                Container[i][1] += 1
        return Container, len(Container[:,0])-1

    def save_frame(self,Edited=True):
        if self.multiple:
            Set_Choice = tk.Tk()
            Set_Choice.geometry(f"300x{(len(self.Sets)+2)*50}")
            Set_Choice.eval('tk::PlaceWindow . center')
            Set_Choice.attributes('-topmost','true')
            Set_Choice.overrideredirect(True)
            Text = tk.Canvas(Set_Choice,width=300,height=50,bg='lightgrey')
            Text.create_text(150,25,font=('Helvetica 15 bold'),text="Select Dataset")
            Text.place(relheight=1/(len(self.Sets)+2),relwidth=1,rely=0)
            for idx,dir in enumerate(self.Sets):
                New_Button = tk.Button(Set_Choice,text=dir,command = lambda choice = dir: self.set_Dataset(choice,Set_Choice,Edited))
                New_Button.place(relheight=1/(len(self.Sets)+2),relwidth=1,rely=(idx+1)/(len(self.Sets)+2))
            Cancel_Button = tk.Button(Set_Choice,text='Cancel',command = lambda: self.set_Dataset('Cancel',Set_Choice))
            Cancel_Button.place(relheight=1/(len(self.Sets)+2),relwidth=1,rely=(idx+2)/(len(self.Sets)+2))
            Set_Choice.mainloop()
        else: #correction mode
            map_1, map_2 = self.create_maps()
            cv2.imwrite(self.file[0:len(self.file)-6]+"_B.jpg",self.frame)
            if not self.file[-3:] == 'jpg': #single photo mode
                cv2.imwrite(self.file[0:len(self.file)-6]+"_C.jpg",map_1)
                cv2.imwrite(self.file[0:len(self.file)-6]+"_D.jpg",map_2)
            self.Saved = True
    
    def set_Dataset(self,Choice,root,Edited=True):
        root.destroy()
        print(Choice)
        if Choice != 'Cancel':
            os.chdir(os.path.join(self.path,Choice))
            map_1, map_2 = self.create_maps()
            Key = 0
            print("Test")
            cv2.destroyWindow("Edit Frame")
            cv2.namedWindow("Review",cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("Review",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Review",map_1)
            self.showMessage(0,"Confirm Saving","Frame "+self.file[0:len(self.file)-4]+"_"+str(self.frame_number)[0:len(str(self.frame_number))-2]+" about to save to Set '"+Choice+"'. Review the mask and confirm with 'Enter' or Cancel and go back to the previous screen with 'Escape'.")
            while Key != ord('q') and Key != 0x1B and Key != 0x08 and Key != 0x20 and Key != 13:    
                Key = cv2.waitKey(0)
            if Key == ord('q') or Key == 0x1B or Key == 0x08: #q, escape, backspace
                cv2.destroyWindow("Review")
                return
            else: # space, enter
                self.Saved = True
                cv2.imwrite(self.file[0:len(self.file)-4]+"_"+str(self.frame_number)[0:len(str(self.frame_number))-2]+"_A.jpg",self.base_frame)
                if Edited == True:
                    cv2.imwrite(self.file[0:len(self.file)-4]+"_"+str(self.frame_number)[0:len(str(self.frame_number))-2]+"_B.jpg",self.frame)
                    cv2.imwrite(self.file[0:len(self.file)-4]+"_"+str(self.frame_number)[0:len(str(self.frame_number))-2]+"_C.jpg",map_1)
                    cv2.imwrite(self.file[0:len(self.file)-4]+"_"+str(self.frame_number)[0:len(str(self.frame_number))-2]+"_D.jpg",map_2)
                    os.chdir(self.path+"/"+"data")
                    try:
                        np.savetxt(self.file[0:len(self.file)-4]+"_"+str(self.frame_number)[0:len(str(self.frame_number))-2]+"_data.csv", np.concatenate([np.array([[Point[0],Point[1],Poly[1],idx] for Point in Poly[0]]) for idx,Poly in enumerate(self.Edits)]), delimiter=",",fmt='%1.0f')
                    except:
                        if self.showMessage(1,"Saving Data Failed","Data could from this Edit could not be stored because the Data Folder is inaccesable or the access to the file is restricted. Do you want to store this data as the template?"):
                            self.boat = copy.deepcopy(self.Edits)
                cv2.destroyWindow("Review")

    def create_maps(self):
        if self.multiple:
            map_1 = np.full((1440,1920),255,dtype=np.uint8) #bw map for identifying water
            map_2 = np.full((1440,1920),255,dtype=float) #grayscale map for complete classification
            for alphaMap in self.AlphaMap:
                map_1[alphaMap[0][:,:,0]>254] = 0
                map_2[alphaMap[0][:,:,0]>254] = 255*alphaMap[1]/10
        else:
            map_1 = cv2.imread(self.video[:len(self.video)-6]+"_C.jpg")
            map_2 = cv2.imread(self.video[:len(self.video)-6]+"_D.jpg")
        for Polygon, ColorCode in self.Edits:
            if ColorCode > -1:
                cv2.fillPoly(map_1,np.array([Polygon]),(0,0,0))
                cv2.fillPoly(map_2,np.array([Polygon]),(255*ColorCode/10))
        return map_1, map_2

    def declare_boundaries(self,event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.moving == 1:
                self.changeMode(x,y)
            elif self.moving == 0:
                x,y = self.snap(x,y,self.snapG)
                self.Polygon.append([x,y])
                cv2.line(self.frame,self.Polygon[len(self.Polygon)-2],self.Polygon[len(self.Polygon)-1],(255*self.ColorCode[self.ZoneIndex][0],255*self.ColorCode[self.ZoneIndex][1],255*self.ColorCode[self.ZoneIndex][2]),2)
            self.redraw(Indicator=self.Indicator,Update=True)
            return
        if event == cv2.EVENT_RBUTTONDOWN and len(self.Polygon) > 1:
            self.add_poligon()
 
    def snap(self,x,y,snapG):
        if snapG == True: #snapping to the nearest existing point
            minDist = [10000,x,y]
            for Polygon, Colorcode in self.Edits:
                for Point in Polygon:
                    if np.sqrt((x-Point[0])**2+(y-Point[1])**2) < minDist[0] and Colorcode > -1:
                        minDist = [np.sqrt((x-Point[0])**2+(y-Point[1])**2),Point[0],Point[1]]
            return minDist[1],minDist[2]
        if self.snapH == True:
            x = 1920 if x > 960 else 0
        if self.snapV == True:
            y = 1440 if y > 720 else 0
        return x,y
    
    def add_poligon(self): #add currently stored Polygon to the list of Edits
        if len(self.Polygon) == 0:
            return
        for i in range(len(self.Polygon)):
            if self.Polygon[len(self.Polygon)-1-i]==self.Polygon[len(self.Polygon)-2-i]:
                self.Polygon.pop(len(self.Polygon)-2-i)
        self.Edits.append(list((self.Polygon,self.ZoneIndex)))
        self.Polygon = []
        self.redraw(Indicator=False,Update=True) #no indicator since Polygon is Empty

    def followPolygon(self): #snaps to the closest point on a polygon or follows it if on existing point
        self.Direction = []
        x,y = self.Polygon[len(self.Polygon)-1]
        for Polygon, _ in self.Edits:
            for Index in range(len(Polygon)): # find all adjacent points
                if [x,y] == Polygon[Index]:
                    self.Direction.append(Polygon[Index-1])
                    self.Direction.append(Polygon[Index+1-len(Polygon)])
        if len(self.Polygon) > 1: # continue in current direction
            for Index in range(len(self.Direction)):
                if self.Direction[Index] == self.Polygon[len(self.Polygon)-2]: #found previous Point
                    self.SnapSpin = Index-2*(Index%2)+1
                    break
        if len(self.Direction) == 0:
            self.Direction.append(self.snap(x,y,True))
            self.SnapSpin = 0
        try:
            self.Polygon.append(self.Direction[self.SnapSpin])
        except:
            return
        self.redraw(Indicator = True)

    def redraw(self,Overlay=True,Indicator=False,Update=False,Moving = [-1,-1]): #draw all the Polygons on the raw frame
        self.frame = copy.deepcopy(self.base_frame) #take the raw image
        for alphaMap in self.AlphaMap: #Display alphamaps
            self.frame[alphaMap[0][:,:,0]>254] = [self.ColorCode[alphaMap[1]][2]*255,self.ColorCode[alphaMap[1]][1]*255,self.ColorCode[alphaMap[1]][0]*255]
        for Polygon, ColorCode in self.Edits: #redraw polygons
            if ColorCode > -1:
                cv2.fillPoly(self.frame,np.array([Polygon],dtype=int),(255*self.ColorCode[ColorCode][0],255*self.ColorCode[ColorCode][1],255*self.ColorCode[ColorCode][2]))
                if self.moving == 1: #dots on every corner
                    for Point in Polygon:
                        cv2.circle(self.frame,Point,7,(255*self.ColorCode[ColorCode][0],255*self.ColorCode[ColorCode][1],255*self.ColorCode[ColorCode][2]),-1)
        if self.moving == 2: #show active Polygon
            for i in range(len(self.Edits)): 
                if i == Moving[0]:
                    for Point in self.Edits[i][0]:
                        cv2.circle(self.frame,Point,7,(0,0,0),-1)
        if Indicator == True or self.snapG==True or len(self.Polygon)==1:
            if len(self.Polygon)>0:
                cv2.circle(self.frame,self.Polygon[len(self.Polygon)-1],10,(255*self.ColorCode[self.ZoneIndex][0],255*self.ColorCode[self.ZoneIndex][1],255*self.ColorCode[self.ZoneIndex][2]),-1)
        if self.moving == 2 or self.moving == 1:
            cv2.polylines(self.frame,np.array([[(0,0),(1920,0),(1920,1440),(0,1440)]]),True,(255,255,255),5)
            if Moving[0] != -1:
                cv2.circle(self.frame,self.Edits[Moving[0]][0][Moving[1]],10,(255,255,255),-1)
        if Overlay == True:    
            cv2.fillPoly(self.frame,np.array([[(0-self.Offset[0], 600), (250-self.Offset[0], 600), (250-self.Offset[0], 630), (280-self.Offset[0], 630), (280-self.Offset[0], 800), (250-self.Offset[0], 800), (250-self.Offset[0], 830), (0-self.Offset[0], 830)]]),(200,200,200))
            cv2.circle(self.frame,(250-self.Offset[0], 630),30,(200,200,200),-1)
            cv2.circle(self.frame,(250-self.Offset[0], 800),30,(200,200,200),-1)
            cv2.fillPoly(self.frame,np.array([[(655, 0-self.Offset[1]), (655, 50-self.Offset[1]), (685, 80-self.Offset[1]), (1250, 80-self.Offset[1]), (1280, 50-self.Offset[1]), (1280, 0-self.Offset[1])]]),(100,100,100))
            cv2.circle(self.frame,(685, 50-self.Offset[1]),30,(100,100,100),-1)
            cv2.circle(self.frame,(1250, 50-self.Offset[1]),30,(100,100,100),-1)
        self.frame = np.array(cv2.addWeighted(self.base_frame,0.5,self.frame,0.5,0)) #make anything drawn transparent
        if Overlay == True:
            for index in range(len(self.Polygon)-1): #redraw lines
                cv2.line(self.frame,self.Polygon[index],self.Polygon[index+1],(255*self.ColorCode[self.ZoneIndex][0],255*self.ColorCode[self.ZoneIndex][1],255*self.ColorCode[self.ZoneIndex][2]),2)
            self.frame = cv2.putText(self.frame,f"New snapping settings:",(10-self.Offset[0],650),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),2)       
            self.frame = cv2.putText(self.frame,f"Horizontal: {self.snapH}",(10-self.Offset[0],700),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),2)       
            self.frame = cv2.putText(self.frame,f"Vertical: {self.snapV}",(10-self.Offset[0],750),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),2)       
            self.frame = cv2.putText(self.frame,f"Existing: {self.snapG}",(10-self.Offset[0],800),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),2)
            if self.Display[1] == 0:
                self.frame = cv2.putText(self.frame,f"The new ZoneIndex is {self.ZoneIndex}, {self.classes[self.ZoneIndex]}",(780-len(self.classes[self.ZoneIndex]*10),50-self.Offset[1]),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2)
            elif self.Display[1] == 1:
                self.frame = cv2.putText(self.frame,f"The template has been updated!",(666,50-self.Offset[1]),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2)
            elif self.Display[1] == 2:
                self.frame = cv2.putText(self.frame,f"This is the Original Frame!",(750,50-self.Offset[1]),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2)
            elif self.Display[1] == 3:
                self.frame = cv2.putText(self.frame,f"Select a starting Point to follow!",(710,50-self.Offset[1]),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2)
        if Update == True:
            cv2.imshow("Edit Frame",self.frame)

    def OverlayUpdate(self): #creates Annotations sliding in from the edges for information; implemented: left, top
        if self.Refresh == 5:
            if self.State[0] != -1:
                if self.Offset[0] > 0 and self.State[0] == 0: # left
                    self.Offset[0] -= int(5 + self.Offset[0] / 50)
                elif self.State[0] > 5:
                    self.State[0] -= 50
                elif self.Offset[0] < 10 and self.State[0] == 0:
                    self.State[0] = 1001
                elif self.State[0] == 1 and self.Offset[0] < 280:
                    self.Offset[0] += int(5 + self.Offset[0] / 50)
                else:
                    self.State[0] = -1
            if self.State[1] != -1:
                if self.Offset[1] > 0 and self.State[1] == 0: # top
                    self.Offset[1] -= int(5 + self.Offset[1] / 50)
                elif self.State[1] > 5:
                    self.State[1] -= 50
                elif self.Offset[1] < 10 and self.State[1] == 0:
                    self.State[1] = 1001
                elif self.State[1] == 1 and self.Offset[1] < 100:
                    self.Offset[1] += int(2 + self.Offset[1] / 50)
                else:
                    self.State[1] = -1
                    self.Display[1] = 0              
            if self.State[0] == -1 and self.State[1] == -1: # all text gone
                self.Refresh = 0
            self.redraw(Indicator=self.Indicator)

    def checkTrimap(self): #check if both background and unknown are defined
            check = np.array([False,False])
            for _,ColorCode in self.Edits: 
                if ColorCode ==8:
                    check[0] = True
                if ColorCode == 9:
                    check[1] = True
            return check.all() == True

    def pymatting(self,Confirm=True): #use Polygons to create an Alpha matting map
        trimap = np.zeros((1440,1920))
        display = np.zeros((1440,1920,1))
        display = cv2.putText(display,"Loading. Please wait.",(480,780),cv2.FONT_HERSHEY_SIMPLEX,3,[255],2)
        if Confirm:
            cv2.destroyWindow("Edit Frame")
        cv2.namedWindow("Loading",cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Loading",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Loading",display)
        cv2.waitKey(1)
        for Polygon, Colorcode in self.Edits:
            if Colorcode == 8 or Colorcode == 9:
                cv2.fillPoly(trimap,np.array([Polygon]),[0.5*(10-Colorcode)])
        image = np.array(copy.deepcopy(self.base_frame),dtype=float)/255
        try:
            gc.collect() #clear memory
            output = pymatting.estimate_alpha_cf(image,trimap)
        except:
            self.showMessage(0,"Mapping Failed","The solver failed to reach a result for the given input. Validate the input and try again.")
            cv2.destroyWindow("Loading")
            return
        cv2.destroyWindow("Loading")
        output = cv2.GaussianBlur(output,(5,5), sigmaX=np.sqrt(5), sigmaY=np.sqrt(5))
        output[output<0.5] = 0
        output[output>0.5] = 1
        new = np.empty((1440,1920,3))
        new[:,:,0],new[:,:,1] ,new[:,:,2]  = output,output,output
        new = new*-1 +1
        testframe = image + new * 0.7
        cv2.namedWindow("Output",cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Output",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Output",testframe)
        if Confirm and self.showMessage(1,"Confirm Map","Should this Map be added to the frame?"):
            Set_Choice = tk.Tk()
            Set_Choice.geometry(f"300x{(len(self.Sets)+2)*50}")
            Set_Choice.eval('tk::PlaceWindow . center')
            Set_Choice.attributes('-topmost','true')
            Set_Choice.overrideredirect(True)
            Text = tk.Canvas(Set_Choice,width=300,height=50,bg='lightgrey')
            Text.create_text(150,25,font=('Helvetica 15 bold'),text="Select Dataset")
            Text.place(relheight=1/(len(self.Sets)+2),relwidth=1,rely=0)
            for idx,dir in enumerate(self.classes):
                New_Button = tk.Button(Set_Choice,text=dir,command = lambda choice = idx: self.set_Class(choice,Set_Choice))
                New_Button.place(relheight=1/(len(self.Sets)+2),relwidth=1,rely=(idx+1)/(len(self.Sets)+2))
            Cancel_Button = tk.Button(Set_Choice,text='Cancel',command = lambda: self.set_Class('Cancel',Set_Choice))
            Cancel_Button.place(relheight=1/(len(self.Sets)+2),relwidth=1,rely=(idx+2)/(len(self.Sets)+2))
            Set_Choice.mainloop()
        if self.AlphaMapClass != len(self.classes):
            self.AlphaMap.append(np.array([(new*255).astype(np.uint8),self.AlphaMapClass],dtype=object))
            for Polygon in self.Edits:
                if Polygon[1] == 8:
                    Polygon[1] = -(self.AlphaMapClass+2*len(self.classes)*self.AlphaMapNumber)
                if Polygon[1] == 9:
                    Polygon[1] = -(self.AlphaMapClass+2*len(self.classes)*(self.AlphaMapNumber)+len(self.classes))
            self.AlphaMapNumber +=1
        cv2.destroyWindow("Output")
        if Confirm:
            self.redraw()
    
    def set_Class(self,choice,Window):
        self.AlphaMapClass = choice
        Window.destroy()

    def importAlphaMaps(self,Num_Maps):
        cv2.waitKey(0)
        for idx in range(Num_Maps):
            for Index, _ in enumerate(self.Edits):
                if self.Edits[Index][1] < -len(self.classes)*2*idx and self.Edits[Index][1] > -(len(self.classes)*2*idx+1+len(self.classes)):
                    self.AlphaMapClass = -(self.Edits[Index][1]+len(self.classes)*2*idx)
                    self.Edits[Index][1] = 8
                if self.Edits[Index][1] < -(len(self.classes)*2*idx+len(self.classes)) and self.Edits[Index][1] > -(len(self.classes)*2*idx+1+2*len(self.classes)):
                    self.Edits[Index][1] = 9
            self.pymatting(False)


    
    def EdgeDetection(self):
        Key = 0
        th1 = 100
        th2 = 20012
        cv2.namedWindow("Canny edge detection",cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Canny edge detection",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        while Key != 13:
            edges = cv2.Canny(cv2.GaussianBlur(copy.deepcopy(self.base_frame),(3,3), sigmaX=0, sigmaY=0), threshold1=th1, threshold2 = th2)
            edges_disp = cv2.putText(edges,f"Lower Threshold: {th1:.0f}",(1600,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)
            edges_disp = cv2.putText(edges_disp,f"Upper Threshold: {th2:.0f}",(1600,100),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)
            cv2.imshow("Canny edge detection", edges_disp)
            Key = cv2.waitKey(0)
            th1 = th1 + (10 if Key == ord('u') else 0) - (10 if Key == ord('j')else 0)
            th2 = th2 + (10 if Key == ord('i') else 0) - (10 if Key == ord('k')else 0)
        cv2.destroyWindow("Canny edge detection")


if __name__ == "__main__":
    vid1 = converter(dir_root,video_file,start_frame)
    vid1.extract()
    cv2.destroyAllWindows()
