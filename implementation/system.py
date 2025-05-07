from enum import Enum
import cv2
import numpy as np
import time
from pynq.overlays.base import BaseOverlay
from pynq.lib.video import *
from game_loop import GameLoop

class SystemState(Enum):
    IDLE = 1
    GAME_LOOP = 2
    GAME_OVER = 3
    PAUSED = 4

class PauseReason(Enum):
    USER_PAUSED = 1
    SYSTEM_PAUSED = 2
    FOCUS_LOST = 3

class FaceFrenzySystem:
    def __init__(self):
        # Initialize PYNQ hardware
        self.base = BaseOverlay("base.bit")
        
        # Monitor configuration: 640*480 @ 60Hz
        mode = VideoMode(640, 480, 24)
        self.hdmi_out = self.base.video.hdmi_out
        self.hdmi_out.configure(mode, PIXEL_BGR)
        self.hdmi_out.start()
        
        # Initialize camera from OpenCV
        self.video_in = cv2.VideoCapture(0)
        self.video_in.set(cv2.CAP_PROP_FRAME_WIDTH, 640);
        self.video_in.set(cv2.CAP_PROP_FRAME_HEIGHT, 480);
        
        if not self.video_in.isOpened():
            raise RuntimeError("Failed to open camera.")
            
        print("Capture device is open: " + str(self.video_in.isOpened()))
        
        # Initialize system state
        self.state = SystemState.IDLE
        self.pause_reason = None
        self.game_loop = None
        self.final_score = 0
        
        # Variable to track if pause button is pressed
        self.pause_requested = False
        
    def run(self):
        """Run the main system loop"""
        try:
            while True:
                # Check for pause input (this would be replaced with actual input detection)
                self._check_pause_input()
                
                if self.pause_requested and self.state != SystemState.PAUSED:
                    # Store current state before pausing
                    self.previous_state = self.state
                    self.state = SystemState.PAUSED
                    self.pause_reason = PauseReason.USER_PAUSED
                    self.pause_requested = False
                    
                if self.state == SystemState.IDLE:
                    self._handle_idle()
                elif self.state == SystemState.GAME_LOOP:
                    self._handle_game_loop()
                elif self.state == SystemState.GAME_OVER:
                    self._handle_game_over()
                elif self.state == SystemState.PAUSED:
                    self._handle_paused()
                    
        except KeyboardInterrupt:
            print("Program interrupted by user")
        finally:
            self._cleanup()
            
    def _check_pause_input(self):
        """Check if pause button is pressed. This is a placeholder."""
        # In a real implementation, this would check GPIO pins, keyboard input, etc.
        # For now, we just set it to False
        self.pause_requested = False
        
    def _handle_idle(self):
        """Display idle screen and wait for start input"""
        outframe = self.hdmi_out.newframe()
        np_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        cv2.putText(
            img=np_frame,
            text="Face Frenzy",
            org=(200, 200),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.5,
            color=(255, 255, 255),
            thickness=2,
            lineType=cv2.LINE_AA
        )
        
        cv2.putText(
            img=np_frame,
            text="Press any key to start",
            org=(180, 250),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=2,
            lineType=cv2.LINE_AA
        )
        
        outframe[0:480, 0:640, :] = np_frame
        self.hdmi_out.writeframe(outframe)
        
        # Wait for a key press (could be replaced with GPIO button press)
        key = cv2.waitKey(1) & 0xFF
        if key != 255:
            # Any key pressed, start the game
            self.game_loop = GameLoop(self.hdmi_out, self.video_in)
            self.state = SystemState.GAME_LOOP
            
    def _handle_game_loop(self):
        """Handle the game loop state"""
        # Run one iteration of the game loop
        game_over = self.game_loop.run()
        
        if game_over:
            self.final_score = self.game_loop.get_score()
            self.state = SystemState.GAME_OVER
            
    def _handle_game_over(self):
        """Display game over screen and wait for restart input"""
        outframe = self.hdmi_out.newframe()
        np_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        cv2.putText(
            img=np_frame,
            text="Game Over",
            org=(220, 180),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.5,
            color=(0, 0, 255),
            thickness=2,
            lineType=cv2.LINE_AA
        )
        
        cv2.putText(
            img=np_frame,
            text=f"Final Score: {self.final_score}",
            org=(220, 230),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=2,
            lineType=cv2.LINE_AA
        )
        
        cv2.putText(
            img=np_frame,
            text="Press any key to play again",
            org=(170, 280),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=2,
            lineType=cv2.LINE_AA
        )
        
        outframe[0:480, 0:640, :] = np_frame
        self.hdmi_out.writeframe(outframe)
        
        # Wait for a key press
        key = cv2.waitKey(1) & 0xFF
        if key != 255:
            # Any key pressed, return to idle state
            self.state = SystemState.IDLE
            
    def _handle_paused(self):
        """Handle the paused state"""
        outframe = self.hdmi_out.newframe()
        np_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Display different messages based on pause reason
        if self.pause_reason == PauseReason.USER_PAUSED:
            pause_text = "Game Paused by User"
        elif self.pause_reason == PauseReason.SYSTEM_PAUSED:
            pause_text = "Game Paused by System"
        elif self.pause_reason == PauseReason.FOCUS_LOST:
            pause_text = "Game Paused - Focus Lost"
        else:
            pause_text = "Game Paused"
            
        cv2.putText(
            img=np_frame,
            text=pause_text,
            org=(180, 200),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255, 255, 0),
            thickness=2,
            lineType=cv2.LINE_AA
        )
        
        cv2.putText(
            img=np_frame,
            text="Press any key to resume",
            org=(180, 250),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=2,
            lineType=cv2.LINE_AA
        )
        
        outframe[0:480, 0:640, :] = np_frame
        self.hdmi_out.writeframe(outframe)
        
        # Wait for a key press to resume
        key = cv2.waitKey(1) & 0xFF
        if key != 255:
            # Any key pressed, resume the game
            self.state = self.previous_state
            
    def _cleanup(self):
        """Clean up resources"""
        print("Cleaning up resources...")
        if self.video_in is not None:
            self.video_in.release()
            
        if self.hdmi_out is not None:
            self.hdmi_out.stop()
            del self.hdmi_out
            
        print("Resources cleaned up. Exiting.")

if __name__ == "__main__":
    system = FaceFrenzySystem()
    system.run()