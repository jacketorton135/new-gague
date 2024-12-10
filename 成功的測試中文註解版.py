import tkinter as tk  # 匯入 tkinter 模組，用於創建圖形用戶界面
from tkinter import ttk  # 匯入 tkinter 的 ttk 模組，用於創建改進的 GUI 元件
from datetime import datetime  # 匯入 datetime 模組，用於處理日期和時間
import pymysql  # 匯入 pymysql 模組，用於操作 MySQL 資料庫
import io  # 匯入 io 模組，用於處理 I/O 操作
from PIL import Image, ImageTk, ImageOps, ImageDraw  # 匯入 PIL 模組，用於圖像處理
import matplotlib.pyplot as plt  # 匯入 matplotlib 的 pyplot 模組，用於創建圖表
import numpy as np  # 匯入 numpy 模組，用於數據處理
import webbrowser  # 匯入 webbrowser 模組，用於開啟網頁
import requests  # 匯入 requests 模組，用於發送 HTTP 請求
import csv  # 匯入 csv 模組，用於處理 CSV 文件
from apscheduler.schedulers.background import BackgroundScheduler  # 匯入 apscheduler 模組，用於定時任務調度
import time  # 匯入 time 模組，用於時間處理
import os  # 匯入 os 模組，用於操作系統功能
import matplotlib.dates as mdates  # 匯入 matplotlib.dates 模組，用於處理日期格式
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # 匯入 matplotlib 的 tkinter 背後繪圖畫布模組
from matplotlib.patches import Wedge  # 匯入 matplotlib 的 Wedge 類別，用於繪製圓形扇形
from matplotlib.animation import FuncAnimation  # 匯入 matplotlib 的 FuncAnimation 類別，用於創建動畫
from data_sync import connect_and_sync  # 從 data_sync 模組匯入 connect_and_sync 函數
from 合併搜尋 import UnifiedHealthApp

from tkinterweb import HtmlFrame
import subprocess

def start_data_sync():
    connect_and_sync()  # 呼叫 connect_and_sync 函數進行數據同步
    button = tk.Button(button_frame, text="連線", command=connect_and_sync)  # 創建一個按鈕，點擊時進行數據同步
    print("數據同步已啟動")  # 在控制台打印數據同步啟動的消息


def open_webview():
    # 使用 PyWebView 開啟嵌入的網頁
    webbrowser.open('嵌入網頁', 'https://9ffea55d-e78d-470b-b56c-c9b2bbe836c1-00-3bgh7eg56lmo3.pike.replit.dev/')
    webview.start()
def open_merge_search():
    # 使用 subprocess 執行合併搜尋.py
    subprocess.run(["python", "合併搜尋.py"])
def generate_qr_code(data, filename="linebotchat.png"):
    qr = qrcode.QRCode(
        version=1,  # 設定 QR 碼的版本
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 設定錯誤糾正級別
        box_size=5,  # 設定每個框的像素大小
        border=4,  # 設定邊框的框數
    )
    qr.add_data(data)  # 添加數據到 QR 碼中
    qr.make(fit=True)  # 使 QR 碼適應數據大小
    img = qr.make_image(fill_color="black", back_color="white")  # 生成 QR 碼圖像，設置前景色和背景色
    img.save(filename)  # 將 QR 碼圖像保存到指定文件

def open_qr_code():
    filename = "F:\\物聯網123\\視覺化\\linebotchat.png"  # 指定 QR 碼圖像的文件名
    if not os.path.exists(filename):  # 如果文件不存在
        generate_qr_code("https://example.com", filename)  # 生成 QR 碼圖像
    os.startfile(filename)  # 在 Windows 系統中打開文件



