#Back end Server and database
from repositories.DataRepository import DataRepository
from flask import Flask,request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

# Start app

import time
import threading 
from datetime import datetime

#PI Resources
from RPi import GPIO 
from serial import Serial, PARITY_NONE 
from LCD2 import LCD
from subprocess import check_output 

# Setup GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(6,GPIO.OUT)  #Small fan
GPIO.setup(23,GPIO.OUT) # Air Humidifier
GPIO.setup(24,GPIO.IN, pull_up_down=GPIO.PUD_UP)

p = GPIO.PWM(6 , 100)   #Start pwm for fan 
p.start(0)

# Declaring global variables
status = 0          # status for the toggle button
temp = 0            # variables to keep current sensor data
hum = 0
dust = 0
aq = 0
timer = 0           # timer to debounce the button

automatic_v = True  # Automatic variables for the actuators
automatic_l = True

def teller(knop=False):   # On press of the button up the status else just refresh the value on the LCD
    global status
    global timer
    # if button hasn't been pressed in 0.5 seconds
    if timer + 0.5 < time.perf_counter():  
        # only up status is button has been pressed
        if knop:    
            if status == 2:
                status = 0
            else:
                status += 1
        # Show ip address on display
        if status == 0:                     
            ips = check_output(['hostname', '--all-ip-addresses'])      # Get ip addresses
            ips = str(ips)
            ips = ips.replace('\\n','')
            ips = ips.replace("b'",'')
            ips = ips.split(" ")
            lcd.clear_display()
            lcd.first_line(ips[1])
            lcd.second_line(ips[2])
        # Show Temperature and Humidity on Display 
        elif status == 1:                   
            global temp
            global hum
            temperatuur = "Temp: " + str(temp) + " ßC"
            humidity = "Hum: " + str(hum) + " %" 
            lcd.clear_display()
            lcd.first_line(temperatuur)
            lcd.second_line(humidity)
        # Show Dust amount and Air quality on Display     
        elif status == 2:                   
            global dust
            global aq
            dust_sensor = "Dust: " + str(dust)
            air_quality = "AQ: " + str(aq) + "%"
            lcd.clear_display()
            lcd.first_line(dust_sensor)
            lcd.second_line(air_quality)
    
    timer = time.perf_counter() # restart timer for debounce

# Get data from Arduino 
def read_data():
    with Serial('/dev/ttyUSB0', 9600, bytesize=8, parity=PARITY_NONE, stopbits=1) as port:
        status_v = "OFF" # start status for fan is off
        status_l = "OFF" # start status for air humidifier is off

        while True:
            vorigestatus_v = status_v
            vorigestatus_l = status_l
            data = "data"
            data += "\n"
            # print("writing data")
            port.write(data.encode('utf-8'))   # ask for data from the arduino
            # print("reading data")
            line = port.readline()
            line = line.decode('utf-8')
            line = str(line)
            data = line.strip("\r\n")   # parse data from arduino
            

            now = datetime.now()
            current_date_time = now.strftime("%Y-%m-%d %H:%M:%S") # get current_time
            
            if data == 0 or data == "Sensor ready.":
                print("De data wordt klaar gemaakt.")
                
            elif data:  
                data = data.split(",")
                i = 1
                print(data)
                # for each value in list add value to Database
                for d in data:
                    nieuw_id = DataRepository.create_historiek(i,current_date_time,d)
                    print(nieuw_id)
                    i += 1
                
                global dust
                global aq
                global hum
                global temp
                global status
                global automatic_l
                global automatic_v
                # put all values in global values for LCD display 
                dust = float(data[0])
                aq = float(data[1])
                hum = float(data[2])
                temp = float(data[3])
                
                # if automatic is True automatically put on fan 
                if automatic_v:
                    
                    high_d = float(data[0]) + 500
                    high_a = float(data[1]) + 5

                    if (2000 <= float(data[0]) < 3500) or (4000 <= high_d < 4500)  or (20 <= float(data[1]) < 35) or (40 <= high_a < 45):
                        p.ChangeDutyCycle(33)
                        status_v = "LOW"
                    elif (4000 <= float(data[0]) < 4500) or (5000 <= high_d < 5500) or (40 <= float(data[1]) < 55) or (60 <= high_a < 65):
                        p.ChangeDutyCycle(66)
                        status_v ="MEDIUM"
                    elif 5000 <= float(data[0]) or 60 <= float(data[1]):
                        p.ChangeDutyCycle(100)
                        status_v ="HIGH"
                    elif 2000 > high_d or 20 > high_a:
                        p.ChangeDutyCycle(0)
                        status_v ="OFF"

                    # if status fan has changed send row to database and update all connected clients
                    if status_v != vorigestatus_v:
                        nieuw_id = DataRepository.create_historiek(5,current_date_time,None,status_v)
                        print(nieuw_id)
                        print(status_v)
                        socketio.emit("B2F_status_actuator", {"device_id": 5, "status": status_v}, broadcast=True)

                # if automatic is True automatically put on air humidifier 
                if automatic_l:
                    
                    if 45 >= hum:
                        GPIO.output(23,GPIO.HIGH)
                        status_l = "ON"
                    else:
                        GPIO.output(23,GPIO.LOW)
                        status_l = "OFF"
                    # if status air humidifier has changed send row to database and update all connected clients
                    if status_l != vorigestatus_l:
                        nieuw_id = DataRepository.create_historiek(6,current_date_time,None,status_l)
                        print(nieuw_id)
                        print(status_l)
                        socketio.emit("B2F_status_actuator",{"device_id": 6, "status": status_l}, broadcast=True)
                        

            
            time.sleep(1)
            # update values on lcd if status is not 0
            if status != 0:
                teller(False)

            time.sleep(59)

