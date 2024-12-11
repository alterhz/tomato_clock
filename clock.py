import logging
import sys
import threading
import tkinter as tk
from tkinter import messagebox

from playsound import playsound
from logger_utils import init_logging_basic_config
import configparser

DEBUG = False
# 暂停标记
pause_timer = False
total_seconds = 0
music_path = "alert.wav"
play_music = False
auto_rest = False

concentration_count = 0

WINDOW_WIDTH = 334
WINDOW_MIN_HEIGHT = 110
WINDOW_MAX_HEIGHT = 450

# 创建配置解析器对象
config = configparser.ConfigParser()

countdown_minutes = 0


def countdown(minutes):
    global total_seconds, play_music, countdown_minutes
    total_seconds = minutes * 60
    # total_seconds = minutes
    countdown_minutes = minutes
    play_music = True
    logging.info(f"开始倒计时：{minutes} 分钟")
    log_box.insert(tk.END, f"{get_current_time()} 开始倒计时：{minutes} 分钟。")
    # 滚动到最后一行
    log_box.see(tk.END)


def update_time():
    root.after(1000, update_time)
    if pause_timer:
        time_str.set(f"已暂停")
        return

    global total_seconds, concentration_count
    if total_seconds > 0:
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_label.config(fg='white')
        time_str.set(f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
        total_seconds -= 1
    elif total_seconds == 0:
        global play_music
        if play_music:
            logging.info("倒计时结束")
            log_box.insert(tk.END, f"{get_current_time()} 倒计时结束。")
            # 滚动到最后一行
            log_box.see(tk.END)
            time_label.config(fg='red')
            time_str.set("00:00:00")
            play_music = False

            if countdown_minutes == 25:
                concentration_count = concentration_count + 1
                # 更新total_label显示
                total_label.config(text=f"专注总次数：{concentration_count}\n专注总时间：{concentration_count * 25}分钟")
                # 更新标题
                root.title(f"番茄计时器 +{concentration_count}")

            threading.Thread(target=play_alert).start()
            flash_window()
            # 弹窗提示倒计时结束
            messagebox.showinfo("提示", "倒计时完毕")
            if auto_rest and auto_rest_var.get():
                start_countdown(5)


def play_alert():
    playsound(music_path)


def start_countdown(minutes):
    global auto_rest, pause_timer
    pause_timer = False
    if minutes != 5:
        auto_rest = True
    else:
        auto_rest = False
    countdown(minutes)
    if auto_minimize_var.get() and minutes == 25:
        # 将窗口最小化
        change_window_size(None)


def flash_window():
    center_window()
    # 之后再将其显示出来
    root.wm_deiconify()
    # 将窗口最大化
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_MAX_HEIGHT}")
    set_transparent_when_mini(False)


def get_current_time():
    import datetime
    return datetime.datetime.now().strftime('%H:%M:%S')


def save_config():
    config.has_section('Settings') or config.add_section('Settings')
    config.set('Settings', 'topmost', str(topmost_var.get()))
    config.set('Settings', 'auto_minimize', str(auto_minimize_var.get()))
    config.set('Settings', 'auto_rest', str(auto_rest_var.get()))
    config.set('Settings', 'transparent', str(transparent_var.get()))
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    logging.debug(
        f"保存配置：topmost={topmost_var.get()}，auto_minimize={auto_minimize_var.get()}，auto_rest={auto_rest_var.get()}")


def menu():
    # 创建菜单栏
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    # 创建一个子菜单
    view_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="设置", menu=view_menu)
    # 添加窗口置顶选项
    view_menu.add_command(label="测试", command=lambda: start_countdown(0.05))


def pause_or_resume():
    # 获取当前按钮的文本
    global pause_timer
    if pause_timer:
        pause_timer = False
    else:
        pause_timer = True


