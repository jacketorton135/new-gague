import tkinter as tk  # 導入 tkinter 模組，創建 GUI
from tkinter import ttk, messagebox  # 導入 ttk 標準元件和訊息框
import mysql.connector  # 導入 MySQL 連接模組
from datetime import datetime  # 導入 datetime 用於處理日期時間

class BMIApp:
    def __init__(self, master):
        self.master = master  # 保存主窗口參考
        self.master.title("BMI 紀錄系統")  # 設置窗口標題
        
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
        
        # 獲取資料表結構
        self.get_table_structure()
        
        # 創建 GUI 元件
        self.create_widgets()
        
        # 加載初始資料
        self.load_data()

    def get_table_structure(self):
        try:
            self.cursor.execute("DESCRIBE bmi")  # 執行 SQL 語句，獲取表結構
            self.columns = []  # 儲存欄位名稱
            self.column_types = {}  # 儲存欄位類型
            for column in self.cursor.fetchall():
                self.columns.append(column[0])  # 添加欄位名稱到列表
                self.column_types[column[0]] = column[1]  # 添加欄位類型到字典
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法獲取表格結構: {err}")  # 顯示錯誤訊息
            self.master.destroy()  # 關閉應用程式

    def create_widgets(self):
        # 搜尋框
        self.search_label = ttk.Label(self.master, text="搜尋:")  # 搜尋標籤
        self.search_label.grid(row=0, column=0, padx=5, pady=5)  # 放置標籤
        self.search_entry = ttk.Entry(self.master)  # 搜尋輸入框
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)  # 放置輸入框
        self.search_button = ttk.Button(self.master, text="搜尋", command=self.search_data)  # 搜尋按鈕
        self.search_button.grid(row=0, column=2, padx=5, pady=5)  # 放置按鈕

        # 輸入欄位
        self.entries = {}  # 儲存輸入框的字典
        for i, field in enumerate(self.columns, start=1):  # 從第1行開始創建欄位
            ttk.Label(self.master, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)  # 標籤
            if field == '正常_異常':
                self.entries[field] = ttk.Combobox(self.master, values=['0', '1'])  # 下拉框
            else:
                self.entries[field] = ttk.Entry(self.master)  # 文本框
            self.entries[field].grid(row=i, column=1, padx=5, pady=5)  # 放置輸入框

        # 按鈕
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

    def load_data(self, search_term=None):
        # 清除現有項目
        for item in self.tree.get_children():
            self.tree.delete(item)  # 刪除樹狀視圖中的所有項目

        try:
            # 從資料庫獲取資料
            if search_term:
                sql = f"SELECT {', '.join(self.columns)} FROM bmi WHERE {self.columns[0]} LIKE %s"  # 帶條件的查詢
                self.cursor.execute(sql, (f'%{search_term}%',))  # 執行查詢
            else:
                sql = f"SELECT {', '.join(self.columns)} FROM bmi"  # 獲取所有資料
                self.cursor.execute(sql)  # 執行查詢
            
            rows = self.cursor.fetchall()  # 獲取所有行數據

            # 將數據插入樹狀視圖
            for row in rows:
                self.tree.insert("", "end", values=row)  # 插入每一行數據
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法載入資料: {err}")  # 顯示錯誤訊息

    def search_data(self):
        search_term = self.search_entry.get()  # 獲取搜尋詞

        if not search_term:  # 如果搜尋框為空，則加載所有資料
            self.load_data()
            return

        try:
            # 建立 WHERE 條件，將所有欄位都包含在內
            search_conditions = " OR ".join([f"{col} LIKE %s" for col in self.columns])  # 創建查詢條件
            sql = f"SELECT {', '.join(self.columns)} FROM bmi WHERE {search_conditions}"  # 完整查詢語句
            # 將搜尋詞包裹在百分號符號內，以便能進行部分匹配
            search_values = tuple(f"%{search_term}%" for _ in self.columns)  # 構建查詢參數
            self.cursor.execute(sql, search_values)  # 執行查詢
            rows = self.cursor.fetchall()  # 獲取結果

            # 清除現有的資料並重新插入新的搜尋結果
            for item in self.tree.get_children():
                self.tree.delete(item)  # 刪除現有項目

            for row in rows:
                self.tree.insert("", "end", values=row)  # 插入搜尋結果

        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法搜尋資料: {err}")  # 顯示錯誤訊息

    def validate_and_convert_data(self, values):
        converted_values = []  # 儲存轉換後的值
        for field, value in zip(self.columns, values):  # 遍歷每個欄位和其值
            if field == '正常_異常':
                if value not in ['0', '1']:  # 驗證 '正常_異常' 欄位的值
                    raise ValueError("'正常_異常' 欄位必須是 0 或 1")
                converted_values.append(int(value))  # 轉換為整數
            elif 'int' in self.column_types[field]:  # 如果欄位類型是整數
                converted_values.append(int(value) if value else None)  # 轉換為整數，空值則為 None
            elif 'float' in self.column_types[field]:  # 如果欄位類型是浮點數
                converted_values.append(float(value) if value else None)  # 轉換為浮點數
            elif 'datetime' in self.column_types[field]:  # 如果欄位類型是日期時間
                converted_values.append(datetime.strptime(value, "%Y-%m-%d %H:%M:%S") if value else None)  # 轉換為日期時間
            else:
                converted_values.append(value)  # 直接使用值
        return converted_values  # 返回轉換後的值

    def add_record(self):
        values = [self.entries[field].get() for field in self.columns]  # 獲取所有輸入框的值
        
        try:
            converted_values = self.validate_and_convert_data(values)  # 驗證和轉換數據
            
            # 插入到資料庫
            sql = f"""INSERT INTO bmi ({', '.join(self.columns)})
                     VALUES ({', '.join(['%s']*len(self.columns))})"""  # 插入語句

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
            sql = f"""UPDATE bmi SET {', '.join([f'{col} = %s' for col in self.columns])}
                     WHERE {self.columns[0]} = %s"""  # 更新語句
            self.cursor.execute(sql, converted_values + [converted_values[0]])  # 執行更新
            self.conn.commit()  # 提交更改

            self.load_data()  # 刷新樹狀視圖
            messagebox.showinfo("成功", "記錄已更新")  # 顯示成功訊息
        except ValueError as err:
            messagebox.showerror("輸入錯誤", str(err))  # 顯示驗證錯誤
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法更新記錄: {err}")  # 顯示資料庫錯誤

    def delete_record(self):
        selected_items = self.tree.selection()  # 獲取選中的項目
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇一條記錄")  # 提示用戶選擇記錄
            return

        values = self.tree.item(selected_items[0])['values']  # 獲取選中項目的值
        
        try:
            # 從資料庫刪除
            sql = f"DELETE FROM bmi WHERE {self.columns[0]} = %s"  # 刪除語句
            self.cursor.execute(sql, (values[0],))  # 執行刪除
            self.conn.commit()  # 提交更改

            self.load_data()  # 刷新樹狀視圖
            messagebox.showinfo("成功", "記錄已刪除")  # 顯示成功訊息
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法刪除記錄: {err}")  # 顯示資料庫錯誤

    def item_selected(self, event):
        selected_items = self.tree.selection()  # 獲取選中的項目
        if selected_items:
            values = self.tree.item(selected_items[0])['values']  # 獲取選中項目的值
            for i, field in enumerate(self.columns):  # 遍歷欄位
                self.entries[field].delete(0, tk.END)  # 清空輸入框
                self.entries[field].insert(0, values[i])  # 插入選中項目的值

    def __del__(self):
        # 關閉資料庫連接
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()  # 關閉游標
            self.conn.close()  # 關閉連接

if __name__ == "__main__":
    root = tk.Tk()  # 創建主窗口
    app = BMIApp(root)  # 初始化應用程式
    root.mainloop()  # 啟動事件循環
