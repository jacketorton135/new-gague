import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, FancyArrowPatch
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button

# Function to create a gauge
def gauge(ax, value=0):
    colors = ["#2bad4e", "#eff229", "#f25829"]
    color_texts = ["LOW", "Normal", "HIGH"]

    for i in range(len(colors)):
        start_angle = 60 * i
        end_angle = 60 * (i + 1)
        wedge = Wedge((0.5, 0), 0.4, start_angle, end_angle, width=0.1, facecolor=colors[i])
        ax.add_artist(wedge)

    for i in range(len(colors)):
        mid_angle = np.radians(60 * (i + 0.5))
        x = 0.5 + 0.35 * np.cos(mid_angle)
        y = 0.35 * np.sin(mid_angle)
        ax.text(x, y, color_texts[i], ha='center', va='center', fontsize=8, color='black')

    # Create the arrow with FancyArrowPatch
    arrow = FancyArrowPatch((0.5, 0), (0.5, 0.3), mutation_scale=20, color='black', arrowstyle='-|>', linewidth=1.5)
    ax.add_patch(arrow)

    ax.set_xlim(0, 1)
    ax.set_ylim(-0.1, 0.5)
    ax.axis('off')

    return arrow

# Create the figure and axes
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
fig.delaxes(axes[1, 2])  # Remove extra subplot

arrows = []
for ax in axes.flatten()[:5]:  # Use only the first 5 subplots
    arrows.append(gauge(ax))

# Animation update function
def update(frame):
    for i, arrow in enumerate(arrows):
        # Calculate the angle for the arrow based on the frame
        angle = 180 * np.sin((frame + i * 20) * 0.1)**2
        rad = np.radians(angle)
        x_end = 0.5 + 0.3 * np.sin(rad)
        y_end = 0.3 * np.cos(rad)
        
        # Update the arrow's position and direction
        arrow.set_positions((0.5, 0), (x_end, y_end))
    return arrows

# Initialize animation
anim = FuncAnimation(fig, update, frames=100, interval=50, blit=True)

# Define button callbacks
def start_animation(event):
    global anim
    anim.event_source.start()

def stop_animation(event):
    global anim
    anim.event_source.stop()

def reset_animation(event):
    global anim
    anim.event_source.stop()
    anim.event_source.start()
    anim.event_source.stop()
    anim.event_source.start()  # Restart animation from the beginning

# Create buttons
ax_start = plt.axes([0.1, 0.02, 0.1, 0.075])
btn_start = Button(ax_start, 'Start')
btn_start.on_clicked(start_animation)

ax_stop = plt.axes([0.25, 0.02, 0.1, 0.075])
btn_stop = Button(ax_stop, 'Stop')
btn_stop.on_clicked(stop_animation)

ax_reset = plt.axes([0.4, 0.02, 0.1, 0.075])
btn_reset = Button(ax_reset, 'Reset')
btn_reset.on_clicked(reset_animation)

plt.tight_layout()
plt.show()


