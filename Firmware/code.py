"""
Firmware for the HexRiver project.

@author: Spencer Shaffer
- All rights reserved
"""

import time
import tile as t
from adafruit_servokit import ServoKit
import board
from digitalio import DigitalInOut, Direction, Pull
import neopixel


# Controls whether the servo controller boards are active or not
servo_enable = DigitalInOut(board.D5)
# Controls the NO relay from the power supply to the servos
pwr_relay = DigitalInOut(board.D2)
# Motion sensor input pin for controlling a sleep mode to be implemented in the future
pir_sensor = DigitalInOut(board.D7)

# Side panel buttons to be implemented in the future
top_button = DigitalInOut(board.A1)
middle_button = DigitalInOut(board.A0)


servo_enable.direction = Direction.OUTPUT
pwr_relay.direction = Direction.OUTPUT

pir_sensor.direction = Direction.INPUT
top_button.direction = Direction.INPUT
middle_button.direction = Direction.INPUT

# Adafruit Metro's on board LED for status indication
led = neopixel.NeoPixel(board.NEOPIXEL, 1)

led.brightness = 0.3

# List containing the grouping of the servos for the wave effect
wave_values = []


def manual():
    """
    A general purpose debug manual mode for controlling many of the functions of the project
    """

    count = 0
    manual_mode = True
    new_angle = 0
    changed_neutral = False

    while manual_mode:
        print(f"\nCurrently on tile #{tiles[count].get_id()}")
        print(
            "Type 'n' to continue, any number to set the angle, 'q' to quit, 'b' to go back, 'c' to set current angle as neutral, 'go=[num]' to go to the specified tile id, '+/-[angle]' to go the specified offset from neutral, 'p' to enter function running mode")

        inpt = input("Enter command > ")
        print("")

        if inpt == "n":
            if count == 106:
                manual_mode = False
            else:
                count += 1

        elif inpt == "b" and count > 0:
            count -= 1

        elif inpt == "q":
            manual_mode = False

        elif inpt == "p":
            print("---------------------")
            print("Function Mode Entered")
            print("    1.) resetAll")
            print("    2.) sweep")
            print("    3.) wave")
            choice = input(" > ")
            if choice == "1":
                resetAll()
            elif choice == "2":
                print("Enter the following parameters '+/-[num],[delay],[range - ie. 1-25 (max 1-107)]'")
                params = input("> ").split(",")
                degree = params[0]
                delay = params[1]
                rangeInpt = params[2]
                sweep(degree, delay, rangeInpt)
            elif choice == "3":
                wave()

        elif inpt == "c":
            tiles[count].set_neutral(new_angle)
            print(f"Set tile #{tiles[count].get_id()}'s neutral position to {new_angle}")
            changed_neutral = True
            count += 1

        elif "go" in inpt:
            try:
                goto = int(inpt.split("=")[1])
                if goto <= 107 and goto > 0:
                    count = goto - 1
            except:
                print("Error: Unknown Command")

        elif "+" in inpt:
            try:
                angle = int(inpt[1:])
                new_angle = tiles[count].get_neutral() + angle
                tiles[count].move(new_angle)
                print(f"Moved tile {tiles[count].get_id()} to {new_angle} degrees\n")
            except:
                print("Error: Unknown Command")

        elif "-" in inpt:
            try:
                angle = int(inpt[1:])
                new_angle = tiles[count].get_neutral() - angle
                tiles[count].move(new_angle)
                print(f"Moved tile {tiles[count].get_id()} to {new_angle} degrees\n")
            except:
                print("Error: Unknown Command")

        else:
            try:
                tiles[count].move(int(inpt))
                new_angle = int(inpt)
                print(f"Moved tile to {inpt} degrees\n")
            except:
                print("Unrecognized input\n")

    if changed_neutral:
        for tile in tiles:
            print(f"Tile #{tile.get_id()} Neutral:{tile.get_neutral()}")


