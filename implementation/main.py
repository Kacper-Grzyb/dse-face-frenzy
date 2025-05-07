from pynq.overlays.base import BaseOverlay
from pynq.lib.video import *
from enum import Enum
import random
import math

class Game(Enum):
    COUNTDOWN = 1
    FACEDETECT = 2
    RANDOMIZE_TIMER = 3


base = BaseOverlay("base.bit")

# monitor configuration: 640*480 @ 60Hz
Mode = VideoMode(640,480,24)
hdmi_out = base.video.hdmi_out
hdmi_out.configure(Mode,PIXEL_BGR)
hdmi_out.start()

# monitor (output) frame buffer size
frame_out_w = 1920
frame_out_h = 1080
# camera (input) configuration
frame_in_w = 640
frame_in_h = 480

# initialize camera from OpenCV
import cv2

videoIn = cv2.VideoCapture(0)
videoIn.set(cv2.CAP_PROP_FRAME_WIDTH, frame_in_w);
videoIn.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_in_h);

print("Capture device is open: " + str(videoIn.isOpened()))

# Capture webcam image
import numpy as np
import time

game_state = Game.RANDOMIZE_TIMER
duration = 0
start_time = 0

while base.buttons[3].read()==0:
    match game_state:
        case Game.RANDOMIZE_TIMER:
            start_time = time.time()
            duration = random.uniform(2, 5)
            game_state = Game.COUNTDOWN
        case Game.COUNTDOWN:
            ret, frame_vga = videoIn.read()
            outframe = hdmi_out.newframe()

            # Display webcam image via HDMI Out

            if not ret:
                    raise RuntimeError("Failed to read from camera.")

            #cv2.imwrite("output.jpg", frame_vga)

            np_frame = frame_vga

            cv2.putText(
              img=np_frame,
              text=f"{math.ceil(duration-(time.time()-start_time))}",
              org=(50, 50),
              fontFace=cv2.FONT_HERSHEY_SIMPLEX,
              fontScale=1,
              color=(255, 255, 255),
              thickness=2,
              lineType=cv2.LINE_AA
           )



            outframe[0:480,0:640,:] = frame_vga[0:480,0:640,:]
            hdmi_out.writeframe(outframe)

            if time.time() - start_time > duration:
                print(time.time())
                print(time.time() - start_time)
                game_state = Game.FACEDETECT
        case Game.FACEDETECT:
            ret, frame_vga = videoIn.read()
            outframe = hdmi_out.newframe()

            if not ret:
                    raise RuntimeError("Failed to read from camera.")

            np_frame = frame_vga

            # randomize timer
            face_cascade = cv2.CascadeClassifier(
                '/home/xilinx/jupyter_notebooks/base/video/data/'
                'haarcascade_frontalface_default.xml')
            eye_cascade = cv2.CascadeClassifier(
                '/home/xilinx/jupyter_notebooks/base/video/data/'
                'haarcascade_eye.xml')

            gray = cv2.cvtColor(np_frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            print(f"Faces detected: {len(faces)}")

            for (x,y,w,h) in faces:
                cv2.rectangle(np_frame,(x,y),(x+w,y+h),(255,0,0),2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = np_frame[y:y+h, x:x+w]

                eyes = eye_cascade.detectMultiScale(roi_gray)
                for (ex,ey,ew,eh) in eyes:
                    cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

            outframe[0:480,0:640,:] = frame_vga[0:480,0:640,:]
            hdmi_out.writeframe(outframe)
            time.sleep(3)
            game_state = Game.RANDOMIZE_TIMER


    # Output OpenCV results via HDMI

    #cv2.imwrite(f"output1_{i}.jpg",outframe)
print("done")
videoIn.release()
hdmi_out.stop()
print("deleting hdmi_out")
del hdmi_out
print("finished")
