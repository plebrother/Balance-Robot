#include <Arduino.h>
String command = "";


void handleCommand(const String& cmd) {
  if (cmd == "ping") {
    Serial.println("pong");
  } else if (cmd == "id") {
    Serial.println("ESP32-TEST-001");
  } else {
    Serial.println("Unknown: " + cmd);
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  //Serial.println("");
  //Serial.println("ESP32 started");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      handleCommand(command);
      command = "";
    } else {
      command += c;
    }
  }
  delay(10);
}
