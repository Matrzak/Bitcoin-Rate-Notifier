import RPi.GPIO as GPIO
import requests
import time
import pygame
import bluetooth
import matplotlib.pyplot as plt
from RPLCD import CharLCD

API_URL = "https://api.coindesk.com/v1/bpi/currentprice.json"
LAST_RATE = None

# Configure raspberry
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)

# Configure LCD display
#lcd = CharLCD(numbering_mode=GPIO.BCM, cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33, 31, 29, 23])

# Configure plot
x = []
y = []
i = 0

plt.title('Bitcoin rate plot')
plt.xlabel('Iteration')
plt.ylabel('Rate (thousands)')
plt.ion()
plt.show()
plt.pause(0.001)


def get_rate():
    response = requests.get(API_URL)
    json = response.json()
    rate = json["bpi"]["USD"]["rate"]

    return rate.split(".")[0].replace(",", ".")


# Check if I am in range of
# raspberry to prevent unnecessary
# actions
def am_i_in_range():
    nearby_devices = bluetooth.discover_devices(lookup_names=True)

    for name, addr in nearby_devices:
        if "iPhone (Mateusz)" in name:
            return True

    return False

def check_percentage(percentage, use_red_led):
    LED = 18
    if use_red_led:
        LED = 19

    if percentage >= 0.8:
        GPIO.output(LED, GPIO.HIGH)

    if percentage >= 1.0:
        # If difference is higher than 1%
        # play beep audio
        pygame.mixer.music.load("alert.mp3")
        pygame.mixer.music.play()

        # Wait till audio end
        while pygame.mixer.music.get_busy():
            continue

    time.sleep(3)
    GPIO.output(LED, GPIO.LOW)


# Main script logic, get current rate
# and react via sending text output
# to monitor component, playing sound, etc..
def check_rate():
    global LAST_RATE, x, y, i, lcd
    
    # Get BitCoin Rate In USD
    rate = get_rate()

    print("Aktualny kurs bitcoina")
    print("$" + rate)
    
    # Convert to float
    converted_rate = float(rate)
    #lcd.write_string("$" + rate)
    
    y.append(converted_rate)
    
    i += 1
    x.append(i)
     
    plt.plot(x, y)
    
    if LAST_RATE != converted_rate:
        LAST_RATE = converted_rate
        return

    try:
        data = {
            "barear": "p7cznFIwwnl6mGzsJenIhO1KNzKYNj",
            "rate": convert_rate
        }
        requests.post("https://api.matrzak.pl/btcrate", json=data)
    except:
        pass

    # Check if I'm in range
    if not am_i_in_range():
        return
    
    if LAST_RATE > converted_rate:
        check_percentage((LAST_RATE - rate) / LAST_RATE * 100, True)
        return

    if LAST_RATE < converted_rate:
        check_percentage((rate - LAST_RATE) / LAST_RATE * 100, False)
        return


check_rate()
while True:
    time.sleep(5)
    plt.pause(3)
    check_rate()
