#! /usr/bin/python
#  Change the above line to match the appropriate OS



"""  Servo Recorder Interface Example

Modify and distribute freely

This is an example program to control a modified servo with feedback.  It is meant to be run with the "ServoFeedback" example firmware for the arduino microcontroller.  It generates a 4 button interface that will record a servo position to be played back later.  

The buttons have the following functions:

Record:  Tells the arduino to save the current position of the servo.
Play: Plays the recorded servo position
Stop: Stops playback.  The servo can be repositioned to another position.

Usage
1. Move the servo arm to the required position
2. Press the record button.  The servo arm can still be moved freely.
3. Press the play button to move the arm to the recorded position.
4. Press the stop button to allow the arm to be moved to another position.  Pressing play again at any time will return the arm to the last recorded position.

This software requires the pySerial library.  It can be downloaded here:
http://pyserial.wiki.sourceforge.net/pySerial
"""

from Tkinter import *
import time
import serial

master = Tk()                    #  Create a TK instance
master.title("Servo Recorder")   #  Title


"""Connect to the Serial Port.  This line should be changed for a different port.  Under windows the com number can be used.  The com port in windows will be one less than the one reported by the Device Manager since pySerial enumerates it's ports starting at 0.

For example, to connect to com 8 use this:
 ser = serial.Serial("7", 9600)  
 """

ser = serial.Serial("/dev/ttyUSB0", 9600)   

def record():           #  Send "a" out the serial port when record is pressed
   ser.write("a")

def stop():          #  Send "b" out the serial port when the stop button is pressed
    ser.write("b")

def play():          #  Send "c" out the serial port when the play button is pressed
    ser.write("c")
    
def calibrate():        #  Send "d" out the serial port when the play button is pressed
    ser.write("d")
    
def quit():        #  Send "d" out the serial port when the play button is pressed
    ser.close()
    master.destroy()
    
    
recordButton = Button(master, text="Record", command=record)   # Create the record button on the grid and hook it to the record function
recordButton.grid(row=1, column=1)

stopButton = Button(master, text="Stop", command=stop)         #  Create the stop button on the grid and hook it to the stop function
stopButton.grid(row=1, column=2)

playButton = Button(master, text="Play", command=play)         #  Create the play button on the grid and hook it to the play function
playButton.grid(row=1, column=4)

calButton = Button(master, text="Calibrate", command=calibrate)         #  Create the calibrate button on the grid and hook it to the play function
calButton.grid(row=1, column=5)

quitButton = Button(master, text="Quit", command=quit)         #  Create the calibrate button on the grid and hook it to the play function
quitButton.grid(row=2, column=3)

mainloop()
