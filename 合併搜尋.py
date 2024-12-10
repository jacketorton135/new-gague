import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime

class UnifiedHealthApp:
    def __init__(self, master):
        self.master = master
        self.master.title("健康紀錄系統")

        # Database connection
        self.connect_to_database()

        # 創造 notebook for tabs
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(pady=10, expand=True)

        # 創造 tabs for Heart Rate, BMI, and DHT11
        self.create_heart_rate_tab()
        self.create_bmi_tab()
        self.create_dht11_tab()
        self.create_blood_tab()

    def connect_to_database(self):
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',
                password='oneokrock12345',
                database='heart rate monitor'
            )
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫連接錯誤", f"無法連接到資料庫: {err}")
            self.master.destroy()
            return

    # Heart Rate Tab
    def create_heart_rate_tab(self):
        heart_rate_frame = ttk.Frame(self.notebook)
        self.notebook.add(heart_rate_frame, text="心跳紀錄")

        self.heart_rate_columns = ['時間戳記', '心跳', '心跳狀態', '心跳_正常_異常']
        self.heart_rate_entries = {}

        for i, field in enumerate(self.heart_rate_columns):
            ttk.Label(heart_rate_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            if field == '心跳_正常_異常':
                self.heart_rate_entries[field] = ttk.Combobox(heart_rate_frame, values=['0', '1'])
            else:
                self.heart_rate_entries[field] = ttk.Entry(heart_rate_frame)
            self.heart_rate_entries[field].grid(row=i, column=1, padx=5, pady=5)

        ttk.Button(heart_rate_frame, text="新增", command=self.add_heart_rate_record).grid(row=len(self.heart_rate_columns)+1, column=0, padx=5, pady=5)
        ttk.Button(heart_rate_frame, text="更新", command=self.update_heart_rate_record).grid(row=len(self.heart_rate_columns)+1, column=1, padx=5, pady=5)
        ttk.Button(heart_rate_frame, text="刪除", command=self.delete_heart_rate_record).grid(row=len(self.heart_rate_columns)+1, column=2, padx=5, pady=5)

        self.heart_rate_tree = ttk.Treeview(heart_rate_frame, columns=self.heart_rate_columns, show="headings")
        self.heart_rate_tree.grid(row=len(self.heart_rate_columns)+2, column=0, columnspan=3, padx=5, pady=5)

        for col in self.heart_rate_columns:
            self.heart_rate_tree.heading(col, text=col)
            self.heart_rate_tree.column(col, width=100)

        self.heart_rate_tree.bind('<<TreeviewSelect>>', self.heart_rate_item_selected)
        self.load_heart_rate_data()

        # Search section
        self.heart_rate_search_entry = ttk.Entry(heart_rate_frame)
        self.heart_rate_search_entry.grid(row=len(self.heart_rate_columns)+3, column=0, padx=5, pady=5)
        ttk.Button(heart_rate_frame, text="搜尋", command=self.search_heart_rate_record).grid(row=len(self.heart_rate_columns)+3, column=1, padx=5, pady=5)

    def load_heart_rate_data(self):
        for item in self.heart_rate_tree.get_children():
            self.heart_rate_tree.delete(item)

        try:
            self.cursor.execute("SELECT 時間戳記, 心跳, 心跳狀態, 心跳_正常_異常 FROM heart_rate")
            rows = self.cursor.fetchall()
            for row in rows:
                self.heart_rate_tree.insert("", "end", values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法載入資料: {err}")

    def add_heart_rate_record(self):
        values = [self.heart_rate_entries[field].get() for field in self.heart_rate_columns]
        try:
            converted_values = self.validate_and_convert_data(values, self.heart_rate_columns)
            sql = "INSERT INTO heart_rate (時間戳記, 心跳, 心跳狀態, 心跳_正常_異常) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(sql, converted_values)
            self.conn.commit()
            self.load_heart_rate_data()
            messagebox.showinfo("成功", "心跳記錄已新增")
        except ValueError as err:
            messagebox.showerror("輸入錯誤", str(err))
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法新增心跳記錄: {err}")

    def update_heart_rate_record(self):
        selected_items = self.heart_rate_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇一條記錄")
            return

        values = [self.heart_rate_entries[field].get() for field in self.heart_rate_columns]
        try:
            converted_values = self.validate_and_convert_data(values, self.heart_rate_columns)
            sql = "UPDATE heart_rate SET 心跳 = %s, 心跳狀態 = %s, 心跳_正常_異常 = %s WHERE 時間戳記 = %s"
            self.cursor.execute(sql, [converted_values[1], converted_values[2], converted_values[3], converted_values[0]])
            self.conn.commit()
            self.load_heart_rate_data()
            messagebox.showinfo("成功", "心跳記錄已更新")
        except ValueError as err:
            messagebox.showerror("輸入錯誤", str(err))
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法更新心跳記錄: {err}")

    def delete_heart_rate_record(self):
        selected_items = self.heart_rate_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇一條記錄")
            return

        values = self.heart_rate_tree.item(selected_items[0])['values']
        try:
            sql = "DELETE FROM heart_rate WHERE 時間戳記 = %s"
            self.cursor.execute(sql, (values[0],))
            self.conn.commit()
            self.load_heart_rate_data()
            messagebox.showinfo("成功", "心跳記錄已刪除")
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法刪除心跳記錄: {err}")

    def search_heart_rate_record(self):
        search_value = self.heart_rate_search_entry.get().strip()
        if not search_value:
            messagebox.showwarning("警告", "請輸入搜尋條件")
            return

        for item in self.heart_rate_tree.get_children():
            self.heart_rate_tree.delete(item)

        try:
            if search_value.lower() in ['正常', '0']:
                sql = "SELECT 時間戳記, 心跳, 心跳狀態, 心跳_正常_異常 FROM heart_rate WHERE 心跳_正常_異常 = 0"
                self.cursor.execute(sql)
            elif search_value.lower() in ['異常', '1']:
                sql = "SELECT 時間戳記, 心跳, 心跳狀態, 心跳_正常_異常 FROM heart_rate WHERE 心跳_正常_異常 = 1"
                self.cursor.execute(sql)
            elif '-' in search_value:  # 假設是日期格式 (例如: 07-14)
                sql = "SELECT 時間戳記, 心跳, 心跳狀態, 心跳_正常_異常 FROM heart_rate WHERE DATE_FORMAT(時間戳記, '%m-%d') = %s"
                self.cursor.execute(sql, (search_value,))
            elif search_value.isdigit() and len(search_value) == 4:  # 假設是年份
                sql = "SELECT 時間戳記, 心跳, 心跳狀態, 心跳_正常_異常 FROM heart_rate WHERE YEAR(時間戳記) = %s"
                self.cursor.execute(sql, (search_value,))
            else:
                sql = "SELECT 時間戳記, 心跳, 心跳狀態, 心跳_正常_異常 FROM heart_rate WHERE 時間戳記 LIKE %s OR 心跳 LIKE %s OR 心跳狀態 LIKE %s"
                self.cursor.execute(sql, (f'%{search_value}%', f'%{search_value}%', f'%{search_value}%'))

            rows = self.cursor.fetchall()

            if rows:
                for row in rows:
                    # 將 bit(1) 轉換為更易讀的格式
                    normal_abnormal = '正常' if row[3] == 0 else '1'
                    display_row = list(row[:3]) + [normal_abnormal]
                    self.heart_rate_tree.insert("", "end", values=display_row)
            else:
                messagebox.showinfo("搜尋結果", "沒有找到相關的心跳記錄")
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"搜尋時出錯: {err}")

    def heart_rate_item_selected(self, event):
        selected_item = self.heart_rate_tree.selection()
        if selected_item:
            item_data = self.heart_rate_tree.item(selected_item)
            values = item_data['values']
            if values:
                for i, field in enumerate(self.heart_rate_columns):
                    self.heart_rate_entries[field].delete(0, tk.END)
                    self.heart_rate_entries[field].insert(0, values[i])


    def create_blood_tab(self):
        blood_frame = ttk.Frame(self.notebook)
        self.notebook.add(blood_frame, text="血壓血糖膽固醇")

        self.blood_columns = [
            '時間戳記', '舒張壓', '收縮壓', '血糖', '膽固醇', '脈搏',
            '舒張壓狀態', '收縮壓狀態', '血糖狀態', '膽固醇狀態', '脈搏狀態',
            '舒張壓正常', '收縮壓正常', '血糖正常', '膽固醇正常', '脈搏正常'
        ]
        self.blood_entries = {}

        for i, field in enumerate(self.blood_columns):
            ttk.Label(blood_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            if field in ['舒張壓正常', '收縮壓正常', '血糖正常', '膽固醇正常', '脈搏正常']:
                self.blood_entries[field] = ttk.Combobox(blood_frame, values=['0', '1'])
            else:
                self.blood_entries[field] = ttk.Entry(blood_frame)
            self.blood_entries[field].grid(row=i, column=1, padx=5, pady=5)

        ttk.Button(blood_frame, text="新增", command=self.add_blood_record).grid(row=len(self.blood_columns)+1, column=0, padx=5, pady=5)
        ttk.Button(blood_frame, text="更新", command=self.update_blood_record).grid(row=len(self.blood_columns)+1, column=1, padx=5, pady=5)
        ttk.Button(blood_frame, text="刪除", command=self.delete_blood_record).grid(row=len(self.blood_columns)+1, column=2, padx=5, pady=5)

        self.blood_tree = ttk.Treeview(blood_frame, columns=self.blood_columns, show="headings")
        self.blood_tree.grid(row=len(self.blood_columns)+2, column=0, columnspan=3, padx=5, pady=5)

        for col in self.blood_columns:
            self.blood_tree.heading(col, text=col)
            self.blood_tree.column(col, width=100)

        self.blood_tree.bind('<<TreeviewSelect>>', self.blood_item_selected)
        self.load_blood_data()

        # Search section
    def create_blood_tab(self):
        blood_frame = ttk.Frame(self.notebook)
        self.notebook.add(blood_frame, text="血壓血糖膽固醇")

        self.blood_columns = [
            '時間戳記', '舒張壓', '收縮壓', '血糖', '膽固醇', '脈搏',
            '舒張壓狀態', '收縮壓狀態', '血糖狀態', '膽固醇狀態', '脈搏狀態',
            '舒張壓正常', '收縮壓正常', '血糖正常', '膽固醇正常', '脈搏正常'
        ]
        self.blood_entries = {}

        for i, field in enumerate(self.blood_columns):
            ttk.Label(blood_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            if field in ['舒張壓正常', '收縮壓正常', '血糖正常', '膽固醇正常', '脈搏正常']:
                self.blood_entries[field] = ttk.Combobox(blood_frame, values=['0', '1'])
            else:
                self.blood_entries[field] = ttk.Entry(blood_frame)
            self.blood_entries[field].grid(row=i, column=1, padx=5, pady=5)

        ttk.Button(blood_frame, text="新增", command=self.add_blood_record).grid(row=len(self.blood_columns)+1, column=0, padx=5, pady=5)
        ttk.Button(blood_frame, text="更新", command=self.update_blood_record).grid(row=len(self.blood_columns)+1, column=1, padx=5, pady=5)
        ttk.Button(blood_frame, text="刪除", command=self.delete_blood_record).grid(row=len(self.blood_columns)+1, column=2, padx=5, pady=5)

        self.blood_tree = ttk.Treeview(blood_frame, columns=self.blood_columns, show="headings", height=6)  # 設置顯示 6 行
        self.blood_tree.grid(row=len(self.blood_columns)+2, column=0, columnspan=3, padx=5, pady=5)


        for col in self.blood_columns:
            self.blood_tree.heading(col, text=col)
            self.blood_tree.column(col, width=100)

        self.blood_tree.bind('<<TreeviewSelect>>', self.blood_item_selected)
        self.load_blood_data()

        # Search section
        self.blood_search_entry = ttk.Entry(blood_frame)
        self.blood_search_entry.grid(row=len(self.blood_columns)+3, column=0, padx=5, pady=5)
        ttk.Button(blood_frame, text="搜尋", command=self.search_blood_record).grid(row=len(self.blood_columns)+3, column=1, padx=3, pady=3)


    def load_blood_data(self):
        for item in self.blood_tree.get_children():
            self.blood_tree.delete(item)

        try:
            self.cursor.execute("SELECT 時間戳記, 舒張壓, 收縮壓, 血糖, 膽固醇, 脈搏, "
                                "舒張壓狀態, 收縮壓狀態, 血糖狀態, 膽固醇狀態, 脈搏狀態, "
                                "舒張壓正常, 收縮壓正常, 血糖正常, 膽固醇正常, 脈搏正常 FROM blood_records ")
            rows = self.cursor.fetchall()
            for row in rows:
                self.blood_tree.insert("", "end", values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法載入資料: {err}")


    def add_blood_record(self):
        values = [self.blood_entries[field].get() for field in self.blood_columns]
        try:
            # Validate and convert data here, e.g. ensure float or int as needed
            converted_values = self.validate_and_convert_data(values, self.blood_columns)
            sql = "INSERT INTO blood_records (時間戳記, 舒張壓, 收縮壓, 血糖, 膽固醇, 脈搏, " \
                "舒張壓狀態, 收縮壓狀態, 血糖狀態, 膽固醇狀態, 脈搏狀態, " \
                "舒張壓正常, 收縮壓正常, 血糖正常, 膽固醇正常, 脈搏正常) VALUES (%s, %s, %s, %s, %s, %s, " \
                "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            self.cursor.execute(sql, converted_values)
            self.conn.commit()
            self.load_blood_data()
            messagebox.showinfo("成功", "血液記錄已新增")
        except ValueError as err:
            messagebox.showerror("輸入錯誤", str(err))
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法新增血液記錄: {err}")


    def update_blood_record(self):
        selected_items = self.blood_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇一條記錄")
            return

        values = [self.blood_entries[field].get() for field in self.blood_columns]
        try:
            converted_values = self.validate_and_convert_data(values, self.blood_columns)
            sql = "UPDATE blood_records SET 舒張壓 = %s, 收縮壓 = %s, 血糖 = %s, 膽固醇 = %s, 脈搏 = %s, " \
                "舒張壓狀態 = %s, 收縮壓狀態 = %s, 血糖狀態 = %s, 膽固醇狀態 = %s, 脈搏狀態 = %s, " \
                "舒張壓正常 = %s, 收縮壓正常 = %s, 血糖正常 = %s, 膽固醇正常 = %s, 脈搏正常 = %s WHERE 時間戳記 = %s"
            self.cursor.execute(sql, [*converted_values[1:], converted_values[0]])
            self.conn.commit()
            self.load_blood_data()
            messagebox.showinfo("成功", "血液記錄已更新")
        except ValueError as err:
            messagebox.showerror("輸入錯誤", str(err))
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法更新血液記錄: {err}")


    def delete_blood_record(self):
        selected_items = self.blood_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇一條記錄")
            return

        values = self.blood_tree.item(selected_items[0])['values']
        try:
            sql = "DELETE FROM blood_records WHERE 時間戳記 = %s"
            self.cursor.execute(sql, (values[0],))
            self.conn.commit()
            self.load_blood_data()
            messagebox.showinfo("成功", "血液記錄已刪除")
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法刪除血液記錄: {err}")


    def search_blood_record(self):
        search_value = self.blood_search_entry.get().strip()
        if not search_value:
            messagebox.showwarning("警告", "請輸入搜尋條件")
            return

        for item in self.blood_tree.get_children():
            self.blood_tree.delete(item)

        try:
            # Search query logic here
            sql = f"SELECT 時間戳記, 舒張壓, 收縮壓, 血糖, 膽固醇, 脈搏, " \
                f"舒張壓狀態, 收縮壓狀態, 血糖狀態, 膽固醇狀態, 脈搏狀態, " \
                f"舒張壓正常, 收縮壓正常, 血糖正常, 膽固醇正常, 脈搏正常 FROM blood_records WHERE " \
                f"時間戳記 LIKE %s OR 血糖 LIKE %s"
            self.cursor.execute(sql, (f"%{search_value}%", f"%{search_value}%"))
            rows = self.cursor.fetchall()

            if rows:
                for row in rows:
                    self.blood_tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("搜尋結果", "沒有找到相關的血液記錄")
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"搜尋時出錯: {err}")


    def blood_item_selected(self, event):
        selected_item = self.blood_tree.selection()
        if selected_item:
            item_data = self.blood_tree.item(selected_item)
            values = item_data['values']
            if values:
                for i, field in enumerate(self.blood_columns):
                    self.blood_entries[field].delete(0, tk.END)
                    self.blood_entries[field].insert(0, values[i])

    # BMI Tab
    def create_bmi_tab(self):
        bmi_frame = ttk.Frame(self.notebook)
        self.notebook.add(bmi_frame, text="BMI 紀錄")

        self.bmi_columns = ['時間戳記', '姓名', '性別', '身高', '體重', 'BMI', '標準體重', '檢查結果', '正常_異常']
        self.bmi_entries = {}

        for i, field in enumerate(self.bmi_columns):
            ttk.Label(bmi_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            if field == '正常_異常':
                self.bmi_entries[field] = ttk.Combobox(bmi_frame, values=['0', '1'])
            elif field == '性別':
                self.bmi_entries[field] = ttk.Combobox(bmi_frame, values=['男', '女'])
            else:
                self.bmi_entries[field] = ttk.Entry(bmi_frame)
            self.bmi_entries[field].grid(row=i, column=1, padx=5, pady=5)

        ttk.Button(bmi_frame, text="新增", command=self.add_bmi_record).grid(row=len(self.bmi_columns)+1, column=0, padx=5, pady=5)
        ttk.Button(bmi_frame, text="更新", command=self.update_bmi_record).grid(row=len(self.bmi_columns)+1, column=1, padx=5, pady=5)
        ttk.Button(bmi_frame, text="刪除", command=self.delete_bmi_record).grid(row=len(self.bmi_columns)+1, column=2, padx=5, pady=5)

        self.bmi_tree = ttk.Treeview(bmi_frame, columns=self.bmi_columns, show="headings")
        self.bmi_tree.grid(row=len(self.bmi_columns)+2, column=0, columnspan=3, padx=5, pady=5)

        for col in self.bmi_columns:
            self.bmi_tree.heading(col, text=col)
            self.bmi_tree.column(col, width=100)

        self.bmi_tree.bind('<<TreeviewSelect>>', self.bmi_item_selected)
        self.load_bmi_data()

        # Search section
        self.bmi_search_entry = ttk.Entry(bmi_frame)
        self.bmi_search_entry.grid(row=len(self.bmi_columns)+3, column=0, padx=5, pady=5)
        ttk.Button(bmi_frame, text="搜尋", command=self.search_bmi_record).grid(row=len(self.bmi_columns)+3, column=1, padx=5, pady=5)

    def load_bmi_data(self):
        for item in self.bmi_tree.get_children():
            self.bmi_tree.delete(item)

        try:
            self.cursor.execute("SELECT 時間戳記, 姓名, 性別, 身高, 體重, BMI, 標準體重, 檢查結果, 正常_異常 FROM bmi")
            rows = self.cursor.fetchall()
            for row in rows:
                self.bmi_tree.insert("", "end", values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法載入資料: {err}")

    def add_bmi_record(self):
        values = [self.bmi_entries[field].get() for field in self.bmi_columns]
        try:
            converted_values = self.validate_and_convert_data(values, self.bmi_columns)
            sql = """INSERT INTO bmi (時間戳記, 姓名, 性別, 身高, 體重, BMI, 標準體重, 檢查結果, 正常_異常) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(sql, converted_values)
            self.conn.commit()
            self.load_bmi_data()
            messagebox.showinfo("成功", "BMI 記錄已新增")
        except ValueError as err:
            messagebox.showerror("輸入錯誤", str(err))
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法新增 BMI 記錄: {err}")

    # 同樣修改 update_bmi_record 和 delete_bmi_record

    def update_bmi_record(self):
        selected_items = self.bmi_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇一條記錄")
            return

        values = [self.bmi_entries[field].get() for field in self.bmi_columns]
        try:
            converted_values = self.validate_and_convert_data(values, self.bmi_columns)
            sql = """UPDATE bmi SET 姓名 = %s, 性別 = %s, 身高 = %s, 體重 = %s, BMI = %s, 
                     標準體重 = %s, 檢查結果 = %s, 正常_異常 = %s WHERE 時間戳記 = %s"""
            self.cursor.execute(sql, converted_values[1:] + [converted_values[0]])
            self.conn.commit()
            self.load_bmi_data()
            messagebox.showinfo("成功", "BMI 記錄已更新")
        except ValueError as err:
            messagebox.showerror("輸入錯誤", str(err))
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法更新 BMI 記錄: {err}")

    def delete_bmi_record(self):
        selected_items = self.bmi_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇一條記錄")
            return

        values = self.bmi_tree.item(selected_items[0])['values']
        try:
            sql = "DELETE FROM bmi WHERE 時間戳記 = %s"
            self.cursor.execute(sql, (values[0],))
            self.conn.commit()
            self.load_bmi_data()
            messagebox.showinfo("成功", "BMI 記錄已刪除")
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法刪除 BMI 記錄: {err}")

    def search_bmi_record(self):
        search_value = self.bmi_search_entry.get().strip()
        if not search_value:
            messagebox.showwarning("警告", "請輸入搜尋條件")
            return

        for item in self.bmi_tree.get_children():
            self.bmi_tree.delete(item)

        try:
            sql = """SELECT 時間戳記, 姓名, 性別, 身高, 體重, BMI, 標準體重, 檢查結果, 正常_異常 
                     FROM bmi WHERE 時間戳記 LIKE %s OR 姓名 LIKE %s OR 性別 LIKE %s"""
            self.cursor.execute(sql, (f'%{search_value}%', f'%{search_value}%', f'%{search_value}%'))
            rows = self.cursor.fetchall()

            if rows:
                for row in rows:
                    self.bmi_tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("搜尋結果", "沒有找到相關的 BMI 記錄")
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"搜尋時出錯: {err}")

    # DHT11 Tab
    def create_dht11_tab(self):
        dht11_frame = ttk.Frame(self.notebook)
        self.notebook.add(dht11_frame, text="環境溫濕度體溫紀錄")

        self.dht11_columns = ['時間戳記', '溫度', '濕度', '溫度狀態', '濕度狀態', '溫度_正常_異常', '濕度_正常_異常', '體溫', '體溫狀態', '體溫_正常_異常']
        self.dht11_entries = {}

        for i, field in enumerate(self.dht11_columns):
            ttk.Label(dht11_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            if '_正常_異常' in field:
                self.dht11_entries[field] = ttk.Combobox(dht11_frame, values=['0', '1'])
            else:
                self.dht11_entries[field] = ttk.Entry(dht11_frame)
            self.dht11_entries[field].grid(row=i, column=1, padx=5, pady=5)

        ttk.Button(dht11_frame, text="新增", command=self.add_dht11_record).grid(row=len(self.dht11_columns)+1, column=0, padx=5, pady=5)
        ttk.Button(dht11_frame, text="更新", command=self.update_dht11_record).grid(row=len(self.dht11_columns)+1, column=1, padx=5, pady=5)
        ttk.Button(dht11_frame, text="刪除", command=self.delete_dht11_record).grid(row=len(self.dht11_columns)+1, column=2, padx=5, pady=5)

        self.dht11_tree = ttk.Treeview(dht11_frame, columns=self.dht11_columns, show="headings")
        self.dht11_tree.grid(row=len(self.dht11_columns)+2, column=0, columnspan=3, padx=5, pady=5)

        for col in self.dht11_columns:
            self.dht11_tree.heading(col, text=col)
            self.dht11_tree.column(col, width=100)

        self.dht11_tree.bind('<<TreeviewSelect>>', self.dht11_item_selected)
        self.load_dht11_data()

        # Search section
        self.dht11_search_entry = ttk.Entry(dht11_frame)
        self.dht11_search_entry.grid(row=len(self.dht11_columns)+3, column=0, padx=5, pady=5)
        ttk.Button(dht11_frame, text="搜尋", command=self.search_dht11_record).grid(row=len(self.dht11_columns)+3, column=1, padx=5, pady=5)

    def load_dht11_data(self):
        for item in self.dht11_tree.get_children():
            self.dht11_tree.delete(item)

        try:
            self.cursor.execute("""SELECT 時間戳記, 溫度, 濕度, 溫度狀態, 濕度狀態, 溫度_正常_異常, 濕度_正常_異常, 
                                   體溫, 體溫狀態, 體溫_正常_異常 FROM dht11""")
            rows = self.cursor.fetchall()
            for row in rows:
                self.dht11_tree.insert("", "end", values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法載入資料: {err}")

    def add_dht11_record(self):
        values = [self.dht11_entries[field].get() for field in self.dht11_columns]
        try:
            converted_values = self.validate_and_convert_data(values, self.dht11_columns)
            sql = """INSERT INTO dht11 (時間戳記, 溫度, 濕度, 溫度狀態, 濕度狀態, 溫度_正常_異常, 濕度_正常_異常, 
                    體溫, 體溫狀態, 體溫_正常_異常) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(sql, converted_values)
            self.conn.commit()
            self.load_dht11_data()
            messagebox.showinfo("成功", "DHT11 記錄已新增")
        except ValueError as err:
            messagebox.showerror("輸入錯誤", str(err))
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法新增 DHT11 記錄: {err}")

    # 同樣修改 update_dht11_record 和 delete_dht11_record

    def update_dht11_record(self):
        selected_items = self.dht11_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇一條記錄")
            return

        values = [self.dht11_entries[field].get() for field in self.dht11_columns]
        try:
            converted_values = self.validate_and_convert_data(values, self.dht11_columns)
            sql = "UPDATE dht11 SET 溫度 = %s, 濕度 = %s, 溫度狀態 = %s, 濕度狀態 = %s WHERE 時間戳記 = %s"
            self.cursor.execute(sql, converted_values[1:] + [converted_values[0]])
            self.conn.commit()
            self.load_dht11_data()
            messagebox.showinfo("成功", "DHT11 記錄已更新")
        except ValueError as err:
            messagebox.showerror("輸入錯誤", str(err))
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法更新 DHT11 記錄: {err}")

    def delete_dht11_record(self):
        selected_items = self.dht11_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇一條記錄")
            return

        values = self.dht11_tree.item(selected_items[0])['values']
        try:
            sql = "DELETE FROM dht11 WHERE 時間戳記 = %s"
            self.cursor.execute(sql, (values[0],))
            self.conn.commit()
            self.load_dht11_data()
            messagebox.showinfo("成功", "DHT11 記錄已刪除")
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法刪除 DHT11 記錄: {err}")

    def search_dht11_record(self):
        search_value = self.dht11_search_entry.get().strip()
        if not search_value:
            messagebox.showwarning("警告", "請輸入搜尋條件")
            return

        for item in self.dht11_tree.get_children():
            self.dht11_tree.delete(item)

        try:
            sql = "SELECT 時間戳記, 溫度, 濕度, 溫度狀態, 濕度狀態 FROM dht11 WHERE 時間戳記 LIKE %s OR 溫度 LIKE %s OR 濕度 LIKE %s"
            self.cursor.execute(sql, (f'%{search_value}%', f'%{search_value}%', f'%{search_value}%'))
            rows = self.cursor.fetchall()

            if rows:
                for row in rows:
                    self.dht11_tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("搜尋結果", "沒有找到相關的 DHT11 記錄")
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"搜尋時出錯: {err}")

    def validate_and_convert_data(self, values, columns):
        converted_values = []
        for i, value in enumerate(values):
            if columns[i] == '時間戳記':
                try:
                    converted_values.append(datetime.strptime(value, '%Y-%m-%d %H:%M:%S'))
                except ValueError:
                    raise ValueError("無效的時間格式，請使用 YYYY-MM-DD HH:MM:SS")
            elif columns[i] in ['溫度', '濕度', '身高', '體重', 'BMI', '標準體重', '體溫']:
                try:
                    converted_values.append(float(value))
                except ValueError:
                    raise ValueError(f"{columns[i]} 應該是數字")
            elif columns[i] == '心跳':
                try:
                    converted_values.append(int(value))
                except ValueError:
                    raise ValueError("心跳應該是整數")
            elif '_正常_異常' in columns[i] or columns[i] == '正常異常':
                converted_values.append(1 if value in [1, '1', 'True', 'true', 'Yes', 'yes'] else 0)
            else:
                converted_values.append(value)
        return converted_values

    def bmi_item_selected(self, event):
        selected_item = self.bmi_tree.selection()
        if selected_item:
            item_data = self.bmi_tree.item(selected_item)
            values = item_data['values']
            if values:
                self.bmi_entries['時間戳記'].delete(0, tk.END)
                self.bmi_entries['時間戳記'].insert(0, values[0])

                self.bmi_entries['BMI'].delete(0, tk.END)
                self.bmi_entries['BMI'].insert(0, values[1])

    def dht11_item_selected(self, event):
        selected_item = self.dht11_tree.selection()
        if selected_item:
            item_data = self.dht11_tree.item(selected_item)
            values = item_data['values']
            if values:
                for i, field in enumerate(self.dht11_columns):
                    self.dht11_entries[field].delete(0, tk.END)
                    self.dht11_entries[field].insert(0, values[i])

if __name__ == "__main__":
    root = tk.Tk()
    app = UnifiedHealthApp(root)
    root.mainloop()