# GUI 函數
def create_gauge_image(current_value, min_value=0, max_value=50):
    fig, ax = plt.subplots(figsize=(2.5, 2), subplot_kw={'projection': 'polar'})  # 創建極坐標系的圖形和軸
    current_value = max(min_value, min(current_value, max_value))  # 限制當前值在最小值和最大值之間
    ax.set_thetamin(0)  # 設定極坐標的最小角度
    ax.set_thetamax(180)  # 設定極坐標的最大角度
    ax.set_ylim(0, 1)  # 設定極坐標的半徑範圍
    ax.set_yticks([])  # 隱藏 y 軸刻度
    ax.set_xticks([])  # 隱藏 x 軸刻度
    colors = ["#2bad4e", "#eff229", "#f25829"]  # 定義顏色列表
    colors_text = ["LOW", "Normal", "HIGH"]  # 定義顏色對應的文字
    bounds = np.linspace(0, np.pi, len(colors) + 1)  # 計算顏色區間的角度範圍
    for i in range(len(colors)):  # 遍歷每種顏色
        ax.fill_between(np.linspace(bounds[i], bounds[i+1], 100), 0.6, 1, color=colors[i], alpha=0.3)  # 填充顏色區域
        mid_angle = (bounds[i] + bounds[i+1]) / 2  # 計算顏色區域的中間角度
        ax.text(mid_angle, 0.8, colors_text[i], ha='center', va='center', fontsize=10, color='black')  # 在顏色區域中間添加文字
    value_angle = np.interp(current_value, [min_value, max_value], [0, np.pi])  # 計算當前值對應的角度
    ax.plot([value_angle, value_angle], [0, 0.5], color='black', linewidth=2)  # 繪製指針
    ax.text(0, -0.2, f"IoT sensor Level\nValue = {current_value:.2f}", ha='center', va='center')  # 添加當前值的文字說明
    buf = io.BytesIO()  # 創建內存中的緩衝區
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)  # 保存圖形到緩衝區
    buf.seek(0)  # 重置緩衝區的位置
    plt.close(fig)  # 關閉圖形
    return Image.open(buf)  # 返回圖像對象

def create_circle_image(color, radius=20):
    fig, ax = plt.subplots(figsize=(2*radius/100, 2*radius/100), dpi=100)  # 創建一個圖形和軸，設置大小和解析度
    ax.add_patch(plt.Circle((0.5, 0.5), 0.5, color=color))  # 添加圓形補丁到圖形中
    ax.set_xlim(0, 1)  # 設定 x 軸的範圍
    ax.set_ylim(0, 1)  # 設定 y 軸的範圍
    ax.axis('off')  # 隱藏坐標軸
    buf = io.BytesIO()  # 創建內存中的緩衝區
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)  # 保存圖形到緩衝區
    buf.seek(0)  # 重置緩衝區的位置
    plt.close(fig)  # 關閉圖形
    image = Image.open(buf)  # 打開圖像對象
    image = ImageOps.fit(image, (radius*2, radius*2), centering=(0.5, 0.5))  # 裁剪圖像為圓形
    mask = Image.new('L', (radius*2, radius*2), 0)  # 創建一個新的黑色蒙版圖像
    draw = ImageDraw.Draw(mask)  # 創建繪圖對象
    draw.ellipse((0, 0, radius*2, radius*2), fill=255)  # 在蒙版上繪製白色圓形
    image.putalpha(mask)  # 將蒙版應用到圖像上
    return image  # 返回圖像對象

def show_current_time():
    current_time = datetime.now().strftime("系統時間:%Y-%m-%d %H:%M:%S")  # 獲取當前時間並格式化
    time_label.config(text=current_time)  # 更新時間標籤的文本
    main_window.after(1000, show_current_time)  # 每秒調用一次 show_current_time 函數

def toggle_treeview():
    if treeview_frame.winfo_viewable():  # 如果 treeview_frame 可見
        treeview_frame.pack_forget()  # 隱藏 treeview_frame
    else:
        treeview_frame.pack(fill=tk.BOTH, expand=True)  # 顯示 treeview_frame，並擴展以填充父容器
        load_data_from_db()  # 從資料庫加載數據
