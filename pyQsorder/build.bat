c:\users\uncle_ziba\qsorder-travis\lib\site-packages\PySide\pyside-rcc.exe -o bkg_img_rc.py bkg_img.qrc
pyside-uic qsorder.ui -o qsorder_ui.py
rem pyinstaller --upx-dir=C:\upx\upx391w -w --onefile qsorder.py 