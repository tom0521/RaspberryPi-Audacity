import os
import sys
import time
from gpiozero import LED, Button
from threading import Thread

# Initialize LEDs and Buttons
LEDS = [ LED(0), LED(1), LED(2) ]
record_button = Button(3)
pause_button = Button(4)
stop_button = Button(5)

# Path to files that sends/receives commands/values to/from audacity
TONAME = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
FROMNAME = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
TOFILE = None
FROMFILE = None

def setup:
	record_button.when_pressed = record
	pause_button.when_pressed = pause
	stop_button.when_pressed = stop
	if not (os.path.exists(TONAME) and os.path.exists(FROMNAME)):
		print("mod-script-pipe not found...")
		sys.exit()

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

def loading_anim(thread):
	while thread.is_active():
		for i in range(3):
			LEDS[i].on()
		for i in range(3):
			LEDS[i].off()
		for i in range(2,-1,-1):
			LEDS[i].on()
		for i in range(2,-1,-1):
			LEDS[i].off()
		
# load the audacity script-pipe

def save():
	do_command('SaveProject2: Filename=' + time.asctime(time.localtime(time.time())))
	# TODO
	# connect to server
	# save file on server

def reset():
	do_command('PlayStop:')
	save()
	do_command('Close:')
	do_command('New:')

def stop():
	""" Stop recording and save the project """
	save_thread = Thread(target=reset)
	save_thread.start()
	loading_anim(save_thread)
	save_thread.join()
	LEDS[2].on()

def record():
	do_command('Record1stChoice:')
	LEDS[0].on()

def pause():
	do_command('Pause:')
	LEDS[1].on()

setup_thread = Thread(target=setup)
setup_thread.start()
loading_anim(setup_thread)
setup_thread.join()
