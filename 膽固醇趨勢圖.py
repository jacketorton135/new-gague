import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pymysql
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

# Function to fetch blood data from the database
def fetch_blood_data():
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor')
    cursor = conn.cursor()
    
    try:
        # SQL query to fetch timestamp and cholesterol status
        sql_query = """SELECT `時間戳記`, `膽固醇正常` FROM `blood_records` ORDER BY `時間戳記` ASC"""
        print(f"Executing SQL Query: {sql_query}")
        cursor.execute(sql_query)
        result = cursor.fetchall()
        print(f"Query Result: {result}")
        
        # Convert the query result to a list of tuples
        blood_data = [(mdates.date2num(row[0]), row[1]) for row in result]
        return blood_data
    except pymysql.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Function to plot the blood data
def plot_blood_data(ax, blood_data):
    if not blood_data:
        return

    times = [row[0] for row in blood_data]  # Timestamp in numeric format
    cholesterol_normal = [row[1] for row in blood_data]  # Normal/Abnormal flag (1 or 0)

    ax.clear()

    # Plot the cholesterol status as a step plot (square wave)
    ax.step(times, cholesterol_normal, label='Cholesterol Status', color='g', linewidth=2.5, where='post')

    # Set y-axis limits to show 0 and 1 for normal/abnormal status
    ax.set_ylim(-0.1, 1.1)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Abnormal', 'Normal'], fontsize=8)

    # Set x-axis formatting for timestamps
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=6)

    ax.set_xlabel('Time')
    ax.set_ylabel('Cholesterol Status')

    # Set plot title
    ax.set_title('Cholesterol Status Over Time (Step Plot)', fontsize=14, fontweight='bold')

    # Add a legend
    ax.legend(loc='upper left')

# Function to update the plot every 5 seconds
def update_plot():
    blood_data = fetch_blood_data()
    plot_blood_data(ax, blood_data)
    canvas.draw()
    root.after(5000, update_plot)  # Update plot every 5 seconds

# Create Tkinter window
root = tk.Tk()
root.title("Real-time Cholesterol Status")

# Create a matplotlib figure and axis
fig, ax = plt.subplots(figsize=(10, 6))  # Set figure size
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

# Initial plot update and periodic updates every 5 seconds
update_plot()

# Start the Tkinter main loop
root.mainloop()


