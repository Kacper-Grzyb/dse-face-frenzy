from enum import Enum
import cv2
import numpy as np
import time
import random
import math

class ShowFacesState(Enum):
    RANDOMIZE_TIMER = 1
    COUNTDOWN = 2
    CAPTURE_AND_DETECT = 3

class ShowFaces:
    def __init__(self, hdmi_out, video_in):
        self.hdmi_out = hdmi_out
        self.video_in = video_in
        self.state = ShowFacesState.RANDOMIZE_TIMER
        self.duration = 0
        self.start_time = 0
        self.face_cascade = cv2.CascadeClassifier(
            '/home/xilinx/jupyter_notebooks/base/video/data/haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(
            '/home/xilinx/jupyter_notebooks/base/video/data/haarcascade_eye.xml')
        self.detected_faces = []

    def run(self):
        """Run one iteration of the ShowFaces state machine and return True if completed"""
        if self.state == ShowFacesState.RANDOMIZE_TIMER:
            self._randomize_timer()
            return False
        elif self.state == ShowFacesState.COUNTDOWN:
            self._countdown()
            return False
        elif self.state == ShowFacesState.CAPTURE_AND_DETECT:
            self._capture_and_detect()
            # Reset state for next time
            self.state = ShowFacesState.RANDOMIZE_TIMER
            return True  # Completed the ShowFaces process
        
        return False

    def get_detected_faces(self):
        """Return the number of detected faces from the last run"""
        return self.detected_faces

    def _randomize_timer(self):
        """Set a random countdown duration"""
        self.start_time = time.time()
        self.duration = random.uniform(2, 5)
        self.state = ShowFacesState.COUNTDOWN
        
    def _countdown(self):
        """Display countdown on screen"""
        ret, frame_vga = self.video_in.read()
        outframe = self.hdmi_out.newframe()

        if not ret:
            raise RuntimeError("Failed to read from camera.")

        np_frame = frame_vga
        
        # Display countdown
        cv2.putText(
            img=np_frame,
            text=f"{math.ceil(self.duration-(time.time()-self.start_time))}",
            org=(50, 50),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=2,
            lineType=cv2.LINE_AA
        )

        outframe[0:480, 0:640, :] = frame_vga[0:480, 0:640, :]
        self.hdmi_out.writeframe(outframe)

        # Check if countdown is complete
        if time.time() - self.start_time > self.duration:
            self.state = ShowFacesState.CAPTURE_AND_DETECT
            
    def _capture_and_detect(self):
        """Capture image and detect faces"""
        ret, frame_vga = self.video_in.read()
        outframe = self.hdmi_out.newframe()

        if not ret:
            raise RuntimeError("Failed to read from camera.")

        np_frame = frame_vga

        # Detect faces
        gray = cv2.cvtColor(np_frame, cv2.COLOR_BGR2GRAY)
        self.detected_faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        print(f"Faces detected: {len(self.detected_faces)}")

        # Draw rectangles around faces and eyes
        for (x, y, w, h) in self.detected_faces:
            cv2.rectangle(np_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = np_frame[y:y+h, x:x+w]

            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

        outframe[0:480, 0:640, :] = frame_vga[0:480, 0:640, :]
        self.hdmi_out.writeframe(outframe)
        time.sleep(3)  # Show the detection results for 3 seconds
