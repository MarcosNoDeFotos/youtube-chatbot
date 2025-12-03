#include <Adafruit_NeoPixel.h>
#define RGB_DATA_PIN A0
#define NUM_LEDS 36


class Color{
  public:
    int r;
    int g;
    int b;
    Color(int r1, int g1, int b1);
    String getRGB();
};

Color::Color(int r1, int g1, int b1) {
  r   = r1;
  g   = g1;
  b   = b1;
}
String Color::getRGB(){
  return ""+r+g+b;
}

String animacionActual = "";
Color colorActual(0, 0, 0);
Color lastColor = colorActual;
bool running = false;

Adafruit_NeoPixel leds(NUM_LEDS, RGB_DATA_PIN, NEO_GRB + NEO_KHZ800);



int steps = 50;         // cantidad de pasos para el fade
int delayTime = 20;     // tiempo entre pasos (ms)


void setup() {
  Serial.begin(9600);
  leds.begin();
  leds.show();
}

void loop() {
  String teststr = Serial.readString();
  if (teststr != "" && teststr.indexOf("|") != -1) {
    String data = teststr.substring(teststr.indexOf("|")+1);
    Serial.println(data);
    String idAccion = teststr;
    data.trim();
    idAccion.trim();
    idAccion.replace("|"+data, "");
    if(idAccion == "set_color_global"){
      if(data.indexOf(",") != -1){
        // Color color = new Color(3, 2, 1);
        int p1 = data.indexOf(',');
        int p2 = data.indexOf(',', p1 + 1);
        colorActual.r = data.substring(0, p1).toInt();
        colorActual.g = data.substring(p1 + 1, p2).toInt();
        colorActual.b = data.substring(p2 + 1).toInt();
        Serial.println(colorActual.r);
        Serial.println(colorActual.g);
        Serial.println(colorActual.b);
        if(data.indexOf("|animacion=") != -1){
          animacionActual = data.substring(data.indexOf("|animacion=")+11);
          animacionActual.trim();
          Serial.println(animacionActual);
        }
        running = true;
      }
    }
  }
  if(running){
    if (colorActual.getRGB() != lastColor.getRGB()) {
      for (int i = 0; i < NUM_LEDS; i++) {
        // leds.setPixelColor(i, leds.Color(255, 0, 0));
        leds.setPixelColor(i, leds.Color(colorActual.r, colorActual.g, colorActual.b));
        leds.show();
        delay(20);    
      }
      lastColor = colorActual;
    }
    if(animacionActual == "loop"){
      fadeLED(0, colorActual.r, colorActual.g, colorActual.b);
    }
  }else{
    leds.clear();
    leds.show();
  }

  delay(100);
}


void fadeLED(int ledIndex, int r, int g, int b) {
  // Fade out
  for (int i = steps; i >= 0; i--) {
    int r_val = (r * i) / steps;
    int g_val = (g * i) / steps;
    int b_val = (b * i) / steps;

    leds.fill(leds.Color(r_val, g_val, b_val), 0, NUM_LEDS);
    leds.show();
    delay(delayTime);
  }
  
  // Fade in
  for (int i = 0; i <= steps; i++) {
    int r_val = (r * i) / steps;
    int g_val = (g * i) / steps;
    int b_val = (b * i) / steps;

    leds.fill(leds.Color(r_val, g_val, b_val), 0, NUM_LEDS);
    leds.show();
    delay(delayTime);
  }

  
}