def load_data_from_db():
    # 連接到 MySQL 數據庫，提供連接的主機、端口、用戶名、密碼和數據庫名稱
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor')
    cursor = conn.cursor()  # 創建游標以執行 SQL 查詢

    # 清除 tree 中的所有子項目
    for item in tree.get_children():
        tree.delete(item)

    # 定義要查詢的表格名稱
    tables = ['heart_rate', 'dht11', 'bmi','blood_records']
    table_structures = {}  # 存儲表格結構
    time_columns = {}  # 存儲每個表格的時間戳記列名稱

    # 遍歷每個表格，檢查其結構並找到時間戳記列
    for table in tables:
        cursor.execute(f"DESCRIBE {table}")  # 查詢表格的結構
        columns = cursor.fetchall()  # 獲取表格的列名
        table_structures[table] = [row[0] for row in columns]  # 存儲列名

        # 假設時間戳記列的名稱包含 "時間" 或 "time"，遍歷表格列名來尋找時間戳記列
        time_column = next((col[0] for col in columns if '時間' in col[0].lower() or 'time' in col[0].lower()), None)
        if time_column:
            time_columns[table] = time_column  # 找到時間戳記列，保存到 time_columns
        else:
            print(f"Warning: No time column found in table {table}")  # 如果沒有找到時間戳記列，顯示警告

    # 輸出每個表格的結構和時間戳記列
    print("Table structures:", table_structures)
    print("Time columns:", time_columns)

    # 確保我們找到了所有表格所需的時間戳記列
    if len(time_columns) != len(tables):
        raise ValueError("Could not find time columns for all tables")  # 如果缺少時間戳記列，則拋出異常

    # 編寫查詢語句，從不同表格中選取異常數據，並且按照時間戳記排序
    query = f"""
    SELECT * FROM (
        SELECT 
            hr.{time_columns['heart_rate']} as timestamp,  -- 選取心跳表的時間戳記列
            '心跳' as field_name, hr.心跳 as value, hr.心跳狀態 as status
        FROM 
            heart_rate hr
        WHERE 
            hr.心跳狀態 != '心跳正常'  -- 篩選出心跳狀態不正常的數據
        UNION
        SELECT 
            d.{time_columns['dht11']} as timestamp,  -- 選取 DHT11 表的時間戳記列
            '溫度' as field_name, d.溫度 as value, d.溫度狀態 as status
        FROM 
            dht11 d
        WHERE 
            d.溫度狀態 != '溫度正常'  -- 篩選出溫度不正常的數據
        UNION
        SELECT 
            d.{time_columns['dht11']} as timestamp,  -- 選取 DHT11 表的時間戳記列
            '濕度' as field_name, d.濕度 as value, d.濕度狀態 as status
        FROM 
            dht11 d
        WHERE 
            d.濕度狀態 != '濕度正常'  -- 篩選出濕度不正常的數據
        UNION
        SELECT 
            d.{time_columns['dht11']} as timestamp,  -- 選取 DHT11 表的時間戳記列
            '體溫' as field_name, d.體溫 as value, d.體溫狀態 as status
        FROM 
            dht11 d
        WHERE 
            d.體溫狀態 != '體溫正常'  -- 篩選出體溫不正常的數據
        UNION
        SELECT 
            b.{time_columns['bmi']} as timestamp,  -- 選取 BMI 表的時間戳記列
            'BMI' as field_name, b.BMI as value, b.檢查結果 as status
        FROM 
            bmi b
        WHERE 
            b.檢查結果 IN ('體重過輕', '過重', '輕度肥胖', '重度肥胖')  -- 篩選出 BMI 不正常的數據
                UNION
    SELECT 
        b.{time_columns['blood_records']} as timestamp, 
        '舒張壓' as field_name, 
        b.舒張壓 as value, 
        b.舒張壓狀態 as status
    FROM blood_records b
    WHERE b.舒張壓狀態 != '正常'
    UNION
    SELECT 
        b.{time_columns['blood_records']} as timestamp, 
        '收縮壓' as field_name, 
        b.收縮壓 as value, 
        b.收縮壓狀態 as status
    FROM blood_records b
    WHERE b.收縮壓狀態 != '正常'
    UNION
    SELECT 
        b.{time_columns['blood_records']} as timestamp, 
        '血糖' as field_name, 
        b.血糖 as value, 
        b.血糖狀態 as status
    FROM blood_records b
    WHERE b.血糖狀態 != '正常'
    UNION
    SELECT 
        b.{time_columns['blood_records']} as timestamp, 
        '膽固醇' as field_name, 
        b.膽固醇 as value, 
        b.膽固醇狀態 as status
    FROM blood_records b
    WHERE b.膽固醇狀態 != '正常'
    UNION
    SELECT 
        b.{time_columns['blood_records']} as timestamp, 
        '脈搏' as field_name, 
        b.脈搏 as value, 
        b.脈搏狀態 as status
    FROM blood_records b
    WHERE b.脈搏狀態 != '正常'
    ) AS combined_data
    ORDER BY timestamp DESC  -- 根據時間戳記進行降序排列
    """

    # 輸出生成的 SQL 查詢語句
    print("Generated query:", query)

    try:
        # 執行查詢
        cursor.execute(query)
        abnormal_data = cursor.fetchall()  # 獲取查詢結果

        # 將異常數據逐行插入到 tree 控件中
        for row in abnormal_data:
            timestamp, field_name, value, status = row
            tree.insert("", "end", values=(timestamp, field_name, value, status))

    except pymysql.Error as e:
        # 捕捉並打印數據庫錯誤
        print(f"Database error: {e}")
    finally:
        # 無論是否發生錯誤，確保關閉游標和數據庫連接
        cursor.close()
        conn.close()


