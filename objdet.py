# import the necessary packages
import numpy as np
import argparse
import imutils
import time
import cv2
import os
from PIL import Image as imggg
from PIL import ImageTk
from tkinter import *
from tkinter import messagebox
from imutils.video import VideoStream
import datetime
import telegram_send

#telegram_send.send(messages=["App is running"])
root = Tk()
root.title("Real-Time Intrusion Detector")
root.iconbitmap("icon.ico")
fr = Frame(root)
fr.grid(row=0,column=1, sticky=N)

video = Label(root)
video.grid(row=0,column=0, sticky=W)#Video location in tkinter

canvas = Canvas(fr, width=20, height=20, highlightthickness=0)
canvas.grid(row=7,column=1, sticky=N)           #Canvas to display flashing red dot
tex=Label(fr, text="Contraband \n items detected")
tex.grid(row=7,column=2, sticky=N)              #to display text of detected

canvas.grid_remove()
tex.grid_remove()#hides text and flashing dot, use grid remove to restore again


YOLO_PATH="yolo-coco"
OUTPUT_FILE="output/outfile.avi"
# load the COCO class names from coco.names
labelsPath = os.path.sep.join([YOLO_PATH, "coco.names"])
LABELS = open(labelsPath).read().strip().split("\n")
CONFIDENCE=0.35
THRESHOLD=0.3


# initialize a list of colors to represent each possible class label
np.random.seed(42)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
        dtype="uint8")


# derive the paths to the YOLO weights and model configuration
weightsPath = os.path.sep.join([YOLO_PATH, "yolov4-tiny.weights"])
configPath = os.path.sep.join([YOLO_PATH, "yolov4-tiny.cfg"])

# load our YOLO object detector trained on COCO dataset (80 classes)
# and determine only the *output* layer names that we need from YOLO
print("[INFO] loading YOLO from disk...")
net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# initialize the video stream, pointer to output video file, and
# frame dimensions
vs = cv2.VideoCapture(0)

writer = None
(W, H) = (None, None)

val, val2, val3, val4, val5, val6, val7, val8, val9, val10= IntVar(),IntVar(),IntVar(),IntVar(),IntVar(),IntVar(),IntVar(),IntVar(),IntVar(),IntVar()#assigns integer to variable
checkboxes = [val, val2, val3, val4, val5, val6, val7, val8, val9, val10]#list of variables

text=Label(fr, text="Contraband items")
text.grid(row=0,column=0, sticky=N)
c = Checkbutton(fr, text = "Person",  variable=val)
c.grid(row=1,column=0, sticky=N)

c2 = Checkbutton(fr, text = "car      ",  variable=val2)
c2.grid(row=2,column=0, sticky=N)

c3 = Checkbutton(fr, text = "bicycle",  variable=val3)
c3.grid(row=3,column=0, sticky=N)

c4 = Checkbutton(fr, text = "cat      ",  variable=val4)
c4.grid(row=4,column=0, sticky=N)

c5 = Checkbutton(fr, text = "dog      ",  variable=val5)
c5.grid(row=5,column=0, sticky=N)

c6 = Checkbutton(fr, text = "knife         ",  variable=val6)
c6.grid(row=1,column=1, sticky=N)

c7 = Checkbutton(fr, text = "sissors       ",  variable=val7)
c7.grid(row=2,column=1, sticky=N)

c8 = Checkbutton(fr, text = "cell phone",  variable=val8)
c8.grid(row=3,column=1, sticky=N)

c9 = Checkbutton(fr, text = "laptop       ",  variable=val9)
c9.grid(row=4,column=1, sticky=N)

c10 = Checkbutton(fr, text = "handbag   ",  variable=val10)
c10.grid(row=5,column=1, sticky=N)

contr = ["person", "car", "bicycle", "cat", "dog", "knife", "sissors", "cell phone", "laptop", "handbag"]

contraband = ["aeroplane"]
#Checks which checkboxes are checked
def updat():
        contraband.clear()#clears all values in list
        for ck in checkboxes:
                if ck.get()==1:
                        ind=checkboxes.index(ck)
                        contraband.append(contr[ind])
        #print(contraband)

b1 = Button(fr, text="Update list", padx=5, pady=5, command=updat)
b1.grid(row=6, column=0, sticky=N)
flag=False #This flag will define if currently any contraband is detected or not
def clr():
        global flag
        flag=not flag
        canvas.grid_remove()
        tex.grid_remove()#hides text and flashing dot,
        telegram_send.send(messages=["Warning has been cleared"])

b4 = Button(fr, text="Clear warning", padx=5, pady=5, command=clr)
b4.grid(row=7, column=0, sticky=N)

def snap():
        takeSnapshot()

b2 = Button(root, text="Take Screenshot", padx=270, pady=5, command=snap)
b2.grid(row=1, column=0, sticky=W)

def clos():
        on_close()

