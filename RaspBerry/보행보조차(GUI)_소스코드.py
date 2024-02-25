# GUI import
import tkinter as tk
from threading import Thread
from tkinter import simpledialog
import time
from tkinter import messagebox

# 통신관련 import
import socket
import json
import asyncio
import websockets
import requests
import serial

# 보행보조차 관련 셋팅 -------------------------------------------------------------------------------------
port = 'COM9'  # 사용할 시리얼 포트 번호 (예: 'COM1', 'COM2' 등)
baudrate = 115200  # 보드레이트 설정
arduino_serial = serial.Serial(port, baudrate=baudrate, timeout=None)

travel_range = 0
tmp = 0
bpm = 0
rehabilityTimeSecond = 0
rehabilityTime = 0
rehabilityId = 0
oxygenSaturation = 0

stop_time = 0
rest_time = 0
button_state = 0

# 수신 정보
HOST = '192.168.50.202'  # 수신 ip : raspberrypi ip주소, 이게 라즈베리파이가 될 것임
PORT = 50538  # 수신 포트 번호 : 포트 번호는 50000이상이 사설 포트 !
SERVER_IP = 'http://192.168.50.202:8080'

# --------------------------------------------------------------------------------------------
def convert_seconds_to_minutes(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    if remaining_seconds > 0:
        minutes += 1
    return minutes
# --------------------------------------------------------------------------------------------
async def emergency_signal(rehabilitation_id):
    uri = SERVER_IP + "/api/fcm/emergency/" + str(rehabilitation_id)

    response = requests.post(uri, headers={"Content-Type" : "application/json"})

    if response.status_code == 200:
        print("안전사고 발생 신호가 성공적으로 전송되었습니다.")
    else:
        print(response.status_code)
# --------------------------------------------------------------------------------------------
async def call_signal(rehabilitation_id):
    uri = SERVER_IP + "/api/fcm/call/" + str(rehabilitation_id)

    response = requests.post(uri, headers={"Content-Type" : "application/json"})

    if response.status_code == 200:
        print("관리자 호출 신호가 성공적으로 전송되었습니다.")
    else:
        print(response.status_code)
# --------------------------------------------------------------------------------------------
async def biological_start_send_data(rehabilitation_id): # 재활 id
    uri = SERVER_IP + "/rehabilitations/" + str(rehabilitation_id) + "/start"  # POST 요청

    response = requests.post(uri, headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        print("첫번째 데이터가 성공적으로 전송되었습니다.")
    else:
        print(response.status_code)
# ---------------------------------------------------------------------------------------------
async def biological_end_send_data(rehabilitation_id, slope, travel_range, remaining_time): # 재활 id, bpm, 이동거리, 남은 시간
    uri = SERVER_IP + "/rehabilitations/" + str(rehabilitation_id) + "/end"  # POST 요청

    data = {'travelRange': travel_range,
            'slope' : slope,
            'remainingTime' : remaining_time
            }
    
    json_data = json.dumps(data)
    response = requests.post(uri, data=json_data, headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        print("마지막 데이터가 성공적으로 전송되었습니다.")
    else:
        print(response.status_code)

    print('마지막 데이터 전송 완료')
    print(data)
# ---------------------------------------------------------------------------------------------
async def biological_send_data(rehabilitation_id, bpm, oxygenSaturation, tmp): # 재활 id, bpm, 산소포화도, 체온
    uri = "ws://192.168.50.202:8080/ws/biometric"  # 웹소켓 서버의 주소 (예: "ws://localhost:8000")

    async with websockets.connect(uri) as websocket:

        # 전송할 데이터, 여기서 센서값 받기 메서드를 작성해야 할 수도..
        # message = str(rehabilityTimeSecond)
        data = {'rehabilitationId': rehabilitation_id,
               'oxygenSaturation': oxygenSaturation,
               'bpm': bpm,
               'temperature': tmp
                }
        
        print(data)
        
        message = json.dumps(data)
        
        # 데이터 전송
        await websocket.send(message)
        print('실시간 데이터 전송 완료')
# ---------------------------------------------------------------------------------------------
def main():
    global travel_range, slope, rehabilityTimeSecond, rehabilityTime, rehabilityId, rehabilitation_status, button_state # travelRange, slope(?)
    global bpm, tmp, oxygenSaturation # 생체 정보 
    global patient_id, remaining_time, distance, heart_beats, stop_time # GUI 변수

    def start_socket_communication():
        global rehabilityTime, rehabilityId, rehabilityTimeSecond, button_state, rest_time, bpm, travel_range
        breakTime = False

        while(True):
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((HOST, PORT))
            server_socket.listen(1)
            print('수신 대기 중...')

            client_socket, addr = server_socket.accept()
            print('관리자 스마트폰과 연결, 현재 보행보조차 IP:', addr)

            received_data = client_socket.recv(1024).decode('utf-8')
            data = json.loads(received_data)

            print('수신 데이터:', data)
            rehabilityTime = data['time']
            rehabilityId = data['rehabliltyId']
            update_patient_id() # 재활 아이디 바뀔 시 GUI의 재활 id 표시값 변경
            rehabilityTimeSecond = rehabilityTime * 60
            update_time() # 재활 시간 바뀔 시 GUI의 재활 시간 표시값 변경
            update_rehabilitation_status() # 재활중인지 아닌지
            arduino_serial.write(str(rehabilityTimeSecond).encode())

            client_socket.close()
            print("보행보조차 셋팅 완료, 일정거리 움직일 경우 재활 시작합니다.")

            while True:
                if arduino_serial.in_waiting != 0:
                    content = arduino_serial.readline().decode()
        
                    if 'start' in content:
                        break

            asyncio.run(biological_start_send_data(rehabilitation_id=rehabilityId))

            while True:
                if button_state == 0:
                    if arduino_serial.in_waiting != 0:

                        content = arduino_serial.readline().decode()

                        if '5seconds bpm' in content:
                            bpm = float(content[15:])

                        if '5seconds spo2' in content:
                            oxygenSaturation = float(content[16:])

                        if '5seconds tmp' in content:
                            tmp = float(content[15:])
                        
                        if 'distance' in content:
                            travel_range = float(content[11:]) # 거리

                        if 'human' in content:
                            asyncio.run(emergency_signal(rehabilitation_id=rehabilityId)) # FCM 요청
                            distance_raw = arduino_serial.readline().decode() # 추가로 FCM Message 서버로 요청
                            travel_range = float(distance_raw[11:]) # 거리
                            asyncio.run(biological_end_send_data(rehabilitation_id=rehabilityId, slope=0.01, travel_range=travel_range, remaining_time=int(convert_seconds_to_minutes(rehabilityTimeSecond)))) # 거리값 포함 재활 종료
                            rehabilityTimeSecond = 0
                            print("human stop")
                            messagebox.showinfo("재활 종료", "사람이 넘어지는 안전사고 발생, 재활을 종료합니다.")
                            break

                        if 'car' in content:
                            asyncio.run(emergency_signal(rehabilitation_id=rehabilityId)) # FCM 요청
                            distance_raw = arduino_serial.readline().decode() # 추가로 FCM Message 서버로 요청
                            travel_range = float(distance_raw[11:]) # 거리
                            asyncio.run(biological_end_send_data(rehabilitation_id=rehabilityId, slope=0.01, travel_range=travel_range, remaining_time=int(convert_seconds_to_minutes(rehabilityTimeSecond)))) # 거리값 포함 재활 종료
                            rehabilityTimeSecond = 0
                            print("car stop")
                            messagebox.showinfo("재활 종료", "차량과 사람이 함께 넘어지는 안전사고 발생, 재활을 종료합니다.")
                            break

                        if 'nomal' in content:
                            distance_raw = arduino_serial.readline().decode() # 재활 정상 종료
                            travel_range = float(distance_raw[11:]) # 거리
                            asyncio.run(biological_end_send_data(rehabilitation_id=rehabilityId, slope=0.01, travel_range=travel_range, remaining_time=0)) # 거리값 포함 재활 종료
                            rehabilityTimeSecond = 0
                            print("nomal stop")
                            messagebox.showinfo("재활 종료", "정상적으로 재활이 종료되었습니다.")
                            break

                        if 'start break' in content:
                            print("재활 휴식 시작")
                            messagebox.showinfo("재활 휴식 시작", "의자에 앉으셨습니다. 재활을 중지합니다.")
                            while True:
                                if arduino_serial.in_waiting != 0:
                                    content = arduino_serial.readline().decode()

                                    if 'stop' in content:
                                        distance_raw = arduino_serial.readline().decode() 
                                        travel_range = float(distance_raw[11:]) # 거리
                                        asyncio.run(biological_end_send_data(rehabilitation_id=rehabilityId, slope=0.01, travel_range=travel_range, remaining_time=int(convert_seconds_to_minutes(rehabilityTimeSecond)))) # 거리값 포함 재활 종료
                                        print("재활 종료")
                                        messagebox.showinfo("재활 종료", "시간이 오래 경과되었으므로 재활을 종료합니다.")
                                        breakTime = True
                                        rehabilityTimeSecond = 0
                                        break

                                    if 'end break' in content:
                                        print("재활 휴식 종료")

                                        content = arduino_serial.readline().decode()
                                        if '5seconds bpm' in content:
                                            bpm = float(content[15:])
                                            print(bpm)
                                            
                                        break
                        
                        if (breakTime == True):
                            break
                        
                        content = arduino_serial.readline().decode()

                        if '5seconds bpm' in content:
                            bpm = float(content[15:])

                        if '5seconds spo2' in content:
                            oxygenSaturation = float(content[16:])

                        if '5seconds tmp' in content:
                            tmp = float(content[15:])
                            
                        if 'distance' in content:
                            travel_range = float(content[11:]) # 거리

                        if 'human' in content:
                            asyncio.run(emergency_signal(rehabilitation_id=rehabilityId)) # FCM 요청
                            distance_raw = arduino_serial.readline().decode() # 추가로 FCM Message 서버로 요청
                            travel_range = float(distance_raw[11:]) # 거리
                            asyncio.run(biological_end_send_data(rehabilitation_id=rehabilityId, slope=0.01, travel_range=travel_range, remaining_time=int(convert_seconds_to_minutes(rehabilityTimeSecond)))) # 거리값 포함 재활 종료
                            rehabilityTimeSecond = 0
                            print("human stop")
                            messagebox.showinfo("재활 종료", "사람이 넘어지는 안전사고 발생, 재활을 종료합니다.")
                            break

                        if 'car' in content:
                            asyncio.run(emergency_signal(rehabilitation_id=rehabilityId)) # FCM 요청
                            distance_raw = arduino_serial.readline().decode() # 추가로 FCM Message 서버로 요청
                            travel_range = float(distance_raw[11:]) # 거리
                            asyncio.run(biological_end_send_data(rehabilitation_id=rehabilityId, slope=0.01, travel_range=travel_range, remaining_time=int(convert_seconds_to_minutes(rehabilityTimeSecond)))) # 거리값 포함 재활 종료
                            rehabilityTimeSecond = 0
                            print("car stop")
                            messagebox.showinfo("재활 종료", "차량과 사람이 함께 넘어지는 안전사고 발생, 재활을 종료합니다.")
                            break

                        if 'nomal' in content:
                            distance_raw = arduino_serial.readline().decode() # 재활 정상 종료
                            travel_range = float(distance_raw[11:]) # 거리
                            asyncio.run(biological_end_send_data(rehabilitation_id=rehabilityId, slope=0.01, travel_range=travel_range, remaining_time=int(convert_seconds_to_minutes(rehabilityTimeSecond)))) # 거리값 포함 재활 종료
                            rehabilityTimeSecond = 0
                            print("nomal stop")
                            messagebox.showinfo("재활 종료", "정상적으로 재활이 종료되었습니다.")
                            break

                        content = arduino_serial.readline().decode()

                        if '5seconds bpm' in content:
                            bpm = float(content[15:])

                        if '5seconds spo2' in content:
                            oxygenSaturation = float(content[16:])

                        if '5seconds tmp' in content:
                            tmp = float(content[15:])

                        if 'distance' in content:
                            travel_range = float(content[11:]) # 거리

                        if 'human' in content:
                            asyncio.run(emergency_signal(rehabilitation_id=rehabilityId)) # FCM 요청
                            distance_raw = arduino_serial.readline().decode() # 추가로 FCM Message 서버로 요청
                            travel_range = float(distance_raw[11:]) # 거리
                            asyncio.run(biological_end_send_data(rehabilitation_id=rehabilityId, slope=0.01, travel_range=travel_range, remaining_time=int(convert_seconds_to_minutes(rehabilityTimeSecond)))) # 거리값 포함 재활 종료
                            rehabilityTimeSecond = 0
                            print("human stop")
                            messagebox.showinfo("재활 종료", "사람이 넘어지는 안전사고 발생, 재활을 종료합니다.")
                            break

                        if 'car' in content:
                            asyncio.run(emergency_signal(rehabilitation_id=rehabilityId)) # FCM 요청
                            distance_raw = arduino_serial.readline().decode() # 추가로 FCM Message 서버로 요청
                            travel_range = float(distance_raw[11:]) # 거리
                            asyncio.run(biological_end_send_data(rehabilitation_id=rehabilityId, slope=0.01, travel_range=travel_range, remaining_time=int(convert_seconds_to_minutes(rehabilityTimeSecond)))) # 거리값 포함 재활 종료
                            rehabilityTimeSecond = 0
                            print("car stop")
                            messagebox.showinfo("재활 종료", "차량과 사람이 함께 넘어지는 안전사고 발생, 재활을 종료합니다.")
                            break

                        if 'nomal' in content:
                            distance_raw = arduino_serial.readline().decode() # 재활 정상 종료
                            travel_range = float(distance_raw[11:]) # 거리
                            asyncio.run(biological_end_send_data(rehabilitation_id=rehabilityId, slope=0.01, travel_range=travel_range, remaining_time=int(convert_seconds_to_minutes(rehabilityTimeSecond)))) # 거리값 포함 재활 종료
                            rehabilityTimeSecond = 0
                            print("nomal stop")
                            messagebox.showinfo("재활 종료", "정상적으로 재활이 종료되었습니다.")
                            break
                        
                        content = arduino_serial.readline().decode()

                        if '5seconds bpm' in content:
                            bpm = float(content[15:])

                        if '5seconds spo2' in content:
                            oxygenSaturation = float(content[16:])

                        if '5seconds tmp' in content:
                            tmp = float(content[15:])

                        if 'distance' in content:
                            travel_range = float(content[11:]) # 거리

                        if 'human' in content:
                            asyncio.run(emergency_signal(rehabilitation_id=rehabilityId)) # FCM 요청
                            distance_raw = arduino_serial.readline().decode() # 추가로 FCM Message 서버로 요청
                            travel_range = float(distance_raw[11:]) # 거리
                            asyncio.run(biological_end_send_data(rehabilitation_id=rehabilityId, slope=0.01, travel_range=travel_range, remaining_time=int(convert_seconds_to_minutes(rehabilityTimeSecond)))) # 거리값 포함 재활 종료
                            rehabilityTimeSecond = 0
                            print("human stop")
                            messagebox.showinfo("재활 종료", "사람이 넘어지는 안전사고 발생, 재활을 종료합니다.")
                            break

                        if 'car' in content:
                            asyncio.run(emergency_signal(rehabilitation_id=rehabilityId)) # FCM 요청
                            distance_raw = arduino_serial.readline().decode() # 추가로 FCM Message 서버로 요청
                            travel_range = float(distance_raw[11:]) # 거리
                            asyncio.run(biological_end_send_data(rehabilitation_id=rehabilityId, slope=0.01, travel_range=travel_range, remaining_time=int(convert_seconds_to_minutes(rehabilityTimeSecond)))) # 거리값 포함 재활 종료
                            rehabilityTimeSecond = 0
                            print("car stop")
                            messagebox.showinfo("재활 종료", "차량과 사람이 함께 넘어지는 안전사고 발생, 재활을 종료합니다.")
                            break

                        if 'nomal' in content:
                            distance_raw = arduino_serial.readline().decode() # 재활 정상 종료
                            travel_range = float(distance_raw[11:]) # 거리
                            asyncio.run(biological_end_send_data(rehabilitation_id=rehabilityId, slope=0.01, travel_range=travel_range, remaining_time=int(convert_seconds_to_minutes(rehabilityTimeSecond)))) # 거리값 포함 재활 종료
                            rehabilityTimeSecond = 0
                            print("nomal stop")
                            messagebox.showinfo("재활 종료", "정상적으로 재활이 종료되었습니다.")
                            break

                        asyncio.run(biological_send_data(
                            rehabilitation_id=rehabilityId,
                            tmp=tmp,
                            bpm=bpm,
                            oxygenSaturation=oxygenSaturation,
                        ))

                        update_bpm() # GUI bpm 변경
                        update_distance() # GUI distance 변경
                        rehabilityTimeSecond -= 5
                        print(rehabilityTimeSecond)
                        update_time() # 재활 시간 바뀔 시 GUI의 재활 시간 표시값 변경


                else:
                    arduino_serial.write(b'p') # 아두이노에 'p' 전송해서 멈추기
                    content = arduino_serial.readline().decode()
                    print(content) # 아두이노에서 전송하는 doctor call stop
                    distance_raw = arduino_serial.readline().decode() # 재활 정상 종료
                    travel_range = float(distance_raw[11:]) # 거리
                
                    # asyncio.run(biological_end_send_data(
                    #     rehabilitation_id=rehabilityId, 
                    #     slope=0.01, 
                    #     travel_range=travel_range, 
                    #     remaining_time=int(convert_seconds_to_minutes(rehabilityTimeSecond)))) # 거리값 포함 재활 종료
                    
                    while(button_state == 1):
                        time.sleep(1) # 1초 증가
                        rest_time += 1
                        if (rest_time == 30): # 관리자 호출 후 30 될 경우 재활 종료, 일단 테스트용이므로 
                            print("재활 종료")
                            rehabilityTimeSecond = 0
                            break

                    if(rest_time == 30): # 관리자 호출 후 30초가 될 경우 재활 종료
                        rehabilityTimeSecond = 0 # 재활 루프 탈출
                        button_state = 0
                        action_button.config(text="관리자 호출", bg=BUTTON_COLOR)
                        messagebox.showinfo("재활 종료", "관리자 호출 후 시간이 오래 지났으므로 재활을 종료합니다.")
                        break
                    else: # 만약 시간 내로 다시 재활 재개를 누를 경우 남은시간 만큼 재활 재시작
                        # asyncio.run(biological_start_send_data(rehabilitation_id=rehabilityId))
                        # arduino_serial.write(str(rehabilityTimeSecond).encode()) # 남은 시간 전송
                        # print(rehabilityTimeSecond)
                        rest_time = 0 # rest_time 초기화
                        content = arduino_serial.readline().decode()
                        print(content)

                if (rehabilityTimeSecond <= 0):
                    button_state = 0
                    print("재활 종료")

                    asyncio.run(biological_end_send_data(
                        rehabilitation_id=rehabilityId, 
                        slope=0.01, 
                        travel_range=travel_range, 
                        remaining_time=int(convert_seconds_to_minutes(rehabilityTimeSecond)))) # 거리값 포함 재활 종료
                    break
            
            rehabilityId = 0
            rehabilityTimeSecond = 0
            bpm = 0
            travel_range = 0
            tmp = 0
            breakTime = False

            # GUI 변수 변경
            update_patient_id()
            update_bpm()
            update_distance()
            update_time()
            update_rehabilitation_status() # 재활중인지 아닌지

    # --------------------------------------------------- 아래부터 GUI -------------------------------------------------------
    win = tk.Tk()
    win.geometry("800x480+0+0")
    win.title("Sliver Fox")

    # GUI 변수
    rehabilitation_status = True
    patient_id_gui = tk.IntVar()
    remaining_time_gui = tk.IntVar()
    distance_gui = tk.DoubleVar()
    bpm_gui = tk.DoubleVar()
    rehabilitation_status_gui = tk.StringVar()
    # 정적 변수
    patient_id_gui_text = tk.StringVar()
    time_gui_text = tk.StringVar()
    bpm_gui_text = tk.StringVar()
    distance_gui_text = tk.StringVar()
    
    # 단위 변수
    time_gui_text_2 = tk.StringVar()
    bpm_gui_text_2 = tk.StringVar()
    distance_gui_text_2 = tk.StringVar()

    win.resizable(False,False)

    run_thread = Thread(target=start_socket_communication) # 멀티쓰레드로 소켓 통신중
    run_thread.daemon = True
    run_thread.start()

    # 추가 안건 : 보행보조차 자동 등록 시스템 및 선택한 보행보조차 재활 셋팅
    # 보행보조차 스마트폰 

    BUTTON_COLOR = "#4CAF50"
    BUTTON_ACTIVE_COLOR = "#45a049"
    BACKGROUND_COLOR = "#f2f2f2"
    TEXT_COLOR = "#333333"
    LABEL_FONT = ('Helvetica', 20)
    # BUTTON_FONT = ('Helvetica', 16)
    win.configure(background=BACKGROUND_COLOR)

    def ask_passcode():
        global rehabilityId, travel_range, rehabilityTimeSecond
        if (rehabilityId != 0):
            password = simpledialog.askstring("Password", "Enter password:", show='*')
            if password == rehabilityId:
                rehabilityTimeSecond = 0
                end_rehabilitation(rehabilityId=rehabilityId, slope=0.1, travelRange=travel_range, remainingTime=rehabilityTimeSecond)# 재활 중지
            else:
                print("비밀번호가 틀렸습니다")
        else:
            print("재활 설정이 되지 않았습니다.")
            messagebox.showerror("경고", "재활 설정이 필요합니다.")

    def send_start_signal(rehabilitationId): # 재활 시작 신호
        global rehabilitation_status, button_state
        rehabilitation_status = True
        button_state = 0
        action_button.config(text="관리자 호출", bg="orange")
        print("재활 시작 신호를 보냈습니다.")
        asyncio.run(biological_start_send_data(rehabilitation_id=rehabilitationId))

    def end_rehabilitation(rehabilityId, travelRange, remainingTime, slope): # 재활 종료 신호
        asyncio.run(biological_end_send_data(rehabilitation_id=rehabilityId, travel_range=travelRange, remaining_time=remainingTime, slope=slope))
    
    def button_command():
        # 관리자 호출 과정 -> 관리자 호출 버튼 -> 아두이노에 'p' 신호 송신 (아두이노에서는 시간 초기화 및 재입력 대기) -> FCM ->
        # -> 60초 동안 버튼 안누를 경우 재활 종료, 재활 재개 버튼 누를 경우 아두이노에 시간초값 전송 -> 3m 이동 후 재활 재개 
        # 파훼 방법 : 아두이노는 시간 값을 초기화 하지않고 대기, 재활 재개 판단시 start 메시지 라즈베리 파이로 입력
        # 라즈베리 파이는 60초 전까지 start 메시지를 받지 않으면 재활 종료라 판단하기
        global button_state, travelRange, rehabilityTimeSecond, rehabilityId, rehabilityTimeSecond, bpm, temp, oxygenSaturation
        global arduino_serial

        if rehabilityId != 0:
            if button_state == 0:
                asyncio.run(call_signal(rehabilitation_id=rehabilityId)) # 스마트폰에 알림 송신
                button_state = 1
                action_button.config(text="재활 재개", bg="orange")

            elif button_state == 1:
                # send_start_signal(rehabilitationId=rehabilityId)  # 재활 재개 신호를 보냄
                arduino_serial.write(str(rehabilityTimeSecond).encode()) # 아두이노에 남은 시간 전송해서 재활 마무리 하기
                button_state = 0
                action_button.config(text="관리자 호출", bg=BUTTON_COLOR)
        else:
            print("재활 설정이 되지 않았습니다.")
            messagebox.showerror("경고", "재활 설정이 필요합니다.")

    # 값 변화시 GUI 변수 변화
    def update_patient_id(*args):
        global rehabilityId
        patient_id_gui.set(rehabilityId) # patient_id GUI 변수의 변화가 발생할 경우 

    def update_bpm(*args):
        global bpm
        bpm_gui.set(bpm) # bpm GUI 변수의 변화가 발생할 경우 

    def update_distance(*args):
        global travel_range
        distance_gui.set(travel_range) # bpm GUI 변수의 변화가 발생할 경우 

    def update_time(*args):
        global rehabilityTimeSecond
        remaining_time_gui.set(rehabilityTimeSecond) # bpm GUI 변수의 변화가 발생할 경우 update_rehabilitation_status

    def update_rehabilitation_status(*args):
        global rehabilityId
        if (rehabilityId != 0):
            rehabilitation_status_gui.set("재활 중")
            rehabilitation_status_label.config(bg=BUTTON_ACTIVE_COLOR)
        else:
            rehabilitation_status_gui.set("재활 전")
            rehabilitation_status_label.config(bg="red")

    # 시작/종료 버튼
    action_button = tk.Button(win, text="관리자 호출", command=button_command, bg=BUTTON_COLOR, activebackground=BUTTON_ACTIVE_COLOR, bd=0, relief="groove", width=10, height=2)
    end_button = tk.Button(win, text = "재활 종료",command=ask_passcode, activebackground="darkred", bd=0, relief="solid", background=BUTTON_COLOR, width=10, height=2)

    # GUI 초기 변수 설정을 해 주어야 한다
    patient_id_gui.set(0)
    distance_gui.set(0)
    bpm_gui.set(0)
    remaining_time_gui.set(0)
    rehabilitation_status_gui.set("재활 전")

    patient_id_gui_text.set("환자 ID : ")
    time_gui_text.set("남은 시간 : ")
    bpm_gui_text.set("심박 수 : ")
    distance_gui_text.set("이동 거리 : ")

    time_gui_text_2.set("Second")
    bpm_gui_text_2.set("BPM")
    distance_gui_text_2.set("m")

    # 동적 레이블
    id_label = tk.Label(win, textvariable=patient_id_gui, font=LABEL_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
    time_label = tk.Label(win, textvariable=remaining_time_gui, font=LABEL_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
    distance_label = tk.Label(win, textvariable=distance_gui, font=LABEL_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
    heart_beats_label = tk.Label(win, textvariable=bpm_gui, font=LABEL_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
    rehabilitation_status_label = tk.Label(win, textvariable=rehabilitation_status_gui, font=LABEL_FONT, bg="red", fg=TEXT_COLOR)
    # 고정 레이블
    id_text = tk.Label(win, textvariable=patient_id_gui_text, font=LABEL_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
    time_text = tk.Label(win, textvariable=time_gui_text, font=LABEL_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
    heart_beats_text = tk.Label(win, textvariable=bpm_gui_text, font=LABEL_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
    distance_text = tk.Label(win, textvariable=distance_gui_text, font=LABEL_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)

    time_text_2 = tk.Label(win, textvariable=time_gui_text_2, font=LABEL_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
    heart_beats_text_2 = tk.Label(win, textvariable=bpm_gui_text_2, font=LABEL_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
    distance_text_2 = tk.Label(win, textvariable=distance_gui_text_2, font=LABEL_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
    # 레이블 및 버튼 배치
    # 재활 ID
    id_text.place(x=50, y=50)
    id_label.place(x=200, y=50)
    # 남은 시간
    time_text.place(x=50, y=150)
    time_label.place(x=200, y=150) 
    time_text_2.place(x=300, y=150)
    # 심박수
    heart_beats_text.place(x=50, y=250)
    heart_beats_label.place(x=200, y=250) 
    heart_beats_text_2.place(x=300, y=250)
    # 이동 거리
    distance_text.place(x=50, y=350)
    distance_label.place(x=200, y=350)
    distance_text_2.place(x=300, y=350)
    # 버튼
    end_button.place(x=600, y=50)
    action_button.place(x=600, y=150)
    rehabilitation_status_label.place(x=600, y=250)
    # 라벨 값 변화 감지 및 수정
    patient_id_gui.trace("w", update_patient_id)
    bpm_gui.trace("w", update_bpm)
    distance_gui.trace("w", update_distance)
    remaining_time_gui.trace("w", update_time)
    rehabilitation_status_gui.trace("w", update_rehabilitation_status)

    win.mainloop()

if __name__ == "__main__":
    main()