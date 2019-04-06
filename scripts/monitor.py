#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import time

import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI
import psutil
import math
import requests
import json
import time


from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from subprocess import check_output
from gpiozero import CPUTemperature
from wireless import Wireless

wireless = Wireless()


# Raspberry Pi software SPI config:
SCLK = 17
DIN = 18
DC = 27
RST = 23
CS = 8

# Software SPI usage (defaults to bit-bang SPI interface):
disp = LCD.PCD8544(DC, RST, SCLK, DIN, CS)

# Initialize library.
disp.begin(contrast=100)

# Clear display.
disp.clear()
disp.display()

image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))
draw = ImageDraw.Draw(image)

#font = ImageFont.truetype('res/fonts/silkscreen.ttf', 8)
#font = ImageFont.truetype('res/fonts/retro_c.ttf', 7)
#font = ImageFont.truetype('res/fonts/minecraftia.ttf', 8)
#font = ImageFont.truetype('res/fonts/type_writer.ttf', 8)
#font = ImageFont.truetype('res/fonts/pixelade.ttf', 14)
font = ImageFont.truetype('res/fonts/digitalix.ttf', 5)
#font = ImageFont.load_default()

# data
currentTime = 0

cpu = CPUTemperature()
initDate = time.time()

ipAddressUpdateInterval = 15 * 60
ramUsageUpdateInterval = 10
cpuUsageUpdateInterval = 5
cpuTempUpdateInterval = 5
currentWlanDataUpdateInterval = 15 * 60
weatherUpdateInterval = 2 * 60 * 60
workingTimeUpdateInterval = 1

ipAddressValue = ""
ramUsageValue = ""
cpuUsageValue = ""
cpuTempValue = ""
currentWlanDataValue = ""
weatherValue = ""
workingTime = ""

def updateWeather():
	global weatherValue 
	global weatherUpdateInterval
	
	data = {
		'id': '100703448'
	}
	
	try:
		r = requests.post("https://www.foreca.com/lv", data=data)

		data = r.json()["lv"][0]

		city = data[1]
		country = data[2]
		temp = data[3]

		weatherValue = country + ":" + city + " " + temp + " C`"
		weatherUpdateInterval = 2 * 60 * 60
	except:
		print("Unable to request weather")
		weatherUpdateInterval = 15
		
	
	

def updateMonitoringData(force):
	global ipAddressValue
	global ramUsageValue
	global cpuUsageValue
	global cpuTempValue
	global currentWlanDataValue	
	global weatherValue
	global workingTime
	
	if (force or currentTime < 15 or currentTime % ipAddressUpdateInterval == 0):
		ipAddressValue = "ip: " + check_output(['hostname', '-I'])
	if (force or currentTime % ramUsageUpdateInterval == 0):
		ramUsageValue  = "ram: " + str(psutil.virtual_memory().used / 1024 / 1024 ) + "/" + str(psutil.virtual_memory().total / 1024 / 1024 ) + " MB"
	if (force or currentTime % cpuUsageUpdateInterval == 0):	
		cpuUsageValue  = "cpu: " + str(psutil.cpu_percent()) + " %"
	if (force or currentTime % cpuTempUpdateInterval == 0):
		cpuTempValue = "TEMP: " + str(math.floor(cpu.temperature)) + " C`"
	if (force or currentTime % currentWlanDataUpdateInterval == 0):
		currentWlanDataValue = wireless.current()
	if (force or currentTime % weatherUpdateInterval == 0):
		updateWeather()
	if (force or currentTime % workingTimeUpdateInterval == 0):
		now = time.time()
		delta = now - initDate
		workingTime = formatDate(delta)

def formatDate(seconds):
	result = ""	
	
	if ( seconds < 24 * 60 * 60 ):
		s = str(int(seconds % 60))
		result = s + "s"
	
	if ( seconds > 60 and (seconds < 365 * 24 * 60 * 60) ):	
		m = str(int((seconds / 60) % 60))
		result = m + "m " + result 
	
	if ( seconds > 60 * 60 ):
		h = str(int((seconds / (60 * 60)) % 24))
		result = h + "h " + result 
		
	if ( seconds > 24 * 60 * 60 ):
		d = str(int((seconds / (24 * 60 * 60)) % 365 ))
		result = d + "d " + result 
		
	if ( seconds > 365 * 24 * 60 * 60 ):
		y = str(int((seconds / (365 * 24 * 60 * 60))))
		result = y + "y " + result 
	
	return "WT: " + result





def redraw():
	draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)
	
	renderData()
	
	disp.image(image)
	disp.display()
	

def renderTextLine(line, text, drawLine):
	lineHeight = 7
	lineOffset = 7
	offset = 0
	
	draw.text((0,( line * lineHeight + offset )), text, font=font, fill=0)
	
	if ( drawLine ):
		draw.line((4,( line * lineHeight ) + lineOffset,LCD.LCDWIDTH - 8,( line * lineHeight ) + lineOffset), fill=0)
	

def renderData():
	updateMonitoringData(False)
	
	renderTextLine( 0, currentWlanDataValue, False )
	
	renderTextLine( 1, ipAddressValue, False )
	renderTextLine( 2, cpuUsageValue, False )
	renderTextLine( 3, ramUsageValue, False )
	renderTextLine( 4, cpuTempValue, False )
	renderTextLine( 5, weatherValue, False )
	renderTextLine( 6, workingTime, False )



updateWeather()
updateMonitoringData(True)


print('Press Ctrl-C to quit.')
while True:
	currentTime+=1
	redraw()
	time.sleep(1.0)
