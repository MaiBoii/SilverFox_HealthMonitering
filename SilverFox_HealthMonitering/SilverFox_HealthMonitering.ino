#include "MyVariables.h"
#include "MyFunctions.h"
#define BUZZER_PIN 9 // 스피커에 연결된 핀 번호

void setup() {
  Serial.begin(9600);
  pinMode(BUZZER_PIN, OUTPUT);
  //ss.begin(GPSBaud);

  // 초음파 센서 핀 설정
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  measureInitGradient();
}

void loop() {
  //GpsReceiver();
  if (checkEmergencySituation()) {
    Serial.println("Emergency situation detected!"); 
  }
}
