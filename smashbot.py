#!/usr/bin/python3
import argparse
import os
import signal
import sys

import melee

from esagent import ESAgent


def check_port(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 4:
        raise argparse.ArgumentTypeError("%s is an invalid controller port. \
        Must be 1, 2, 3, or 4." % value)
    return ivalue


def is_dir(dirname):
    """Checks if a path is an actual directory"""
    if not os.path.isdir(dirname):
        msg = "{0} is not a directory".format(dirname)
        raise argparse.ArgumentTypeError(msg)
    else:
        return dirname


parser = argparse.ArgumentParser(description='Example of libmelee in action')
parser.add_argument('--port', '-p', type=check_port,
                    help='The controller port your AI will play on',
                    default=2)
parser.add_argument('--opponent', '-o', type=check_port,
                    help='The controller port the opponent will play on',
                    default=1)
parser.add_argument('--debug', '-d', action='store_true',
                    help='Debug mode. Creates a CSV of all game state')
parser.add_argument('--difficulty', '-i', type=int, default=-1,
                    help='Manually specify difficulty level of SmashBot')
parser.add_argument('--dolphinexecutable', '-e', type=is_dir,
                    help='Manually specify Dolphin executable')
parser.add_argument('--stage', '-s', default="FD",
                    help='Specify which stage to select')

stagedict = {
    "FD": melee.Stage.FINAL_DESTINATION,
    "BF": melee.Stage.BATTLEFIELD,
    "YS": melee.Stage.YOSHIS_STORY,
    "FOD": melee.Stage.FOUNTAIN_OF_DREAMS,
    "DL": melee.Stage.DREAMLAND,
    "PS": melee.Stage.POKEMON_STADIUM
}

args = parser.parse_args()

log = None
if args.debug:
    log = melee.logger.Logger()

# Create our console object. This will be the primary object that we will interface with
console = melee.console.Console(path=args.dolphinexecutable,
                                tmp_home_directory=False,
                                copy_home_directory=False,
                                logger=log,
                                system='dolphin',
                                fullscreen=False)

controller_one = melee.controller.Controller(console=console, port=args.port)

# initialize our agent
agent1 = ESAgent(console, args.port, args.opponent, controller_one, args.difficulty)


def signal_handler(signal, frame):
    console.stop()
    if args.debug:
        log.writelog()
        print("") # because the ^C will be on the terminal
        print("Log file created: " + log.filename)
    print("Shutting down cleanly...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# If Dolphin is already running try to connect. If it is not, we need to instantiate the client again, as it cannot
# try to connect twice for the same object.
if not console.connect():
    console = melee.console.Console(path=args.dolphinexecutable,
                                    tmp_home_directory=False,
                                    copy_home_directory=False,
                                    logger=log,
                                    system='dolphin',
                                    fullscreen=False)

    # Run dolphin
    console.run()

    if not console.connect():
        print("Connecting to console...")
        if not console.connect():
            print("ERROR: Failed to connect to the console.")
            print("\tIf you're trying to autodiscover, local firewall settings can " +
                  "get in the way. Try specifying the address manually.")
            sys.exit(-1)

print("Connected")

# Plug our controller in
controller_one.connect()

# Main loop
while True:
    # "step" to the next frame
    gamestate = console.step()

    # What menu are we in?
    if gamestate.menu_state == melee.Menu.IN_GAME:
        agent1.act(gamestate)
    else:
        melee.menuhelper.MenuHelper.menu_helper_simple(gamestate,
                                                       controller_one,
                                                       melee.Character.JIGGLYPUFF,
                                                       stagedict.get(args.stage, melee.Stage.FINAL_DESTINATION),
                                                       autostart=False,
                                                       swag=True)
        if log:
            log.skipframe()
