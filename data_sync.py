import requests
import csv
import pymysql
import mysql.connector
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

class 資料庫:     
    def __init__(self):         
        self.conn = mysql.connector.connect(             
            host='localhost',             
            port=3306,             
            user='root',             
            password='oneokrock12345',  # 替換為實際密碼             
            database='heart rate monitor'  # 替換為您的資料庫名稱         
        )         
        self.cursor = self.conn.cursor()  

    def insert_blood_records(self, 資料):  # 確保方法名稱正確
        # 檢查時間戳記是否已存在
        查詢查詢 = "SELECT COUNT(*) FROM blood_records WHERE `時間戳記` = %s"
        self.cursor.execute(查詢查詢, (資料[0],))
        result = self.cursor.fetchone()

        # 如果時間戳記已存在，跳過插入
        if result[0] > 0:
            print(f"時間戳記 {資料[0]} 已存在，跳過此行資料插入。")
            return

        # 如果時間戳記不存在，則插入資料
        插入查詢 = """     
        INSERT INTO blood_records (         
            `時間戳記`, `舒張壓`, `收縮壓`, `血糖`, `膽固醇`, `脈搏`,         
            `舒張壓狀態`, `收縮壓狀態`, `血糖狀態`, `膽固醇狀態`, `脈搏狀態`,         
            `舒張壓正常`, `收縮壓正常`, `血糖正常`, `膽固醇正常`, `脈搏正常`     
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)     
        """          

        # 執行插入語句     
        self.cursor.execute(插入查詢, 資料)     
        self.conn.commit()

    def 關閉(self):
        self.cursor.close()
        self.conn.close()

def 判斷狀態(值, 正常範圍):
    if 正常範圍[0] <= 值 <= 正常範圍[1]:
        return "正常", 1
    else:
        return "異常", 0

def 安全浮點數(值):
    try:
        return float(值)
    except (ValueError, TypeError):
        return None

def 安全整數(值):
    try:
        return int(值)
    except (ValueError, TypeError):
        return None

