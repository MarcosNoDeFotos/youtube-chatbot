#include <Adafruit_NeoPixel.h>
#define RGB_DATA_PIN A0
#define NUM_LEDS 36
Adafruit_NeoPixel leds(NUM_LEDS, RGB_DATA_PIN, NEO_GRB + NEO_KHZ800);

float brilloGlobal = 0.5;  // De 0 a 1 (lo dejas como está, tu clase Color lo usa)
int cantidadLedsCuandoAnimacionVuelta = 8;

// ------------------ Clase Color (Mantenida) ------------------
class Color {
public:
  int r;
  int g;
  int b;
  float brillo;
  Color(int r1, int g1, int b1);
  String getRGB();
  void setColor(int r1, int g1, int b1);
  void setBrillo(float brilloSet);
  int getR();
  int getG();
  int getB();
};

Color::Color(int r1, int g1, int b1) {
  r = r1 * brilloGlobal;
  g = g1 * brilloGlobal;
  b = b1 * brilloGlobal;
}
String Color::getRGB() {
  return "r:" + String(r) + ", g:" + String(g) + ", b:" + String(b) + ", brillo:" + String(brillo);
}
int Color::getR() {
  return r * brilloGlobal;
}
int Color::getG() {
  return g * brilloGlobal;
}
int Color::getB() {
  return b * brilloGlobal;
}
void Color::setColor(int r1, int g1, int b1) {
  r = r1 * brilloGlobal;
  g = g1 * brilloGlobal;
  b = b1 * brilloGlobal;
}
void Color::setBrillo(float brilloSet) {
  brillo = brilloSet;
}

Color generarColorRandom() {
  int r = random(0, 256);
  int g = random(0, 256);
  int b = random(0, 256);
  return Color(r, g, b);
}

// -------------------------------------------------------------

// Estado global y serial
String animacionActual = "static";
Color colorActual(0, 0, 0);
Color lastColor = colorActual;
bool running = false;

String inputBuffer = "";
unsigned long nowMillis = 0;

// ------------------ Interfaz Animacion ------------------
class Animacion {
public:
  unsigned long intervalo = 70;      // tiempo entre pasos (ms) por defecto
  unsigned long lastStep = 0;
  virtual void begin() { lastStep = 0; }
  virtual void reset() { lastStep = 0; }
  virtual void update() = 0;
  virtual ~Animacion() {}
};

// ------------- Animacion: StaticColor (mantener color) -------------
class AnimStatic : public Animacion {
public:
  void update() override {
    // no hace nada en cada paso; la actualización de color se gestiona globalmente
  }
};

// ------------- Animacion: Loop (fade global in/out) -------------
class AnimLoop : public Animacion {
public:
  int steps = 50;
  int stepIndex = 0;
  bool fadingIn = true;
  unsigned long stepInterval = 20; // ms entre pasos de fade (ajustable)

  AnimLoop() { intervalo = stepInterval; }

  void reset() override {
    stepIndex = 0;
    fadingIn = true;
    lastStep = 0;
  }

  void update() override {
    if (millis() - lastStep < intervalo) return;
    lastStep = millis();

    // avanzar un paso de fade
    if (fadingIn) {
      stepIndex++;
      if (stepIndex >= steps) {
        stepIndex = steps;
        fadingIn = false;
      }
    } else {
      stepIndex--;
      if (stepIndex <= 0) {
        stepIndex = 0;
        fadingIn = true;
      }
    }

    float factor = float(stepIndex) / float(steps);
    int r = int(colorActual.getR() * factor);
    int g = int(colorActual.getG() * factor);
    int b = int(colorActual.getB() * factor);

    leds.fill(leds.Color(r, g, b), 0, NUM_LEDS);
    leds.show();
  }
};
// ------------- Animacion: fill (desde el centro, rellena el color hacia los dos lados y vuelve a apagarse) -------------
class AnimFill : public Animacion {
public:
  int stepIndex = 0;
  int ledIzquierda = NUM_LEDS/2-2;
  int ledIzquierdaInicial = ledIzquierda;
  int ledDerecha = ledIzquierda+1;
  int ledDerechaInicial = ledDerecha;
  int steps = NUM_LEDS/2;
  bool fadingIn = true;
  int cantidadLeds = 8;
  unsigned long stepInterval = 60; // ms entre pasos de fade (ajustable)