def sweep(degree, delayInpt, rangeInpt):
    """
    A sequential 'sweep' of all of the tiles at a set interval and a set angle

    :param degree: The degree to move each servo tile from neutral in format of +/-[angle] i.e. "+10" 
            would result in a movement of 10 degrees from the tile's neutral position
    :param delayInpt: The delay in seconds between each tile being moved
    :param rangeInpt: The range of tiles to be moved lowerBound(inclusive)-upperBound(exclusive) i.e. "1-108" for all of the tiles
    """
    print("Starting Sweep")

    if "+" in degree:
        angle = ["+", int(degree[1:])]
    elif "-" in degree:
        angle = ["-", int(degree[1:])]
    else:
        angle = 0

    try:
        delay = float(delayInpt)
        if delay <= 0:
            print("Delay must be a positive, non-zero number; Defaulting to .25 seconds")
            delay = 0.25
    except:
        print("Error: Delay defaulting to .25 seconds")
        delay = 0.25

    temp_range = rangeInpt.split("-")
    tile_range = [int(temp_range[0]), int(temp_range[1])]

    for i in range(tile_range[0], tile_range[1]):
        tile = tiles[i-1]

        try:
            if angle[0] == "-":
                new_angle = tile.get_neutral() - angle[1]
            else:
                new_angle = tile.get_neutral() + angle[1]

            tile.move(new_angle)
            print(f"Moved tile {tile.get_id()} to {new_angle} degrees.\n")
            time.sleep(delay)
        except:
            print(f"Error moving Tile #{tile.get_id()}")
            time.sleep(delay)


def resetAll():
    """
    Reset all of the tiles to their neutral position
    """
    print("Resetting tiles.")
    for tile in tiles:
        try:
            tile.neutral()
            print(f"    - Moved tile {tile.get_id()} to neutral.\n")
            time.sleep(0.05)
        except:
            print(f"    - Error moving Tile #{tile.get_id()}")
            time.sleep(0.05)
    print("Tile Resetting Completed.")


def wave():
    """
    A wave motion, moving the tiles row by row at a 10 deg deflection from neutral with a 0.1 second delay between rows
    - Futher testing is needed to determine the upper bound of deflection permitted before reaching servo power constraints
    """
    for i in range(len(wave_values)+2):
        if i > 1 and i < len(wave_values)+2:
            for servo in wave_values[i-2]:
                tiles[int(servo)-1].move(tiles[int(servo)-1].get_neutral()+0)
                time.sleep(0.005)
        if i < len(wave_values):
            for servo in wave_values[i]:
                if (int(servo) >= 57 and int(servo) <= 70) or (int(servo) >= 82):
                    tiles[int(servo)-1].move(tiles[int(servo)-1].get_neutral()-10)
                else:
                    tiles[int(servo)-1].move(tiles[int(servo)-1].get_neutral()+10)
                time.sleep(0.005)
        time.sleep(0.1)


def boot():
    """
    Main boot sequence for the device, controls proper power sequencing to the servo drivers

    :return: List containing all of the Tile objects
    """
    print("\nInitalizing")

    values = []

    # Disable the servo driver boards
    print("Disabling servo drivers")
    servo_enable.value = True
    time.sleep(0.25)

    # Process and create all of the tile objects
    print("Creating Tile objects")
    # File formatted as: register_address,servo_id,servo_board_pin,neutral_position
    file = open("connections_final.txt", "r")
    for line in file:
        data = line.split(",")
        values.append([data[0], data[1], data[2], data[3].replace("\n", "")])

    file.close()

    boards = [ServoKit(channels=16, address=0x40), ServoKit(channels=16, address=0x41), ServoKit(channels=16, address=0x42), ServoKit(
        channels=16, address=0x43), ServoKit(channels=16, address=0x44), ServoKit(channels=16, address=0x45), ServoKit(channels=16, address=0x46)]

    tiles = []

    for servo in values:
        servo_board = int(servo[0][-1:])
        tiles.append(t.Tile(boards[servo_board], int(servo[2]), int(servo[1]), int(servo[3])))

    file = open("wave.txt", "r")
    for line in file:
        data = line.split(",")
        data[-1] = data[-1].replace("\n", "")
        wave_values.append(data)

    # Enable power to the servos and re-enable the servo driver boards
    # Time values are arbitrary
    led[0] = (0, 0, 255)
    time.sleep(2)
    print("Turning on servo power")
    pwr_relay.value = True
    time.sleep(3)
    print("Enabling servo drivers")
    servo_enable.value = False
    time.sleep(1)

    print("Boot sequence completed")
    led[0] = (0, 255, 0)
    time.sleep(1)
    led[0] = (0, 0, 0)

    return tiles


# Initiate the tile objects and enable the power supply
tiles = boot()
time.sleep(1)

# Decide on which to run
manual()
# displayMode() - to be implemented in the future
