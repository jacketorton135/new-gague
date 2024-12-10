import tkinter as tk      # 引入 tkinter 模組，tkinter 是 Python 標準庫中用來創建 GUI 應用程式的模組
from tkinter import ttk  # 從 tkinter 模組中引入 ttk 子模組，用來創建主題化的控件
import matplotlib.pyplot as plt  # 引入 matplotlib 的 pyplot 模組，用來創建靜態或互動式的圖表
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # 引入 FigureCanvasTkAgg，用來將 Matplotlib 圖形嵌入到 Tkinter 中
import numpy as np  # 引入 numpy 模組，用來處理數值計算和數組操作
import time               # 引入 time 模組，用來進行時間相關操作，如延遲或計時
import threading       # 引入 threading 模組，用來進行多線程操作
import RPi.GPIO as GPIO  # 引入 RPi.GPIO 模組，用於控制 Raspberry Pi 的 GPIO

GPIO.setwarnings(False)  # 關閉 GPIO 警告
GPIO.setmode(GPIO.BCM)  # 設定 GPIO 的編號模式為 BCM
GPIO.setup(22, GPIO.IN)  # 設定 GPIO 22 為輸入模式

# 創建主窗口
root = tk.Tk()  # 創建一個 Tkinter 主窗口
root.title("Tkinter 與 Matplotlib 動態圖形")  # 設定窗口標題

# 創建一個 Matplotlib figure
fig, ax = plt.subplots()  # 使用 subplots 創建一個 Matplotlib figure 和子圖 (ax)

# 初始化 x_data 和 y_data
x_data = np.array([])  # x 軸數據，初始化為空數組
y_data = np.array([])  # y 軸數據，初始化為空數組
line, = ax.plot(x_data, y_data)  # 在 ax 子圖上畫出 x 和 y 數據的線條，並返回該線條對象

# Matplotlib 與 Tkinter 結合
canvas = FigureCanvasTkAgg(fig, master=root)  # 將 Matplotlib 的 figure 嵌入到 Tkinter 主窗口中
canvas.draw()  # 繪製圖形
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)  # 將畫布小部件添加到主窗口，設定為頂部對齊並填充可用空間
i=0
# 更新圖形的函數
def update_plot():
    global x_data, y_data,i  # 使用全域變數
    while True:  # 進行一個無限循環，不斷更新圖形
        value22 = GPIO.input(22)  # 讀取 GPIO 22 的值
        
        # 更新 x_data 和 y_data
        x_data = np.append(x_data, i)  # x 軸數據為當前時間
        y_data = np.append(y_data, value22)  # y 軸數據為 GPIO 22 的值
        i=i+1     
        # 如果數據超過 20 筆，則移除最前面的數據
        if len(x_data) > 20:
            x_data = x_data[1:]
            y_data = y_data[1:]
        
        # 更新圖形
        line.set_xdata(x_data)  # 更新線條的 x 軸數據
        line.set_ydata(y_data)  # 更新線條的 y 軸數據
        ax.relim()  # 重新計算數據範圍
        ax.autoscale_view()  # 自動調整視圖
        
        canvas.draw()  # 重新繪製圖形以顯示更新
        time.sleep(1)  # 暫停 1 秒，以控制更新頻率

# 啟動更新圖形的線程
thread = threading.Thread(target=update_plot)  # 創建一個新線程來執行 update_plot 函數
thread.start()  # 啟動該線程

# 按鈕的回調函數
def on_button_click():
    print("按鈕被點擊了！")  # 當按鈕被點擊時，打印一條消息到控制台

# 創建按鈕
button = ttk.Button(root, text="點我", command=on_button_click)  # 創建一個按鈕，並綁定回調函數 on_button_click
button.pack(side=tk.BOTTOM, pady=20)  # 將按鈕添加到主窗口，設定為底部對齊並設置一些內邊距

# 開始 Tkinter 主循環
root.mainloop()  # 開始 Tkinter 的主事件循環，保持窗口顯示並處理用戶交互