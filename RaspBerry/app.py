import serial
import os
import time
import json
from dotenv import load_dotenv
import mysql.connector
import MyFunctions
import asyncio

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
    ser = serial.Serial(ser_port, ser_baud)
    serial_data = ser.readline().strip().decode('utf-8')
    while True:
        if 'Weight' in serial_data:
        #workout 테이블의 오늘치 데이터에 today_weight의 값이 0.0일시에만 데이터를 입력
        #오늘치 데이터가 없으면 입력
            if MyFunctions.isThereTodayWeight(mycursor, mydb):
                print('오늘치 데이터가 없습니다.')
                print('데이터를 입력합니다.')
                #serial_data를 json으로 변환
                serial_data = json.loads(serial_data)
                #serial_data의 Weight값을 today_weight에 입력
                sql = "UPDATE workout SET today_weight = %s WHERE today_weight = 0.0 AND date = CURDATE()"
                val = (serial_data['Weight'],)
                mycursor.execute(sql, val)
                mydb.commit()
                print(mycursor.rowcount, "record(s) affected")
                print('데이터 입력 완료')
                break
            else:
                #오늘치 데이터가 있으면 지금 측정한 데이터와 평균값으로 수정
                print('오늘치 데이터가 있습니다.')
                print('데이터를 수정합니다.')
                #serial_data를 json으로 변환
                serial_data = json.loads(serial_data)
                #serial_data의 Weight값을 today_weight에 입력
                sql = "UPDATE workout SET today_weight = %s WHERE date = CURDATE()"
                val = (serial_data['Weight'],)
                mycursor.execute(sql, val)
                mydb.commit()
                print(mycursor.rowcount, "record(s) affected")
                print('데이터 수정 완료')
                break
        elif 'Distance' in serial_data:
        #workout 테이블의 오늘치 데이터에 today_distance의 값이 0.0일시에만 데이터를 입력
           if MyFunctions.isThereTodayDistance(mycursor, mydb):
                print('오늘치 데이터가 없습니다.')
                print('데이터를 입력합니다.')
                #serial_data를 json으로 변환
                serial_data = json.loads(serial_data)
                #serial_data의 Distance값을 today_distance에 입력
                sql = "UPDATE workout SET today_distance = %s WHERE today_distance = 0.0 AND date = CURDATE()"
                val = (serial_data['Distance'],)
                mycursor.execute(sql, val)
                mydb.commit()
                print(mycursor.rowcount, "record(s) affected")
                print('데이터 입력 완료')
                break
           
        #
      
if __name__ == "__main__":
    main()