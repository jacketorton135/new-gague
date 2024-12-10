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

# Rest of your code


def show_current_time():
    current_time = datetime.now().strftime("系統時間: %Y-%m-%d %H:%M:%S")
    time_label.config(text=current_time)
    main_window.after(1000, show_current_time)


def create_gauge_image(frame, current_value, min_value=0, max_value=50):
    fig, ax = plt.subplots(figsize=(2.5, 2))
    
    colors = ["#2bad4e", "#eff229", "#f25829"]
    colors_text = ["LOW", "Normal", "HIGH"]
    
    # Set up background wedges
    for i in range(len(colors)):
        start_angle = 60 * i
        end_angle = 60 * (i + 1)
        wedge = Wedge((0.5, 0), 0.4, start_angle, end_angle, width=0.1, facecolor=colors[i], alpha=0.3)
        ax.add_artist(wedge)
    
    # Add text labels
    for i in range(len(colors)):
        mid_angle = np.radians(60 * (i + 0.5))
        x = 0.5 + 0.35 * np.cos(mid_angle)
        y = 0.35 * np.sin(mid_angle)
        ax.text(x, y, colors_text[i], ha='center', va='center', fontsize=10, color='black')
    
    # Set axis properties
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.1, 0.5)
    ax.axis('off')
    
    # Add IoT sensor level text
    level_text = ax.text(0.5, -0.05, f"IoT sensor Level\nValue = {current_value:.2f}", ha='center', va='center', fontsize=8)
    
    arrow = ax.arrow(0.5, 0, 0, 0.3, width=0.01, head_width=0.03, head_length=0.05, fc='black', ec='black')

    # Embed the figure in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def update_gauge(value):
        nonlocal arrow
        arrow.remove()
        angle = np.interp(value, [min_value, max_value], [0, np.pi])
        arrow = ax.arrow(0.5, 0, 0.3 * np.sin(angle), 0.3 * np.cos(angle),
                         width=0.01, head_width=0.03, head_length=0.05, fc='black', ec='black')
        level_text.set_text(f"IoT sensor Level\nValue = {value:.2f}")
        canvas.draw()
        frame.after(100, lambda: update_gauge(value))  # Update every 100ms

    frame.after(100, lambda: update_gauge(current_value))

    return canvas_widget