def create_gauge(fig, ax, min_value, max_value, ranges):
    colors = ["#2bad4e", "#eff229", "#f25829"]  # 定義顏色列表
    color_texts = ["LOW", "Normal", "HIGH"]  # 定義顏色對應的文字
    angle_ranges = [0, 60, 120]  # 定義顏色區間的角度範圍

    # 增加圖表的尺寸
    fig.set_size_inches(3, 2)  # 調整這裡的數值來增加表頭之間的距離

    for i in range(len(colors)):  # 遍歷每種顏色
        start_angle = angle_ranges[i]  # 獲取顏色區域的起始角度
        end_angle = angle_ranges[i] + 60  # 獲取顏色區域的結束角度
        wedge = Wedge((0.5, 0), 0.4, start_angle, end_angle, width=0.1, facecolor=colors[i])  # 創建扇形區域
        ax.add_artist(wedge)  # 添加扇形區域到圖形中

        mid_angle = np.radians(angle_ranges[i] + 30)  # 計算顏色區域的中間角度
        x = 0.5 + 0.35 * np.cos(mid_angle)  # 計算文字的 x 座標
        y = 0.35 * np.sin(mid_angle)  # 計算文字的 y 座標
        ax.text(x, y, color_texts[i], ha='center', va='center', fontsize=10, color='black')  # 在扇形區域中間添加文字，並設置字體大小

    ax.set_xlim(0, 1)  # 設定 x 軸的範圍
    ax.set_ylim(-0.1, 0.5)  # 設定 y 軸的範圍
    ax.axis('off')  # 隱藏坐標軸

    # 使用列表來存儲當前箭頭，這樣可以在函數外部訪問
    current_arrow = [None]

    def set_needle(value):
        # 如果存在舊箭頭，先移除它
        if current_arrow[0] is not None:
            current_arrow[0].remove()
            
        if value <= ranges[0][1]:  # 如果數值在範圍 0 的最大值內
            angle = 45  # 設置箭頭的角度為 45°
        elif value <= ranges[1][1]:  # 如果數值在範圍 1 的最大值內
            angle = 90  # 設置箭頭的角度為 90°
        else:  # 如果數值超過範圍 1 的最大值
            angle = 135  # 設置箭頭的角度為 135°

        rad = np.radians(angle)  # 將角度轉換為弧度
        dx = 0.3 * np.cos(rad)  # 計算箭頭在 x 軸上的移動距離
        dy = 0.3 * np.sin(rad)  # 計算箭頭在 y 軸上的移動距離
            
        # 創建新箭頭並存儲引用
        current_arrow[0] = ax.arrow(0.5, 0, dx, dy, width=0.02, 
                                  head_width=0.05, head_length=0.07, 
                                  fc='black', ec='black')
        
        # 不需要手動添加箭頭到畫布，因為arrow()函數已經完成了這個操作
        return current_arrow[0]

    return set_needle
