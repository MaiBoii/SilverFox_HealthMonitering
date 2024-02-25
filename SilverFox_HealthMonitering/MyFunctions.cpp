// MyFunctions.cpp
// 함수의 구현 부분을 작성한 파일입니다.
#include "MyFunctions.h"
#include "MyVariables.h"
#include <TinyGPS.h>
#include <SoftwareSerial.h>
#include <Arduino.h>
#include "HX711.h"

#define BUZZER_PIN 9 // 스피커에 연결된 핀 번호

// GPS 수신기 객체 및 시리얼 통신 객체 생성
//SoftwareSerial ss(RXPin, TXPin);
TinyGPS gps;

//응급상황시 스피커 재생 함수
void musicStart() {
  // melody와 noteDurations 배열 초기화
  int melody[] = {
    NOTE_C4, NOTE_C4, NOTE_G4, NOTE_G4, 
    NOTE_A4, NOTE_A4, NOTE_G4,
    NOTE_F4, NOTE_F4, NOTE_E4, NOTE_E4,
    NOTE_D4, NOTE_D4, NOTE_C4
  };

  int noteDurations[] = {
    4, 4, 4, 4, 
    4, 4, 2,
    4, 4, 4, 4,
    4, 4, 2
  };
  for (int i = 0; i < sizeof(melody) / sizeof(melody[0]); i++) {
    int noteDuration = 1000 / noteDurations[i];
    tone(BUZZER_PIN, melody[i], noteDuration);

    int pauseBetweenNotes = noteDuration * 1.30;
    delay(pauseBetweenNotes);
    noTone(BUZZER_PIN);
  }

  delay(2000); // 다음 반복을 위한 딜레이
}

// void GpsReceiver() {
// // GPS 수신기 관련 핀 초기화
//   const int TXPin = 12;
//   const int RXPin = 11;
//   // GPS 데이터 수신 및 처리
//   while (ss.available() > 0) {
//     char c = ss.read();
//     if (gps.encode(c)) {
//       // 위치 정보가 업데이트되었을 때, 정보 출력
//       float latitude, longitude;
//       unsigned long fix_age;
//       gps.f_get_position(&latitude, &longitude, &fix_age);
//       Serial.print("위도: ");
//       Serial.print(latitude, 6);
//       Serial.print(" 경도: ");
//       Serial.println(longitude, 6);
//     }
//   }

//   // 1초마다 반복
//   delay(1000);
// }

// 사람과의 거리 측정 함수
bool measureDistanceFromHuman() {
  // 사람과의 거리 측정 관련 변수 초기화
  long duration;
  float cm;

  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  duration = pulseIn (ECHO, HIGH);
  cm = duration / 58.0; 

  if (cm<30){
    return true;
  }
  else {
    return false;
  }
  delay(2000);
}
//기울기 초깃값 측정
void measureInitGradient() {
  const int xPin = 0;
  const int yPin = 1;
  const int zPin = 2;

  // 초기값 측정
  initialX = analogRead(xPin);
  initialY = analogRead(yPin);
  initialZ = analogRead(zPin);
}

// 기울기 측정 센서
void measureGradient() {
  const int xPin = 0;
  const int yPin = 1;
  const int zPin = 2;

  int minVal = 265;
  int maxVal = 402;

  double x;
  double y;
  double z;

  int xRead = analogRead(xPin);
  int yRead = analogRead(yPin);
  int zRead = analogRead(zPin);

  int xAng = map(xRead, minVal, maxVal, -90, 90);
  int yAng = map(yRead, minVal, maxVal, -90, 90);
  int zAng = map(zRead, minVal, maxVal, -90, 90);

  // 현재값과 초기값의 차이 계산
  int deltaX = xRead - initialX;
  int deltaY = yRead - initialY;
  int deltaZ = zRead - initialZ;

  x = RAD_TO_DEG * (atan2(-yAng, -zAng) + PI);
  y = RAD_TO_DEG * (atan2(-xAng, -zAng) + PI);
  z = RAD_TO_DEG * (atan2(-yAng, -xAng) + PI);

  // 변화량 출력
  Serial.print("Change in X: ");
  Serial.println(deltaX);
  Serial.print("Change in Y: ");
  Serial.println(deltaY);
  Serial.print("Change in Z: ");
  Serial.println(deltaZ);

  // 각도 출력
  Serial.print("X Angle: ");
  Serial.println(x);
  Serial.print("Y Angle: ");
  Serial.println(y);
  Serial.print("Z Angle: ");
  Serial.println(z);

  delay(1000);
}

// 위급상황 판단 함수
bool judgeEmergency(){
  measureGradient(); // 기울기 측정
  measureDistanceFromHuman(); // 사용자와의 거리 측정

  // 기울기나 거리가 일정 범위를 벗어나면 응급상황으로 간주
  if ((abs(x) > 60 || abs(y) > 60 || abs(z) > 60) || cm  30) {
    return true; // 응급상황
  } else {
    return false; // 정상 상태
  }
}

// 이동거리 측정
void measureDistance() {
  hall_value = digitalRead(hall);
  if (isMagnet == true) {
    if (hall_value == HIGH) {
      distance += PI * 2 * radius;
      isMagnet = false;
    }
  } else {
    if (hall_value == LOW) {
      isMagnet = true;
      //lastMovementTime = millis();
    }
  }
}

// // 로드셀 모듈로 체중값 읽어오기 
// void measureWeight() {
//   //일단 비워두기
// }

// 시리얼 모니터 출력 테스트용 
void ForTestSerialMonitor(){
    Serial.println("This is for test 12345...");
    delay(1000);
}