def 轉換時間戳記(時間戳):
    try:
        時間戳 = 時間戳.replace('上午', 'AM').replace('下午', 'PM')
        return datetime.strptime(時間戳, "%Y/%m/%d %p %I:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        print(f"無效的時間戳格式: {時間戳}")
        return None

def 取得血液記錄CSV():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT4lrpABu1Cfv5Ow4fWrNzJj-FdEGxpaJA-O82pEdtRut2RbLnJLzUwWjftBv2TR9I2joZJVq8a9c0c/pub?output=csv"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"下載 CSV 失敗，狀態碼: {response.status_code}")
        return []

    csv_content = response.content.decode('utf-8')
    reader = csv.reader(csv_content.splitlines())
    next(reader)  # 跳過表頭

    資料 = []
    for row in reader:
        if len(row) >= 6:
            時間戳記 = 轉換時間戳記(row[0].strip())
            舒張壓 = 安全整數(row[1].strip())
            收縮壓 = 安全整數(row[2].strip())
            血糖 = 安全浮點數(row[3].strip())
            膽固醇 = 安全浮點數(row[4].strip())
            脈搏 = 安全整數(row[5].strip())

            if None in [舒張壓, 收縮壓, 血糖, 膽固醇, 脈搏, 時間戳記]:
                continue

            舒張壓狀態, 舒張壓正常 = 判斷狀態(舒張壓, (60, 80))
            收縮壓狀態, 收縮壓正常 = 判斷狀態(收縮壓, (90, 120))
            血糖狀態, 血糖正常 = 判斷狀態(血糖, (70, 100))
            膽固醇狀態, 膽固醇正常 = 判斷狀態(膽固醇, (0, 200))
            脈搏狀態, 脈搏正常 = 判斷狀態(脈搏, (60, 100))

            資料.append((
                時間戳記, 舒張壓, 收縮壓, 血糖, 膽固醇, 脈搏,
                舒張壓狀態, 收縮壓狀態, 血糖狀態, 膽固醇狀態, 脈搏狀態,
                舒張壓正常, 收縮壓正常, 血糖正常, 膽固醇正常, 脈搏正常
            ))

    return 資料

def convert_to_mysql_datetime(date_str):
    if not date_str:
        return None
    time_pattern = '%Y/%m/%d 上午 %I:%M:%S' 
    if '下午' in date_str:
        time_pattern = '%Y/%m/%d 下午 %I:%M:%S'
    return datetime.strptime(date_str, time_pattern).strftime('%Y-%m-%d %H:%M:%S')

def convert_normal_abnormal(value):
    if value == '0':
        return 0
    elif value == '1':
        return 1
    else:
        print(f"未知值: {value}")
        return None

def is_valid_row(row):
    return all(field for field in row[:3])

def get_heart_rate_csv_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSULVwFdSh9_HuIJe1dWPae-jzcQYsyYb5DuRfXHtDenUlr1oSYTRcVIbvmt_7qJ/pub?output=csv"
    response = requests.get(url)
    csv_content = response.content.decode('utf-8')

    csv_file = csv.reader(csv_content.splitlines())
    next(csv_file)  # 跳過標題行
    data = [row for row in csv_file]

    return data

def save_heart_rate_to_mysql(data):
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor', charset='utf8mb4')
        cursor = conn.cursor()

        cursor.execute('DELETE FROM heart_rate;')
        
        for row in data:
            if all(not cell for cell in row):
                continue
            
            row[0] = convert_to_mysql_datetime(row[0])
            row[3] = convert_normal_abnormal(row[3])
            
            try:
                cursor.execute(
                    """INSERT INTO heart_rate (時間戳記, 心跳, 心跳狀態, 心跳_正常_異常) 
                    VALUES (%s, %s, %s, %s)""",
                    (row[0], row[1], row[2], row[3])
                )
            except Exception as e:
                print(f"插入行時出錯: {e}, 行: {row}")
        
        conn.commit()
        conn.close()
        print("心跳數據同步成功")

    except Exception as e:
        print('心跳資料庫連線失敗: ', e)

def get_dht11_csv_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5C_o47POhPXTZEgq40budOJB1ygTTZx9D_086I-ZbHfApFPZB_Ra5Xi09Qu6hxzk9_QXJ-7-QFoKD/pub?output=csv"
    response = requests.get(url)
    csv_content = response.content.decode('utf-8')

    csv_file = csv.reader(csv_content.splitlines())
    next(csv_file)  # 跳過標題行
    data = [row for row in csv_file]

    return data

def save_dht11_to_mysql(data):
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor', charset='utf8mb4')
        cursor = conn.cursor()

        cursor.execute('DELETE FROM dht11;')
        
        for row in data:
            if not is_valid_row(row):
                print(f"跳過無效行: {row}")
                continue
            
            row[0] = convert_to_mysql_datetime(row[0])
            
            row[5] = convert_normal_abnormal(row[5])
            row[6] = convert_normal_abnormal(row[6])
            row[9] = convert_normal_abnormal(row[9])
            
            row = [0 if v is None else v for v in row]
            
            try:
                cursor.execute(
                    """INSERT INTO dht11 (時間戳記, 溫度, 濕度, 溫度狀態, 濕度狀態, 溫度_正常_異常, 濕度_正常_異常, 體溫, 體溫狀態, 體溫_正常_異常) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
                )
            except Exception as e:
                print(f"插入行時出錯: {e}, 行: {row}")
        
        conn.commit()
        conn.close()
        print("DHT11數據同步成功")

    except Exception as e:
        print('DHT11資料庫連線失敗: ', e)

def get_bmi_csv_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTbj3f0rhEu2aCljm1AgkPiaqU7XLGfLUfmL_3NVClYABWXmarViEg1RSE4Q9St0YG_rR74VZyNh7MF/pub?output=csv"
    response = requests.get(url)
    csv_content = response.content.decode('utf-8')

    csv_file = csv.reader(csv_content.splitlines())
    next(csv_file)  # 跳過標題行
    data = [row for row in csv_file]

    return data

def save_bmi_to_mysql(data):
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor', charset='utf8mb4')
        cursor = conn.cursor()

        cursor.execute('DELETE FROM bmi;')
        
        for row in data:
            if all(not cell for cell in row):
                continue
            
            row[0] = convert_to_mysql_datetime(row[0])
            row[9] = convert_normal_abnormal(row[9])
            
            try:
                cursor.execute(
                    """INSERT INTO bmi (時間戳記, 姓名, 性別, 身高, 體重, BMI, 標準體重, 檢查結果, 正常_異常) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[9])
                )
            except Exception as e:
                print(f"插入行時出錯: {e}, 行: {row}")
        
        conn.commit()
        conn.close()
        print("BMI數據同步成功")

    except Exception as e:
        print('BMI資料庫連線失敗: ', e)

def save_blood_records_to_mysql(資料):
    try:
        db = 資料庫()
        for row in 資料:
            db.insert_blood_records(row)
        db.關閉()
        print("血液記錄同步成功")
    except Exception as e:
        print(f'血液記錄資料庫連線失敗: {e}')

def update_data():
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: 開始更新資料...')
    
    # 更新心跳數據
    heart_rate_data = get_heart_rate_csv_data()
    save_heart_rate_to_mysql(heart_rate_data)
    
    # 更新DHT11數據
    dht11_data = get_dht11_csv_data()
    save_dht11_to_mysql(dht11_data)
    
    # 更新BMI數據
    bmi_data = get_bmi_csv_data()
    save_bmi_to_mysql(bmi_data)
    
    # 更新血液記錄
    blood_records_data = 取得血液記錄CSV()
    save_blood_records_to_mysql(blood_records_data)
    
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: 更新資料完成')

def connect_and_sync():
    update_data()  # 立即執行一次數據更新
    
    scheduler = BackgroundScheduler(timezone="Asia/Taipei")
    scheduler.add_job(update_data, 'interval', seconds=30)
    scheduler.start()
    
    print("連接成功，數據同步已啟動")
    
    

    



