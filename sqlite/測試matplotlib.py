import pymysql
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

# 資料庫連線設定
conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor')
cursor = conn.cursor()

# 定義每個儀表的範圍
ranges_spec = {
    '溫度': [(0, 20), (20, 40), (40, 100)],
    '濕度': [(0, 40), (40, 75), (75, 100)],
    '體溫': [(0, 25), (25, 37), (37, 45)],
    '心跳': [(0, 60), (60, 140), (140, 160)],
    'bmi': [(0, 18.5), (18.5, 24), (24, 27)]
}

# 定義繪製儀表的函數
def gauge(ax, value=0, min_value=0, max_value=100, ranges=None):
    colors = ["#2bad4e", "#eff229", "#f25829"]
    color_texts = ["LOW", "Normal", "HIGH"]

    # 定義顏色區域的角度範圍，0度, 60度, 120度
    angle_ranges = [0, 60, 120]

    # 如果未提供範圍，使用預設範圍
    if ranges is None:
        ranges = [(0, max_value * 0.33), (max_value * 0.33, max_value * 0.66), (max_value * 0.66, max_value)]

    # 創建每個顏色區域的扇形
    for i in range(len(colors)):
        start_angle = angle_ranges[i]
        end_angle = angle_ranges[i] + 60  # 每個扇形60度
        wedge = Wedge((0.5, 0), 0.4, start_angle, end_angle, width=0.1, facecolor=colors[i])
        ax.add_artist(wedge)

        # 添加文字標籤
        mid_angle = np.radians(angle_ranges[i] + 30)
        x = 0.5 + 0.35 * np.cos(mid_angle)
        y = 0.35 * np.sin(mid_angle)
        ax.text(x, y, color_texts[i], ha='center', va='center', fontsize=8, color='black')

    # 初始化箭頭
    arrow = ax.arrow(0.5, 0, 0, 0.3, width=0.01, head_width=0.03, head_length=0.05, fc='black', ec='black')

    # 設置坐標軸屬性
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.1, 0.5)
    ax.axis('off')

    # 定義設置指針角度的內部函數
    def set_needle(value):
        nonlocal arrow
        # 根據值確定指針應該指向哪個區域
        if value <= ranges[0][1]:
            angle = 45  # LOW
        elif value <= ranges[1][1]:
            angle = 90  # Normal
        else:
            angle = 135  # HIGH

        rad = np.radians(angle)
        dx = 0.3 * np.cos(rad)
        dy = 0.3 * np.sin(rad)
        
        # 移除舊的箭頭
        arrow.remove()
        
        # 創建新的箭頭
        arrow = ax.arrow(0.5, 0, dx, dy, width=0.01, head_width=0.03, head_length=0.05, fc='black', ec='black')
        ax.add_artist(arrow)
        return arrow

    return arrow, set_needle

# 獲取最新數據的函數
def get_latest_data():
    queries = {
        '溫度': "SELECT 溫度 FROM dht11 ORDER BY 時間戳記 DESC LIMIT 1",
        '濕度': "SELECT 濕度 FROM dht11 ORDER BY 時間戳記 DESC LIMIT 1",
        '體溫': "SELECT 體溫 FROM dht11 ORDER BY 時間戳記 DESC LIMIT 1",
        '心跳': "SELECT 心跳 FROM heart_rate ORDER BY 時間戳記 DESC LIMIT 1",
        'bmi': "SELECT bmi FROM bmi ORDER BY 時間戳記 DESC LIMIT 1"
    }
    data = {key: None for key in queries.keys()}
    for key, sql in queries.items():
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            if result:
                data[key] = result[0]
        except pymysql.Error as e:
            print(f"資料庫錯誤 ({key}): {e}")
    return data

# 更新動畫的函數
def update(frame):
    data = get_latest_data()

    for i, (key, value) in enumerate(data.items()):
        if value is not None and i < len(needle_positions):
            needle, set_needle = needle_positions[i]
            new_needle = set_needle(value)
            if new_needle is not None:
                needle_positions[i] = (new_needle, set_needle)

    return [n[0] for n in needle_positions if n[0] is not None]

# 創建Tkinter窗口
root = tk.Tk()
root.title("Gauge Animation")

# 創建圖形和坐標軸
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
fig.delaxes(axes[1, 2])  # 刪除多餘的子圖

# 定義每行的標題
top_values = ["Temperature", "Humidity", "Body Temperature"]
bottom_values = ["Heart Rate", "BMI"]

# 初始化每個儀表的指針，並設置正確的範圍和顏色段
needle_positions = []
for i, (key, ranges) in enumerate(ranges_spec.items()):
    ax = axes[i // 3, i % 3]
    needle, set_needle = gauge(ax, min_value=ranges[0][0], max_value=ranges[-1][1], ranges=ranges)
    needle_positions.append((needle, set_needle))

# 設置每個儀表的標題
axes[0, 0].set_title(top_values[0], fontsize=10)
axes[0, 1].set_title(top_values[1], fontsize=10)
axes[0, 2].set_title(top_values[2], fontsize=10)
axes[1, 0].set_title(bottom_values[0], fontsize=10)
axes[1, 1].set_title(bottom_values[1], fontsize=10)

# 將圖表嵌入到Tkinter窗口
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# 初始化函數
def init():
    return [n[0] for n in needle_positions]

# 創建動畫
anim = FuncAnimation(fig, update, init_func=init, frames=100, interval=1000, blit=True)

# 啟動Tkinter主循環
root.mainloop()

# 關閉資料庫連接
cursor.close()
conn.close()











