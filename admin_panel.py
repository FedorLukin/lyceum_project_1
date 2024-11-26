import sys
import time
import shutil
import PyQt6
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from telebot.apihelper import ApiTelegramException
from bot import bot, main_schedule_parse
from db.models import *


class Panel(QMainWindow):
    def __init__(self) -> None:
        """
        Инициализация админ-панели.

        Аргументы:
            None: Функция не принимает аргументов.

        Возвращает:
            None: Функция ничего не возвращает.
        """
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
        self.initial_pos = None

    def mousePressEvent(self, event: PyQt6.QtGui.QMouseEvent) -> None:
        """
        Обработчик нажатия на окно для его перемещения.

        Аргументы:
            Event: Событие нажатия мыши на окно.

        Возвращает:
            None: Функция ничего не возвращает.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.position().toPoint()

    def mouseMoveEvent(self, event: PyQt6.QtGui.QMouseEvent) -> None:
        """
        Обработчик перемещения мыши при зажатой левой клавише, перемещающий окно вслед за мышью.

        Аргументы:
            Event: Событие перемещения мыши.

        Возвращает:
            None: Функция ничего не возвращает.
        """
        if self.initial_pos:
            delta = event.position().toPoint() - self.initial_pos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )

    def mouseReleaseEvent(self, event: PyQt6.QtGui.QMouseEvent) -> None:
        """
        Обработчик отпускания кнопки мыши.

        Аргументы:
            Event: Событие отпускания кнопки мыши.

        Возвращает:
            None: Функция ничего не возвращает.
        """
        self.initial_pos = None

    def add_photo(self) -> None:
        """
        Функция добавления изображения для рассылки.

        Функция открывает диалоговое окно выбора изображения в формате .jpg или .png, после выбора сохраняет путь
        к изображению и отображает его для предпросмотра перед рассылкой.

        Аргументы:
            None: Функция ничего не принимает.

        Возвращает:
            None: Функция ничего не возвращает.
        """
        path = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '', 'Изображение (*.jpg);;Изображение (*.png)')[0]
        if path:
            self.photo_path = path
            image = QImage(path).scaled(230, 230)
            self.photo.setPixmap(QPixmap.fromImage(image))

    def send_message(self) -> None:
        """
        Функция рассылки сообщения пользователям.

        Функция получает queryset выбранных получателей из бд, итерируется по нему и отправляет сообщение пользователям.

        Аргументы:
            None: Функция ничего не принимает.

        Возвращает:
            None: Функция ничего не возвращает.
        """
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
                    if photo_bytes:
                        bot.send_photo(user.user_id, caption=text, photo=photo_bytes)
                        break
                    else:
                        bot.send_message(user.user_id, text)
                except ApiTelegramException as ex:
                    if ex.description == 'Forbidden: bot was blocked by the user':
                        user.delete()
                time.sleep(0.036)
            self.clear()
            self.statusBar().showMessage('Сообщение отправлено', 3000)

    def add_schedule(self) -> None:
        """
        Функция добавления расписания.

        Функция открывает диалоговое окно выбора файла в формате .xlsx, создаёт копию выбранного файла в директории
        ./uploads и передаёт имя файла в качестве аргумента функции main_schedule_parse из файла bot.py.

        Аргументы:
            None: Функция ничего не принимает.

        Возвращает:
            None: Функция ничего не возвращает.
        """
        file_path = QFileDialog.getOpenFileName(self, 'Выбрать файл', '', 'Файл (*.xlsx)')[0]
        if file_path:
            file_name = file_path.split('/')[-1]
            shutil.copy(file_path, f'./uploads/{file_name}')
            self.statusBar().showMessage(main_schedule_parse(file_name), 3000)

    def clear(self) -> None:
        """
        Функция сброса сообщения для рассылки.

        Функция очищает поле ввода текста и окно с изображением сообщения для рассылки.

        Аргументы:
            None: Функция ничего не принимает.
        
        Возвращает:
            None: Функция ничего не возвращает.
        """
        self.text_edit.clear()
        self.photo.clear()
        self.photo_path = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = Panel()
    widget.show()
    sys.exit(app.exec())
