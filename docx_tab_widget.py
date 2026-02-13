import re

from PyQt6 import QtCore
from PyQt6.QtWidgets import QTabWidget, QWidget, QHBoxLayout, QTextEdit, QVBoxLayout, QLabel, QDateTimeEdit, QLineEdit, \
    QPushButton
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QAction
from html_text_gen import parse_document, time_limiter
import os


class DocxTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith('.docx'):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.docx'):
                self.add_docx_tab(file_path)
        event.acceptProposedAction()

    def add_docx_tab(self, file_path):
        # Создаем вкладку с информацией о файле
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
        from PyQt6.QtCore import Qt

        tab = QWidget()
        layout = QVBoxLayout(tab)
        label = QLabel(f"Файл: {os.path.basename(file_path)}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.addTab(tab, os.path.basename(file_path))
        self.setCurrentWidget(tab)

    def add_new_tab(self, filepath):
        html, doc_date, doc_num = parse_document(filepath)
        document_date = re.findall(r'\d{2}\.\d{2}\.\d{4}', doc_date)[0]
        print(document_date)
        # print(html)
        """Добавляет новую вкладку в tabWidget"""
        # Создаем содержимое для новой вкладки
        new_widget = QWidget()

        # Создаем основной layout (например, QHBoxLayout для разделения на две части)
        main_layout = QHBoxLayout(new_widget)

        # Левая часть: области для кода и текста
        left_widget = QWidget()
        left_layout = QHBoxLayout(left_widget)

        code_area = QTextEdit()
        code_area.setPlaceholderText("Введите код здесь...")
        code_area.setPlainText(html)

        text_area = QTextEdit()
        text_area.setPlaceholderText("Введите текст здесь...")
        text_area.setHtml(html)
        # text_area.setAcceptRichText(True)
        text_area.setPlainText(text_area.toPlainText())

        # print(text_area.toHtml())
        # print(code_area.toPlainText())
        # link_html_editors(code_area, text_area)
        # set_observalbe_text(code_area, text_area)
        # left_layout.addWidget(QLabel("Код:"))
        left_layout.addWidget(code_area)
        # left_layout.addWidget(QLabel("Текст:"))
        left_layout.addWidget(text_area)

        # Правая часть: панель инструментов
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Элементы для панели инструментов
        datetime_lbl = QLabel("Дата и время:")
        datetime_edit = QDateTimeEdit()
        datetime_edit.setCalendarPopup(True)
        # datetime_edit.setDate(QtCore.QDate.fromString(document_date, "dd.MM.yyyy"))
        final_date = QtCore.QDate.fromString(document_date, "dd.MM.yyyy")
        time_h, time_m = time_limiter(doc_num)
        datetime_ = QtCore.QDateTime(final_date.year(), final_date.month(), final_date.day(), time_h, time_m)
        datetime_edit.setDateTime(datetime_)
        # time_now = QTime(time.localtime().tm_hour, time.localtime().tm_min)
        # print(time_now)
        # datetime_edit.setTime(time_now)

        header_lbl = QLabel("Заголовок:")
        header_edit = QLineEdit()
        header_edit.setPlaceholderText("Введите заголовок...")
        date_num = doc_date.split(' ', 1)
        header_edit.setText(f"{date_num[0]} Постановление {date_num[1]}")

        public_btn = QPushButton("Опубликовать")

        # Добавляем элементы в правый layout
        right_layout.addWidget(datetime_lbl)
        right_layout.addWidget(datetime_edit)
        right_layout.addSpacing(10)  # отступ

        right_layout.addWidget(header_lbl)
        right_layout.addWidget(header_edit)
        right_layout.addSpacing(20)  # отступ

        right_layout.addWidget(public_btn)
        right_layout.addStretch()  # растягивающийся спейсер

        # Добавляем левую и правую части в основной layout
        main_layout.addWidget(left_widget, 3)  # коэффициент растяжения 3
        main_layout.addWidget(right_widget, 1)  # коэффициент растяжения 1

        # Добавляем новую вкладку
        tab_index = self.addTab(new_widget, os.path.basename(filepath))

        # Переключаемся на новую вкладку
        self.setCurrentIndex(tab_index)

        if self.window():
            action_text = self.window().findChild(QAction, "action_text")
            action_html = self.window().findChild(QAction, "action_HTML")

            if action_text:
                # Используем isChecked() для начального состояния
                text_area.setHidden(not action_text.isChecked())
                # Подключаем сигнал
                action_text.toggled.connect(
                    lambda checked, ta=text_area: ta.setHidden(not checked)
                )

            if action_html:
                # Используем isChecked() для начального состояния
                code_area.setHidden(not action_html.isChecked())
                # Подключаем сигнал
                action_html.toggled.connect(
                    lambda checked, ca=code_area: ca.setHidden(not checked)
                )

        action_text.toggled.connect(lambda: text_area.setHidden(not action_text.isChecked()))
        action_html.toggled.connect(lambda: code_area.setHidden(not action_html.isChecked()))
        # Сохраняем ссылки на виджеты, если нужно
        new_widget.code_area = code_area
        new_widget.text_area = text_area
        new_widget.datetime_edit = datetime_edit
        new_widget.header_edit = header_edit
        new_widget.public_btn = public_btn