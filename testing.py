import tkinter as tk
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import webbrowser

# 設定 Edge 瀏覽器選項
options = webdriver.EdgeOptions()
options.add_argument("--start-maximized")
options.add_argument("--headless")  # 添加這行設置無頭模式
options.add_argument("--disable-gpu")  # 如果需要，添加這行
options.add_argument("--window-size=1920,1080")  # 設置窗口大小

# 使用 EdgeChromiumDriverManager 自動管理 EdgeDriver
driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)

# 全局變數來儲存較便宜的產品網址
cheaper_product_url = ""

def open_product_page():
    if cheaper_product_url:
        webbrowser.open(cheaper_product_url)
    else:
        display_text.insert(tk.END, "未找到可購買的產品頁面。\n")

def search():
    global cheaper_product_url
    query = search_var.get()
    status_label.config(text="正在運行...")  # 更新狀態為「正在運行」
    display_text.delete(1.0, tk.END)
    display_text.insert(tk.END, f"搜尋結果：{query}\n")
    root.update_idletasks()  # 刷新界面

    # 初始化價格和庫存變數
    brickpapa_price = None
    brickpapa_in_stock = False
    bidbuy4u_price = None
    bidbuy4u_in_stock = False
    brickpapa_url = ""
    bidbuy4u_url = ""

    try:
        # 爬取第一個網站
        driver.get("https://www.brickpapa.com.tw/")
        wait = WebDriverWait(driver, 20)  # 延長等待時間
        target_element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/nav[1]/div/div[2]/ul/li[1]/a/span')))

        actions = ActionChains(driver)
        actions.move_to_element(target_element).perform()

        input_element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/nav[1]/div/div[2]/ul/li[1]/div/form/input')))
        input_element.click()
        input_element.send_keys(query)
        input_element.send_keys(Keys.RETURN)

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'Label-price')))
        price_elements = driver.find_elements(By.CLASS_NAME, 'Label-price')
        display_text.insert(tk.END, "brickpapa\n")
        if price_elements:
            brickpapa_price = price_elements[0].text.strip()
            display_text.insert(tk.END, f"價錢：{brickpapa_price}\n")
            brickpapa_url = driver.current_url  # 儲存產品網址
        else:
            display_text.insert(tk.END, "未找到價錢資訊。\n")

        sold_out_elements = driver.find_elements(By.CLASS_NAME, 'sold-out-item-content')
        if not sold_out_elements:
            brickpapa_in_stock = True
            display_text.insert(tk.END, "有貨\n")
        else:
            display_text.insert(tk.END, "售完\n")

        # 爬取第二個網站
        driver.get("https://www.bidbuy4u.com.tw/")
        wait = WebDriverWait(driver, 10)
        hover_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fixed-menu-container"]/div[2]/div[3]/form/button/span')))

        actions = ActionChains(driver)
        actions.move_to_element(hover_element).perform()

        search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fixed-menu-container"]/div[2]/div[3]/form/input')))
        search_box.click()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'price-sale')))
        price_elements = driver.find_elements(By.CLASS_NAME, 'price-sale')
        display_text.insert(tk.END, "必買站\n")
        if price_elements:
            bidbuy4u_price = price_elements[0].text.strip()
            display_text.insert(tk.END, f"價錢：{bidbuy4u_price}\n")
            bidbuy4u_url = driver.current_url  # 儲存產品網址
        else:
            display_text.insert(tk.END, "未找到價錢資訊。\n")

        sold_out_elements = driver.find_elements(By.CLASS_NAME, 'sold-out-item')
        if not sold_out_elements:
            bidbuy4u_in_stock = True
            display_text.insert(tk.END, "有貨\n")
        else:
            display_text.insert(tk.END, "售完\n")

        # 比較價格並顯示較便宜的
        if brickpapa_price and bidbuy4u_price:
            brickpapa_price_value = float(''.join(filter(str.isdigit, brickpapa_price)))
            bidbuy4u_price_value = float(''.join(filter(str.isdigit, bidbuy4u_price)))

            if brickpapa_price_value < bidbuy4u_price_value:
                display_text.insert(tk.END, f"較便宜的是 brickpapa，價錢：{brickpapa_price}\n")
                cheaper_product_url = brickpapa_url
            elif bidbuy4u_price_value < brickpapa_price_value:
                display_text.insert(tk.END, f"較便宜的是 必買站，價錢：{bidbuy4u_price}\n")
                cheaper_product_url = bidbuy4u_url
            else:
                display_text.insert(tk.END, "價格相同\n")
                if brickpapa_in_stock:
                    display_text.insert(tk.END, f"有貨的是 brickpapa，價錢：{brickpapa_price}\n")
                    cheaper_product_url = brickpapa_url
                elif bidbuy4u_in_stock:
                    display_text.insert(tk.END, f"有貨的是 必買站，價錢：{bidbuy4u_price}\n")
                    cheaper_product_url = bidbuy4u_url
                else:
                    display_text.insert(tk.END, "兩個網站都沒有庫存。\n")
                    cheaper_product_url = ""
        elif brickpapa_price:
            display_text.insert(tk.END, f"只有 brickpapa 找到價格，價錢：{brickpapa_price}\n")
            cheaper_product_url = brickpapa_url
        elif bidbuy4u_price:
            display_text.insert(tk.END, f"只有 必買站 找到價格，價錢：{bidbuy4u_price}\n")
            cheaper_product_url = bidbuy4u_url
        else:
            display_text.insert(tk.END, "查無此貨\n")
            cheaper_product_url = ""

    except Exception as e:
        display_text.insert(tk.END, "查無此貨\n")
        cheaper_product_url = ""

    status_label.config(text="運行完成")  # 更新狀態為「運行完成」
    root.update_idletasks()  # 刷新界面

# 建立主應用程式窗口
root = tk.Tk()
root.title("搜尋介面")

# 設定視窗大小
root.geometry("500x300")

# 建立搜尋欄和顯示框框架
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# 設置網格布局的行和列的權重
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# 建立搜尋欄
search_label = ttk.Label(frame, text="搜尋：")
search_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

search_var = tk.StringVar()
search_entry = ttk.Entry(frame, width=30, textvariable=search_var)
search_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

# 建立顯示框
display_frame = ttk.LabelFrame(frame, text="顯示區域", padding="10")
display_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

display_text = tk.Text(display_frame, wrap="word", width=40, height=10)
display_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# 設置顯示框的滾動條
scrollbar = ttk.Scrollbar(display_frame, orient="vertical", command=display_text.yview)
scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

display_text['yscrollcommand'] = scrollbar.set

# 建立搜尋按鈕
search_button = ttk.Button(frame, text="搜尋", command=search)
search_button.grid(row=0, column=2, padx=5, pady=5)

# 建立狀態標籤
status_label = ttk.Label(frame, text="等待搜尋")
status_label.grid(row=2, column=0, columnspan=3, pady=5)

# 建立“買”按鈕
buy_button = ttk.Button(frame, text="買", command=open_product_page)
buy_button.grid(row=3, column=0, columnspan=3, pady=5)

# 啟動主事件迴圈
root.mainloop()
