import tkinter as tk
import random
import time

class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("600x600")
        self.root.title("打地鼠遊戲")
        self.canvas = tk.Canvas(self.root, width=600, height=600, bg="green")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.click)
        self.holes = []
        self.timer = None  # 定時器
        self.mouse = None  # 地鼠
        self.time_start = None  # 遊戲開始時間
        self.clktime = None  # 分數
        self.text = None  # 列印字串
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

    def show_mouse(self):
        if self.mouse: # 如果有地鼠(不是None)，就刪除
            self.canvas.delete(self.mouse)
            self.canvas.delete(self.clktime)
        hole = random.choice(self.holes)  # 從洞的清單中隨機選一個洞
        x1, y1, x2, y2 = self.canvas.coords(hole)  # 取得洞的座標(x1,y1代表左上角，x2,y2代表右下角)
        x = x1 + 50  # 一伴的地方畫圓形
        y = y1 + 50
        self.mouse = self.canvas.create_oval(x-25, y-25, x+25, y+25, fill="gray")  # 地鼠(新的canvas物件)
        self.time_start = time.time()

    def click(self, event):
        x, y = event.x, event.y  # 取得滑鼠點擊的座標
        overlap = self.canvas.find_overlapping(x-1, y-1, x+1, y+1)  # 找出重疊的物件
        if self.mouse in overlap:  # 如果有重疊到地鼠(overlap是滑鼠附近畫出來的canvas物件)，mouse是canvas物件
            self.clktime = round(time.time() - self.time_start, 2)  # 計算用時
            self.root.after(random.randint(950, 4000), self.show_mouse)  # 隨機時間後再出現地鼠
            self.show_time()

    def show_str(self, string, x, y, size=30, color="white", time=900):
        self.text = self.canvas.create_text(x, y, text=string, font=("Arial", size), fill=color)
        self.root.after(time, self.del_str)  # 0.9秒後刪除顯示分數

    def del_str(self):
        self.canvas.delete(self.text)
        self.text = None

    def show_time(self):
        self.canvas.delete(self.mouse)
        self.mouse = None
        self.show_str(f"用時：{self.clktime} 秒", 300, 300, 30, "white", 900)

if __name__ == '__main__':
    game = Game()
    game.run()
    print("遊戲結束")