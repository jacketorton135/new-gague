import requests
import csv
import sqlite3
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import time

# 將日期時間格式轉換為 SQLite DATETIME 格式
def convert_to_sqlite_datetime(date_str):
    if not date_str:
        return None
    time_pattern = '%Y/%m/%d 上午 %I:%M:%S'  # 設定上午時間模式
    if '下午' in date_str:
        time_pattern = '%Y/%m/%d 下午 %I:%M:%S'  # 設定下午時間模式
    return datetime.strptime(date_str, time_pattern).strftime('%Y-%m-%d %H:%M:%S')  # 轉換並格式化時間

# 轉換正常/異常為 0/1
def convert_normal_abnormal(value):
    if value == '0':
        return 0  # 正常值轉換為0
    elif value == '1':
        return 1  # 異常值轉換為1
    else:
        print(f"未知值: {value}")  # 打印未知值
        return None  # 返回None，或者其他適當的預設值，例如 -1

# 檢查數據行是否有空值
def is_valid_row(row):
    return all(field for field in row[:3])  # 檢查前3個字段 (時間戳記, 溫度, 濕度) 是否有值

# 插入心跳數據到 SQLite 資料庫
def save_heart_rate_to_sqlite(data):
    try:
        conn = sqlite3.connect('heartrate.db')
        cursor = conn.cursor()

        # 清空心跳表格數據（可選）
        cursor.execute('DELETE FROM heart_rate;')
        
        for row in data:
            # 調試信息：打印每一行數據
            print(f"Inserting row: {row}")

            # 跳過空行
            if all(not cell for cell in row):
                continue
            
            # 轉換日期時間格式
            row[0] = convert_to_sqlite_datetime(row[0])
            
            # 轉換正常/異常值
            row[3] = convert_normal_abnormal(row[3])
            
            # 插入數據
            try:
                cursor.execute(
                    """INSERT INTO heart_rate (時間戳記, 心跳, 心跳狀態, 心跳_正常_異常) 
                    VALUES (?, ?, ?, ?)""",
                    (row[0], row[1], row[2], row[3])
                )
            except Exception as e:
                print(f"插入行時出錯: {e}, 行: {row}")
        
        conn.commit()
        conn.close()
        print("心跳數據同步成功")

    except Exception as e:
        print('心跳資料庫連線失敗: ', e)

# 獲取心跳 CSV 數據
def get_heart_rate_csv_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSULVwFdSh9_HuIJe1dWPae-jzcQYsyYb5DuRfXHtDenUlr1oSYTRr-AQ-aMthcCsNRTcVIbvmt_7qJ/pub?output=csv"
    response = requests.get(url)
    csv_content = response.content.decode('utf-8')

    csv_file = csv.reader(csv_content.splitlines())
    header = next(csv_file)  # 跳過標題行
    data = [row for row in csv_file]  # 讀取數據行

    return data

# 插入DHT11數據到 SQLite 資料庫
def save_dht11_to_sqlite(data):
    try:
        conn = sqlite3.connect('heartrate.db')
        cursor = conn.cursor()

        # 清空DHT11表格數據（可選）
        cursor.execute('DELETE FROM dht11;')
        
        for row in data:
            if not is_valid_row(row):
                print(f"跳過無效行: {row}")
                continue
            
            # 調試信息：打印每一行數據
            print(f"Inserting row: {row}")
            
            # 轉換日期時間格式
            row[0] = convert_to_sqlite_datetime(row[0])
            
            # 轉換正常/異常值
            row[5] = convert_normal_abnormal(row[5])
            row[6] = convert_normal_abnormal(row[6])
            row[9] = convert_normal_abnormal(row[9])
            
            # 檢查是否有 None 值並設置為默認值（例如 0）
            row = [0 if v is None else v for v in row]
            
            # 插入數據
            try:
                cursor.execute(
                    """INSERT INTO dht11 (時間戳記, 溫度, 濕度, 溫度狀態, 濕度狀態, 溫度_正常_異常, 濕度_正常_異常, 體溫, 體溫狀態, 體溫_正常_異常) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
                )
            except Exception as e:
                print(f"插入行時出錯: {e}, 行: {row}")
        
        conn.commit()
        conn.close()
        print("DHT11數據同步成功")

    except Exception as e:
        print('DHT11資料庫連線失敗: ', e)

# 獲取DHT11 CSV 數據
def get_dht11_csv_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5C_o47POhPXTZEgq40budOJB1ygTTZx9D_086I-ZbHfApFPZB_Ra5Xi09Qu6hxzk9_QXJ-7-QFoKD/pub?output=csv"
    response = requests.get(url)
    csv_content = response.content.decode('utf-8')

    csv_file = csv.reader(csv_content.splitlines())
    header = next(csv_file)  # 跳過標題行
    data = [row for row in csv_file]  # 讀取數據行

    return data

# 插入BMI數據到 SQLite 資料庫
def save_bmi_to_sqlite(data):
    try:
        conn = sqlite3.connect('heartrate.db')
        cursor = conn.cursor()

        # 清空BMI表格數據（可選）
        cursor.execute('DELETE FROM bmi;')
        
        for row in data:
            # 調試信息：打印每一行數據
            print(f"Inserting row: {row}")

            # 跳過空行
            if all(not cell for cell in row):
                continue
            
            # 轉換日期時間格式
            row[0] = convert_to_sqlite_datetime(row[0])
            
            # 轉換正常/異常值
            row[9] = convert_normal_abnormal(row[9])
            
            # 插入數據
            try:
                cursor.execute(
                    """INSERT INTO bmi (時間戳記, 姓名, 性別, 身高, 體重, BMI, 標準體重, 檢查結果, 正常_異常) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[9])
                )
            except Exception as e:
                print(f"插入行時出錯: {e}, 行: {row}")
        
        conn.commit()
        conn.close()
        print("BMI數據同步成功")

    except Exception as e:
        print('BMI資料庫連線失敗: ', e)

# 獲取BMI CSV 數據
def get_bmi_csv_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTbj3f0rhEu2aCljm1AgkPiaqU7XLGfLUfmL_3NVClYABWXmarViEg1RSE4Q9St0YG_rR74VZyNh7MF/pub?output=csv"
    response = requests.get(url)
    csv_content = response.content.decode('utf-8')

    csv_file = csv.reader(csv_content.splitlines())
    header = next(csv_file)  # 跳過標題行
    data = [row for row in csv_file]  # 讀取數據行

    return data

# 更新所有數據的主程序
def update_data():
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: 開始更新資料...')
    
    # 更新心跳數據
    heart_rate_data = get_heart_rate_csv_data()
    save_heart_rate_to_sqlite(heart_rate_data)
    
    # 更新DHT11數據
    dht11_data = get_dht11_csv_data()
    save_dht11_to_sqlite(dht11_data)
    
    # 更新BMI數據
    bmi_data = get_bmi_csv_data()
    save_bmi_to_sqlite(bmi_data)
    
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: 更新資料完成')

def connect_and_sync():
    update_data()  # 立即執行一次數據更新
    
    scheduler = BackgroundScheduler(timezone="Asia/Taipei")
    scheduler.add_job(update_data, 'interval', seconds=30)
    scheduler.start()
    
    print("連接成功，數據同步已啟動")

if __name__ == "__main__":
    connect_and_sync()

    