b3 = Button(root, text="Quit", padx=20, pady=5, command=clos)
b3.grid(row=1, column=3,sticky=SE)


dot = canvas.create_oval(0, 0, 20, 20, outline='')
def blinking_dot(i=0):
    colors = ("white", "red")
    canvas.itemconfigure(dot, fill=colors[i])
    root.after(250, blinking_dot, 1-i)
blinking_dot()



cnt=0
# loop over frames from the video file stream
while True:
        cnt+=1
        # read the next frame from the file
        (grabbed, frame) = vs.read()

        # if the frame was not grabbed, then we have reached the end
        # of the stream
        if not grabbed:
                break
        # if the frame dimensions are empty, grab them
        if W is None or H is None:
                (H, W) = frame.shape[:2]

        # construct a blob from the input frame and then send to 
        #the YOLO object detector, giving us our bounding boxes
        # and associated probabilities
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
                swapRB=True, crop=False)
        net.setInput(blob)
        start = time.time()
        layerOutputs = net.forward(ln)
        end = time.time()

        # initialize our lists of detected bounding boxes, confidences,
        # and class IDs, respectively
        boxes = []
        confidences = []
        classIDs = []

        # loop over each of the layer outputs
        for output in layerOutputs:
                # loop over each of the detections
                for detection in output:
                        # extract the class ID and confidence (i.e., probability)
                        # of the current object detection
                        scores = detection[5:]
                        classID = np.argmax(scores)
                        confidence = scores[classID]

                        # filter out weak predictions by ensuring the detected
                        # probability is greater than the minimum probability
                        if confidence > CONFIDENCE:
                                # scale the bounding box coordinates back to
                                # the size of the image
                                box = detection[0:4] * np.array([W, H, W, H])
                                (centerX, centerY, width, height) = box.astype("int")
                                #YOLO gives us the center (x, y) coordinates of the bounding box
                                # use the center (x, y)-coordinates to derive the top
                                # and and left corner of the bounding box
                                x = int(centerX - (width / 2))
                                y = int(centerY - (height / 2))

                                # update our list of bounding box coordinates,
                                # confidences, and class IDs
                                boxes.append([x, y, int(width), int(height)])
                                confidences.append(float(confidence))
                                classIDs.append(classID)

        # suppress and remove weak confidence, overlapping bounding boxes
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE,
                THRESHOLD)
        

        # ensure at least one detection exists
        if len(idxs) > 0:
                # loop over the indexes we are keeping
                for i in idxs.flatten():
                        # extract the bounding box coordinates
                        (x, y) = (boxes[i][0], boxes[i][1])
                        (w, h) = (boxes[i][2], boxes[i][3])

                        # draw a bounding box rectangle and label on the frame
                        color = [int(c) for c in COLORS[classIDs[i]]]
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        text = "{}".format(LABELS[classIDs[i]])
                        conf=confidences[i]
                        namee=LABELS[classIDs[i]]

                        for ct in contraband:
                                if ct in text and flag==False:
                                        if conf>0.65:
                                                ts = datetime.datetime.now()#gets current time
                                                ts = ts.strftime("%m/%d/%Y, %H:%M:%S")
                                                print("A "+ct+" is detected at "+ts+"!")#Make into function, gui should have option to click the items and show if detected
                                                flag=True
                                                canvas.grid()
                                                tex.grid()#Restores hidden widgets
                                                telegram_send.send(messages=["Warning! An unauthorised object/person has been detected! "+ct+" detected at"+ts+"!"])

                        #Check for contraband in the detected objects if any
                        #Print That contraband is detected if yes.
                        


                        cv2.putText(frame, text, (x, y - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # check if the video writer is None
        
        
        
        if writer is None:
                # initialize our video writer
                fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                writer = cv2.VideoWriter(OUTPUT_FILE, fourcc, 30,
                        (frame.shape[1], frame.shape[0]), True)
        

        # write the output frame to disk
        writer.write(frame)
        def takeSnapshot():
                # grab the current timestamp and use it to construct theoutput path
                ts = datetime.datetime.now()
                filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
                p = os.path.join(( filename))#Give name to file
                # save the file
                oo = cv2.imwrite(p+".jpg", frame)
                if oo==1:
                        print("Screenshot saaved :"+p)
                else:
                        print("save failure")


        #Converting the video for Tkinter
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = imggg.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)

        
        #Setting the image on the label
        video.config(image=imgtk)
        def on_close():
                close = messagebox.askokcancel("Close", "Would you like to close the program?")
                if close:
                  root.destroy()
                  cv2.destroyAllWindows()
                  writer.release()
                  vs.release()

        root.protocol("WM_DELETE_WINDOW",  on_close)
        root.update() #Updates the Tkinter window




#remove all opened windows
cv2.destroyAllWindows()
#release the file pointers
print("[INFO] cleaning up...")
writer.release()
vs.release()


