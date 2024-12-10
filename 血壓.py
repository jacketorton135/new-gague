import pymysql
import csv
import requests
from io import StringIO
from datetime import datetime

# 1. Download the CSV from Google Sheets
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT4lrpABu1Cfv5Ow4fWrNzJj-FdEGxpaJA-O82pEdtRut2RbLnJLzUwWjftBv2TR9I2joZJVq8a9c0c/pub?output=csv"
response = requests.get(csv_url)

# Check if the request was successful
if response.status_code == 200:
    csv_data = response.text
else:
    print("Failed to download CSV data.")
    exit(1)

# 2. Establish a connection to the MySQL database
conn = pymysql.connect(host='localhost', port=3306, user='root', password='oneokrock12345', database='heart rate monitor', charset='utf8mb4')
cursor = conn.cursor()

# Table name
table_name = 'blood'

# 3. Parse the CSV data
# Use 'utf-8-sig' to better handle BOM or special characters
csv_reader = csv.reader(StringIO(response.content.decode('utf-8-sig')))

# Skip the header row if necessary
next(csv_reader)

# 4. Helper function to convert timestamp format to MySQL-compatible format
def convert_timestamp(timestamp_str):
    try:
        # Check if the timestamp has "上午" or "下午"
        if "上午" in timestamp_str or "下午" in timestamp_str:
            # Remove "上午"/"下午"
            timestamp_str = timestamp_str.replace("上午", "").replace("下午", "")
            
            # Check if it's "下午" and adjust the hour accordingly
            if "下午" in timestamp_str:
                time_obj = datetime.strptime(timestamp_str, "%Y/%m/%d %I:%M:%S")  # Using %I for 12-hour format with AM/PM
                return time_obj.strftime("%Y-%m-%d %H:%M:%S")  # Convert to 24-hour format
            else:
                time_obj = datetime.strptime(timestamp_str, "%Y/%m/%d %I:%M:%S")
                return time_obj.strftime("%Y-%m-%d %H:%M:%S")  # 24-hour format for AM

        else:
            # Fallback to "YYYY-MM-DD HH:MM:SS" format
            return datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    
    except ValueError:
        # If conversion fails, return None
        return None

# 5. Insert data into MySQL
for row in csv_reader:
    # Assuming the order of columns in the CSV is: Timestamp, Diastolic, Systolic, Pulse
    timestamp, diastolic, systolic, pulse = row
    
    # Convert the timestamp format
    timestamp = convert_timestamp(timestamp)
    
    if not timestamp:
        print(f"Invalid timestamp format for row: {row}")
        continue  # Skip this row if the timestamp is invalid

    # Validate that the diastolic, systolic, and pulse are valid integers
    try:
        diastolic = int(diastolic)
        systolic = int(systolic)
        pulse = int(pulse)
    except ValueError:
        print(f"Invalid numeric values for row: {row}")
        continue  # Skip this row if the values are not valid integers
    
    # Prepare your SQL insert statement
    insert_query = f"""
    INSERT INTO {table_name} (`時間戳記`, `舒張壓`, `收縮壓`, `脈搏`)
    VALUES (%s, %s, %s, %s);
    """

    # Insert the row into the database
    try:
        cursor.execute(insert_query, (timestamp, diastolic, systolic, pulse))
    except pymysql.MySQLError as e:
        print(f"Error inserting row {row}: {e}")
        continue

# Commit changes to the database
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()

print("Data successfully inserted into the database.")





