import re

from PyQt6 import uic, QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QToolButton, QGridLayout, QFrame, QTextEdit
from PyQt6.QtGui import QAction, QIcon
from html_converter import convert


def align_text(html, side):
    return


def text_make_bold(text_edit, is_bold):
    full_text = convert(text_edit.toHtml())
    sel_text = text_edit.textCursor().selectedText()

    # Экранируем спецсимволы в выделенном тексте
    escaped_sel_text = re.escape(sel_text)

    # Ищем паттерн (re.DOTALL для учета переносов строк, re.UNICODE для юникода)
    pattern = f"<strong>.*?{escaped_sel_text}.*?</strong>"
    match = re.search(pattern, full_text, re.DOTALL | re.UNICODE)

    return


def test(text_edit):
    #te = QTextEdit()
    full_text = convert(text_edit.toHtml())
    sel_text = text_edit.textCursor().selectedText()

    #converted_text = convert(sel_text)
    print(sel_text)
    return


def add_icon_btn(name, img_path, action, is_trigger=False, shortcut="None"):
    btn = QToolButton()
    btn.setIcon(QIcon(img_path))

    if is_trigger:
        ""
    if shortcut != "None":
        btn.setShortcut(shortcut)
    btn.clicked.connect(action)
    return btn


def separator(width, height, color):
    sep = QFrame()
    sep.setFixedWidth(width)
    sep.setFixedHeight(height)  # Высота под размер иконок
    sep.setStyleSheet(f"background-color: {color}; margin: 0 6px;")
    return sep


def add_tool_bar(text_edit) -> QFrame:
    frame = QFrame()
    frame.setObjectName("toolbar_frame")  # Даём уникальное имя

    # Стиль применяется ТОЛЬКО к объекту с именем toolbar_frame
    frame.setStyleSheet("""
            #toolbar_frame {
                background-color: #ccc;
                padding: 5px;
            }
        """)

    btn_align_right = add_icon_btn("По правому краю", "icons/text-align-right.svg", lambda: align_text("", "right"))
    btn_align_left = add_icon_btn("По левому краю", "icons/text-align-left.svg", lambda: align_text("", "left"))
    btn_align_justify = add_icon_btn("По ширине", "icons/text-align-justify.svg", lambda: align_text("", "justify"))
    btn_align_center = add_icon_btn("По центру", "icons/text-align-center.svg", lambda: align_text("", "center"))
    btn_bold = add_icon_btn("Жирный текст", "icons/text-bold.svg", lambda: test(text_edit))

    toolbar = QGridLayout()

    #toolbar.setAlignment(Qt.AlignLeft)  # Выравнивание всего layout по левому краю
    toolbar.setHorizontalSpacing(2)  # Отступ между элементами (в пикселях)
    toolbar.setVerticalSpacing(2)  # Вертикальный отступ (если будет несколько строк)
    toolbar.setContentsMargins(0, 0, 0, 0)  # Убираем внешние отступы

    frame.setLayout(toolbar)
    toolbar.addWidget(btn_align_left, 0, 0)
    toolbar.addWidget(btn_align_center, 0, 1)
    toolbar.addWidget(btn_align_right, 0, 2)
    toolbar.addWidget(btn_align_justify, 0, 3)
    toolbar.addWidget(separator(1, 24, "#999"), 0, 4)
    toolbar.addWidget(btn_bold, 0, 5)
    toolbar.setColumnStretch(6, 1)  # 4-я колонка (несуществующая) будет растягиваться

    return frame