  AnimFill() { intervalo = stepInterval; }

  void reset() override {
    stepIndex = 0;
    fadingIn = true;
    lastStep = 0;
    ledIzquierda = ledIzquierdaInicial;
    ledDerecha = ledDerechaInicial;
    leds.clear();
    leds.show();
  }

  void update() override {
    if (millis() - lastStep < intervalo) return;
    lastStep = millis();
    if (fadingIn) {
      stepIndex++;
      ledIzquierda-=1;
      ledDerecha+=1;
      if (stepIndex >= steps) {
        stepIndex = steps;
        fadingIn = false;
        leds.clear();
      }
    } else {
      stepIndex--;
      ledIzquierda+=1;
      ledDerecha-=1;
      if (stepIndex <= 0) {
        stepIndex = 0;
        fadingIn = true;
        leds.clear();
      }
    }
    leds.clear();
    if(ledIzquierda >= 0){
      for (int i = 0; i < cantidadLeds; i++) {
        int led = ledIzquierda-i;
        if (led < 0) {
          led = 0;
        }
        leds.setPixelColor(led, leds.Color(colorActual.getR(), colorActual.getG(), colorActual.getB()));
      }
    }
    if(ledDerecha < NUM_LEDS){
      for (int i = 0; i < cantidadLeds; i++) {
        int led = ledDerecha+i;
        if (led > NUM_LEDS) {
          led = NUM_LEDS;
        }
        leds.setPixelColor(led, leds.Color(colorActual.getR(), colorActual.getG(), colorActual.getB()));
      }
    }
    leds.show();
  }
};
// ------------- Animacion: random (se enciende un led aleatorio con la animación de loop fade in y fadeout) -------------
class AnimRandom : public Animacion {
public:
  int steps = 50;
  int stepIndex = 0;
  bool fadingIn = true;
  unsigned long stepInterval = 20; // ms entre pasos de fade (ajustable)
  int ledActual = random(0, NUM_LEDS);
  int ledAnterior = 0;
  int numLedsEncendidos = 6;
  AnimRandom() { intervalo = stepInterval; }

  void reset() override {
    stepIndex = 0;
    fadingIn = true;
    lastStep = 0;
  }

  void update() override {
    if (millis() - lastStep < intervalo) return;
    lastStep = millis();

    // avanzar un paso de fade
    if (fadingIn) {
      stepIndex++;
      if (stepIndex >= steps) {
        stepIndex = steps;
        fadingIn = false;
      }
    } else {
      stepIndex--;
      if (stepIndex <= 0) {
        stepIndex = 0;
        fadingIn = true;
        ledActual = random(0, NUM_LEDS);
        while(ledActual == ledAnterior){
          ledActual = random(0, NUM_LEDS);
        }
        ledAnterior = ledActual;
      }
    }

    float factor = float(stepIndex) / float(steps);
    int r = int(colorActual.getR() * factor);
    int g = int(colorActual.getG() * factor);
    int b = int(colorActual.getB() * factor);
    leds.clear();
    for(int i = 0; i < numLedsEncendidos; i++){
      int ledEncender = ledActual+i;
      if(ledEncender >= NUM_LEDS){
        ledEncender = 0+i;
      }
      leds.setPixelColor(ledEncender, leds.Color(r, g, b));
    }
    leds.show();
  }
};
// ------------- Animacion: destello (se establece un color y aleatoriamente se encenderá una luz blanca dando sensación de destello) -------------
class AnimDestello : public Animacion {
public:
  int steps = 10;
  int stepsEspera = 10;
  int stepIndex = 0;
  bool fadingIn = true;
  unsigned long stepInterval = 30; // ms entre pasos de fade (ajustable)
  int ledActual = random(0, NUM_LEDS);
  int ledAnterior = 0;
  int numLedsEncendidos = 2;
  bool espera = false;
  AnimDestello() { intervalo = stepInterval; }

  void reset() override {
    stepIndex = 0;
    fadingIn = true;
    lastStep = 0;
  }

