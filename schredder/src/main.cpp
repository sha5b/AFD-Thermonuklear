#include <Arduino.h>

// ===== CONFIGURATION =====
// Pin definitions
const int RELAY_1_PIN = 13;  // D13 -> First relay (IN3)
const int RELAY_2_PIN = 14;  // D14 -> Second relay

// Timing configuration (in milliseconds)
// For production: ON_TIME = 10 * 60 * 1000 (10 minutes)
// For debugging: ON_TIME = 30 * 1000 (30 seconds)
const unsigned long ON_TIME =  300 * 1000;      // 30 seconds for debugging
const unsigned long OFF_TIME = 2 * 1000;       // 2 seconds

// Relay states (change if your relay module is active LOW or HIGH)
const int RELAY_ON = LOW;     // Active-LOW relay module
const int RELAY_OFF = HIGH;   // Active-LOW relay module

// ===== GLOBAL VARIABLES =====
// Relay 1 state tracking
unsigned long relay1_previousMillis = 0;
bool relay1_state = false;

// Relay 2 state tracking
unsigned long relay2_previousMillis = 0;
bool relay2_state = false;

void setup() {
  // Initialize serial communication for debugging
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n=================================");
  Serial.println("ESP32 Dual Relay Controller");
  Serial.println("=================================");
  Serial.printf("Relay 1 Pin: GPIO %d\n", RELAY_1_PIN);
  Serial.printf("Relay 2 Pin: GPIO %d\n", RELAY_2_PIN);
  Serial.printf("ON Time: %lu ms (%.1f seconds)\n", ON_TIME, ON_TIME / 1000.0);
  Serial.printf("OFF Time: %lu ms (%.1f seconds)\n", OFF_TIME, OFF_TIME / 1000.0);
  Serial.println("=================================\n");
  
  // Configure relay pins as outputs
  pinMode(RELAY_1_PIN, OUTPUT);
  pinMode(RELAY_2_PIN, OUTPUT);
  
  // Initialize relays to OFF state
  digitalWrite(RELAY_1_PIN, RELAY_OFF);
  digitalWrite(RELAY_2_PIN, RELAY_OFF);
  
  Serial.println("Relays initialized to OFF state");
  Serial.println("Starting relay control cycle...\n");
  
  // Initialize timers
  relay1_previousMillis = millis();
  relay2_previousMillis = millis();
  
  // Start with relays ON
  relay1_state = true;
  relay2_state = true;
  digitalWrite(RELAY_1_PIN, RELAY_ON);
  digitalWrite(RELAY_2_PIN, RELAY_ON);
  Serial.println("RELAY 1: ON");
  Serial.println("RELAY 2: ON");
}

void loop() {
  unsigned long currentMillis = millis();
  
  // ===== RELAY 1 CONTROL =====
  if (relay1_state) {
    // Relay 1 is ON - check if ON_TIME has elapsed
    if (currentMillis - relay1_previousMillis >= ON_TIME) {
      relay1_state = false;
      digitalWrite(RELAY_1_PIN, RELAY_OFF);
      relay1_previousMillis = currentMillis;
      Serial.println("RELAY 1: OFF");
    }
  } else {
    // Relay 1 is OFF - check if OFF_TIME has elapsed
    if (currentMillis - relay1_previousMillis >= OFF_TIME) {
      relay1_state = true;
      digitalWrite(RELAY_1_PIN, RELAY_ON);
      relay1_previousMillis = currentMillis;
      Serial.println("RELAY 1: ON");
    }
  }
  
  // ===== RELAY 2 CONTROL =====
  if (relay2_state) {
    // Relay 2 is ON - check if ON_TIME has elapsed
    if (currentMillis - relay2_previousMillis >= ON_TIME) {
      relay2_state = false;
      digitalWrite(RELAY_2_PIN, RELAY_OFF);
      relay2_previousMillis = currentMillis;
      Serial.println("RELAY 2: OFF");
    }
  } else {
    // Relay 2 is OFF - check if OFF_TIME has elapsed
    if (currentMillis - relay2_previousMillis >= OFF_TIME) {
      relay2_state = true;
      digitalWrite(RELAY_2_PIN, RELAY_ON);
      relay2_previousMillis = currentMillis;
      Serial.println("RELAY 2: ON");
    }
  }
  
  // Small delay to prevent excessive CPU usage
  delay(10);
}
