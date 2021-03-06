import os
import sys
import time
import subprocess
from gpiozero import LED, Button
from threading import Thread
from signal import pause

""" Code partially adapted from the audacity scripting repo """

""" Initialize LEDs and Buttons """
LEDS = [ LED(4), LED(17), LED(27) ] # RED, YELLOW, GREEN
record_button = Button(23)
pause_button = Button(24)
stop_button = Button(25)

# Path to files that sends/receives commands/values to/from audacity
TONAME = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
FROMNAME = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
""" Run audacity and wait 10 seconds for it to start """
#subprocess.Popen(sys.argv[1] + '/audacity')
#wait_thread = Thread(target=time.sleep(90))
#thread.start()
#loading_animation(wait_thread)
#wait_thread.join()
""" Check for the script-pipes and open them """
if not (os.path.exists(TONAME) and os.path.exists(FROMNAME)):
    print("mod-script-pipe not found...")
    sys.exit(0)
print(" -- Pipes found!")
TOFILE = open(TONAME, 'w')
print(" -- To Pipe opened")
FROMFILE = open(FROMNAME, 'rt')
print(" -- From Pipe opened")

def send_command(command):
    """ Send a command """
    print("Send: >>> \n" + command)
    TOFILE.write(command + '\n')
    TOFILE.flush()

def get_response():
    """ Return a command response """
    result = ''
    line = ''
    while line != '\n':
    	result += line
	line = FROMFILE.readline()
    return result

def do_command(command):
    """ Send a command and receive a response """
    send_command(command)
    response = get_response()
    print("Received: <<< \n" + response)
    return response

def leds_off():
    """ Turn all LEDs off """
    for led in LEDS:
	led.off()

def loading_anim(thread, sleeptime=0.25):
    """ Run through LED animation while the thread is active """
    leds_off()
    while thread.is_alive():
    	for led in LEDS:
        	led.on()
		time.sleep(sleeptime)
	for led in LEDS:
		led.off()
		time.sleep(sleeptime)
	for led in reversed(LEDS):
		led.on()
		time.sleep(sleeptime)
	for led in reversed(LEDS):
		led.off()
		time.sleep(sleeptime)
		
def save():
    """ Saves the current project with filename of its timestamp """
    do_command('SaveProject2: Filename=' + time.asctime(time.localtime(time.time())))
    # TODO
    # connect to server
    # save file on server

def reset():
    """ Stop recording, save and close the project then open a new one """
    do_command('PlayStop')
    save()

def stop():
    """ Stop recording and save the project """
    """   While saving play LED animation   """
    """  When finished, turn on green LED   """
    leds_off()
    save_thread = Thread(target=reset)
    save_thread.start()
    loading_anim(save_thread)
    save_thread.join()
    LEDS[0].on()

def record():
    """ Start recording and turn on the Red LED """
    leds_off()
    do_command('Record1stChoice:')
    LEDS[2].on()

def pause_rec():
    """ Pause recording and turn on the Yellow LED """
    leds_off()
    do_command('Pause:')
    LEDS[1].on()

""" Set event listener methods for button presses """
record_button.when_pressed = record
pause_button.when_pressed = pause_rec
stop_button.when_pressed = stop
LEDS[0].on()
pause()
