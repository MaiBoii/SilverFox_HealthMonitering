"""
구현해야하는 기능들 
1. 시리얼 통신으로 받은 TodayWeight, workout_time, distance 데이터를 데이터베이스에 저장
2. 시리얼 통신으로 받은 위치정보 실시간으로 전역변수 location에 저장
3. 긴급 상황시 보호자 스마트폰으로 가장 최근의 위치정보 송신

"""


import serial
import os
import json
from dotenv import load_dotenv
import mysql.connector
import MyFunctions

# .env 파일로부터 환경 변수 로드
load_dotenv()

# 데이터베이스 관련 환경 변수 로드
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")

# MySQL 서버에 연결
mydb = mysql.connector.connect(
  host = db_host,
  user = db_user,
  password = db_pass,
  database = db_name
)

# 연결이 성공하면 'Connected!'를 출력
if mydb.is_connected():
  print('Connected with '+ db_name +' database!')

# 데이터베이스에서 쿼리를 실행하는 커서 객체 생성
mycursor = mydb.cursor()

# 시리얼 통신 관련 환경 변수 로드
ser_port = os.getenv("SER_PORT")
ser_baud = os.getenv("SER_BAUD")

def main():
    # 실시간으로 바뀌는 위치정보를 담는 전역변수 
    ser = serial.Serial(ser_port, ser_baud)
    serial_data = ser.readline().strip().decode('utf-8')
    while True:
        #실시간으로 바뀌는 위치정보를 담는 전역변수 선언
        global location

        #시리얼 통신으로 받은 데이터가 'Weight'일 경우
        if 'Weight' in serial_data:
            if MyFunctions.isThereTodayWeight(mycursor, mydb):
                print('오늘치 데이터가 없습니다.\n데이터를 입력합니다.')
                #serial_data를 json으로 변환
                serial_data = json.loads(serial_data)
                #serial_data의 Weight값을 today_weight에 입력
                sql = "UPDATE workout SET today_weight = %s WHERE today_weight = 0.0 AND date = CURDATE()"
                val = (serial_data['Weight'],)
                mycursor.execute(sql, val)
                mydb.commit()
                print('데이터 입력 완료')
                break
            else:
                #오늘치 데이터가 있으면 지금 측정한 데이터와 평균값으로 수정
                print('오늘치 데이터가 있습니다.\n데이터를 수정합니다.')
                #serial_data를 json으로 변환
                serial_data = json.loads(serial_data)
                #serial_data의 Weight값을 today_weight에 입력
                sql = "UPDATE workout SET today_weight = %s WHERE date = CURDATE()"
                val = (serial_data['Weight'],)
                mycursor.execute(sql, val)
                mydb.commit()
                print('데이터 수정 완료')
                break
        
        #시리얼 통신으로 받은 데이터가 Distance일 경우
        elif 'Distance' in serial_data:
           if MyFunctions.isThereTodayDistance(mycursor, mydb):
                print('오늘치 데이터가 없습니다.\n데이터를 입력합니다.')
                #serial_data를 json으로 변환
                serial_data = json.loads(serial_data)
                #serial_data의 Distance값을 today_distance에 입력
                sql = "UPDATE workout SET today_distance = %s WHERE today_distance = 0.0 AND date = CURDATE()"
                val = (serial_data['Distance'],)
                mycursor.execute(sql, val)
                mydb.commit()
                print('데이터 입력 완료')
                break
           
        #실시간으로 갱신되는 위치정보를 시리얼 통신으로 받아오는 코드
        elif 'Location' in serial_data:
            print('위치정보를 갱신합니다.')
            serial_data = json.loads(serial_data)
            location = serial_data['Location']
            break
           
        #긴급 상황시 보호자 스마트폰으로 위치정보 송신
        elif 'Emergency' in serial_data:
            print('긴급 상황입니다.\n보호자 스마트폰으로 위치정보를 송신합니다.')
            MyFunctions.emergencyCall(mycursor, mydb, '010-1234-5678')
            break
    
if __name__ == "__main__":
    main()