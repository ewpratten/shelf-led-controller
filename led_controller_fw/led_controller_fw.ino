#include <Adafruit_NeoPixel.h>
#include <stdint.h>

// Hardware Config
#define LED_DI_PIN 6
#define BUTTON_PIN 8
#define PIXEL_COUNT 36
#define BUTTON_HOLD_THRESHOLD_MS 200

// Wrapper class for the lights
Adafruit_NeoPixel pixels(PIXEL_COUNT, LED_DI_PIN, NEO_GRB + NEO_KHZ800);

// Colors
uint32_t COLORS[] = {
  pixels.Color(255,255,255), // WHITE
  pixels.Color(245, 135, 10), // ORANGE-ISH
  pixels.Color(66, 135, 245),
  pixels.Color(66, 245, 120),
  pixels.Color(255,0,0),
  pixels.Color(0,255,0),
  pixels.Color(0,0,255),
};
size_t total_color_count = sizeof(COLORS) / sizeof(uint32_t);
size_t current_color_index = 0;
bool leds_enabled = false;

// Button state
bool last_button_state = false;
long button_state_changed_at = 0;

void setup() {
  // Start a serial connection
  Serial.begin(9600);

  // Set up the LED strip
  pixels.begin();
  pinMode(BUTTON_PIN, INPUT);

  // Reset everything
  pixels.clear();
  pixels.show();
  pixels.setBrightness(255);
  current_color_index = 0;
  leds_enabled = false;
  button_state_changed_at = millis();
}

void loop() {
  // Timing logic
  long now = millis();

  // Check up on the button
  bool current_button_state = digitalRead(BUTTON_PIN);
  bool button_state_just_changed = (current_button_state != last_button_state);
  bool button_just_released = button_state_just_changed && (current_button_state==false);
  bool button_held_past_threshold = ((now-button_state_changed_at) > BUTTON_HOLD_THRESHOLD_MS);
  if (button_state_just_changed) { button_state_changed_at = now; }
  last_button_state = current_button_state;

  // Toggle the lights if needed
  if (button_just_released && button_held_past_threshold) {
    leds_enabled = !leds_enabled;
  }

  // Cycle the lights if needed
  if (button_just_released && !button_held_past_threshold) {
    current_color_index += 1;
    if (current_color_index >= total_color_count){
      current_color_index = 0;
    }
  }

  // We only really need to send commands on state change
  if (button_state_just_changed) {

    // Handle the lights
    if (leds_enabled){
      uint32_t current_color = COLORS[current_color_index];

      // Write to all lights
      for (int i=0; i<pixels.numPixels(); i++) {
        pixels.setPixelColor(i, current_color);
      }
      pixels.show();

    } else {
      pixels.clear();
      pixels.show();

      // Send a 0x00 back to indicate the lights are off
      Serial.write((uint8_t) 0x00);
    }
  }

  // Check if we got a serial byte
  if (Serial.available() > 0) {
    int incoming_byte = Serial.read();

    // Set the lights to whatever that byte is
    for (int i=0; i<pixels.numPixels(); i++) {
      pixels.setPixelColor(i, incoming_byte);
    }
    pixels.show();

    // Echo the byte back
    Serial.write(incoming_byte);
  }
  
}