if __name__ == '__main__':
    init_logging_basic_config()

    logging.info("启动倒计时提醒程序")
    root = tk.Tk()
    root.resizable(False, False)
    root.title("番茄计时器")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_MAX_HEIGHT}")

    if hasattr(sys, '_MEIPASS'):
        root.iconbitmap(sys._MEIPASS + '/clock.ico')
        music_path = sys._MEIPASS + '/alert.wav'
    else:
        root.iconbitmap('clock.ico')

    font_style = ("Microsoft YaHei", 48)
    time_str = tk.StringVar()
    time_str.set("00:00:00")
    time_label = tk.Label(root, textvariable=time_str, font=font_style, fg='red', bg='black', width=10)
    time_label.pack()

    pause_str = tk.StringVar()
    pause_str.set("左键Mini窗口，右键暂停继续")
    pause_label = tk.Label(root, textvariable=pause_str, fg='green', bg='black', width=50)
    pause_label.pack()


    def change_window_size(event):
        window_height = root.winfo_height()
        if window_height > WINDOW_MIN_HEIGHT:
            root.geometry(f"{WINDOW_WIDTH}x{WINDOW_MIN_HEIGHT}")
            set_transparent_when_mini(True)
        else:
            root.geometry(f"{WINDOW_WIDTH}x{WINDOW_MAX_HEIGHT}")
            set_transparent_when_mini(False)


    time_label.bind("<Button-1>", change_window_size)


    def right_click(event):
        pause_or_resume()


    time_label.bind("<Button-3>", right_click)

    # 创建一个Frame用于放置Checkbox和按钮
    frame = tk.Frame(root)
    frame.pack()

    # 窗口置顶Checkbox
    topmost_var = tk.BooleanVar()
    # 尝试从配置文件中读取窗口置顶状态，如果没有则设置为False
    try:
        config.read('config.ini')
        topmost_var.set(config.getboolean('Settings', 'topmost', fallback=False))
    except (configparser.NoSectionError, configparser.NoOptionError):
        topmost_var.set(False)

    if topmost_var.get():
        root.attributes("-topmost", True)


    def toggle_topmost():
        if topmost_var.get():
            root.attributes("-topmost", True)
        else:
            root.attributes("-topmost", False)

        # 更新配置文件
        save_config()


    topmost_checkbox = tk.Checkbutton(frame, text="窗口置顶", variable=topmost_var, onvalue=True, offvalue=False,
                                      command=toggle_topmost)
    topmost_checkbox.pack(side=tk.LEFT)

    # 自动最小化Checkbox
    auto_minimize_var = tk.BooleanVar()
    # 尝试从配置文件中读取自动最小化状态，如果没有则设置为False
    try:
        config.read('config.ini')
        auto_minimize_var.set(config.getboolean('Settings', 'auto_minimize', fallback=False))
    except (configparser.NoSectionError, configparser.NoOptionError):
        auto_minimize_var.set(False)

    auto_minimize_checkbox = tk.Checkbutton(frame, text="Mini窗口", variable=auto_minimize_var, onvalue=True,
                                            offvalue=False, command=save_config)
    auto_minimize_checkbox.pack(side=tk.LEFT)

    # 工作完毕自动休息Checkbox
    auto_rest_var = tk.BooleanVar()
    try:
        config.read('config.ini')
        auto_rest_var.set(config.getboolean('Settings', 'auto_rest', fallback=False))
    except (configparser.NoSectionError, configparser.NoOptionError):
        auto_rest_var.set(False)


    def toggle_auto_rest():
        global auto_rest
        if auto_rest_var.get():
            auto_rest = True
        else:
            auto_rest = False
        save_config()


    auto_rest_checkbox = tk.Checkbutton(frame, text="自动休息", variable=auto_rest_var, onvalue=True,
                                        offvalue=False, command=toggle_auto_rest)
    auto_rest_checkbox.pack(side=tk.LEFT)


    def toggle_transparent():
        save_config()
        if transparent_var.get():
            change_window_size(None)


    def set_transparent_when_mini(mini: bool):
        """
        勾选半透明后，mini窗口半透明，最大化，取消半透明
        """
        if transparent_var.get():
            root.attributes('-alpha', 0.5 if mini else 1.0)
        else:
            root.attributes('-alpha', 1.0)


    transparent_var = tk.BooleanVar()
    # 尝试从配置文件中读取自动最小化状态，如果没有则设置为False
    try:
        config.read('config.ini')
        transparent_var.set(config.getboolean('Settings', 'transparent', fallback=False))
    except (configparser.NoSectionError, configparser.NoOptionError):
        transparent_var.set(False)
    transparent_checkbox = tk.Checkbutton(frame, text="半透明", variable=transparent_var, onvalue=True,
                                          offvalue=False, command=toggle_transparent)
    transparent_checkbox.pack(side=tk.LEFT)

    # 添加一个frame
    frame = tk.Frame(root)
    frame.pack()

    button_font_style = ("Microsoft YaHei", 18)
    start_0_1_min_button = tk.Button(frame, text="工作25分钟", command=lambda: start_countdown(25),
                                     font=button_font_style, bd=5, width=10)
    start_0_1_min_button.pack(side=tk.LEFT)
    start_5_min_button = tk.Button(frame, text="休息5分钟", command=lambda: start_countdown(5),
                                   font=button_font_style, bd=5, width=10)
    start_5_min_button.pack(side=tk.LEFT)

    # 添加一个Label来显示专注总次数和总时间

    total_label = tk.Label(root, text=f"专注总次数：{concentration_count}\n专注总时间：{concentration_count * 25}分钟", font=("Microsoft YaHei", 12))
    total_label.pack()

    # 添加Listbox来记录计时器日志
    log_box = tk.Listbox(root, font=("Microsoft YaHei", 12))
    log_box.config(height=8)  # 设置Listbox的行数为10
    log_box.pack(fill=tk.BOTH, expand=True)

    if DEBUG:
        menu()

    update_time()


    def center_window():
        # 获取屏幕宽度和高度
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        # 确保窗口布局已经完成，再获取窗口的实际宽度和高度
        root.update_idletasks()
        # 获取窗口宽度和高度
        window_width = root.winfo_width()
        window_height = root.winfo_height()
        # 计算窗口左上角的坐标
        x = (screen_width - window_width) / 2
        y = (screen_height - window_height) / 2
        logging.debug(
            f"屏幕宽度：{screen_width}，屏幕高度：{screen_height}，窗口宽度：{window_width}，窗口高度：{window_height}")
        root.geometry('+%d+%d' % (x, y))

    center_window()

    root.mainloop()
    logging.info("退出倒计时提醒程序")
