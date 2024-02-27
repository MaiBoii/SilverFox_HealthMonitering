#include "MyVariables.h"
#include "MyFunctions.h"
#define BUZZER_PIN 9 // 스피커에 연결된 핀 번호


void setup() {
  Serial.begin(9600);

  //스피커 핀 설정
  pinMode(BUZZER_PIN, OUTPUT);

  // GPS 수신기 핀 설정
  //ss.begin(GPSBaud);

  // 초음파 센서 핀 설정
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  measureInitGradient();

  // HX711 무게 센서 핀 설정
  scale.begin(DOUT, SCK);
  scale.set_scale(6000);  // 기본 측정 단위로 보정합니다.
  scale.tare();
}

void loop() {
  //GpsReceiver();
  if (checkEmergencySituation()) {
    Serial.println("Emergency situation detected!"); 
    musicStart();
  }
}
