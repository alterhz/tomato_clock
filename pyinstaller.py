import PyInstaller.__main__

# 设置输出文件名
output_filename = 'TomatoClock'

PyInstaller.__main__.run([
    'clock.py',
    '--noconfirm',
    '--onefile',
    '--windowed',
    '--add-data=alert.wav;.',
    '--add-data=clock.ico;.',
    f'--name={output_filename}',
    f'--icon=clock.ico'
])
