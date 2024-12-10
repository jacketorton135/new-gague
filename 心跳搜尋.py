import tkinter as tk  # 導入 tkinter 模組以創建 GUI
from tkinter import ttk, messagebox  # 導入 ttk 元件和訊息框
import mysql.connector  # 導入 MySQL 連接模組
from datetime import datetime  # 導入 datetime 用於處理日期時間

class HeartRateApp:
    def __init__(self, master):
        self.master = master  # 保存主窗口參考
        self.master.title("心跳紀錄系統")  # 設置窗口標題

        # 資料庫連接
        try:
            self.conn = mysql.connector.connect(
                host='localhost',  # 資料庫主機
                port=3306,  # 資料庫端口
                user='root',  # 資料庫用戶名
                password='oneokrock12345',  # 資料庫密碼
                database='heart rate monitor'  # 要連接的資料庫名稱
            )
            self.cursor = self.conn.cursor()  # 創建游標對象
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫連接錯誤", f"無法連接到資料庫: {err}")  # 顯示錯誤訊息
            self.master.destroy()  # 關閉應用程式
            return

        # 定義欄位
        self.columns = [
            '時間戳記', '心跳', '心跳狀態', '心跳_正常_異常'
        ]

        # 創建 GUI 元件
        self.create_widgets()
        
        # 載入初始資料
        self.load_data()

    def create_widgets(self):
        # 輸入欄位
        self.entries = {}  # 儲存輸入框的字典
        for i, field in enumerate(self.columns):
            ttk.Label(self.master, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)  # 標籤
            if field == '心跳_正常_異常':
                self.entries[field] = ttk.Combobox(self.master, values=['0', '1'])  # 下拉框
            else:
                self.entries[field] = ttk.Entry(self.master)  # 文本框
            self.entries[field].grid(row=i, column=1, padx=5, pady=5)  # 放置輸入框

        # 搜尋框
        ttk.Label(self.master, text="搜尋心跳紀錄:").grid(row=len(self.columns), column=0, padx=5, pady=5)  # 搜尋標籤
        self.search_entry = ttk.Entry(self.master)  # 搜尋輸入框
        self.search_entry.grid(row=len(self.columns), column=1, padx=5, pady=5)  # 放置搜尋框
        ttk.Button(self.master, text="搜尋", command=self.search_record).grid(row=len(self.columns), column=2, padx=5, pady=5)  # 搜尋按鈕

        # 功能按鈕
        ttk.Button(self.master, text="新增", command=self.add_record).grid(row=len(self.columns)+1, column=0, padx=5, pady=5)  # 新增按鈕
        ttk.Button(self.master, text="更新", command=self.update_record).grid(row=len(self.columns)+1, column=1, padx=5, pady=5)  # 更新按鈕
        ttk.Button(self.master, text="刪除", command=self.delete_record).grid(row=len(self.columns)+1, column=2, padx=5, pady=5)  # 刪除按鈕

        # 樹狀視圖
        self.tree = ttk.Treeview(self.master, columns=self.columns, show="headings")  # 創建樹狀視圖
        self.tree.grid(row=len(self.columns)+2, column=0, columnspan=3, padx=5, pady=5)  # 放置樹狀視圖

        # 設置欄位標題
        for col in self.columns:
            self.tree.heading(col, text=col)  # 設置每一欄的標題
            self.tree.column(col, width=100)  # 設置每一欄的寬度

        self.tree.bind('<<TreeviewSelect>>', self.item_selected)  # 綁定選擇事件

    def load_data(self):
        # 清除現有項目
        for item in self.tree.get_children():
            self.tree.delete(item)  # 刪除樹狀視圖中的所有項目

        try:
            # 從資料庫獲取資料
            self.cursor.execute("SELECT 時間戳記, 心跳, 心跳狀態, 心跳_正常_異常 FROM heart_rate")  # 查詢資料表
            rows = self.cursor.fetchall()  # 獲取所有行數據

            # 將數據插入樹狀視圖
            for row in rows:
                self.tree.insert("", "end", values=row)  # 插入每一行數據
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法載入資料: {err}")  # 顯示錯誤訊息

    def validate_and_convert_data(self, values):
        converted_values = []  # 儲存轉換後的值
        for field, value in zip(self.columns, values):  # 遍歷欄位和值
            if field == '心跳_正常_異常':
                if value not in ['0', '1']:  # 驗證值是否為 0 或 1
                    raise ValueError(f"'{field}' 欄位必須是 0 或 1")  # 當不符合時引發錯誤
                converted_values.append(int(value))  # 轉換為整數
            elif field == '心跳':
                converted_values.append(int(value) if value else None)  # 轉換為整數
            elif field == '時間戳記':
                converted_values.append(datetime.strptime(value, "%Y-%m-%d %H:%M:%S") if value else None)  # 轉換為日期時間
            else:
                converted_values.append(value)  # 直接使用值
        return converted_values  # 返回轉換後的值

    def add_record(self):
        values = [self.entries[field].get() for field in self.columns]  # 獲取所有輸入框的值
        
        try:
            converted_values = self.validate_and_convert_data(values)  # 驗證和轉換數據
            
            # 插入到資料庫
            sql = f"""INSERT INTO heart_rate (時間戳記, 心跳, 心跳狀態, 心跳_正常_異常)
                     VALUES (%s, %s, %s, %s)"""  # 插入語句

            self.cursor.execute(sql, converted_values)  # 執行插入
            self.conn.commit()  # 提交更改

            self.load_data()  # 刷新樹狀視圖
            messagebox.showinfo("成功", "記錄已新增")  # 顯示成功訊息
        except ValueError as err:
            messagebox.showerror("輸入錯誤", str(err))  # 顯示驗證錯誤
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法新增記錄: {err}")  # 顯示資料庫錯誤

    def update_record(self):
        selected_items = self.tree.selection()  # 獲取選中的項目
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇一條記錄")  # 提示用戶選擇記錄
            return

        values = [self.entries[field].get() for field in self.columns]  # 獲取所有輸入框的值
        
        try:
            converted_values = self.validate_and_convert_data(values)  # 驗證和轉換數據
            
            # 更新資料庫
            sql = f"""UPDATE heart_rate SET 心跳 = %s, 心跳狀態 = %s, 心跳_正常_異常 = %s
                     WHERE 時間戳記 = %s"""  # 更新語句
            self.cursor.execute(sql, converted_values[1:] + [converted_values[0]])  # 執行更新
            self.conn.commit()  # 提交更改

            self.load_data()  # 刷新樹狀視圖
            messagebox.showinfo("成功", "記錄已更新")  # 顯示成功訊息
        except ValueError as err:
            messagebox.showerror("輸入錯誤", str(err))  # 顯示驗證錯誤
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法更新記錄: {err}")  # 顯示資料庫錯誤

    def delete_record(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇一條記錄")
            return

        values = self.tree.item(selected_items[0])['values']
        
        try:
            # Delete from database
            sql = "DELETE FROM heart_rate WHERE 時間戳記 = %s"
            self.cursor.execute(sql, (values[0],))
            self.conn.commit()

            self.load_data()  # Refresh the treeview
            messagebox.showinfo("成功", "記錄已刪除")
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法刪除記錄: {err}")


    def search_record(self):
        search_value = self.search_entry.get().strip()
        if not search_value:
            messagebox.showwarning("警告", "請輸入搜尋條件")
            return

    # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            sql = "SELECT 時間戳記, 心跳, 心跳狀態, 心跳_正常_異常 FROM heart_rate WHERE 1=1"
            params = []

        # Check if the input is a valid date (MM-DD format)
            if len(search_value) == 5 and search_value[2] == '-':
                try:
                    month, day = map(int, search_value.split('-'))
                    sql += " AND (MONTH(時間戳記) = %s AND DAY(時間戳記) = %s)"
                    params.append(month)
                    params.append(day)
                except ValueError:
                    messagebox.showerror("錯誤", "日期格式無效，請輸入 MM-DD 格式")
                    return

        # Check if the search value is numeric (0 or 1 for 心跳_正常_異常)
            elif search_value.isdigit():
                if search_value in ['0', '1']:
                    sql += " AND 心跳_正常_異常 = %s"
                    params.append(int(search_value))
                else:
                    messagebox.showerror("錯誤", "心跳_正常_異常 欄位必須是 0 或 1")
                    return

        # Check if the input is part of 心跳狀態
            else:
                sql += " AND 心跳狀態 LIKE %s"
                params.append(f'%{search_value}%')

        # Execute the query
            self.cursor.execute(sql, params)
            rows = self.cursor.fetchall()

        # Insert data into treeview
            if rows:
                for row in rows:
                    self.tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("搜尋結果", "未找到符合條件的記錄")

        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法搜尋資料: {err}")

    def item_selected(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            values = self.tree.item(selected_items[0])['values']
            for i, field in enumerate(self.columns):
                self.entries[field].delete(0, tk.END)
                self.entries[field].insert(0, values[i])

    def __del__(self):
        # Close database connection
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = HeartRateApp(root)
    root.mainloop()

