# 작성자: 마승욱
# 작성일: 2024년 2월 27일
# Silverfox 보행보조차 제어부에서 사용되는 함수들을 모아놓은 파일입니다.

# 오늘치 workout 데이터에 today_weight의 값이 있으면 True, 없으면 False
def isThereTodayWeight(mycursor, mydb):
    mycursor.execute("SELECT today_weight FROM workout WHERE today_weight = 0.0 AND date=CURDATE()")
    myresult = mycursor.fetchall()
    if myresult:
        return True
    else:
        return False

# 오늘치 workout 데이터에 distance의 값이 있으면 True, 없으면 False
def isThereTodayDistance(mycursor, mydb):
    mycursor.execute("SELECT today_distance FROM workout WHERE today_distance = 0.0 AND date=CURDATE()")
    myresult = mycursor.fetchall()
    if myresult:
        return True
    else:
        return False
    
# 오늘치 workout 데이터에 time의 값이 있으면 True, 없으면 False
def isThereTodayTime(mycursor, mydb):
    mycursor.execute("SELECT today_time FROM workout WHERE today_time = 00:00:00 AND date=CURDATE()")
    myresult = mycursor.fetchall()
    if myresult:
        return True
    else:
        return False

# 오늘치 workout 데이터가 있으면 True, 없으면 False
def isThereTodayWorkout(mycursor, mydb):
    mycursor.execute("SELECT * FROM workout WHERE date=CURDATE()")
    myresult = mycursor.fetchall()
    if myresult:
        return True
    else:
        return False
    

# 긴급 상황시 보호자 스마트폰으로 위치정보 송신
async def emergencyCall(mycursor, mydb, phone_number):
    mycursor.execute("SELECT * FROM user WHERE phone_number = %s", (phone_number,))
    myresult = mycursor.fetchall()
    if myresult:
        return True
    else:
        return False
    
