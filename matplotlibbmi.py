import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image, ImageTk
import pymysql
import tkinter as tk
from matplotlib.patches import Polygon
from matplotlib.transforms import Affine2D

def fetch_latest_bmi():
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor')
    cursor = conn.cursor()
    
    try:
        sql_query = "SELECT `BMI`, `時間戳記`, `姓名`, `性別`, `體重`, `身高`, `標準體重`, `檢查結果`, `正常_異常` FROM `bmi` ORDER BY `時間戳記` DESC LIMIT 1"
        print(f"Executing SQL Query: {sql_query}")
        cursor.execute(sql_query)
        result = cursor.fetchone()
        print(f"Query Result: {result}")
        if result:
            bmi, timestamp, name, gender, weight, height, standard_weight, check_result, normal_abnormal = result
            return {
                'bmi': float(bmi),
                'timestamp': timestamp,
                'name': name,
                'gender': gender,
                'weight': float(weight),
                'height': float(height),
                'standard_weight': float(standard_weight),
                'check_result': check_result,
                'normal_abnormal': normal_abnormal
            }
        else:
            return None
    except pymysql.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def create_bmi_gauge(bmi_data):
    if not bmi_data:
        return None

    fig, ax = plt.subplots(figsize=(4, 2.5), subplot_kw={'projection': 'polar'})
    
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi)
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xticks([])

    colors = ["#2bad4e", "#eff229", "#f25829"]
    color_texts = ["LOW", "Normal", "HIGH"]
    bounds = [0, 18.5, 24, 27, 40]

    # Ensure equal distribution of the colors in the half-circle
    for i in range(len(colors)):
        start_angle = np.radians(60 * i)
        end_angle = np.radians(60 * (i + 1))
        ax.fill_between(np.linspace(start_angle, end_angle, 100), 0.6, 1, color=colors[i], alpha=0.3)
        mid_angle = np.radians(60 * (i + 0.5))
        ax.text(mid_angle, 0.8, color_texts[i], ha='center', va='center', fontsize=10, color='black')

    bmi_value = max(bounds[0], min(bmi_data['bmi'], bounds[-1]))
    if bmi_value <= 18.5:
        status = "LOW"
        value_angle = np.interp(bmi_value, [bounds[0], 18.5], [0, np.radians(60)])
    elif bmi_value <= 24:
        status = "Normal"
        value_angle = np.interp(bmi_value, [18.5, 24], [np.radians(60), np.radians(120)])
    elif bmi_value <= 27:
        status = "HIGH"
        value_angle = np.interp(bmi_value, [24, 27], [np.radians(120), np.radians(180)])
    else:
        status = "VERY HIGH"
        value_angle = np.interp(bmi_value, [27, bounds[-1]], [np.radians(180), np.radians(240)])

    # Draw the pointer
    pointer = Polygon([(0, 0), (-0.05, 0.5), (0.05, 0.5)], closed=True, facecolor='black', edgecolor='none')
    pointer.set_transform(ax.transData + Affine2D().rotate(value_angle))
    ax.add_patch(pointer)

    ax.text(0, -0.3, f"BMI: {bmi_value:.1f}", ha='center', va='center', fontsize=12, fontweight='bold')

    info_text = (f"{bmi_data['timestamp']}\n"
                 f"{bmi_data['name']} {bmi_data['gender']} "
                 f"{bmi_data['weight']}kg, {bmi_data['height']}cm\n"
                 f"BMI: {bmi_data['bmi']:.1f}, 標準體重: {bmi_data['standard_weight']:.1f}kg\n"
                 f"檢查結果: {bmi_data['check_result']}")
    ax.text(0, -0.5, info_text, ha='center', va='center', fontsize=8, color='black')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig)
    
    return Image.open(buf)

def update_gauge():
    bmi_data = fetch_latest_bmi()
    print(f"Fetched BMI Data: {bmi_data}")

    if not bmi_data:
        bmi_data = {
            'bmi': 22.0,
            'timestamp': '2024-08-05 00:00:00',
            'name': '默认姓名',
            'gender': '默认性别',
            'weight': 70.0,
            'height': 175.0,
            'standard_weight': 70.0,
            'check_result': '默认检查结果',
            'normal_abnormal': 1
        }

    gauge_image = create_bmi_gauge(bmi_data)
    if gauge_image:
        photo = ImageTk.PhotoImage(gauge_image)
        label.config(image=photo)
        label.image = photo
    
        bmi_value = bmi_data['bmi']
        if bmi_value <= 18.5:
            status = "LOW"
        elif bmi_value <= 24:
            status = "Normal"
        elif bmi_value <= 27:
            status = "HIGH"
        else:
            status = "VERY HIGH"
    
        status_label.config(text=f"狀態: {status}")
    
    root.after(5000, update_gauge)

root = tk.Tk()
root.title("BMI Gauge")

label = tk.Label(root)
label.pack()

status_label = tk.Label(root, font=("Arial", 12))
status_label.pack()

update_gauge()

root.mainloop()













