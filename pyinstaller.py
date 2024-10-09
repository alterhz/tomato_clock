import PyInstaller.__main__

PyInstaller.__main__.run([
    'clock.py',
    '--noconfirm',
    '--onefile',
    '--windowed',
    '--add-data=alert.wav;.',
    '--add-data=clock.ico;.'
])
