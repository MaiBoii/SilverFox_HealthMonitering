// MyFunctions.h
// 함수 선언만 모아놓은 헤더 파일입니다.
#ifndef MY_FUNCTIONS_H
#define MY_FUNCTIONS_H

void musicStart(); //시작 음악 함수
void ForTestSerialMonitor(); //시리얼 모니터 테스트용 함수

void measureGradient(); //기울기 측정 함수
void measureDistanceFromHuman(); //사람과의 거리 측정 함수
void measureDistance(); //이동거리 측정 함수
void GpsReceiver(); //GPS 정보 수신 함수
//bool judgeEmergency(); //긴급상황 판단 함수
void measureWeight() //체중 측정 함수

//void saveWeightToDatabase(float weight) //체중 데이터베이스에 저장 함수
//void saveDistanceToDatabase(float distance) //이동거리 데이터베이스에 저장 함수
#endif