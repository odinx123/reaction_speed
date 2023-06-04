import socket
import threading
import tkinter as tk
import random
import time

# 參數設定
HOST = '127.0.0.1'
PORT = 8000
MAX_CLIENTS = 2  # 最大客戶端數量
ROUND = 5  # 遊戲回合數

# 變數
clients = []  # 客戶端清單
clients_score = []  # 客戶端分數清單(對應clients)
server_score = 0.0

class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("600x600")
        self.root.title("打地鼠遊戲Server")
        self.canvas = tk.Canvas(self.root, width=600, height=600, bg="green")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.click)
        self.root.bind("<Return>", self.start_game)
        self.holes = []
        self.timer = None  # 定時器
        self.mouse = None  # 地鼠
        self.time_start = None  # 遊戲開始時間
        self.clktime = 5  # 點擊時間
        self.text = None  # 列印字串
        self.round = 1  # 遊戲回合數
        # 產生25個洞
        for i in range(5):
            for j in range(5):
                # 洞的座標
                x1 = i * 100 + 50
                y1 = j * 100 + 50
                x2 = x1 + 100
                y2 = y1 + 100
                # 在畫布上畫一個洞
                hole = self.canvas.create_rectangle(x1, y1, x2, y2, fill="brown", outline="white")
                # 把洞加到洞的清單中
                self.holes.append(hole)

    def run(self):
        self.show_mouse()
        self.root.mainloop()

    def start_game(self, event):
        self.send_msg("show_start")
        self.show_str("遊戲開始", 300, 300, 30, "white", 900)
        self.root.after(1000, self.show_mouse)  # 1秒後顯示地鼠

    def send_msg(self, string):
        for i, connection in enumerate(clients):
            connection.sendall(string.encode())

    def show_mouse(self):
        self.send_msg("show_mouse")
        print(server_score, end=' ')
        print(clients_score)

        if self.mouse: # 如果有地鼠(不是None)，就刪除
            self.canvas.delete(self.mouse)
        hole = random.choice(self.holes)  # 從洞的清單中隨機選一個洞
        x1, y1, x2, y2 = self.canvas.coords(hole)  # 取得洞的座標(x1,y1代表左上角，x2,y2代表右下角)
        x = x1 + 50  # 一半的地方畫圓形
        y = y1 + 50
        self.mouse = self.canvas.create_oval(x-25, y-25, x+25, y+25, fill="gray")

        self.time_start = time.time()  # 畫完地鼠後開始計時
        self.root.after(5000, self.endthisgame)

    def endthisgame(self):
        global server_score
        self.send_msg("round")
        if self.mouse: # 如果有地鼠(不是None)，就刪除
            self.canvas.delete(self.mouse)
        server_score += self.clktime
        self.clktime = 5  # 初始化->沒點擊到會是5秒

        if self.round < ROUND:  # 遊戲還沒結束
            self.round += 1
            self.root.after(100, self.show_mouse)  # 隨機時間後再出現地鼠
        else:
            self.root.after(1000, self.end_game)  # 需要等待最後一次結束

    def end_game(self):
        if self.mouse:  # 如果有地鼠(不是None)，就刪除
            self.canvas.delete(self.mouse)

        print(server_score, end=' ')
        print(clients_score)

        # 結束遊戲，顯示誰少時間
        max_idx = -1
        cur_max = server_score
        for i in range(len(clients)):
            if clients_score[i] < cur_max:
                max_idx = i
                cur_max = clients_score[i]

        if max_idx == -1:
            self.show_str(f"winner is server\ntime={cur_max}", 300, 300, 30, "white", -1)
            self.send_msg(f"end:winner is server\ntime={cur_max}")
        else:
            client_ip = clients[max_idx].getpeername()[0]
            client_port = clients[max_idx].getpeername()[1]
            self.show_str(f"winner is {client_ip}:{client_port}\ntime={cur_max}", 300, 300, 30, "white", -1)
            self.send_msg(f"end:winner is {client_ip}:{client_port}\ntime={cur_max}")

    def click(self, event):
        x, y = event.x, event.y  # 取得滑鼠點擊的座標
        overlap = self.canvas.find_overlapping(x-1, y-1, x+1, y+1)  # 找出重疊的物件
        if overlap and self.mouse in overlap:
            if self.mouse:  # 如果有地鼠(不是None)，就刪除
                self.canvas.delete(self.mouse)
            self.clktime = round(time.time() - self.time_start, 2)  # 計算用時
            self.show_time()

    def show_str(self, string, x, y, size=30, color="white", time=900):
        self.text = self.canvas.create_text(x, y, text=string, font=("Arial", size), fill=color)
        if time != -1:
            self.root.after(time, self.del_str)  # 0.9秒後刪除顯示分數

    def del_str(self):
        self.canvas.delete(self.text)
        self.text = None

    def show_time(self):
        self.canvas.delete(self.mouse)
        self.mouse = None
        self.show_str(f"用時：{self.clktime} 秒", 300, 300, 30, "white", 900)

# 處理客戶端請求的函數
def handle_client(server_socket):
    # 設置 socket 為非阻塞模式
    server_socket.setblocking(False)
    print('Waiting for connection...')
    while True:
        for i, connection in enumerate(clients):
            # 根據收到的資料做相應的處理
            try:
                data = connection.recv(1024).decode()
                clients_score[i] += float(data)
            except:  # 沒有收到資料
                pass

def main():
    # 創建一個socket對象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定到指定的地址和端口
    server_socket.bind((HOST, PORT))
    # 監聽客戶端連接
    server_socket.listen(MAX_CLIENTS)
    print(f'Listening on {HOST}:{PORT}...')

    for i in range(MAX_CLIENTS):
        print('Waiting for connection...')
        connection, client_address = server_socket.accept()
        clients.append(connection)
        clients_score.append(0.0)
        print(f'New connection from {client_address[0]}:{client_address[1]}')

    # 創建一個新的線程來處理客戶端的請求
    client_thread = threading.Thread(target=handle_client, args=(server_socket,), daemon=True)
    client_thread.start()

    game = Game()
    game.run()
    print("遊戲結束")

if __name__ == '__main__':
    main()
