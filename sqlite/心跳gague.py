import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from matplotlib.animation import FuncAnimation

def gauge(ax, value=0):
    colors = ["#2bad4e", "#eff229", "#f25829"]
    color_texts = ["LOW", "Normal", "HIGH"]

    # 設置背景扇形，每個顏色占60度
    for i in range(len(colors)):
        start_angle = 60 * i
        end_angle = 60 * (i + 1)
        wedge = Wedge((0.5, 0), 0.4, start_angle, end_angle, width=0.1, facecolor=colors[i])
        ax.add_artist(wedge)

    # 添加標籤
    for i in range(len(colors)):
        mid_angle = np.radians(60 * (i + 0.5))
        x = 0.5 + 0.35 * np.cos(mid_angle)
        y = 0.35 * np.sin(mid_angle)
        ax.text(x, y, color_texts[i], ha='center', va='center', fontsize=10, color='black')

    # 添加指針
    arrow = ax.arrow(0.5, 0, 0, 0.3, width=0.01, head_width=0.03, head_length=0.05, fc='black', ec='black')

    # 設置軸的屬性
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.1, 0.5)
    ax.axis('off')

    return arrow

fig, ax = plt.subplots(figsize=(6, 3.5))

arrow = gauge(ax)

def update(frame):
    # 計算新的角度 (在0到180度之間)
    angle = 180 * np.sin(frame * 0.1)**2
    # 將角度轉換為弧度
    rad = np.radians(angle)
    # 更新箭頭位置
    arrow.set_data(x=0.5, y=0, dx=0.3*np.sin(rad), dy=0.3*np.cos(rad))
    return arrow,

anim = FuncAnimation(fig, update, frames=100, interval=50, blit=True)

plt.tight_layout()
plt.show()