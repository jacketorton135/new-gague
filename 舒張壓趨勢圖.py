import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pymysql
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

def fetch_blood_data():
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor')
    cursor = conn.cursor()
    
    try:
        # Correct the SQL query to only fetch the '舒張壓正常' (normal status) and timestamp
        sql_query = """SELECT `時間戳記`, `舒張壓正常` FROM `blood_records` ORDER BY `時間戳記` ASC"""
        print(f"Executing SQL Query: {sql_query}")
        cursor.execute(sql_query)
        result = cursor.fetchall()
        print(f"Query Result: {result}")
        
        # Convert query result to a list of tuples, where the first element is the timestamp
        # and second is the '正常' (1 or 0 indicating normal or abnormal)
        blood_data = [(mdates.date2num(row[0]), row[1]) for row in result]
        return blood_data
    except pymysql.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def plot_blood_data(ax, blood_data):
    if not blood_data:
        return

    times = [row[0] for row in blood_data]  # Timestamp in numeric format
    diastolic_normal = [row[1] for row in blood_data]  # Normal/Abnormal flag (1 or 0)

    ax.clear()

    # Plot normal/abnormal status using a step plot (square wave)
    ax.step(times, diastolic_normal, color='b', linewidth=2.5, label='Normal/Abnormal', where='post')

    # Set y-axis limits to show 0 and 1 only (normal vs abnormal)
    ax.set_ylim(-0.1, 1.1)  
    ax.set_yticks([0, 1])  # Normal and abnormal values only
    ax.set_yticklabels(['Abnormal', 'Normal'], fontsize=8)

    # Set x-axis formatting for timestamps
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=6)

    ax.set_xlabel('Time')
    ax.set_ylabel('Diastolic Pressure Status')

    # Set plot title
    ax.set_title('Diastolic Blood Pressure Normal/Abnormal Status', fontsize=14, fontweight='bold')

    # Add a legend
    ax.legend(loc='upper left')

def update_plot():
    blood_data = fetch_blood_data()
    plot_blood_data(ax, blood_data)
    canvas.draw()
    root.after(5000, update_plot)  # Update plot every 5 seconds

# Create Tkinter window
root = tk.Tk()
root.title("Real-time Diastolic Blood Pressure Status")

# Create a matplotlib figure and axis
fig, ax = plt.subplots(figsize=(10, 6))  # Set figure size
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

update_plot()  # Initial plot update

root.mainloop()