# start thread to read data
threading.Timer(30, read_data).start()
# on button press update callback teller function
GPIO.add_event_detect(24, GPIO.RISING,callback=teller, bouncetime=200)  


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hier mag je om het even wat schrijven, zolang het maar geheim blijft en een string is'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app) 

endpoint = '/api/v1'

# SOCKET IO to control device page to control buttons
@socketio.on("connect")
def update_status(): 
    global automatic_v
    global automatic_l

    AP = DataRepository.read_AP_action()
    AH = DataRepository.read_AH_action()

    AP[0]['automatic'] = automatic_v
    AH[0]['automatic'] = automatic_l

    socketio.emit("B2F_status_actuators", [AP[0],AH[0]], broadcast=True)


@socketio.on("F2B_switch_automatic")
def change_automatic(json):
    if json['sensor_id'] == "5":
        global automatic_v 
        automatic_v = json['status']
    elif json['sensor_id'] == "6":
        global automatic_l
        automatic_l = json['status']
    
    update_status()

@socketio.on("F2B_switch_manual")
def change_manual(json):
    now = datetime.now()
    current_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    status = ""
    
    if json['sensor_id'] == "5":
        global automatic_v
        automatic_v = False
        if json['status'] == True:
            status = json['strength']
            if json['strength'] == "LOW":
                p.ChangeDutyCycle(33)
            elif json['strength'] == "MEDIUM":
                p.ChangeDutyCycle(66)
            elif json['strength'] == "HIGH":
                p.ChangeDutyCycle(100)
        elif json['status'] == False:
            status = "OFF"
            p.ChangeDutyCycle(0)

    elif json['sensor_id'] == "6":
        global automatic_l
        automatic_l = False
        if json['status'] == True:
            status = "ON"
            GPIO.output(23,GPIO.HIGH)
        elif json['status'] == False:
            status = "OFF"
            GPIO.output(23,GPIO.LOW)
    nieuw_id = DataRepository.create_historiek(json['sensor_id'] ,current_date_time,None,status)
    print(nieuw_id)
    update_status()


# API ENDPOINTS to control Index page and Historiek page to get data from database to front end 
@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."

@app.route(endpoint + '/device/sensors', methods=['GET'])
def get_sensors():
    if request.method == 'GET':
        data = DataRepository.read_sensors()
        return jsonify(sensors=data), 200

@app.route(endpoint + '/data', methods=['GET'])
def get_data():
    print("Loading Latest Data")
    if request.method == 'GET':
        data = DataRepository.read_latest_data()
        return jsonify(data=data), 200

# Historiek
@app.route(endpoint + '/<device_id>/day/<date>', methods=['GET'])
def get_historiek_by_device_id_and_day(device_id,date):
    if request.method == 'GET':
        data = DataRepository.read_historiek_by_device_id_and_day(device_id,date)

        for d in data:
            
            d['timestamp'] = int(d['timestamp'].strftime("%s%f"))/1000
        
        return jsonify(device=data), 200

@app.route(endpoint + '/<device_id>/month/<date>', methods=['GET'])
def get_historiek_by_device_id_and_month(device_id,date):
    if request.method == 'GET':
        data = DataRepository.read_historiek_by_device_id_and_month(device_id,date)

        for d in data:
            
            d['timestamp'] = int(d['timestamp'].strftime("%s%f"))/1000
        
        return jsonify(device=data), 200

@app.route(endpoint + '/<device_id>/3month/<date>', methods=['GET'])
def get_historiek_by_device_id_and_3month(device_id,date):
    if request.method == 'GET':
        data = DataRepository.read_historiek_by_device_id_and_3month(device_id,date)

        for d in data:
            d['timestamp'] = int(d['timestamp'].strftime("%s%f"))/1000
        
        return jsonify(device=data), 200
    

if __name__ == '__main__':
    try:
        # initialise LCD
        lcd = LCD()
        lcd.init__LCD(0) 
        
        teller()

        socketio.run(app, debug=False, host='0.0.0.0')
    except KeyboardInterrupt as e:
        print(e)
    finally:
        print("---END---")
        GPIO.output(23,GPIO.LOW)
        p.stop()
        lcd.clear_display()
        GPIO.cleanup()