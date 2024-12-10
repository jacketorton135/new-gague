import tkinter as tk
import webview

def open_webview():
    # 使用 PyWebView 開啟嵌入的網頁
    webview.create_window('嵌入網頁', 'https://9ffea55d-e78d-470b-b56c-c9b2bbe836c1-00-3bgh7eg56lmo3.pike.replit.dev/')
    webview.start()

root = tk.Tk()
root.title("Tkinter 嵌入網頁")

button = tk.Button(root, text="在嵌入視窗中打開網頁", command=open_webview)
button.pack(pady=20)

root.mainloop()

