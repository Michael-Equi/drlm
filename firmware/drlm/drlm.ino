#include <OctoWS2811.h>

#define NUMPIXELS 576
#define PIXELSPERSEGMEMT 432

const int ledsPerStrip = PIXELSPERSEGMEMT;
DMAMEM int displayMemory[ledsPerStrip * 6];
int drawingMemory[ledsPerStrip * 6];
const int config = WS2811_GRB | WS2811_800kHz;
OctoWS2811 leds(ledsPerStrip, displayMemory, drawingMemory, config);

char bufr[NUMPIXELS * 3 + 1]; // buffer to hold led config

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
    // Compute parity bit
    for(int i=0; i < NUMPIXELS * 3; i++) {
      parity ^= bufr[i];
    }
    if (bufr[NUMPIXELS * 3] == parity) {
      digitalWrite(LED_BUILTIN, HIGH);
      for (int i = 0; i < NUMPIXELS; i += 1) {
        uint32_t color = bufr[3 * i] << 16 | bufr[3 * i + 1] << 8 | bufr[3 * i + 2];
        leds.setPixel(i, color);
      }
      leds.show();
    }
    bufLoc = 0;
    parity = 0;
    complete = false;
  }
}

void serialEvent() {
  digitalWrite(LED_BUILTIN, LOW);
  Serial.readBytes(bufr, NUMPIXELS * 3 + 1);
  complete = true;
}
