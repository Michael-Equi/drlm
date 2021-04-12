#include <OctoWS2811.h>

#define NUMPIXELS 288

const int ledsPerStrip = NUMPIXELS;
DMAMEM int displayMemory[ledsPerStrip * 6];
int drawingMemory[ledsPerStrip * 6];
const int config = WS2811_GRB | WS2811_800kHz;
OctoWS2811 leds(ledsPerStrip, displayMemory, drawingMemory, config);

byte bufr[NUMPIXELS * 3 + 1]; // buffer to hold led config
int bufLoc = 0; // location at which to write the next byte read in during the loop
byte parity = 0; // byte parity for the given packet
bool complete = false;

void setup() {
  // initialize serial:
  Serial.begin(115200);

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  //  pixels.begin();
  leds.begin();
  leds.show();
}

void loop() {
  if (complete) {
    if (bufr[NUMPIXELS * 3] == parity) {
      digitalWrite(LED_BUILTIN, HIGH);
      for (int i = 0; i < NUMPIXELS; i += 1) {
        //        pixels.setPixelColor(i, pixels.Color(bufr[3 * i], bufr[3 * i + 1], bufr[3 * i + 2]));
        uint32_t color = bufr[3 * i] << 16 | bufr[3 * i + 1] << 8 | bufr[3 * i + 2];
        leds.setPixel(i, color);
      }
      //      pixels.show();
      leds.show();
    }
    serial_flush();
    bufLoc = 0;
    parity = 0;
    complete = false;
  }
}

void serial_flush(void) {
  while (Serial.available()) Serial.read();
}

void serialEvent() {
  digitalWrite(LED_BUILTIN, LOW);
  while (Serial.available()) {
    // get the new byte:
    byte inByte = Serial.read();

    bufr[bufLoc] = inByte;
    bufLoc++;

    if (bufLoc == NUMPIXELS * 3 + 1) {
      complete = true;
    } else {
      parity ^= inByte;
    }
  }
}
