import RPi.GPIO as GPIO
import time
import os
import glob
import random
import sys

# Settings 
PERCENTAGE_PLAY_SOUND = 1
# PERCANTAGE_PLAY_SOUND = .5

SOUND_FOLDER = 'bells'
# SOUND_FOLDER = 'scary'
# SOUND_FOLDER = 'ringtones'
# SOUND_FOLDER = 'funny'

SCAN_DELAY = .1
SAMPLE_SIZE = 10
SCAN_DISCARD = 1

# GPIO Setup
GPIO_TRIGGER = 23
GPIO_ECHO = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# States
STATE_BEGIN = "begin"
STATE_ARMED = "armed"
STATE_TRIGGERED = "triggered"

def get_multi_distance():
    distances = []
    for x in range(0, SAMPLE_SIZE):
        distance = get_distance()
        distances.append(distance)
        distances.sort()
    total_sum = 0
    for y in range(SCAN_DISCARD, (SAMPLE_SIZE - SCAN_DISCARD)):
        total_sum += distances[y]
    average_distance = total_sum / SAMPLE_SIZE - SCAN_DISCARD*2
    return average_distance

def get_distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
def percentage_change(x, y):
     diff = (abs(x - y) / y) * 100
     return diff

def play_sound():
    try:
        sounds = glob.glob("sounds/" + SOUND_FOLDER + "/*.mp3")
        if (len(sounds) == 0):
            print("No sounds!")
        else:
            sound = random.choice(sounds)
            command = 'mpg123 -q ' + os.path.dirname(os.path.realpath(__file__)) + '/' + sound + ' '
            print(sound)
            os.system(command)
    except Exception:
        return

def print_state(state):
    print("State: " + state + " " + time.strftime('%m/%d/%Y %H:%M:%S'))

def list_files():
    files = glob.glob("sounds/" + SOUND_FOLDER + "/*.mp3")
    if (len(files) == 0):
        print("No MP3 files in folder sounds/" + SOUND_FOLDER)
        exit(1)

if len(sys.argv) > 1 and sys.argv[1]:
	SOUND_FOLDER = sys.argv[1]

list_files()

if __name__ == '__main__':
    try:
        state = STATE_BEGIN
        print_state(state)
        count = 0
        last_distance = 0
        while True:
            dist = get_multi_distance()
            if (state == STATE_BEGIN):
                if (percentage_change(last_distance, dist) < 5) :
                    count += 1
                    if (count > 50):
                        state = STATE_ARMED
                        print_state(state)
                else:
                    count = 0
            if (state == STATE_ARMED):
                if (percentage_change(last_distance, dist) > 10) :
                    state = STATE_TRIGGERED
                    print_state(state)
                    if (random.random() < PERCENTAGE_PLAY_SOUND):
                        play_sound()
                    else:
                        print("No sound")
                    count = 0
            if (state == STATE_TRIGGERED):
                count += 1
                if (count > 50):
                    state = STATE_BEGIN
                    print_state(state)
            last_distance = dist

            time.sleep(SCAN_DELAY)
 
    except KeyboardInterrupt:
        GPIO.cleanup()
