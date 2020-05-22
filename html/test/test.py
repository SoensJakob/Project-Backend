from RPi import GPIO


GPIO.setmode(GPIO.BCM)

GPIO.setup(17,GPIO.OUT)
GPIO.setup(21,GPIO.IN, GPIO.PUD_UP)

toggle = 0

try:
    while True:
        knop_status = GPIO.input(21)
        if knop_status == 0:
            if toggle == 1:
                toggle = 0
            else:
                toggle = 1
        
        if toggle == 1:
            GPIO.output(17,GPIO.HIGH)
        else:
            GPIO.output(17,GPIO.LOW)
        
        

except KeyboardInterrupt as e:
    print(e)

finally:
    print("--END--")
    GPIO.cleanup()