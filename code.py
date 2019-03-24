import time
import board
from adafruit_pyportal import PyPortal
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label

import adafruit_touchscreen

from secrets import secrets

device_dict = {
    "z": {
        "58:b1:0f:cf:77:a2": {
            "name": "Galaxy", 
            "status": "unknown"
            }, 
        "e4:42:a6:16:c2:27": {
            "name": "Desktop", 
            "status": "unknown"
            }
        },
    "a": {
        "f8:62:14:a7:02:32": {
            "name": "iPod", 
            "status": "unknown"
            }, 
        "28:c2:dd:a2:5a:d1": {
            "name": "Chromebook", 
            "status": "unknown"
            }, 
        "44:65:0d:b8:8f:95": {
            "name": "Kindle", 
            "status": "unknown"
            }
    },
}

ts = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                      board.TOUCH_YD, board.TOUCH_YU)

pyportal = PyPortal(default_bg="./kids.bmp")
pyportal.set_backlight(.5)

zOn = (44, 212)
zOff = (34, 212)
aOn = (190, 212)
aOff = (180, 212)

onColor = 0x5ff442
offColor = 0xd60000

big_font = bitmap_font.load_font("./fonts/Helvetica-Bold-36.bdf")

refresh_time = None

text_areas = []

def setupText(position, text_color):
    textarea = Label(big_font, text='   ')
    textarea.x = position[0]
    textarea.y = position[1]
    textarea.color = text_color
    pyportal.splash.append(textarea)
    text_areas.append(textarea)

def getStats(kid):
    headers = {"X-Cisco-Meraki-API-Key": secrets['meraki_key'], "Content-Type": "application/json"}
    for device in device_dict[kid]:
        get_status_url = "https://n151.meraki.com/api/v0/networks/N_647955396387945637/clients/{}/policy?timespan=2592000".format(device)
        try:
            response = pyportal.mfetch(get_status_url, headers=headers)
            device_dict[kid][device]['status'] = response['type']
        except (ValueError, RuntimeError) as e:
            print("Failed to get data\n", e)

def setStats(kid, status):
    headers = {"X-Cisco-Meraki-API-Key": secrets['meraki_key'], "Content-Type": "application/json"}
    for device in device_dict[kid]:
        set_status_url = "https://n151.meraki.com/api/v0/networks/N_647955396387945637/clients/{}/policy?timespan=2592000&devicePolicy={}".format(device, status)
        try:
            response = pyportal.mput(set_status_url, headers=headers)
        except (ValueError, RuntimeError) as e:
            print("Failed to reset data\n", e)

def isOnOrOff(kid):
    for dev in device_dict[kid]:
        if device_dict[kid][dev]['status'] == "Blocked":
            return False
    return True

print("Status for Zachary's devices: ")
getStats("z")
zStatus = isOnOrOff("z")

if zStatus == False:
    setupText(zOff, offColor)
    text_areas[0].text = "OFF"
else:
    setupText(zOn, onColor)
    text_areas[0].text = "ON"

print("Status for Amanda's devices: ")
getStats("a")
aStatus = isOnOrOff("a")

if aStatus == False:
    setupText(aOff, offColor)
    text_areas[1].text = "OFF"
else:
    setupText(aOn, onColor)
    text_areas[1].text = "ON"

while True:
    p = ts.touch_point
    if p:
        if (p[0] > 16000 and p[0] < 25000) and p[1] > 46000:
            zStatus = not zStatus
            print("Z: {}".format(zStatus))
            if zStatus == False:
                text_areas[0].text = ""
                text_areas[0].x = zOff[0]
                text_areas[0].y = zOff[1]
                text_areas[0].color = offColor
                text_areas[0].text = "OFF"
                setStats('z', "Blocked")
            else:
                text_areas[0].text = ""
                text_areas[0].x = zOn[0]
                text_areas[0].y = zOn[1]
                text_areas[0].color = onColor
                text_areas[0].text = "ON"
                setStats('z', "Normal")
            time.sleep(1.5)

        if (p[0] > 35000 and p[0] < 46000) and p[1] > 46000:
            aStatus = not aStatus
            print("A: {}".format(aStatus))
            if aStatus == False:
                text_areas[1].text = ""
                text_areas[1].x = aOff[0]
                text_areas[1].y = aOff[1]
                text_areas[1].color = offColor
                text_areas[1].text = "OFF"
                setStats('a', "Blocked")
            else:
                text_areas[1].text = ""
                text_areas[1].x = aOn[0]
                text_areas[1].y = aOn[1]
                text_areas[1].color = onColor
                text_areas[1].text = "ON"
                setStats('a', "Normal")
            time.sleep(1.5)
