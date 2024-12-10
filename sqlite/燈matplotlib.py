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
from data_sync import connect_and_sync

def start_data_sync():
    connect_and_sync()
    print("數據同步已啟動")
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

def add_labels_and_buttons(frame, img, values, google_sheet_url=None):
    label_frame = tk.Frame(frame)
    label_frame.pack(side="left", padx=5, pady=5)

    for value in values:
        label = tk.Label(label_frame, text=value)
        label.pack()

    image_label = tk.Label(label_frame, image=img)
    image_label.pack()

    button_frame = tk.Frame(label_frame)
    button_frame.pack(fill=tk.X, padx=2, pady=2)

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

    # Create trend buttons and other buttons
    button_frame_bottom = tk.Frame(button_frame)
    button_frame_bottom.pack(fill=tk.X, pady=5)
    

    # Add trend buttons
    trend_button_texts = [f"趨勢圖"]
    for btn_text in trend_button_texts:
        trend_button = tk.Button(button_frame_bottom, text=btn_text, command=lambda value=values[0]: open_trend_chart(value))
        trend_button.pack(side='left', padx=2, pady=2)

    # Add Google Sheets button
    if google_sheet_url:
        google_sheet_button = tk.Button(button_frame_bottom, text="Google Sheet連結", command=lambda: webbrowser.open(google_sheet_url))
        google_sheet_button.pack(side='left', padx=2, pady=2)

    # Add label for the indicator image
    labels_text = ["指針圖"]
    for text in labels_text:
        label = tk.Label(label_frame, text=text, font=("Arial", 10))
        label.pack(padx=2, pady=2)

def open_trend_chart(value):
    # Mapping values to trend chart files
    chart_files = {
        "溫度": "溫度趨勢圖.py",
        "濕度": "濕度趨勢圖.py",
        "體溫": "體溫趨勢圖.py",
        "心跳": "心跳趨勢圖.py",
        "BMI": "bmi趨勢圖.py"
    }
    
    chart_file = chart_files.get(value)
    if chart_file:
        os.system(f'python {chart_file}')
    else:
        print(f"No trend chart file found for {value}")


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

top_values = ["溫度", "濕度", "體溫"]
bottom_values = ["心跳", "BMI"]

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
    ("統計圖示", None),  # Replace None with actual function if you have one
    ("Google Sheet連結", None),  # Replace None with actual function if you have one
    ("連線", connect_and_sync),
    ("異常事件紀錄", toggle_treeview),
]

for text, command in buttons:
    button = tk.Button(button_frame, text=text, command=command)
    button.pack(side=tk.LEFT, padx=2, pady=2)

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