def create_circle_image(color, radius):
    image_size = (radius * 2, radius * 2)
    image = Image.new("RGBA", image_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse([(0, 0), image_size], fill=color)
    return image

def add_labels_and_buttons(frame, gauge_widget, values, google_sheet_url=None):
    label_frame = tk.Frame(frame)
    label_frame.pack(side="left", padx=5, pady=5)

    for value in values:
        label = tk.Label(label_frame, text=value)
        label.pack()

    gauge_widget.pack()  # Pack the gauge widget directly

    button_frame = tk.Frame(label_frame)
    button_frame.pack(fill=tk.X, padx=2, pady=2)

    # ... rest of the function remains the same ...

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

def open_trend_chart(value):
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

def handle_abnormal_alert():
    print("Abnormal alert resolved.")

def open_qr_code():
    filename = "F:\\物聯網123\\視覺化\\linebotchat.png"
    if os.path.exists(filename):
        os.startfile(filename)

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

    query = """SELECT * FROM (
        SELECT COALESCE(hr.時間戳記, d.時間戳記, b.時間戳記) as timestamp,
            hr.心跳 as heart_rate, hr.心跳狀態 as heart_rate_status,
            d.溫度 as temperature, d.濕度 as humidity, d.體溫 as body_temperature,
            d.溫度狀態 as temperature_status, d.濕度狀態 as humidity_status, d.體溫狀態 as body_temperature_status,
            b.BMI as bmi, b.檢查結果 as bmi_status
        FROM heart_rate hr
        LEFT JOIN dht11 d ON hr.時間戳記 = d.時間戳記
        LEFT JOIN bmi b ON hr.時間戳記 = b.時間戳記
        WHERE hr.心跳狀態 != '心跳正常'
            OR d.溫度狀態 != '溫度正常'
            OR d.濕度狀態 != '濕度正常'
            OR d.體溫狀態 != '體溫正常'
            OR b.檢查結果 IN ('體重過輕', '過重', '輕度肥胖', '重度肥胖')
        UNION
        SELECT COALESCE(hr.時間戳記, d.時間戳記, b.時間戳記) as timestamp,
            hr.心跳 as heart_rate, hr.心跳狀態 as heart_rate_status,
            d.溫度 as temperature, d.濕度 as humidity, d.體溫 as body_temperature,
            d.溫度狀態 as temperature_status, d.濕度狀態 as humidity_status, d.體溫狀態 as body_temperature_status,
            b.BMI as bmi, b.檢查結果 as bmi_status
        FROM dht11 d
        LEFT JOIN heart_rate hr ON d.時間戳記 = hr.時間戳記
        LEFT JOIN bmi b ON d.時間戳記 = b.時間戳記
        WHERE hr.心跳狀態 != '心跳正常'
            OR d.溫度狀態 != '溫度正常'
            OR d.濕度狀態 != '濕度正常'
            OR d.體溫狀態 != '體溫正常'
            OR b.檢查結果 IN ('體重過輕', '過重', '輕度肥胖', '重度肥胖')
        UNION
        SELECT COALESCE(hr.時間戳記, d.時間戳記, b.時間戳記) as timestamp,
            hr.心跳 as heart_rate, hr.心跳狀態 as heart_rate_status,
            d.溫度 as temperature, d.濕度 as humidity, d.體溫 as body_temperature,
            d.溫度狀態 as temperature_status, d.濕度狀態 as humidity_status, d.體溫狀態 as body_temperature_status,
            b.BMI as bmi, b.檢查結果 as bmi_status
        FROM bmi b
        LEFT JOIN heart_rate hr ON b.時間戳記 = hr.時間戳記
        LEFT JOIN dht11 d ON b.時間戳記 = d.時間戳記
        WHERE hr.心跳狀態 != '心跳正常'
            OR d.溫度狀態 != '溫度正常'
            OR d.濕度狀態 != '濕度正常'
            OR d.體溫狀態 != '體溫正常'
            OR b.檢查結果 IN ('體重過輕', '過重', '輕度肥胖', '重度肥胖')
    ) as combined_table
    ORDER BY timestamp DESC
    LIMIT 20;
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

# 主程序部分
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

google_sheets_urls = {
    "溫度": "https://docs.google.com/spreadsheets/d/12rkfKKxrm3NcnrZNgZPzml9oNZm4alc2l-8UFsA2iCY/edit?resourcekey#gid=1685037583",
    "濕度": "https://docs.google.com/spreadsheets/d/12rkfKKxrm3NcnrZNgZPzml9oNZm4alc2l-8UFsA2iCY/edit?resourcekey#gid=1685037583",
    "體溫": "https://docs.google.com/spreadsheets/d/12rkfKKxrm3NcnrZNgZPzml9oNZm4alc2l-8UFsA2iCY/edit?resourcekey#gid=1685037583",
    "心跳": "https://docs.google.com/spreadsheets/d/1DUD0yMOqnjaZB5fhIytxBM0Ajmg6mP72oAmwC-grT4g/edit?resourcekey=&gid=1895836984#gid=1895836984",
    "BMI": "https://docs.google.com/spreadsheets/d/1ji-9bYlxt3KDxJvFIdat-3NwIkL7ejUa6wMFXgFe2a0/edit?resourcekey=&gid=1661867759#gid=1661867759"
}

top_values = ["溫度", "濕度", "體溫"]
bottom_values = ["心跳", "BMI"]

for i, value in enumerate(top_values + bottom_values):
    frame = tk.Frame(main_window)
    frame.pack(side=tk.LEFT, padx=5, pady=5)
    gauge_widget = create_gauge_image(frame, 18)  # Use appropriate current_value here
    gauges.append(gauge_widget)
    
    if i < 3:  # Top frame
        add_labels_and_buttons(top_frame, gauge_widget, [value], google_sheet_url=google_sheets_urls[value])
    else:  # Bottom frame
        add_labels_and_buttons(bottom_frame, gauge_widget, [value], google_sheet_url=google_sheets_urls[value])

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
