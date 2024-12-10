import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pymysql
import io
from PIL import Image, ImageTk, ImageOps, ImageDraw
import matplotlib.pyplot as plt
import numpy as np
import webbrowser
import requests
import csv
from apscheduler.schedulers.background import BackgroundScheduler
import time
import os
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Wedge
from matplotlib.animation import FuncAnimation


def generate_qr_code(data, filename="linebotchat.png"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)


def open_qr_code():
    filename = "F:\\物聯網123\\視覺化\\linebotchat.png"
    if not os.path.exists(filename):
        generate_qr_code("https://example.com", filename)  # 生成二维码
    os.startfile(filename)  # Windows 系统打开文件
# 辅助函数
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

def save_to_mysql(data):
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM bmi;')
        
        for row in data:
            print(f"Inserting row: {row}")
            
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
                print(f"插入行时出错: {e}, 行: {row}")
        
        conn.commit()
        conn.close()
        print("数据同步成功")
    except Exception as e:
        print('数据库连接失败: ', e)

def get_csv_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTbj3f0rhEu2aCljm1AgkPiaqU7XLGfLUfmL_3NVClYABWXmarViEg1RSE4Q9St0YG_rR74VZyNh7MF/pub?output=csv"
    response = requests.get(url)
    csv_content = response.content.decode('utf-8')
    
    csv_file = csv.reader(csv_content.splitlines())
    header = next(csv_file)  # 跳过标题行
    data = [row for row in csv_file]  # 读取数据行
    
    return data

def scheduled_update():
    data = get_csv_data()
    save_to_mysql(data)

def connect_and_sync():
    data = get_csv_data()
    save_to_mysql(data)
    
    scheduler = BackgroundScheduler(timezone="Asia/Taipei")
    scheduler.add_job(scheduled_update, 'interval', minutes=1)
    scheduler.start()
    
    print("连接成功，数据同步已启动")

# GUI 函数
def create_gauge_image(current_value, min_value=0, max_value=50):
    fig, ax = plt.subplots(figsize=(2.5, 2), subplot_kw={'projection': 'polar'})
    current_value = max(min_value, min(current_value, max_value))
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xticks([])
    colors = ["#2bad4e", "#eff229", "#f25829"]
    colors_text = ["LOW", "Normal", "HIGH"]
    bounds = np.linspace(0, np.pi, len(colors) + 1)
    for i in range(len(colors)):
        ax.fill_between(np.linspace(bounds[i], bounds[i+1], 100), 0.6, 1, color=colors[i], alpha=0.3)
        mid_angle = (bounds[i] + bounds[i+1]) / 2
        ax.text(mid_angle, 0.8, colors_text[i], ha='center', va='center', fontsize=10, color='black')
    value_angle = np.interp(current_value, [min_value, max_value], [0, np.pi])
    ax.plot([value_angle, value_angle], [0, 0.5], color='black', linewidth=2)
    ax.text(0, -0.2, f"IoT sensor Level\nValue = {current_value:.2f}", ha='center', va='center')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig)
    return Image.open(buf)

def create_circle_image(color, radius=20):
    fig, ax = plt.subplots(figsize=(2*radius/100, 2*radius/100), dpi=100)
    ax.add_patch(plt.Circle((0.5, 0.5), 0.5, color=color))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig)
    image = Image.open(buf)
    image = ImageOps.fit(image, (radius*2, radius*2), centering=(0.5, 0.5))
    mask = Image.new('L', (radius*2, radius*2), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, radius*2, radius*2), fill=255)
    image.putalpha(mask)
    return image

def show_current_time():
    current_time = datetime.now().strftime("系統時間:%Y-%m-%d %H:%M:%S")
    time_label.config(text=current_time)
    main_window.after(1000, show_current_time)

def toggle_treeview():
    if treeview_frame.winfo_viewable():
        treeview_frame.pack_forget()
    else:
        treeview_frame.pack(fill=tk.BOTH, expand=True)
        load_data_from_db()

