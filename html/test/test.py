from RPi import GPIO
from serial import Serial, PARITY_NONE 
import threading
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(6,GPIO.OUT)

def read_data():
    with Serial('/dev/ttyUSB0', 9600, bytesize=8, parity=PARITY_NONE, stopbits=1) as port:
        while True:
            data = "data"
            data += "\n"
                
            port.write(data.encode('utf-8'))
            
            line = port.readline()
            
            line = line.decode('utf-8')
            line = str(line)
            data = line.strip("\r\n")
            
            
            if data == 0 or data == "Sensor ready.":
                print("De data wordt klaar gemaakt.")
            elif data:
                data = data.split(",")
                print(data)
            
            time.sleep(5)

threading.Timer(5, read_data).start()



try:
    p = GPIO.PWM(6 , 100)
    p.start(0)
    
    while True:
        p.ChangeDutyCycle(50)
    
        

except KeyboardInterrupt as e:
    print(e)

finally:
    print("--END--")
    
    GPIO.cleanup()
