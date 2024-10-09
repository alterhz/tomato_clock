import logging
import os
import sys
import threading
import tkinter as tk
from playsound import playsound
from logger_utils import init_logging_basic_config

total_seconds = 0
music_path = "alert.wav"
play_music = False


def countdown(minutes):
    global total_seconds, play_music
    total_seconds = minutes * 60
    play_music = True
    logging.info(f"开始倒计时：{minutes} 分钟")
    log_box.insert(tk.END, f"{get_current_time()} 开始倒计时：{minutes} 分钟...")
    # 滚动到最后一行
    log_box.see(tk.END)


def update_time():
    global total_seconds
    if total_seconds > 0:
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str.set(f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
        total_seconds -= 1
    elif total_seconds == 0:
        global play_music
        if play_music:
            logging.info("倒计时结束")
            log_box.insert(tk.END, f"{get_current_time()} 倒计时结束。")
            # 滚动到最后一行
            log_box.see(tk.END)
            time_str.set("00:00:00")
            play_music = False
            threading.Thread(target=play_alert).start()
            flash_window()

    root.after(1000, update_time)


def play_alert():
    playsound(music_path)


def start_countdown(minutes):
    countdown(minutes)


def flash_window():
    # 先最小化窗口
    root.iconify()
    # 之后再将其显示出来
    root.wm_deiconify()


def get_current_time():
    import datetime
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    init_logging_basic_config()

    root = tk.Tk()
    root.title("倒计时提醒")
    logging.info("启动倒计时提醒程序")

    if hasattr(sys, '_MEIPASS'):
        root.iconbitmap(sys._MEIPASS + '/clock.ico')
        music_path = sys._MEIPASS + '/alert.wav'
    else:
        root.iconbitmap('clock.ico')

    # 设置窗口置顶
    font_style = ("Microsoft YaHei", 48)
    root.configure(bg='black')
    time_str = tk.StringVar()
    time_str.set("00:00:00")
    time_label = tk.Label(root, textvariable=time_str, font=font_style, fg='white', bg='black', bd=10)
    time_label.pack()

    button_font_style = ("Microsoft YaHei", 24)
    start_0_1_min_button = tk.Button(root, text="开始倒计时（25 分钟）", command=lambda: start_countdown(25),
                                     font=button_font_style, bd=10, width=20)
    start_5_min_button = tk.Button(root, text="开始倒计时（5 分钟）", command=lambda: start_countdown(5),
                                   font=button_font_style, bd=10, width=20)

    start_0_1_min_button.pack(fill=tk.X)
    start_5_min_button.pack(fill=tk.X)

    # 添加 Listbox 来记录计时器日志
    log_box = tk.Listbox(root, font=("Microsoft YaHei", 12))
    log_box.config(height=8)  # 设置 Listbox 的行数为 10
    log_box.pack(fill=tk.BOTH, expand=True)

    update_time()

    root.mainloop()
    logging.info("退出倒计时提醒程序")