def is_high_or_low(value, ranges):
    # 判斷數值是否在範圍外（高或低）
    return value <= ranges[0][1] or value >= ranges[2][0]

def add_labels_and_buttons(frame, fig, ax, ranges, value, google_sheet_url=None):
    # 在指定的框架中添加標籤和按鈕
    
    label_frame = tk.Frame(frame)  # 創建標籤框架
    label_frame.pack(side="left", padx=5, pady=5)  # 將標籤框架放置在左側，並設置邊距

    label = tk.Label(label_frame, text=value)  # 創建顯示值的標籤
    label.pack()  # 將標籤放置在標籤框架中

    canvas = FigureCanvasTkAgg(fig, master=label_frame)  # 創建圖形的 Canvas
    canvas.draw()  # 繪製 Canvas
    canvas.get_tk_widget().pack()  # 將 Canvas 添加到標籤框架中

    button_frame = tk.Frame(label_frame)  # 創建按鈕框架
    button_frame.pack(fill=tk.X, padx=2, pady=2)  # 將按鈕框架放置在標籤框架中，並設置邊距

    green_circle_image = create_circle_image("green", radius=20)  # 創建綠色圓形圖片
    red_circle_image = create_circle_image("red", radius=20)  # 創建紅色圓形圖片
    green_circle_photo = ImageTk.PhotoImage(green_circle_image)  # 將綠色圓形圖片轉換為 PhotoImage
    red_circle_photo = ImageTk.PhotoImage(red_circle_image)  # 將紅色圓形圖片轉換為 PhotoImage

    green_button = tk.Label(button_frame, image=green_circle_photo, width=40, height=40)  # 創建綠色圓形按鈕
    green_button.image = green_circle_photo  # 保存圖片引用
    green_button.pack(side=tk.LEFT, padx=2)  # 將綠色圓形按鈕放置在按鈕框架中

    red_button = tk.Label(button_frame, image=red_circle_photo, width=40, height=40)  # 創建紅色圓形按鈕
    red_button.image = red_circle_photo  # 保存圖片引用
    red_button.pack_forget()  # 初始時隱藏紅色圓形按鈕
    
    button_frame_bottom = tk.Frame(button_frame)  # 創建按鈕框架底部
    button_frame_bottom.pack(fill=tk.X, pady=5)  # 將底部按鈕框架放置在按鈕框架中

    trend_button = tk.Button(button_frame_bottom, text="趨勢圖", command=lambda: open_trend_chart(value))  # 創建趨勢圖按鈕
    trend_button.pack(side='left', padx=2, pady=2)  # 將趨勢圖按鈕放置在底部按鈕框架中

    if google_sheet_url:
        google_sheet_button = tk.Button(button_frame_bottom, text="Google Sheet連結", command=lambda: webbrowser.open(google_sheet_url))  # 創建 Google Sheet 連結按鈕
        google_sheet_button.pack(side='left', padx=2, pady=2)  # 將 Google Sheet 連結按鈕放置在底部按鈕框架中

    label = tk.Label(label_frame, text="指針圖", font=("Arial", 10))  # 創建指針圖的標籤
    label.pack(padx=2, pady=2)  # 將標籤放置在標籤框架中
    
    return canvas, green_button, red_button  # 返回 Canvas、綠色圓形按鈕和紅色圓形按鈕


