import tkinter as tk

root = tk.Tk()

# 创建一个框架用于布局，方便调整label和滑块的位置关系
frame = tk.Frame(root)
frame.pack()

# 创建一个Label用于显示说明文字
label = tk.Label(frame, text="窗口透明度")
label.pack(side=tk.LEFT)

# 创建滑块来调节透明度
scale = tk.Scale(frame, from_=0.1, to=1.0, resolution=0.1,
                 orient='horizontal',
                 command=lambda value: root.wm_attributes('-alpha', float(value)))
scale.set(1.0)
scale.pack(side=tk.LEFT)

root.mainloop()