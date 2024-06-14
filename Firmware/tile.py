"""
Tile class for the HexRiver project.

@author: Spencer Shaffer
- All rights reserved
"""

import time
from adafruit_servokit import ServoKit


class Tile:

    def __init__(self, servo_board, pin, id, neutral=90):
        """
        Create a new Tile object

        :param servo_board (ServoKit): The ServoKit board on which this Tile is located
        :param pin (int): 0-15, the pin on the servo_board that the Tile is on
        """
        self.__board = servo_board
        self.__pin = pin
        self.__neutral = neutral
        self.__tile_id = id

        # Unused variable for possible future implementation
        self.__pos = neutral

    def move(self, angle):
        """
        Move the servo to a certain angle

        "param angle (int): The angle to set the servo's position to
        """
        if angle >= 45 and angle <= 150:
            self.__board.servo[self.__pin].angle = angle
            self.__pos = angle

    def neutral(self):
        """
        Moves the servo to it's designated neutral position
        """

        self.move(self.__neutral)
        self.__pos = self.__neutral

    def set_neutral(self, neutral):
        """
        Override the default neutral position

        :param neutral (int): the angle at which the servo is considered neutral
        """

        self.__neutral = neutral

    def get_neutral(self):
        """
        Returns the neutral position of the Tile object

        :returns (int): The tile's neutral position
        """
        return self.__neutral

    def get_id(self):
        """
        Returns the Tile's ID number, corrisponding to the labels on each servo wire

        :returns (int): The tile's ID number
        """
        return self.__tile_id