def open_trend_chart(value):
    # 根據值打開對應的趨勢圖文件
    chart_files = {
        "溫度": "溫度趨勢圖.py",
        "濕度": "濕度趨勢圖.py",
        "體溫": "體溫趨勢圖.py",
        "心跳": "心跳趨勢圖.py",
        "BMI": "bmi趨勢圖.py",
        "舒張壓": "舒張壓趨勢圖.py",
        "收縮壓": "收縮壓趨勢圖.py",
        "血糖":   "血糖趨勢圖.py",
        "膽固醇": "膽固醇趨勢圖.py"
    }
    
    chart_file = chart_files.get(value)  # 獲取對應的趨勢圖文件
    if chart_file:
        os.system(f'python {chart_file}')  # 執行趨勢圖文件
    else:
        print(f"No trend chart file found for {value}")  # 如果找不到文件，打印錯誤信息

def open_looker_studio():
    # 打開 Looker Studio 的報告頁面
    url = "https://lookerstudio.google.com/reporting/8661248a-16c8-4735-8d06-5aceb1613022/page/pwl4D"
    webbrowser.open(url)  # 在瀏覽器中打開 URL
def thingspeak():
    # 打開 Looker Studio 的報告頁面
    url = "https://thingspeak.com/channels/2466473"
    webbrowser.open(url)  # 在瀏覽器中打開 URL

# GUI 設置
main_window = tk.Tk()  # 創建主窗口
main_window.title("MR蔣監控系統")  # 設置主窗口標題
main_window.geometry("1200x900")  # 設置主窗口大小

main_frame = tk.Frame(main_window)  # 創建主框架
main_frame.pack(fill=tk.BOTH, expand=True)  # 填滿整個窗口並擴展

top_frame = tk.Frame(main_window)  # 創建頂部框架
top_frame.pack(side=tk.TOP, fill=tk.X)  # 將頂部框架放置在窗口的頂部，並填滿 X 軸

bottom_frame = tk.Frame(main_window)  # 創建底部框架
bottom_frame.pack(side=tk.TOP, fill=tk.X)  # 將底部框架放置在窗口的頂部，並填滿 X 軸

# 定義不同數值範圍
ranges_spec = {
    '溫度': [(0, 20), (20, 40), (40, 100)],
    '濕度': [(0, 40), (40, 75), (75, 100)],
    '體溫': [(0, 25), (25, 37), (37, 45)],
    '心跳': [(0, 60), (60, 140), (140, 160)],
    'BMI': [(0, 18.5), (18.5, 24), (24, 27)],
    '舒張壓': [(0, 60), (60, 80), (80, 100)],
    '收縮壓': [(0, 90), (90, 140), (140, 180)],
    '血糖': [(0, 70), (70, 140), (140, 200)],
    '膽固醇': [(0, 200), (200, 240), (240, 300)]
}

top_values = ["溫度", "濕度", "體溫"]  # 頂部顯示的數值類型
bottom_values = ["心跳", "BMI","舒張壓"]  # 底部顯示的數值類型
final_values= ["收縮壓", "血糖","膽固醇"]


# Google Sheets 連結
google_sheets_urls = {
    "溫度": "https://docs.google.com/spreadsheets/d/12rkfKKxrm3NcnrZNgZPzml9oNZm4alc2l-8UFsA2iCY/edit?resourcekey#gid=1685037583",
    "濕度": "https://docs.google.com/spreadsheets/d/12rkfKKxrm3NcnrZNgZPzml9oNZm4alc2l-8UFsA2iCY/edit?resourcekey#gid=1685037583",
    "體溫": "https://docs.google.com/spreadsheets/d/12rkfKKxrm3NcnrZNgZPzml9oNZm4alc2l-8UFsA2iCY/edit?resourcekey#gid=1685037583",
    "心跳": "https://docs.google.com/spreadsheets/d/1DUD0yMOqnjaZB5fhIytxBM0Ajmg6mP72oAmwC-grT4g/edit?resourcekey=&gid=1895836984#gid=1895836984",
    "BMI": "https://docs.google.com/spreadsheets/d/1ji-9bYlxt3KDxJvFIdat-3NwIkL7ejUa6wMFXgFe2a0/edit?resourcekey=&gid=1661867759#gid=1661867759",
    "舒張壓": "https://docs.google.com/spreadsheets/d/14Aqtn2RVty_Au3h7SUz-jxVqLJKuaLC6KbYfrI18z0Y/edit?resourcekey=&gid=2138244097#gid=2138244097",
    "收縮壓": "https://docs.google.com/spreadsheets/d/14Aqtn2RVty_Au3h7SUz-jxVqLJKuaLC6KbYfrI18z0Y/edit?resourcekey=&gid=2138244097#gid=2138244097",
    "血糖": "https://docs.google.com/spreadsheets/d/14Aqtn2RVty_Au3h7SUz-jxVqLJKuaLC6KbYfrI18z0Y/edit?resourcekey=&gid=2138244097#gid=2138244097",
    "膽固醇": "https://docs.google.com/spreadsheets/d/14Aqtn2RVty_Au3h7SUz-jxVqLJKuaLC6KbYfrI18z0Y/edit?resourcekey=&gid=2138244097#gid=2138244097"

}

