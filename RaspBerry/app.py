import serial
import os
import time
import json
from dotenv import load_dotenv
import mysql.connector

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
        # 만약 시리얼 데이터가 "HumanDistance Over"라면
        if 'HumanDistance' in serial_data:
            sql = "INSERT INTO test (distance) VALUES (1.0)"
            mycursor.execute(sql)
            mydb.commit()
            print(mycursor.rowcount, "record inserted.")

if __name__ == "__main__":
    main()