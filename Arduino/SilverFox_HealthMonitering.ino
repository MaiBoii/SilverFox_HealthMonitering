#include "MyVariables.h"
#include "MyFunctions.h"
//#define BUZZER_PIN 9 // 스피커에 연결된 핀 번호

void setup() {
  Serial.begin(9600);
  //pinMode(BUZZER_PIN, OUTPUT);
  ss.begin(GPSBaud);
}

void loop() {
  GpsReceiver();
  // if (judgeEmergency()) {
  //   Serial.println("응급상황 발생!");
  //   musicStart(); // 응급 상황 발생 시 음악 연주
  // } else {
  //   Serial.println("정상 상태");
  //   // 정상 상태일 때 추가적인 작업을 수행할 수 있음
  // }
  delay(1000); // 상태 확인 주기
  //ForTestSerialMonitor();
}
