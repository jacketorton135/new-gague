import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pymysql
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

def fetch_heart_rate_status():
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor')
    cursor = conn.cursor()
    
    try:
        sql_query = "SELECT `心跳_正常_異常`, `時間戳記` FROM `heart_rate` ORDER BY `時間戳記` ASC"
        cursor.execute(sql_query)
        result = cursor.fetchall()
        
        # 打印查询结果以调试
        print("Fetched Data:", result)
        
        status_list = [(int.from_bytes(row[0], 'big'), row[1]) for row in result if row[0] is not None]
        return status_list
    except pymysql.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def plot_heart_rate_status(ax, heart_rate_status):
    if not heart_rate_status:
        return

    times = [row[1] for row in heart_rate_status]
    statuses = [row[0] for row in heart_rate_status]

    if len(times) > 0:
        extra_time = times[-1] + datetime.timedelta(seconds=1)
        times.append(extra_time)
        statuses.append(statuses[-1])

    ax.clear()
    ax.step(times, statuses, linewidth=2.5, where='post')

    ax.set_ylim(-0.1, 1.1)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Normal', 'Error'], fontsize=8)

    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=6)

    ax.set_xlabel('Time')
    ax.set_ylabel('Heart Rate Status')
    ax.set_title('Heart Rate Status Over Time')

def create_heart_rate_plot_window():
    def update_plot():
        heart_rate_status = fetch_heart_rate_status()
        plot_heart_rate_status(ax, heart_rate_status)
        canvas.draw()
        root.after(5000, update_plot)  # 每5秒更新一次

    root = tk.Tk()
    root.title("Real-time Heart Rate Trend")

    fig, ax = plt.subplots(figsize=(10, 6))
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

    update_plot()  # 初始调用更新函数

    root.mainloop()

if __name__ == '__main__':
    create_heart_rate_plot_window()