  void update() override {
    if (millis() - lastStep < intervalo) return;
    lastStep = millis();

    // avanzar un paso de fade
    if (fadingIn) {
      stepIndex++;
      if (stepIndex >= steps) {
        stepIndex = steps;
        fadingIn = false;
        espera = false;
      }
    } else {
      stepIndex--;
      if (stepIndex <= 0-stepsEspera) {
        stepIndex = 0;
        fadingIn = true;
        ledActual = random(0, NUM_LEDS);
        while(ledActual == ledAnterior){
          ledActual = random(0, NUM_LEDS);
        }
        ledAnterior = ledActual;
      }
      espera = true;
    }

    float factor = float(stepIndex) / float(steps);
    int r = int(255*brilloGlobal * factor);
    int g = int(255*brilloGlobal * factor);
    int b = int(255*brilloGlobal * factor);
    leds.fill(leds.Color(colorActual.getR(), colorActual.getG(), colorActual.getB()));
    if(!espera){
      for(int i = 0; i < numLedsEncendidos; i++){
        int ledEncender = ledActual+i;
        if(ledEncender >= NUM_LEDS){
          ledEncender = 0+i;
        }
        leds.setPixelColor(ledEncender, leds.Color(r, g, b));
      }
    }
    
    leds.show();
  }
};

// ------------- Animacion: Multicolor -------------
class AnimMulticolor : public Animacion {
public:
  int remaining[NUM_LEDS];
  int remainCount = 0;
  unsigned long stepInterval = 30;

  AnimMulticolor() { intervalo = stepInterval; }

  void reset() override {
    // inicializar lista con índices 0..NUM_LEDS-1
    for (int i = 0; i < NUM_LEDS; i++) remaining[i] = i;
    remainCount = NUM_LEDS;
    lastStep = 0;
  }

  void update() override {
    if (remainCount <= 0) {
      // cuando se acaben, volvemos a empezar (o podríamos parar)
      reset();
      return;
    }
    if (millis() - lastStep < intervalo) return;
    lastStep = millis();

    // elegir un índice aleatorio dentro de remaining[0..remainCount-1]
    int pickIndex = random(0, remainCount);
    int ledIndex = remaining[pickIndex];

    // swap out chosen with last and decrement remainCount
    remaining[pickIndex] = remaining[remainCount - 1];
    remainCount--;

    Color c = generarColorRandom();
    int r = int(c.r * brilloGlobal);
    int g = int(c.g * brilloGlobal);
    int b = int(c.b * brilloGlobal);

    leds.setPixelColor(ledIndex, leds.Color(r, g, b));
    leds.show();
  }
};

// ------------- Animacion: Vuelta (ventana que se desplaza) -------------
class AnimVuelta : public Animacion {
public:
  int pos = 0;
  unsigned long stepInterval = 80;

  AnimVuelta() { intervalo = stepInterval; }

  void reset() override {
    pos = 0;
    lastStep = 0;
  }

  void update() override {
    if (millis() - lastStep < intervalo) return;
    lastStep = millis();

    leds.clear();
    for (int j = 0; j < cantidadLedsCuandoAnimacionVuelta; j++) {
      int idx = pos + j;
      if (idx < NUM_LEDS) {
        leds.setPixelColor(idx, leds.Color(colorActual.getR(), colorActual.getG(), colorActual.getB()));
      }
    }
    leds.show();

    pos++;
    if (pos >= NUM_LEDS) {
      pos = 0;
      // opcional: al terminar volver a limpiar
      // leds.clear(); leds.show();
    }
  }
};

// ------------------ Manager de animaciones ------------------
Animacion* currentAnim = nullptr;
AnimStatic animStatic;
AnimLoop animLoop;
AnimMulticolor animMulticolor;
AnimVuelta animVuelta;
AnimFill animFill;
AnimRandom animRandom;
AnimDestello animDestello;

void setAnimationByName(const String &name) {
  if (currentAnim != nullptr) {
    currentAnim->reset();
  }

  if (name == "loop") {
    currentAnim = &animLoop;
  } else if (name == "multicolor") {
    currentAnim = &animMulticolor;
  } else if (name == "vuelta") {
    currentAnim = &animVuelta;
  } else if (name == "fill") {
    currentAnim = &animFill;
  } else if (name == "random") {
    currentAnim = &animRandom;
  } else if (name == "destello") {
    currentAnim = &animDestello;
  } else {
    currentAnim = &animStatic; // "static" o cualquier otro
  }
  currentAnim->begin();
  currentAnim->reset();
  animacionActual = name;
}