needle_positions = []  # 存儲指針位置
canvases = []  # 存儲 Canvas

# 創建按鈕框架
button_frame = tk.Frame(main_window)
button_frame.pack(side=tk.TOP, fill=tk.X)

# 定義按鈕
buttons = [
    ("加入AI小幫手QR code", open_qr_code),
    ("統計圖示", open_looker_studio),  # 如果有其他功能，請替換 None
    ("Thingspeak", thingspeak),  # 如果有其他功能，請替換 None
    ("連線", connect_and_sync),
    ("資料管理", open_merge_search),
    ("異常事件紀錄", toggle_treeview),
    ("歷史紀錄動態網頁", open_webview),
]

# 創建並顯示按鈕
for text, command in buttons:
    button = tk.Button(button_frame, text=text, command=command)  # 創建按鈕
    button.pack(side=tk.LEFT, padx=2, pady=2)  # 將按鈕放置在按鈕框架中

time_label = tk.Label(main_window, font=("Arial", 16), padx=20, pady=10)  # 創建時間標籤
time_label.pack()  # 將時間標籤放置在主窗口中

treeview_frame = tk.Frame(main_window)  # 創建 Treeview 框架
treeview_frame.pack(fill=tk.BOTH, expand=True)  # 填滿整個窗口並擴展

# 創建 Treeview
tree = ttk.Treeview(treeview_frame, columns=("時間","目前欄位", "目前數值", "異常狀態"), show='headings')
tree.heading("時間", text="時間")  # 設置時間列標題
tree.heading("目前欄位", text="目前欄位")  # 設置目前數值列標題
tree.heading("目前數值", text="目前數值")  # 設置目前數值列標題
tree.heading("異常狀態", text="異常狀態")  # 設置異常狀態列標題
tree.column("時間", width=150)  # 設置時間列寬度
tree.column("目前欄位", width=100)  # 設置目前數值列寬度
tree.column("目前數值", width=100)  # 設置目前數值列寬度
tree.column("異常狀態", width=150)  # 設置異常狀態列寬度

tree.pack(fill=tk.BOTH, expand=True)  # 將 Treeview 添加到 Treeview 框架中

def get_latest_data():
    # 獲取最新數據
    queries = {
        '溫度': "SELECT 溫度 FROM dht11 ORDER BY 時間戳記 DESC LIMIT 1",
        '濕度': "SELECT 濕度 FROM dht11 ORDER BY 時間戳記 DESC LIMIT 1",
        '體溫': "SELECT 體溫 FROM dht11 ORDER BY 時間戳記 DESC LIMIT 1",
        '心跳': "SELECT 心跳 FROM heart_rate ORDER BY 時間戳記 DESC LIMIT 1",
        'BMI': "SELECT bmi FROM bmi ORDER BY 時間戳記 DESC LIMIT 1",
        '舒張壓': "SELECT 舒張壓 FROM blood_records ORDER BY 時間戳記 DESC LIMIT 1",
        '收縮壓': "SELECT 收縮壓 FROM blood_records ORDER BY 時間戳記 DESC LIMIT 1",
        '血糖': "SELECT 血糖 FROM blood_records ORDER BY 時間戳記 DESC LIMIT 1",
        '膽固醇': "SELECT 膽固醇 FROM blood_records ORDER BY 時間戳記 DESC LIMIT 1"
    }
    data = {key: None for key in queries.keys()}  # 初始化數據字典
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor')  # 連接資料庫
    cursor = conn.cursor()  # 創建游標
    for key, sql in queries.items():
        try:
            cursor.execute(sql)  # 執行查詢語句
            result = cursor.fetchone()  # 獲取查詢結果
            if result:
                data[key] = result[0]  # 更新數據字典
        except pymysql.Error as e:
            print(f"資料庫錯誤 ({key}): {e}")  # 捕獲並打印錯誤信息
    cursor.close()  # 關閉游標
    conn.close()  # 關閉連接
    return data  # 返回數據

