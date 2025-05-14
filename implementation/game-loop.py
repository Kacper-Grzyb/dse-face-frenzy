from enum import Enum
import cv2
import numpy as np
import time
import random
from show_faces import ShowFaces


class GameLoopState(Enum):
    GET_READY = 1
    SHOW_FACES = 2
    EVALUATE = 3
    UPDATE_SCORE = 4


class GameLoop:
    def __init__(self, hdmi_out, video_in):
        self.hdmi_out = hdmi_out
        self.video_in = video_in
        self.state = GameLoopState.GET_READY
        self.show_faces = ShowFaces(hdmi_out, video_in)

        # Game state variables
        self.score = 0
        self.strikes = 0
        self.expected_faces = 0
        self.detected_faces = []

        # Constants
        self.MAX_STRIKES = 3

    def run(self):
        """Run one iteration of the game loop state machine"""
        if self.state == GameLoopState.GET_READY:
            self._get_ready()
            return False
        elif self.state == GameLoopState.SHOW_FACES:
            complete = self._show_faces()
            if complete:
                self.state = GameLoopState.EVALUATE
            return False
        elif self.state == GameLoopState.EVALUATE:
            self._evaluate()
            return False
        elif self.state == GameLoopState.UPDATE_SCORE:
            complete = self._update_score()
            if complete:
                if self.strikes >= self.MAX_STRIKES:
                    return True  # Game over
                else:
                    self.state = GameLoopState.GET_READY
            return False

    def get_score(self):
        """Return the current score"""
        return self.score

    def get_strikes(self):
        """Return the current number of strikes"""
        return self.strikes

    def _get_ready(self):
        """Show 'Get Ready' screen and randomly determine expected number of faces"""
        outframe = self.hdmi_out.newframe()
        np_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Set the expected number of faces (1-4 for example)
        self.expected_faces = random.randint(1, 4)

        # Display get ready message
        cv2.putText(
            img=np_frame,
            text="Get Ready!",
            org=(200, 200),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=2,
            lineType=cv2.LINE_AA,
        )

        cv2.putText(
            img=np_frame,
            text=f"Show {self.expected_faces} faces",
            org=(180, 250),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=2,
            lineType=cv2.LINE_AA,
        )

        outframe[0:480, 0:640, :] = np_frame
        self.hdmi_out.writeframe(outframe)

        # Wait for 3 seconds before moving to the next state
        time.sleep(3)
        self.state = GameLoopState.SHOW_FACES

    def _show_faces(self):
        """Run the ShowFaces state machine"""
        return self.show_faces.run()

    def _evaluate(self):
        """Evaluate if the player showed the correct number of faces"""
        self.detected_faces = self.show_faces.get_detected_faces()
        self.state = GameLoopState.UPDATE_SCORE

    def _update_score(self):
        """Update the score based on the evaluation"""
        outframe = self.hdmi_out.newframe()
        np_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        detected_count = len(self.detected_faces)

        if detected_count == self.expected_faces:
            # Success! Increment score
            self.score += 1
            result_text = "Correct!"
            color = (0, 255, 0)  # Green
        else:
            # Failure! Increment strikes
            self.strikes += 1
            result_text = "Wrong!"
            color = (0, 0, 255)  # Red

        # Display the results
        cv2.putText(
            img=np_frame,
            text=result_text,
            org=(250, 150),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=color,
            thickness=2,
            lineType=cv2.LINE_AA,
        )

        cv2.putText(
            img=np_frame,
            text=f"Expected: {self.expected_faces}, Detected: {detected_count}",
            org=(150, 200),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=2,
            lineType=cv2.LINE_AA,
        )

        cv2.putText(
            img=np_frame,
            text=f"Score: {self.score} | Strikes: {self.strikes}/{self.MAX_STRIKES}",
            org=(150, 250),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=2,
            lineType=cv2.LINE_AA,
        )

        outframe[0:480, 0:640, :] = np_frame
        self.hdmi_out.writeframe(outframe)

        # Wait for 3 seconds to let the player see the results
        time.sleep(3)
        return True
