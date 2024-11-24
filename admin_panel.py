import sys
import time
import shutil
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from db.models import *
from bot import bot, main_schedule_parse
from telebot.apihelper import ApiTelegramException


class Panel(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('src/vsui.ui', self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(640, 360)
        self.setWindowIcon(QIcon('src/icon.jpg'))
        self.statusBar().setStyleSheet("color: white")
        self.recievers_edit.addItems(['all', '10', '11'])
        self.small_btn.clicked.connect(self.window().showMinimized)
        self.close_btn.clicked.connect(self.window().close)
        self.add_schedule_btn.clicked.connect(self.add_schedule)
        self.add_photo_btn.clicked.connect(self.add_photo)
        self.send_btn.clicked.connect(self.send_message)
        self.clear_btn.clicked.connect(self.clear)
        self.photo_path = None
        self.initial_os = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self.initial_pos:
            delta = event.position().toPoint() - self.initial_pos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )

    def mouseReleaseEvent(self, event):
        self.initial_pos = None

    def add_photo(self):
        path = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
        if path:
            self.photo_path = path
            image = QImage(path).scaled(230, 230)
            self.photo.setPixmap(QPixmap.fromImage(image))

    def send_message(self):
        text = self.text_edit.toPlainText()
        photo_bytes = open(self.photo_path, 'rb') if self.photo_path else None
        if not text and not photo_bytes:
            self.statusBar().showMessage('Введите текст, или прикрепите изображение', 2000)
        else:
            recievers = self.recievers_edit.currentText()
            recievers = users.objects.all() if recievers == 'all' else\
                users.objects.filter(class_letter__startswith=recievers)
            for user in recievers:
                try:
                    if photo_bytes and user.user_id == 5916829058:
                        bot.send_photo(user.user_id, caption=text, photo=photo_bytes)
                        break
                    elif user.user_id == 5916829058:
                        bot.send_message(user.user_id, text)
                except ApiTelegramException as ex:
                    if ex.description == 'Forbidden: bot was blocked by the user':
                        user.delete()
                time.sleep(0.036)
            self.clear()
            self.statusBar().showMessage('Сообщение отправлено', 3000)

    def add_schedule(self):
        file_path = QFileDialog.getOpenFileName(self, 'Выбрать файл', '')[0]
        file_name = file_path.split('/')[-1]
        shutil.copy(file_path, f'./uploads/{file_name}')
        self.statusBar().showMessage(main_schedule_parse(file_name), 3000)

    def clear(self):
        self.text_edit.clear()
        self.photo.clear()
        self.photo_path = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = Panel()
    widget.show()
    sys.exit(app.exec())