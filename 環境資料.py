import tkinter as tk  # 導入 tkinter 模組，用於創建圖形用戶界面 (GUI)
from tkinter import ttk, messagebox  # 導入 ttk 用於更現代的 GUI 元件，messagebox 用於顯示訊息框
import mysql.connector  # 導入 MySQL 連接器，用於與 MySQL 資料庫交互
from datetime import datetime  # 導入 datetime 模組，用於處理日期和時間

class DHT11App:
    def __init__(self, master):
        self.master = master  # 保存主窗口的引用
        self.master.title("DHT11 紀錄系統")  # 設置窗口標題
        
        # 嘗試連接到資料庫
        try:
            self.conn = mysql.connector.connect(
                host='localhost',  # 資料庫主機地址
                port=3306,  # 資料庫端口
                user='root',  # 資料庫用戶名
                password='oneokrock12345',  # 資料庫密碼
                database='heart rate monitor'  # 要使用的資料庫名稱
            )
            self.cursor = self.conn.cursor()  # 創建資料庫游標
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫連接錯誤", f"無法連接到資料庫: {err}")  # 顯示錯誤訊息
            self.master.destroy()  # 關閉應用程式
            return
        
        # 定義資料欄位
        self.columns = [
            '時間戳記', '溫度', '濕度', '溫度狀態', '濕度狀態',
            '溫度_正常_異常', '濕度_正常_異常','體溫','體溫狀態','體溫_正常_異常',
        ]
        
        self.create_widgets()  # 創建 GUI 元件
        self.load_data()  # 加載初始資料

    def create_widgets(self):
        # 創建輸入欄位
        self.entries = {}
        for i, field in enumerate(self.columns):
            ttk.Label(self.master, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            if field in ['溫度_正常_異常', '濕度_正常_異常', '體溫_正常_異常']:
                self.entries[field] = ttk.Combobox(self.master, values=['0', '1'])  # 使用下拉選單
            else:
                self.entries[field] = ttk.Entry(self.master)  # 使用普通輸入框
            self.entries[field].grid(row=i, column=1, padx=5, pady=5)

        # 創建搜尋欄和按鈕
        ttk.Label(self.master, text="搜尋:").grid(row=len(self.columns), column=0, padx=5, pady=5)
        self.search_entry = ttk.Entry(self.master)
        self.search_entry.grid(row=len(self.columns), column=1, padx=5, pady=5)
        ttk.Button(self.master, text="搜尋", command=self.search_records).grid(row=len(self.columns), column=2, padx=5, pady=5)

        # 創建操作按鈕
        ttk.Button(self.master, text="新增", command=self.add_record).grid(row=len(self.columns)+1, column=0, padx=5, pady=5)
        ttk.Button(self.master, text="更新", command=self.update_record).grid(row=len(self.columns)+1, column=1, padx=5, pady=5)
        ttk.Button(self.master, text="刪除", command=self.delete_record).grid(row=len(self.columns)+1, column=2, padx=5, pady=5)

        # 創建樹狀視圖來顯示資料
        self.tree = ttk.Treeview(self.master, columns=self.columns, show="headings")
        self.tree.grid(row=len(self.columns)+2, column=0, columnspan=3, padx=5, pady=5)

        # 設置樹狀視圖的列標題
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.bind('<<TreeviewSelect>>', self.item_selected)  # 綁定選擇事件

    def load_data(self):
        # 載入資料到樹狀視圖
        for item in self.tree.get_children():
            self.tree.delete(item)  # 清除現有資料

        try:
            # 從資料庫獲取資料
            self.cursor.execute(f"SELECT {', '.join(self.columns)} FROM dht11")
            rows = self.cursor.fetchall()

            # 將資料插入樹狀視圖
            for row in rows:
                self.tree.insert("", "end", values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法載入資料: {err}")

    def search_records(self):
        search_query = self.search_entry.get().strip()

        # 清除樹狀視圖中的現有項目
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            # 構建基本 SQL 查詢
            sql = f"SELECT {', '.join(self.columns)} FROM dht11 WHERE 1=1"
            params = []

            # 處理"正常"或"異常"的精確或部分匹配搜尋
            if search_query in ["正常", "異常"]:
                sql += """ AND (溫度狀態 LIKE %s OR 濕度狀態 LIKE %s OR 體溫狀態 LIKE %s)"""
                like_query = f"%{search_query}%"
                params.extend([like_query, like_query, like_query])
            
            # 處理日期相關搜尋（例如 "07-04" 或 "2024"）
            elif len(search_query) == 5 and search_query[2] == '-':  # MM-DD 格式
                try:
                    month, day = map(int, search_query.split('-'))
                    sql += " AND MONTH(時間戳記) = %s AND DAY(時間戳記) = %s"
                    params.extend([month, day])
                except ValueError:
                    messagebox.showwarning("輸入錯誤", "日期格式應為MM-DD (例如: 07-04)")
                    return
            elif len(search_query) == 4 and search_query.isdigit():  # 年份格式（例如 "2024"）
                sql += " AND YEAR(時間戳記) = %s"
                params.append(int(search_query))
            
            # 處理二進制狀態欄位搜尋（例如 "0" 或 "1"）
            elif search_query in ["0", "1"]:
                sql += """ AND (溫度_正常_異常 = %s OR 濕度_正常_異常 = %s OR 體溫_正常_異常 = %s)"""
                params.extend([search_query, search_query, search_query])

            # 執行 SQL 查詢
            self.cursor.execute(sql, tuple(params))
            rows = self.cursor.fetchall()

            # 將匹配的行插入樹狀視圖
            if rows:
                for row in rows:
                    self.tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("搜尋結果", "未找到符合條件的記錄")

        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法搜尋資料: {err}")

    def validate_and_convert_data(self, values):
        # 驗證和轉換輸入的資料
        converted_values = []
        for field, value in zip(self.columns, values):
            if field in ['溫度_正常_異常', '濕度_正常_異常', '體溫_正常_異常']:
                if value not in ['0', '1']:
                    raise ValueError(f"'{field}' 欄位必須是 0 或 1")
                converted_values.append(int(value))
            elif field in ['溫度', '濕度', '體溫']:
                converted_values.append(float(value) if value else None)
            elif field == '時間戳記':
                converted_values.append(datetime.strptime(value, "%Y-%m-%d %H:%M:%S") if value else None)
            else:
                converted_values.append(value)
        return converted_values

    def add_record(self):
        # 新增記錄
        values = [self.entries[field].get() for field in self.columns]
        
        try:
            converted_values = self.validate_and_convert_data(values)
            
            # 插入到資料庫
            sql = f"""INSERT INTO dht11 ({', '.join(self.columns)})
                     VALUES ({', '.join(['%s']*len(self.columns))})"""

            self.cursor.execute(sql, converted_values)
            self.conn.commit()

            self.load_data()  # 重新載入資料
            messagebox.showinfo("成功", "記錄已新增")
        except ValueError as err:
            messagebox.showerror("輸入錯誤", str(err))
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法新增記錄: {err}")

    def update_record(self):
        # 更新記錄
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇一條記錄")
            return

        values = [self.entries[field].get() for field in self.columns]
        
        try:
            converted_values = self.validate_and_convert_data(values)
            
            # 更新資料庫
            sql = f"""UPDATE dht11 SET {', '.join([f'{col} = %s' for col in self.columns])}
                     WHERE 時間戳記 = %s"""
            self.cursor.execute(sql, converted_values + [converted_values[0]])
            self.conn.commit()

            self.load_data()  # 重新載入資料
            messagebox.showinfo("成功", "記錄已更新")
        except ValueError as err:
            messagebox.showerror("輸入錯誤", str(err))
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法更新記錄: {err}")

    def delete_record(self):
        # 刪除記錄
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇一條記錄")
            return

        values = self.tree.item(selected_items[0])['values']
        
        try:
            # 從資料庫刪除
            sql = "DELETE FROM dht11 WHERE 時間戳記 = %s"
            self.cursor.execute(sql, (values[0],))
            self.conn.commit()

            self.load_data()  # 重新載入資料
            messagebox.showinfo("成功", "記錄已刪除")
        except mysql.connector.Error as err:
            messagebox.showerror("資料庫錯誤", f"無法刪除記錄: {err}")

    def item_selected(self, event):
        # 當在樹狀視圖中選擇項目時觸發
        selected_items = self.tree.selection()
        if selected_items:
            values = self.tree.item(selected_items[0])['values']
            for i, field in enumerate(self.columns):
                self.entries[field].delete(0, tk.END)
                self.entries[field].insert(0, values[i])

    def __del__(self):
        # 析構函數，用於關閉資料庫連接
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()  # 創建主窗口
    app = DHT11App(root)  # 初始化應用程式
    root.mainloop()  # 啟動事件循環