def load_data_from_db():
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor')
    cursor = conn.cursor()

    for item in tree.get_children():
        tree.delete(item)

    tables = ['heart_rate', 'dht11', 'bmi']
    table_structures = {}
    for table in tables:
        cursor.execute(f"DESCRIBE {table}")
        table_structures[table] = [row[0] for row in cursor.fetchall()]

    print("Table structures:", table_structures)

    time_column = {table: '時間戳記' for table in tables}
    print("Time columns:", time_column)

    query = f"""
    SELECT * FROM (
        SELECT 
            COALESCE(hr.{time_column['heart_rate']}, d.{time_column['dht11']}, b.{time_column['bmi']}) as timestamp,
            hr.心跳 as heart_rate, hr.心跳狀態 as heart_rate_status,
            d.溫度 as temperature, d.濕度 as humidity, d.體溫 as body_temperature, 
            d.溫度狀態 as temperature_status, d.濕度狀態 as humidity_status, d.體溫狀態 as body_temperature_status,
            b.BMI as bmi, b.檢查結果 as bmi_status
        FROM 
            heart_rate hr
        LEFT JOIN 
            dht11 d ON hr.{time_column['heart_rate']} = d.{time_column['dht11']}
        LEFT JOIN 
            bmi b ON hr.{time_column['heart_rate']} = b.{time_column['bmi']}
        WHERE 
            hr.心跳狀態 != '心跳正常'
            OR d.溫度狀態 != '溫度正常'
            OR d.濕度狀態 != '濕度正常'
            OR d.體溫狀態 != '體溫正常'
            OR b.檢查結果 IN ('體重過輕', '過重', '輕度肥胖', '重度肥胖')
        UNION
        SELECT 
            COALESCE(hr.{time_column['heart_rate']}, d.{time_column['dht11']}, b.{time_column['bmi']}) as timestamp,
            hr.心跳 as heart_rate, hr.心跳狀態 as heart_rate_status,
            d.溫度 as temperature, d.濕度 as humidity, d.體溫 as body_temperature, 
            d.溫度狀態 as temperature_status, d.濕度狀態 as humidity_status, d.體溫狀態 as body_temperature_status,
            b.BMI as bmi, b.檢查結果 as bmi_status
        FROM 
            dht11 d
        LEFT JOIN 
            heart_rate hr ON d.{time_column['dht11']} = hr.{time_column['heart_rate']}
        LEFT JOIN 
            bmi b ON d.{time_column['dht11']} = b.{time_column['bmi']}
        WHERE 
            hr.心跳狀態 != '心跳正常'
            OR d.溫度狀態 != '溫度正常'
            OR d.濕度狀態 != '濕度正常'
            OR d.體溫狀態 != '體溫正常'
            OR b.檢查結果 IN ('體重過輕', '過重', '輕度肥胖', '重度肥胖')
        UNION
        SELECT 
            COALESCE(hr.{time_column['heart_rate']}, d.{time_column['dht11']}, b.{time_column['bmi']}) as timestamp,
            hr.心跳 as heart_rate, hr.心跳狀態 as heart_rate_status,
            d.溫度 as temperature, d.濕度 as humidity, d.體溫 as body_temperature, 
            d.溫度狀態 as temperature_status, d.濕度狀態 as humidity_status, d.體溫狀態 as body_temperature_status,
            b.BMI as bmi, b.檢查結果 as bmi_status
        FROM 
            bmi b
        LEFT JOIN 
            heart_rate hr ON b.{time_column['bmi']} = hr.{time_column['heart_rate']}
        LEFT JOIN 
            dht11 d ON b.{time_column['bmi']} = d.{time_column['dht11']}
        WHERE 
            hr.心跳狀態 != '心跳正常'
            OR d.溫度狀態 != '溫度正常'
            OR d.濕度狀態 != '濕度正常'
            OR d.體溫狀態 != '體溫正常'
            OR b.檢查結果 IN ('體重過輕', '過重', '輕度肥胖', '重度肥胖')
    ) AS combined_data
    ORDER BY timestamp DESC
    """

    print("Generated query:", query)

    try:
        cursor.execute(query)
        abnormal_data = cursor.fetchall()

        for row in abnormal_data:
            timestamp, heart_rate, heart_rate_status, temperature, humidity, body_temp, temperature_status, humidity_status, body_temp_status, bmi, bmi_status = row

            abnormal_values = []
            abnormal_statuses = []

            if heart_rate_status and heart_rate_status != '心跳正常':
                abnormal_values.append(f"{heart_rate}")
                abnormal_statuses.append(heart_rate_status)
            if temperature_status and temperature_status != '溫度正常':
                abnormal_values.append(f"{temperature}")
                abnormal_statuses.append(temperature_status)
            if humidity_status and humidity_status != '濕度正常':
                abnormal_values.append(f"{humidity}")
                abnormal_statuses.append(humidity_status)
            if body_temp_status and body_temp_status != '體溫正常':
                abnormal_values.append(f"{body_temp}")
                abnormal_statuses.append(body_temp_status)
            if bmi_status in ['體重過輕', '過重', '輕度肥胖', '重度肥胖']:
                abnormal_values.append(f"{bmi}")
                abnormal_statuses.append(bmi_status)

            if abnormal_values and abnormal_statuses:
                tree.insert("", "end", values=(timestamp, ", ".join(abnormal_values), ", ".join(abnormal_statuses)))

    except pymysql.Error as e:
        print(f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()

def create_circle_image(color, radius):
    image_size = (radius * 2, radius * 2)
    image = Image.new("RGBA", image_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse([(0, 0), image_size], fill=color)
    return image

def handle_abnormal_alert():
    # Function to handle abnormal alert
    # Replace this with actual handling logic
    print("Abnormal alert resolved.")

def add_labels_and_buttons(frame, img_path, values, google_sheet_url=None):
    label_frame = tk.Frame(frame)
    label_frame.pack(side="left", padx=5, pady=5)

    # Ensure img_path is a valid file path
    if isinstance(img_path, str):
        try:
            # Load image from file path
            image = Image.open(img_path)
            image = ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading image from path {img_path}: {e}")
            return  # Exit the function if image loading fails
    else:
        print(f"Invalid image path type: {type(img_path)}")
        return  # Exit the function if img_path is not a string

    image_label = tk.Label(label_frame, image=image)
    image_label.image = image  # Keep a reference to avoid garbage collection
    image_label.pack()

    button_frame = tk.Frame(label_frame)
    button_frame.pack(fill=tk.X, padx=2, pady=2)

    # Create and pack green and red buttons
    green_circle_image = create_circle_image("green", radius=20)
    red_circle_image = create_circle_image("red", radius=20)
    green_circle_photo = ImageTk.PhotoImage(green_circle_image)
    red_circle_photo = ImageTk.PhotoImage(red_circle_image)

    green_button = tk.Button(button_frame, image=green_circle_photo, width=40, height=40, borderwidth=0)
    green_button.image = green_circle_photo
    green_button.pack(side=tk.LEFT, padx=2)

    red_button = tk.Button(button_frame, image=red_circle_photo, width=40, height=40, borderwidth=0)
    red_button.image = red_circle_photo
    red_button.pack(side=tk.LEFT, padx=2)

    # Create and pack trend and Google Sheets buttons
    button_frame_bottom = tk.Frame(button_frame)
    button_frame_bottom.pack(fill=tk.X, pady=5)

    trend_button_texts = [f"趨勢圖"]
    for btn_text in trend_button_texts:
        trend_button = tk.Button(button_frame_bottom, text=btn_text, command=lambda value=values[0]: open_trend_chart(value))
        trend_button.pack(side='left', padx=2, pady=2)

    if google_sheet_url:
        google_sheet_button = tk.Button(button_frame_bottom, text="Google Sheet連結", command=lambda: webbrowser.open(google_sheet_url))
        google_sheet_button.pack(side='left', padx=2, pady=2)

    abnormal_alert_button = tk.Button(button_frame_bottom, text="異常警報解除", command=handle_abnormal_alert)
    abnormal_alert_button.pack(side='left', padx=2, pady=2)

    labels_text = ["指針圖"]
    for text in labels_text:
        label = tk.Label(label_frame, text=text, font=("Arial", 10))
        label.pack(padx=2, pady=2)


    # Add Google Sheets button
    if google_sheet_url:
        google_sheet_button = tk.Button(button_frame_bottom, text="Google Sheet連結", command=lambda: webbrowser.open(google_sheet_url))
        google_sheet_button.pack(side='left', padx=2, pady=2)

    # Add abnormal alert button
    abnormal_alert_button = tk.Button(button_frame_bottom, text="異常警報解除", command=handle_abnormal_alert)
    abnormal_alert_button.pack(side='left', padx=2, pady=2)

    # Add label for the indicator image
    labels_text = ["指針圖"]
    for text in labels_text:
        label = tk.Label(label_frame, text=text, font=("Arial", 10))
        label.pack(padx=2, pady=2)


# GUI Setup
main_window = tk.Tk()
main_window.title("MR蔣監控系統")
main_window.geometry("1000x650")

main_frame = tk.Frame(main_window)
main_frame.pack(fill=tk.BOTH, expand=True)

top_frame = tk.Frame(main_window)
top_frame.pack(side=tk.TOP, fill=tk.X)

bottom_frame = tk.Frame(main_window)
bottom_frame.pack(side=tk.TOP, fill=tk.X)

gauges = []
for i in range(5):
    gauge_image = create_gauge_image(18)
    gauge_image = ImageTk.PhotoImage(gauge_image)
    gauges.append(gauge_image)

# Define top and bottom values
top_values = ["溫度", "濕度", "體溫"]
bottom_values = ["心跳", "BMI"]

# Define gauge image paths and Google Sheets URLs
gauge_image_paths = {
    "溫度": "溫度gague.py",
    "濕度": "濕度gague.py",
    "體溫": "體溫gague.py",
    "心跳": "心跳gague.py",
    "BMI": "bmi gague.py"
}
google_sheets_urls = {
    "溫度": "https://docs.google.com/spreadsheets/d/12rkfKKxrm3NcnrZNgZPzml9oNZm4alc2l-8UFsA2iCY/edit?resourcekey#gid=1685037583",
    "濕度": "https://docs.google.com/spreadsheets/d/12rkfKKxrm3NcnrZNgZPzml9oNZm4alc2l-8UFsA2iCY/edit?resourcekey#gid=1685037583",
    "體溫": "https://docs.google.com/spreadsheets/d/12rkfKKxrm3NcnrZNgZPzml9oNZm4alc2l-8UFsA2iCY/edit?resourcekey#gid=1685037583",
    "心跳": "https://docs.google.com/spreadsheets/d/1DUD0yMOqnjaZB5fhIytxBM0Ajmg6mP72oAmwC-grT4g/edit?resourcekey=&gid=1895836984#gid=1895836984",
    "BMI": "https://docs.google.com/spreadsheets/d/1ji-9bYlxt3KDxJvFIdat-3NwIkL7ejUa6wMFXgFe2a0/edit?resourcekey=&gid=1661867759#gid=1661867759"
}

for i in range(3):
    add_labels_and_buttons(top_frame, gauges[i], [top_values[i]], google_sheet_url=google_sheets_urls[top_values[i]])

for i in range(2):
    add_labels_and_buttons(bottom_frame, gauges[i+3], [bottom_values[i]], google_sheet_url=google_sheets_urls[bottom_values[i]])

button_frame = tk.Frame(main_window)
button_frame.pack(side=tk.TOP, fill=tk.X)

buttons = [
    ("加入AI小幫手QR code", open_qr_code),
    ("統計圖示", None),
    ("Google Sheet連結", None),
    ("連線", connect_and_sync),
    ("異常事件紀錄", toggle_treeview),
]

for text, command in buttons:
    button = tk.Button(button_frame, text=text, command=command)
    button.pack(side="left", padx=5, pady=5)

time_label = tk.Label(main_window, font=("Arial", 16), padx=20, pady=10)
time_label.pack()

treeview_frame = tk.Frame(main_window)
treeview_frame.pack(fill=tk.BOTH, expand=True)

tree = ttk.Treeview(treeview_frame, columns=("時間", "目前數值", "異常狀態"), show='headings')
tree.heading("時間", text="時間")
tree.heading("目前數值", text="目前數值")
tree.heading("異常狀態", text="異常狀態")
tree.column("時間", width=150)
tree.column("目前數值", width=150)
tree.column("異常狀態", width=200)

tree.pack(fill=tk.BOTH, expand=True)

show_current_time()  # 启动时间更新功能

main_window.mainloop()
