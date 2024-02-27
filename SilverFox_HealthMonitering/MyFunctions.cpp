// MyFunctions.cpp
// 함수의 구현 부분을 작성한 파일입니다.
#include "MyFunctions.h"
#include "MyVariables.h"
#include <TinyGPS.h>
#include <SoftwareSerial.h>
#include <Arduino.h>
#include "HX711.h"

#define BUZZER_PIN 9 // 스피커에 연결된 핀 번호
#define DOUT  5  // HX711 DT 핀을 아두이노의 5번 핀에 연결합니다.
#define SCK  4   // HX711 SCK 핀을 아두이노의 4번 핀에 연결합니다.

// GPS 수신기 객체 및 시리얼 통신 객체 생성
//SoftwareSerial ss(RXPin, TXPin);
TinyGPS gps;

// HX711 객체 생성
HX711 scale;

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

  //만일 사람이 30cm 이상 기기로부터 멀어졌을 경우
  if (cm>30){
    return true;
  }
  else {
    return false;
  }
}

int initialX = 0;
int initialY = 0;
int initialZ = 0;

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
bool measureGradient() {
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

  // 모듈이 60도 이상 기울어졌을 경우
  if ((deltaX > 60) || (deltaY > 60) || (deltaZ > 60)){
    return true;
  }
  else{
    return false;
  }
}

// 위급상황 판단 함수
// 30초마다 확인하고, 둘 다 true를 반환하면 위급 상황으로 간주하는 함수
bool checkEmergencySituation() {
  // 이전 시간을 저장하기 위한 변수
  static unsigned long previousTime = 0;
  // 30초 간격을 설정
  const unsigned long interval = 3000; // milliseconds

  // 현재 시간을 가져옴
  unsigned long currentTime = millis();

  // 30초가 지났는지 확인
  if (currentTime - previousTime >= interval) {
    // 이전 시간을 현재 시간으로 업데이트
    previousTime = currentTime;

    // 거리 측정 함수 호출
    bool distanceFromHuman = measureDistanceFromHuman();
    // 기울기 측정 함수 호출
    bool gradientDetected = measureGradient();

    // 둘 다 true를 반환하면 위급 상황으로 판단
    if (distanceFromHuman && gradientDetected) {
      // 위급 상황으로 간주하고 true 반환
      return true;
    }
  }
  // 위급 상황이 아니라면 false 반환
  return false;
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

// 로드셀 모듈로 체중값 읽어오기 
void measureWeight() {
  // 로드셀에서 값을 읽습니다.
  float weight = scale.get_units(50); // 10번의 샘플링 후 평균값을 사용합니다.
  if (weight > 30) { //측정된 무게가 30kg 이상이면
    Serial.print("{'Weight': ");
    Serial.print(weight, 2); // 소수점 두 자리까지 출력합니다.
    Serial.println("}");
  }
  delay(1000); // 1초 대기 후 다음 측정을 수행합니다.
}

// 시리얼 모니터 출력 테스트용 
void ForTestSerialMonitor(){
    Serial.println("This is for test 12345...");
    delay(1000);
}