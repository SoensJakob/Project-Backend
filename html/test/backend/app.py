from repositories.DataRepository import DataRepository
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

import time
import threading
from datetime import datetime

from RPi import GPIO 
from serial import Serial, PARITY_NONE 

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(6,GPIO.OUT)
p = GPIO.PWM(6 , 100)
p.start(0)

def read_data():
    with Serial('/dev/ttyUSB0', 9600, bytesize=8, parity=PARITY_NONE, stopbits=1) as port:
        status = "OFF"
        
        
        while True:
            vorigestatus = status
            data = "data"
            data += "\n"
            print("writing data")
            port.write(data.encode('utf-8'))
            print("reading data")
            line = port.readline()
            
            line = line.decode('utf-8')
            line = str(line)
            data = line.strip("\r\n")

            now = datetime.now()
            
            current_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
            
            if data == 0 or data == "Sensor ready.":
                print("De data wordt klaar gemaakt.")
                
            elif data:
                data = data.split(",")
                i = 1
                print(data)
                for d in data:
                    nieuw_id = DataRepository.create_historiek(i,current_date_time,d)
                    print(nieuw_id)
                    i += 1
                
                
                high_d = float(data[0]) + 500
                high_a = float(data[1]) + 5

                if (2000 <= float(data[0]) <= 4000) or (4000 <= high_d <= 4500)  or (20 <= float(data[1]) <= 40) or (40 <= high_a <= 45):
                    p.ChangeDutyCycle(33)
                    status = "LOW"
                elif (4000 <= float(data[0]) <= 5000) or (5000 <= high_d <= 5500) or (40 <= float(data[1]) <= 60) or (60 <= high_a <= 65):
                    p.ChangeDutyCycle(66)
                    status ="MEDIUM"
                elif 5000 <= float(data[0]) or 60 <= float(data[1]):
                    p.ChangeDutyCycle(100)
                    status ="HIGH"
                elif 2000 <= high_d or 20 <= high_a:
                    p.ChangeDutyCycle(0)
                    status ="OFF"
            if status != vorigestatus:
                nieuw_id = DataRepository.create_historiek(i,current_date_time,None,status)
                print(nieuw_id)
                print(status)

            time.sleep(30)

threading.Timer(30, read_data).start()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hier mag je om het even wat schrijven, zolang het maar geheim blijft en een string is'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)


# API ENDPOINTS
@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."

@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
