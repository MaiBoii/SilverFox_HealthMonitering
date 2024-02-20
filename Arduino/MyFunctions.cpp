// MyFunctions.cpp
// 함수의 구현 부분을 작성한 파일입니다.
#include "MyFunctions.h"
#include "MyVariables.h"
#include <TinyGPS.h>
#include <SoftwareSerial.h>
#include <Arduino.h>

#define BUZZER_PIN 9 // 스피커에 연결된 핀 번호

// GPS 수신기 객체 및 시리얼 통신 객체 생성
SoftwareSerial ss(RXPin, TXPin);
TinyGPS gps;

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

// 기울기 센서 핀 초기화
const int TXPin = 12;
const int RXPin = 11;

// 보행보조차 기울기 관련 변수 초기화
const int xPin = A3;  
const int yPin = A2;  
const int zPin = A1;  
int xRead, yRead, zRead;
int minVal = 265;
int maxVal = 402;
int xAng, yAng, zAng;
int x, y, z;

// 사람과의 거리 측정 관련 변수 초기화
long duration;
float cm;

void GpsReceiver() {
  // GPS 데이터 수신 및 처리
  while (ss.available() > 0) {
    char c = ss.read();
    if (gps.encode(c)) {
      // 위치 정보가 업데이트되었을 때, 정보 출력
      float latitude, longitude;
      unsigned long fix_age;
      gps.f_get_position(&latitude, &longitude, &fix_age);
      Serial.print("위도: ");
      Serial.print(latitude, 6);
      Serial.print(" 경도: ");
      Serial.println(longitude, 6);
    }
  }

  // 1초마다 반복
  delay(1000);
}

// 사람과의 거리 측정 함수
void measureDistanceFromHuman() {
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  duration = pulseIn (ECHO, HIGH);
  cm = duration / 58.0; 
}

//응급상황시 스피커 재생 함수
void musicStart() {
  for (int i = 0; i < sizeof(melody) / sizeof(melody[0]); i++) {
    int noteDuration = 1000 / noteDurations[i];
    tone(BUZZER_PIN, melody[i], noteDuration);

    int pauseBetweenNotes = noteDuration * 1.30;
    delay(pauseBetweenNotes);
    noTone(BUZZER_PIN);
  }

  delay(2000); // 다음 반복을 위한 딜레이
}

// 기울기 측정 함수
void measureGradient() {
  int minVal = 1023;
  int maxVal = 0;

  // x, y, z 축에서의 아날로그 값 읽기
  xRead = analogRead(xPin);
  yRead = analogRead(yPin);
  zRead = analogRead(zPin);

  // 최소값과 최대값 업데이트
  if (xRead < minVal) minVal = xRead;
  if (xRead > maxVal) maxVal = xRead;
  if (yRead < minVal) minVal = yRead;
  if (yRead > maxVal) maxVal = yRead;
  if (zRead < minVal) minVal = zRead;
  if (zRead > maxVal) maxVal = zRead;

  // x, y, z 축의 각도 계산
  xAng = map(xRead, minVal, maxVal, -90, 90);
  yAng = map(yRead, minVal, maxVal, -90, 90);
  zAng = map(zRead, minVal, maxVal, -90, 90);

  // 각도를 토대로 기울기 계산
  x = int(RAD_TO_DEG * (atan2(-yAng, -zAng) + PI)); //ziro x
  y = int(RAD_TO_DEG * (atan2(-xAng, -zAng) + PI)); //ziro y
  z = int(RAD_TO_DEG * (atan2(-yAng, -xAng) + PI)); //ziro z
}

// // 위급상황 판단 함수
// bool judgeEmergency(){
//   measureGradient(); // 기울기 측정
//   measureDistanceFromHuman(); // 사용자와의 거리 측정

//   // 기울기나 거리가 일정 범위를 벗어나면 응급상황으로 간주
//   if ((abs(x) > 60 || abs(y) > 60 || abs(z) > 60) || cm  30) {
//     return true; // 응급상황
//   } else {
//     return false; // 정상 상태
//   }
// }

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

// 로드셀 모듈로 체중값 읽어오기 
void measureWeight() {
  //일단 비워두기
}

// 시리얼 모니터 출력 테스트용 
void ForTestSerialMonitor(){
    Serial.println("This is for test 12345...");
    delay(1000);
}