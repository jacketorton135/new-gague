import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pymysql
import io
from PIL import Image, ImageTk, ImageOps, ImageDraw
import matplotlib.pyplot as plt
import numpy as np
import webbrowser

def create_gauge_image(current_value, min_value, max_value, low_threshold, normal_threshold, high_threshold):
    fig, ax = plt.subplots(figsize=(3, 2), subplot_kw={'projection': 'polar'})
    
    try:
        current_value = float(current_value)
    except ValueError:
        current_value = 0
    
    current_value = max(min_value, min(current_value, max_value))
    
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi/2)
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xticks([])
    
    # Define color ranges
    colors = ["#2bad4e", "#eff229", "#f25829"]
    color_texts = ["LOW", "Normal", "HIGH"]
    bounds = [min_value, low_threshold, normal_threshold, high_threshold]
    
    for i in range(len(colors)):
        start = np.radians(180 * (bounds[i] - min_value) / (max_value - min_value))
        end = np.radians(180 * (bounds[i+1] - min_value) / (max_value - min_value))
        ax.bar(np.linspace(start, end, 100), 0.8, width=np.radians(1.8), bottom=0.2, color=colors[i], alpha=0.6)
    
    for i, text in enumerate(color_texts):
        angle = np.radians(90 - 180 * (bounds[i] + bounds[i+1]) / (2 * (max_value - min_value)))
        ax.text(angle, 0.7, text, ha='center', va='center', fontsize=8, color='black')
    
    # Add needle
    value_angle = np.radians(180 - 180 * (current_value - min_value) / (max_value - min_value))
    ax.plot([value_angle, value_angle], [0, 0.7], color='black', linewidth=2)
    
    # Add current value text
    ax.text(0, -0.2, f"{current_value:.1f}", ha='center', va='center', fontsize=12, fontweight='bold')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig)
    
    return Image.open(buf)

def update_gauges():
    latest_values = fetch_latest_values()

    gauge_info = {
        "temperature": (0, 100, 20, 40, 100),
        "humidity": (0, 100, 40, 75, 100),
        "body_temperature": (0, 45, 25, 37, 45),
        "heart_rate": (0, 160, 60, 140, 160),
        "bmi": (0, 40, 18.5, 24, 27)
    }

    all_values = top_values + bottom_values
    
    for i, key in enumerate(all_values):
        min_val, max_val, low, normal, high = gauge_info[key]
        current_value = latest_values.get(key, 0)
        gauge_image = create_gauge_image(
            current_value, min_val, max_val, low, normal, high
        )
        gauges[i] = ImageTk.PhotoImage(gauge_image)
        
        frame = top_frame if i < 3 else bottom_frame
        label_index = i if i < 3 else i - 3
        
        try:
            label = frame.children[f'!label{label_index}']
            label.config(image=gauges[i])
            label.image = gauges[i]
            
            # Determine status
            if current_value <= low:
                status = "LOW"
            elif current_value <= normal:
                status = "Normal"
            else:
                status = "HIGH"
            
            status_label = frame.children.get(f'!label_status{label_index}')
            if status_label:
                status_label.config(text=f"狀態: {status}")

        except KeyError:
            print(f"Label !label{label_index} not found in frame.")

    main_window.after(5000, update_gauges)

def show_current_time():
    current_time = datetime.now().strftime("系統時間:%Y-%m-%d %H:%M:%S")
    time_label.config(text=current_time)
    main_window.after(1000, show_current_time)

def toggle_treeview():
    if treeview_frame.winfo_viewable():
        treeview_frame.pack_forget()
    else:
        treeview_frame.pack(fill=tk.BOTH, expand=True)
        load_data_from_db()  # Ensure this line is here

def load_data_from_db():
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor')
    cursor = conn.cursor()

    # Clear Treeview
    for item in tree.get_children():
        tree.delete(item)

    # Get table structures
    tables = ['heart_rate', 'dht11', 'bmi']
    table_structures = {}
    for table in tables:
        cursor.execute(f"DESCRIBE {table}")
        table_structures[table] = [row[0] for row in cursor.fetchall()]

    print("Table structures:", table_structures)  # Debugging information

    # Use correct column names
    time_column = {table: '時間戳記' for table in tables}
    print("Time columns:", time_column)  # Debugging information

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

    print("Generated query:", query)  # Debugging information

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
def fetch_latest_values():
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor')
    cursor = conn.cursor()
    
    latest_values = {}
    
    queries = {
        "temperature": "SELECT 溫度 FROM dht11 ORDER BY 時間戳記 DESC LIMIT 1",
        "humidity": "SELECT 濕度 FROM dht11 ORDER BY 時間戳記 DESC LIMIT 1",
        "body_temperature": "SELECT 體溫 FROM dht11 ORDER BY 時間戳記 DESC LIMIT 1",
        "heart_rate": "SELECT 心跳 FROM heart_rate ORDER BY 時間戳記 DESC LIMIT 1",
        "bmi": "SELECT BMI FROM bmi ORDER BY 時間戳記 DESC LIMIT 1"
    }
    
    try:
        for key, query in queries.items():
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                latest_values[key] = float(result[0])
    except pymysql.Error as e:
        print(f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()
    
    return latest_values

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

    additional_buttons_texts = ["趨勢圖", "異常警報解除"]
    for btn_text in additional_buttons_texts:
        additional_button = tk.Button(button_frame, text=btn_text)
        additional_button.pack(side='left', padx=2, pady=2)

    if google_sheet_url:
        google_sheet_button = tk.Button(button_frame, text="Google Sheet連結", command=lambda: webbrowser.open(google_sheet_url))
        google_sheet_button.pack(side='left', padx=2, pady=2)

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
    gauge_image = create_gauge_image(18, 0, 100, 20, 40, 80)
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
    ("加入AI小幫手QR code", None),
    ("統計圖示", None),
    ("Google Sheet連結", None),
    ("復歸", None),
    ("異常事件紀錄", toggle_treeview)  # 绑定toggle_treeview函数
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












