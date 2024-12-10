import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pymysql
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

def fetch_temperature_status():
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor')
    cursor = conn.cursor()
    
    try:
        # Query '溫度_正常_異常' column and timestamp
        sql_query = "SELECT 溫度_正常_異常, 時間戳記 FROM dht11 ORDER BY 時間戳記 ASC"
        cursor.execute(sql_query)
        result = cursor.fetchall()
        
        # Convert results to list, ignoring rows where 溫度_正常_異常 is None
        status_list = [(int.from_bytes(row[0], 'big'), row[1]) for row in result if row[0] is not None]
        return status_list
    except pymysql.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def plot_temperature_status(ax, temperature_status):
    if not temperature_status:
        return

    times = [row[1] for row in temperature_status]
    statuses = [row[0] for row in temperature_status]

    # Add an additional timestamp to the times list
    if len(times) > 0:
        extra_time = times[-1] + datetime.timedelta(seconds=1)
        times.append(extra_time)

    ax.clear()
    ax.stairs(statuses, times, linewidth=2.5)

    ax.set_ylim(0.1, 0.9)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Normal', 'Error'], fontsize=8)

    # Set x-axis formatting
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

    # Rotate x-axis labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=6)

    ax.set_xlabel('Time')
    ax.set_ylabel('Status')
    ax.set_title('Temperature Status Over Time')

def update_plot():
    temperature_status = fetch_temperature_status()
    plot_temperature_status(ax, temperature_status)
    canvas.draw()
    root.after(5000, update_plot)  # Update every 5 seconds

# Create Tkinter window
root = tk.Tk()
root.title("Real-time Temperature Status")

fig, ax = plt.subplots(figsize=(10, 6))  # Adjust figure size
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

update_plot()  # Initial call to update function

root.mainloop()  # Start the Tkinter event loop



