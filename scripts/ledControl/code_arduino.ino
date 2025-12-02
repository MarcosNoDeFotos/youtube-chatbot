#include <Adafruit_NeoPixel.h>
f:\Documentos\scripts\youtube_chatbot\scripts\ledControl\code_arduino.ino
#define RGB_DATA_PIN A0
#define NUM_LEDS 36

Adafruit_NeoPixel leds(NUM_LEDS, RGB_DATA_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  leds.begin();
  leds.show();
}

void loop() {
  
  for (int i = 0; i < NUM_LEDS; i++) {
    leds.clear();
    leds.setPixelColor(i, leds.Color(136, 37, 211));
    leds.show();
    delay(20);    
  }
  delay(20);  
  for (int i = NUM_LEDS; i >0; i--) {
    leds.clear();
    leds.setPixelColor(i, leds.Color(136, 37, 211));
    leds.show();
    delay(20);    
  }
}
