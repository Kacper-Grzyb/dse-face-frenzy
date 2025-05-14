#!/usr/bin/env python3
# Main entry point for the Face Frenzy game

from system import FaceFrenzySystem
from bottle import route, run

if __name__ == "__main__":
    print("Starting Face Frenzy game...")
    system = FaceFrenzySystem()
    system.run()


@route("/")
def info():
    information = f"""
    Score: {system.final_score}
    Round:
    Strikes: {system.game_loop.strikes}
    Face count: {str(system.game_loop.detected_faces)} 
    Game state: {system.state}
    """

    return information
