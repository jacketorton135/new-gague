import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from matplotlib.animation import FuncAnimation

# Function to create the gauge with an animated arrow
def gauge(ax):
    colors = ["#2bad4e", "#eff229", "#f25829"]
    color_texts = ["LOW", "Normal", "HIGH"]

    # Set up background wedges
    for i in range(len(colors)):
        start_angle = 60 * i
        end_angle = 60 * (i + 1)
        wedge = Wedge((0.5, 0), 0.4, start_angle, end_angle, width=0.1, facecolor=colors[i])
        ax.add_artist(wedge)

    # Add text labels
    for i in range(len(colors)):
        mid_angle = np.radians(60 * (i + 0.5))
        x = 0.5 + 0.35 * np.cos(mid_angle)
        y = 0.35 * np.sin(mid_angle)
        ax.text(x, y, color_texts[i], ha='center', va='center', fontsize=10, color='black')

    # Set axis properties
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.1, 0.5)
    ax.axis('off')

    return ax

# Update function for the animation
def update(frame):
    global arrow
    # Remove the old arrow
    if arrow:
        arrow.remove()
    
    angle = 180 * np.sin(frame * 0.1)**2
    rad = np.radians(angle)

    # Add a new arrow with the updated position
    arrow = ax.arrow(0.5, 0, 0.3 * np.sin(rad), 0.3 * np.cos(rad), 
                     width=0.01, head_width=0.03, head_length=0.05, fc='black', ec='black')
    return arrow,

# Tkinter function to embed the animated gauge
def create_gauge_image(frame):
    global ax, arrow
    fig, ax = plt.subplots(figsize=(6, 3.5))

    gauge(ax)
    arrow = None  # Initialize arrow as None

    # Set up the animation
    anim = FuncAnimation(fig, update, frames=100, interval=50, blit=True)

    # Embed the figure in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    canvas.draw()

    return anim  # Return the animation object to keep a reference

# Tkinter main window
root = tk.Tk()
root.title("Gauge with Animated Arrow")

# Frame to hold the gauge
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# Create the gauge image and animation
create_gauge_image(frame)

# Start the Tkinter main loop
root.mainloop()



