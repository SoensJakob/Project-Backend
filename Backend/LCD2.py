from RPi import GPIO
import time

class LCD:

    def __init__(self,RS=26,E=19,D0=25,D1=8,D2=7,D3=1,D4=12,D5=16,D6=20,D7=21):
        self.Display = [D7,D6,D5,D4,D3,D2,D1,D0]
        self.RS = RS
        self.E = E

        self.setup()
        

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(self.RS, GPIO.OUT)
        GPIO.setup(self.E, GPIO.OUT)
        for D in self.Display:
            GPIO.setup(D, GPIO.OUT)

    def set_data_bits(self, value):
        for i in range(0,8):
            bit = bool(0x80 & (value << i))
            # print(f"{i}: {bit}")
            GPIO.output(self.Display[i], bit)

    def send_instruction(self, value):
        GPIO.output(self.RS, GPIO.LOW)
        GPIO.output(self.E, GPIO.HIGH)
        self.set_data_bits(value)
        GPIO.output(self.E, GPIO.LOW)
        
        time.sleep(0.01)

    def send_character(self, value):
        GPIO.output(self.RS, GPIO.HIGH)
        GPIO.output(self.E, GPIO.HIGH)
        self.set_data_bits(value)
        GPIO.output(self.E, GPIO.LOW)
        
        time.sleep(0.01)

    def init__LCD(self,value = 3):
        self.send_instruction(0b00111000)
        self.send_instruction(0b00001100 + value)
        self.clear_display()
    
    def clear_display(self):
        self.send_instruction(0b00000001)


    def write_message(self, bericht):
        self.clear_display()
        if len(bericht) >= 15:
            for c in range(len(bericht)):
                self.send_character(ord(bericht[c]))
                
                if c == 15:
                    self.second_row()
        
        elif 47 >= len(bericht) >= 31:
            
            while True:
                self.clear_display()
                for c in range(len(bericht)):
                    self.send_character(ord(bericht[c]))
                    if c == 15:
                        self.second_row()
                time.sleep(2)  
                self.clear_display() 
                for c in range(16,len(bericht)):
                    
                    self.send_character(ord(bericht[c]))
                    if c == 31:
                        self.second_row() 
                time.sleep(2)

        elif len(bericht) >= 47:
            
            while True:
                self.clear_display()
                for c in range(len(bericht)):
                    self.send_character(ord(bericht[c]))
                    if c == 15:
                        self.second_row()
                time.sleep(2)  
                self.clear_display() 
                for c in range(16,len(bericht)):
                    
                    self.send_character(ord(bericht[c]))
                    if c == 31:
                        self.second_row() 
                time.sleep(2)
                self.clear_display() 
                for c in range(32,len(bericht)):
                    
                    self.send_character(ord(bericht[c]))
                    if c == 47:
                        self.second_row() 
                time.sleep(2)
        else:
            for c in range(len(bericht)):
                self.send_character(ord(bericht[c]))
        

    def first_line(self, bericht):
        self.send_instruction(0x02)
        for c in range(len(bericht)):
                self.send_character(ord(bericht[c]))

    def second_line(self,bericht):
        self.send_instruction(0xC0)
        for c in range(len(bericht)):
                self.send_character(ord(bericht[c]))