def update_gauges():
    data = get_latest_data()  # 獲取最新的數據
    for i, (key, value) in enumerate(data.items()):  # 遍歷數據字典的每一個鍵值對
        if value is not None and i < len(needle_positions):  # 如果數據有效且指針列表中有對應的元素
            set_needle = needle_positions[i]  # 獲取對應的指針設置函數
            if set_needle is not None:  # 檢查指針設置函數是否有效
                set_needle(value)  # 更新指針位置
            else:
                print(f"Warning: set_needle is None for {key}")  # 如果指針設置函數為 None，則輸出警告
            
            ranges = ranges_spec[key]  # 根據鍵獲取對應的範圍設置
            if is_high_or_low(value, ranges):  # 判斷數據值是否處於高範圍或低範圍
                green_buttons[i].pack_forget()  # 隱藏綠色按鈕
                red_buttons[i].pack(side=tk.LEFT, padx=2)  # 顯示紅色按鈕
            else:
                red_buttons[i].pack_forget()  # 隱藏紅色按鈕
                green_buttons[i].pack(side=tk.LEFT, padx=2)  # 顯示綠色按鈕
    
    for canvas in canvases:  # 更新每個畫布
        canvas.draw()  # 重新繪製圖形
    
    main_window.after(1000, update_gauges)  # 每1秒鐘再次更新


    
def create_and_add_gauge(value, frame):
    fig, ax = plt.subplots(figsize=(2.5, 2))  # 創建一個儀表的畫布，這裡使用了 matplotlib 庫來繪製
    ranges = ranges_spec[value]  # 獲取對應儀表的範圍設定
    set_needle = create_gauge(fig, ax, ranges[0][0], ranges[-1][1], ranges)  # 創建儀表，並返回指針設置函數
    canvas, green_button, red_button = add_labels_and_buttons(frame, fig, ax, ranges, value, google_sheet_url=google_sheets_urls[value])  # 添加標籤和按鈕，並返回畫布和按鈕
    return set_needle, canvas, green_button, red_button  # 返回指針設置函數、畫布和按鈕


needle_positions = []  # 儲存指針設置函數
canvases = []  # 儲存畫布
green_buttons = []  # 儲存綠色按鈕
red_buttons = []  # 儲存紅色按鈕

for i, value in enumerate(top_values + bottom_values + final_values):  # 遍歷 top_values 和 bottom_values
    frame = top_frame if i < 3 else bottom_frame  # 根據索引來選擇顯示的框架
    set_needle, canvas, green_button, red_button = create_and_add_gauge(value, frame)  # 創建儀表
    if set_needle is not None:  # 如果指針設置函數有效
        needle_positions.append(set_needle)  # 儲存指針設置函數
        canvases.append(canvas)  # 儲存畫布
        green_buttons.append(green_button)  # 儲存綠色按鈕
        red_buttons.append(red_button)  # 儲存紅色按鈕
    else:
        print(f"Warning: set_needle is None for {value}")  # 如果指針設置函數無效，輸出警告

update_gauges()  # 更新儀表盤顯示
show_current_time()  # 啟動時間更新功能

main_window.mainloop()  # 啟動主循環