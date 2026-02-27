import re

from PyQt6.QtWidgets import QToolButton, QGridLayout, QFrame, QTextEdit
from PyQt6.QtGui import QIcon
from html.html_converter import convert, check_for_empty_tags


def align_text(text_edit, code_area, side):
    full_text = code_area.toPlainText()
    sel_text = text_edit.textCursor().selectedText()
    escaped_sel_text = re.escape(sel_text)
    pattern = r'<p[^>]*style=[\'"]?[^\'"]*text-align:\s*([^\'";]+)[\'"]?[^>]*>'

    match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
    if match:
        text_align = match.group(1).strip()
        print(f"text-align: {text_align}")  # center
    return


def text_make_bold(text_edit, code_area, is_bold):
    full_text = code_area.toPlainText()
    sel_text = text_edit.textCursor().selectedText()

    # Экранируем спецсимволы в выделенном тексте
    escaped_sel_text = re.escape(sel_text)

    # Ищем паттерн (re.DOTALL для учета переносов строк, re.UNICODE для юникода)
    # Ищем внутри тега <strong>, где между тегами и текстом может быть другой текст
    pattern = fr"<strong>(?:(?!<[^>]*>).)*?({escaped_sel_text})(?:(?!<[^>]*>).)*?</strong>"
    # Для любого HTML тега
    pattern_all = fr"<[^>]+>(?:(?!<[^>]*>).)*?({escaped_sel_text})(?:(?!<[^>]*>).)*?</[^>]+>"
    match = re.search(pattern, full_text, re.DOTALL | re.UNICODE)
    if match:
        print(f"Поиск жирного выделенного текста: {match.group(0)}")
        print(f"Поиск жирного выделенного текста группа 1: {match.group(1)}")

        def replace_bold(m):
            # m.group(0) - всё найденное
            # m.group(1) - искомый текст
            # Заменяем только искомый текст на </strong>{sel_text}<strong>
            return m.group(0).replace(m.group(1), f"</strong>{sel_text}<strong>", 1)

        full_text = re.sub(pattern, replace_bold, full_text, count=1, flags=re.DOTALL | re.UNICODE)
    else:
        match_all = re.search(pattern_all, full_text, re.DOTALL | re.UNICODE)
        if match_all:
            print(f"Нежирный текст найден: {match_all.group(0)}")
            print(f"Нежирный текст найден группа 1: {match_all.group(1)}")

            def replace_any(m):
                # Заменяем только искомый текст на <strong>{sel_text}</strong>
                return m.group(0).replace(m.group(1), f"<strong>{sel_text}</strong>", 1)

            full_text = re.sub(pattern_all, replace_any, full_text, count=1, flags=re.DOTALL | re.UNICODE)
    full_text = check_for_empty_tags(full_text)
    code_area.setPlainText(full_text)
    return


def test(text_edit: QTextEdit):
    # te = QTextEdit()
    full_text = convert(text_edit.toHtml())
    sel_text = text_edit.textCursor().selectedText()

    # converted_text = convert(sel_text)
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


def add_tool_bar(text_edit, code_area) -> QFrame:
    frame = QFrame()
    frame.setObjectName("toolbar_frame")  # Даём уникальное имя

    # Стиль применяется ТОЛЬКО к объекту с именем toolbar_frame
    frame.setStyleSheet("""
            #toolbar_frame {
                background-color: #ccc;
                padding: 5px;
            }
        """)

    btn_align_right = add_icon_btn("По правому краю", "./icons/text-align-right.svg", lambda: align_text(text_edit, code_area, "right"))
    btn_align_left = add_icon_btn("По левому краю", "./icons/text-align-left.svg", lambda: align_text(text_edit, code_area, "left"))
    btn_align_justify = add_icon_btn("По ширине", "./icons/text-align-justify.svg", lambda: align_text(text_edit, code_area, "justify"))
    btn_align_center = add_icon_btn("По центру", "./icons/text-align-center.svg", lambda: align_text(text_edit, code_area, "center"))
    #btn_align_center = add_icon_btn("По центру", "./icons/text-align-center.svg", lambda: test(text_edit))
    btn_bold = add_icon_btn("Жирный текст", "./icons/text-bold.svg",
                            lambda: text_make_bold(text_edit, code_area, False))

    toolbar = QGridLayout()

    # toolbar.setAlignment(Qt.AlignLeft)  # Выравнивание всего layout по левому краю
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
