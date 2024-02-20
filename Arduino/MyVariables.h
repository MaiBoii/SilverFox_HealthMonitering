// MyVariables.h
// 변수 선언만 따로 모아놓은 헤더 파일입니다.
#ifndef MY_VARIABLES_H
#define MY_VARIABLES_H

#include <SoftwareSerial.h>
#include <Arduino.h>

// 초음파 센서 핀 설정
#define TRIG 3 //TRIG 핀 설정(초음파 보내는 핀)
#define ECHO 2 //ECHO 핀 설정(초음파 받는 핀)

#define BUZZER_PIN 9 // 스피커에 연결된 핀 번호

//테스트용 반짝반짝 작은별
#define NOTE_C4  262
#define NOTE_D4  294
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_G4  392
#define NOTE_A4  440
#define NOTE_B4  494
#define NOTE_C5  523

// 외부에서 초기화된 melody와 noteDurations 배열에 대한 선언만 해야 합니다.
extern int melody[];
extern int noteDurations[];

// 나머지 전역 변수들은 선언만 하고 초기화는 cpp 파일에서 해야 합니다.

extern SoftwareSerial ss;

// 이동거리(재활거리) 관련 변수
extern int hall;  // 홀센서 핀번호
extern int hall_value; // 홀센서로 감지한 값(LOW : 자석이 감지됨, HIGH : 자석이 감지되지 않음)
extern float radius; // 바퀴 반지름 : 9.1cm
extern float distance; // 환자의 이동거리
extern bool isMagnet; // 자석 감지 상태를 유지하기 위한 변수
//extern unsigned long lastMovementTime = 0; // 바퀴가 마지막으로 움직인 시각

// 보행보조차 기울기 관련 변수
extern const int xPin;
extern const int yPin;
extern const int zPin;
extern int xRead, yRead, zRead;
extern int minVal;
extern int maxVal;
extern int xAng, yAng, zAng;
extern int x, y, z;

// 사람과의 거리 측정 관련 변수
extern long duration;
extern float cm;

// 체중 측정 관련 변수
extern const int loadcellDout;
extern const int loadcellSck;
extern float weight;

//GPS 위치 정보 관련 변수 
// GPS 모듈과 연결된 핀 설정
extern const int RXPin;
extern const int TXPin;
extern const uint32_t GPSBaud;

#endif
