# import serial

# ser = serial.Serial('/dev/cu.usbmodem11301', 9600)

# while True:
#     print(ser.readline().strip().decode('utf-8'))

import os
from dotenv import load_dotenv

# .env 파일로부터 환경 변수 로드
load_dotenv()

# 환경 변수 사용 예시
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")

print(f"DB Host: {db_host}")
print(f"DB User: {db_user}")
print(f"DB Password: {db_pass}")
