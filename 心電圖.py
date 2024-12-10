import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# 配置串行端口
ser = serial.Serial('/dev/ttyUSB0', 9600)  # 確保這裡的COM端口與Arduino使用的端口相同

# 用於儲存數據的列表
data_list = []

# 設置圖形
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)

# 設置x軸和y軸的範圍
ax.set_xlim(0, 300)
ax.set_ylim(0, 400)
ax.set_title('Heartbeat Data')
ax.set_xlabel('Time')
ax.set_ylabel('Signal')

# 更新圖形的函數
def update(frame):
    global data_list
    line.set_ydata(data_list)
    line.set_xdata(range(len(data_list)))
    return line,

# 初始化函數
def init():
    line.set_ydata([])
    line.set_xdata([])
    return line,

# 動畫函數
def animate(i):
    global data_list
    while ser.in_waiting:
        data = ser.readline().decode('utf-8').strip()
        if 'S' in data:
            data_list = []
        else:
            try:
                data_list.append(int(data))
                if len(data_list) > 300:
                    data_list.pop(0)
            except ValueError:
                pass
    return line,

ani = animation.FuncAnimation(fig, animate, init_func=init, interval=50, blit=True)

plt.show()
