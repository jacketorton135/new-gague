import requests 
import csv 
import mysql.connector 
from datetime import datetime  

# 設定 MySQL 連接 
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

    def insert_data(self, 資料):  # 確保方法名稱正確
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


# 其餘代碼保持不變...

# 插入資料時調用 insert_data 方


# 定義狀態判斷邏輯
def 判斷狀態(值, 正常範圍):
    if 正常範圍[0] <= 值 <= 正常範圍[1]:
        return "正常", 1  # 返回「正常」和數字 1（位元值）
    else:
        return "異常", 0  # 返回「異常」和數字 0（位元值）

# 檢查是否為有效數值，返回數值或 None
def 安全浮點數(值):
    try:
        return float(值)
    except ValueError:
        return None  # 如果無法轉換，返回 None

def 安全整數(值):
    try:
        return int(值)
    except ValueError:
        return None  # 如果無法轉換，返回 None

# 轉換時間戳記格式，處理「上午」和「下午」
def 轉換時間戳記(時間戳):
    try:
        # 將「上午」和「下午」轉換為 24 小時制格式
        時間戳 = 時間戳.replace('上午', 'AM').replace('下午', 'PM')
        return datetime.strptime(時間戳, "%Y/%m/%d %p %I:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        print(f"無效的時間戳格式: {時間戳}")
        return None  # 如果格式不匹配，返回 None

# Google Sheets CSV 連結
# Google Sheets CSV 連結 
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT4lrpABu1Cfv5Ow4fWrNzJj-FdEGxpaJA-O82pEdtRut2RbLnJLzUwWjftBv2TR9I2joZJVq8a9c0c/pub?output=csv"  

# 下載 CSV 文件 
response = requests.get(url) 
if response.status_code == 200:     
    print("CSV 文件下載成功") 
else:     
    print(f"下載 CSV 失敗，狀態碼: {response.status_code}")     
    exit()  # 如果下載失敗，停止程式執行

csv_content = response.content.decode('utf-8')  

# 解析 CSV 文件 
reader = csv.reader(csv_content.splitlines()) 
header = next(reader)  # 跳過表頭  

資料 = []  # 確保在這裡初始化資料列表

# 處理每一行資料 
for row in reader:     
    print(f"處理這一行: {row}")  # 打印每一行     
    if len(row) >= 6:  # 確保每一行有足夠的資料         
        時間戳記 = 轉換時間戳記(row[0].strip())  # 轉換時間戳格式         
        舒張壓 = 安全整數(row[1].strip())  # 假設舒張壓在第2列         
        收縮壓 = 安全整數(row[2].strip())  # 假設收縮壓在第3列         
        血糖 = 安全浮點數(row[3].strip())  # 假設血糖在第4列         
        膽固醇 = 安全浮點數(row[4].strip())  # 假設膽固醇在第5列         
        脈搏 = 安全整數(row[5].strip())  # 假設脈搏在第6列          

        # 如果遇到空值或無效資料，跳過該行         
        if None in [舒張壓, 收縮壓, 血糖, 膽固醇, 脈搏, 時間戳記]:             
            print(f"跳過無效行: {row}")  # 打印跳過的行             
            continue          

        # 設定各項指標的正常範圍並獲得對應的狀態         
        舒張壓狀態, 舒張壓正常 = 判斷狀態(舒張壓, (60, 80))  
        收縮壓狀態, 收縮壓正常 = 判斷狀態(收縮壓, (90, 120))  
        血糖狀態, 血糖正常 = 判斷狀態(血糖, (70, 100))  
        膽固醇狀態, 膽固醇正常 = 判斷狀態(膽固醇, (0, 200))  
        脈搏狀態, 脈搏正常 = 判斷狀態(脈搏, (60, 100))  

        # 準備插入 MySQL 的資料         
        資料.append((             
            時間戳記, 舒張壓, 收縮壓, 血糖, 膽固醇, 脈搏,             
            舒張壓狀態, 收縮壓狀態, 血糖狀態, 膽固醇狀態, 脈搏狀態,             
            舒張壓正常, 收縮壓正常, 血糖正常, 膽固醇正常, 脈搏正常         
        ))  

# 檢查資料是否有被添加進來 
print(f"總共要插入的行數: {len(資料)}")  

# 初始化資料庫連接 
db = 資料庫()  

# 插入資料 
for row in 資料:     
    print(f"插入這一行: {row}")  # 打印即將插入的資料     
    db.insert_data(row)  

# 關閉資料庫連接 
db.關閉()