#!/usr/bin/env python3
# Main entry point for the Face Frenzy game

from system import FaceFrenzySystem
from bottle import route, run
import threading

system = FaceFrenzySystem()

def run_webserver():
    run(host="0.0.0.0", port=8080)

@route("/")
def info():
    information = f"""
    Score: {system.final_score}<br>
    Round:\n<br>
    Strikes: {system.game_loop.strikes}\n<br>
    Face count: {len(system.game_loop.detected_faces)} \n<br>
    Game state: {system.state}\n<br>
    """

    return information



if __name__ == "__main__":
    print("Starting Face Frenzy game...")
    t = threading.Thread(target=run_webserver)
    t.start()
    system.run()


