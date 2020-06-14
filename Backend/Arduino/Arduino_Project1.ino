// Dust Sensor
int DS = 4;
unsigned long duration;
unsigned long starttime;
unsigned long sampletime_ms = 30000;//sample 30s ;
unsigned long lowpulseoccupancy = 0;

// Air Quality
String data = "0";
float ratio = 0;
float concentration = 0;

// DHT22
int pin = 2;
uint8_t bits[5];

int rv;
float humidity;
float temperature;


void setup() {
  Serial.begin(9600);

  pinMode(DS,INPUT);
  starttime = millis();
  Serial.println("Sensor ready.");

}


bool read_sensor() {
    
    uint8_t mask = 128;
    uint8_t idx = 0;

    for (uint8_t i = 0; i < 5; i++) bits[i] = 0;
    
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
    delay(1);
    pinMode(pin, INPUT);
    delayMicroseconds(40);

    uint16_t loopCnt = F_CPU/40000;
    while(digitalRead(pin) == LOW)
    {
        if (--loopCnt == 0) return -2;
    }
    
    loopCnt = F_CPU/40000;

    while(digitalRead(pin) == HIGH)
    {
        if (--loopCnt == 0) return -2;
    }

    for (uint8_t i = 40; i != 0; i--)
    {
        loopCnt = F_CPU/40000;
        while(digitalRead(pin) == LOW)
        {
            if (--loopCnt == 0) return -2;
        }

        uint32_t t = micros();

        loopCnt = F_CPU/40000;
        while(digitalRead(pin) == HIGH)
        {
            if (--loopCnt == 0) return -2;
        }

        if ((micros() - t) > 40)
        {
            bits[idx] |= mask;
        }
        mask >>= 1;
        if (mask == 0)   // next byte?
        {
            mask = 128;
            idx++;
        }
    }   
    return 0;
}
void loop() {
  
  duration = pulseIn(DS, LOW);
  lowpulseoccupancy = lowpulseoccupancy+duration;
  
  if ((millis()-starttime) > sampletime_ms)//if the sample time == 30s
    {
        // Dust Sensor
        ratio = lowpulseoccupancy/(sampletime_ms*10.0);  // Integer percentage 0=>100
        concentration = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62; // using spec sheet curve
        if (concentration > 8000){
          concentration = 8000;
        }
        
        data = String(concentration);
        lowpulseoccupancy = 0;

        // Air Quality
        int quality = analogRead(A5);
        
        quality = (quality / 1023.0 * 100);
        if (quality > 100) {
          quality = 100;
        }
        data = data + "," + String(quality);

        // DHT22
        rv = read_sensor();

        humidity = word(bits[0], bits[1]) * 0.1;
        temperature = word(bits[2] & 0x7F, bits[3]) * 0.1;
        if (bits[2] & 0x80)  // negative temperature
        {
            temperature = -temperature;
        }
    
        uint8_t sum = bits[0] + bits[1] + bits[2] + bits[3];
        if (bits[4] != sum)
        {
           temperature = 0;
           humidity = 0;
        }
        
        data = data + "," + String(humidity) + "," + String(temperature);
        
        starttime = millis();
    }

    // When RPI sends String "data" print out
    if(Serial.available() > 0){
      if(Serial.readStringUntil('\n') == "data"){
        Serial.println(data);
      }
    }
  
  
    
}
