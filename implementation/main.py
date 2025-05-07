from pynq.overlays.base import BaseOverlay
from pynq.lib.video import *
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

while base.buttons[3].read()==0:
	loop_start = time.time()

	t1 = time.time()
	ret, frame_vga = videoIn.read()
	outframe = hdmi_out.newframe()
	t2 = time.time()

	# Display webcam image via HDMI Out

	if not ret:
    		raise RuntimeError("Failed to read from camera.")

	#cv2.imwrite("output.jpg", frame_vga)

	np_frame = frame_vga

	t3 = time.time()
	"""
	face_cascade = cv2.CascadeClassifier(
    		'/home/xilinx/jupyter_notebooks/base/video/data/'
    		'haarcascade_frontalface_default.xml')
	eye_cascade = cv2.CascadeClassifier(
    		'/home/xilinx/jupyter_notebooks/base/video/data/'
    		'haarcascade_eye.xml')
	"""
	#gray = cv2.cvtColor(np_frame, cv2.COLOR_BGR2GRAY)
	
	"""
	faces = face_cascade.detectMultiScale(gray, 1.3, 5)
	"""
	t4 = time.time()
	"""
	print(f"Faces detected: {faces}")

	for (x,y,w,h) in faces:
		cv2.rectangle(np_frame,(x,y),(x+w,y+h),(255,0,0),2)
		roi_gray = gray[y:y+h, x:x+w]
		roi_color = np_frame[y:y+h, x:x+w]

		eyes = eye_cascade.detectMultiScale(roi_gray)
		for (ex,ey,ew,eh) in eyes:
			cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

	"""
	t5 = time.time()
	# Output OpenCV results via HDMI
	outframe[0:480,0:640,:] = frame_vga[0:480,0:640,:]
	hdmi_out.writeframe(outframe)
	#cv2.imwrite(f"output1_{i}.jpg",outframe)
	t6 = time.time()
	print(f"""
        	Read Frame: {t2 - t1:.4f}s
        	Face/Eye Detection: {t4 - t3:.4f}s
        	Drawing Rectangles: {t5 - t4:.4f}s
        	HDMI Output: {t6 - t5:.4f}s
        	Total Loop Time: {t6 - loop_start:.4f}s
	""")

print("done")
videoIn.release()
hdmi_out.stop()
print("deleting hdmi_out")
del hdmi_out
print("finished")