// ------------------ Helper functions ------------------


bool arrayContains(int array[], int arrayLength, int val) {
  for (int i = 0; i < arrayLength; i++) {
    if (array[i] == val) return true;
  }
  return false;
}

// ------------------ Gestión de cambio de color secuencial (un LED por tick) ------------------
bool colorChanging = false;
int colorChangeIndex = 0;
unsigned long colorChangeInterval = 20; // ms entre un LED y el siguiente al rellenar con colorActual
unsigned long colorChangeLast = 0;

void startColorFillSequence() {
  colorChanging = true;
  colorChangeIndex = 0;
  colorChangeLast = 0;
}

void stepColorFillSequence() {
  if (!colorChanging) return;
  if (millis() - colorChangeLast < colorChangeInterval) return;
  colorChangeLast = millis();

  if (colorChangeIndex < NUM_LEDS) {
    leds.setPixelColor(colorChangeIndex, leds.Color(colorActual.getR(), colorActual.getG(), colorActual.getB()));
    leds.show();
    colorChangeIndex++;
  } else {
    colorChanging = false;
    lastColor = colorActual; // acabado
  }
}

// ------------------ Serial y parsing (no bloqueante) ------------------
void procesarComando(const String &teststr) {
  if (teststr != "" && teststr.indexOf("|") != -1) {
    String data = teststr.substring(teststr.indexOf("|") + 1);
    String idAccion = teststr;
    data.trim();
    idAccion.trim();
    idAccion.replace("|" + data, "");

    if (idAccion == "set_color_global") {
      if (data.indexOf(",") != -1) {
        setColorActualDeString(data);
        // si incluye animacion en el mismo comando
        if (data.indexOf("|animacion=") != -1) {
          String a = data.substring(data.indexOf("|animacion=") + 11);
          a.trim();
          setAnimationByName(a);
        }
        running = true;
        // iniciar secuencia de pintado LED por LED
        startColorFillSequence();
      }
    } else if (idAccion == "set_animacion") {
      setAnimationByName(data);
      if (animacionActual == "multicolor") {
        colorActual.setColor(255, 255, 255); // comportamiento previo
      }
      running = true;
    } else if (idAccion == "set_brillo") {
      brilloGlobal = data.toFloat();
      colorActual.setBrillo(brilloGlobal);
      running = true;
      // Si se cambia brillo, recolorear según último color conocido
      startColorFillSequence();
    } else if (idAccion == "get_color_global") {
      Serial.println(colorActual.getRGB());
    }
  }
}

// buffer de serial
void leerInput() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      // línea completa
      if (inputBuffer.length() > 0) {
        procesarComando(inputBuffer);
      }
      inputBuffer = "";
    } else if (c != '\r') {
      // ignoramos CR, acumulamos otros caracteres
      inputBuffer += c;
      // protección contra buffer excesivo
      if (inputBuffer.length() > 200) inputBuffer = inputBuffer.substring(inputBuffer.length() - 200);
    }
  }
}

// ------------------ Utilidades parseo color ------------------
String setColorActualDeString(String data) {
  int p1 = data.indexOf(',');
  int p2 = data.indexOf(',', p1 + 1);
  int rr = data.substring(0, p1).toInt();
  int gg = data.substring(p1 + 1, p2).toInt();
  int bb = data.substring(p2 + 1).toInt();
  colorActual.setColor(rr, gg, bb);
  return "";
}

// ------------------ Setup / Loop ------------------
void setup() {
  Serial.begin(9600);
  randomSeed(analogRead(A0));
  leds.begin();
  leds.show();

  // anim inicial
  setAnimationByName("static");
  running = false;
}

void loop() {
  nowMillis = millis();
  leerInput();

  // si no está corriendo, limpiar y salir rápido
  if (!running) {
    // opcional: mantener leds apagados
    // leds.clear(); leds.show();
    return;
  }

  // si hay una secuencia de llenado por cambio de color, priorizarla
  if (colorChanging) {
    stepColorFillSequence();
    // no return; dejamos que la animación también avance en paralelo si quieres.
  }

  // actualizamos animación actual (cada anim avanzará solo un paso por llamada)
  if (currentAnim != nullptr) {
    currentAnim->update();
  }
}
