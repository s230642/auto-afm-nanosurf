#include <Mouse.h>

void setup() {
  Serial.begin(9600);
  Mouse.begin();

  // Wait for serial connection
  while (!Serial) { ; }  
  Serial.println("READY");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();  // remove any \r\n
    if (cmd == "CLICK") {
      Mouse.click(MOUSE_LEFT);
      Serial.println("Clicked");
    }
  }
}
