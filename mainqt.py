import os
from PyQt6 import uic
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QAction
from html_text_gen import parse_document
from PyQt5.QtCore import QDateTime, Qt


# эта функция срабатывает при нажатии кнопки
def hello_world():
    print("Hello world")


def open_file(parent_window):
    dialog = QFileDialog(parent_window)
    dialog.setNameFilter("Documents (*.doc *.docx)")
    files, ok = dialog.getOpenFileNames()
    for file in files:
        add_new_tab(file)


def link_html_editors(code_area, text_area):
    """Связывает редактор кода и HTML просмотрщик"""
    updating = False

    def code_to_html():
        """Из code_area (текст) в text_area (HTML)"""
        nonlocal updating
        if updating:
            return

        updating = True
        try:
            html_code = code_area.toPlainText()
            # Устанавливаем HTML в text_area
            text_area.setHtml(html_code)
        except Exception as e:
            print(f"Ошибка при установке HTML: {e}")
        finally:
            updating = False

    def html_to_code():
        """Из text_area (HTML) в code_area (текст)"""
        nonlocal updating
        if updating:
            return

        updating = True
        try:
            # Получаем HTML из text_area
            html_code = text_area.toHtml()  # Это строка, а не QTextEdit!
            # Преобразуем в чистый HTML
            clean_html = extract_html_from_qt_html(html_code)  # Изменили имя функции
            code_area.setPlainText(clean_html)
        except Exception as e:
            print(f"Ошибка при получении HTML: {e}")
        finally:
            updating = False

    # Подключаем сигналы
    code_area.textChanged.connect(code_to_html)
    text_area.textChanged.connect(html_to_code)

    # Инициализация
    code_to_html()


def extract_html_from_qt_html(qt_html):
    """
    Извлекает чистый HTML из строки, возвращенной QTextEdit.toHtml()

    Args:
        qt_html: строка HTML с тегами Qt
    Returns:
        Чистый HTML без тегов Qt
    """
    import re

    # Удаляем DOCTYPE и мета-теги Qt
    lines = qt_html.split('\n')
    clean_lines = []

    in_body = False
    for line in lines:
        # Пропускаем заголовок и стили
        if line.strip().startswith('<!DOCTYPE'):
            continue
        if '<head>' in line or '</head>' in line:
            continue
        if '<meta' in line and 'content="text/html;' in line:
            continue

        # Начинаем с body
        if '<body' in line:
            in_body = True
            # Извлекаем содержимое body
            match = re.search(r'<body[^>]*>(.*)</body>', line, re.DOTALL)
            if match:
                clean_lines.append(match.group(1))
            continue

        if '</body>' in line:
            in_body = False
            continue

        if in_body:
            clean_lines.append(line)

    clean_html = '\n'.join(clean_lines)

    # Убираем пустые параграфы, добавленные Qt
    clean_html = clean_html.replace(
        '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"></p>',
        '')
    clean_html = clean_html.replace(
        '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>',
        '')

    return clean_html.strip()
def set_observalbe_text(code_area, text_area):
    def update_text(new_text):
        buffer_text = new_text
        code_area.setPlainText(buffer_text)
        text_area.setText(buffer_text)

    code_area.textChanged().connect(lambda: update_text(code_area.toPlainText()))
    text_area.textChanged().connect(lambda: update_text(text_area.toPlainText()))


def add_new_tab(filepath):
    html = parse_document(filepath)
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
    text_area.setText(html)

    #print(text_area.toHtml())
    #print(code_area.toPlainText())
    link_html_editors(code_area, text_area)
    #set_observalbe_text(code_area, text_area)
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

    header_lbl = QLabel("Заголовок:")
    header_edit = QLineEdit()
    header_edit.setPlaceholderText("Введите заголовок...")

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

    # Добавляем кнопку удаления вкладки внизу правой панели
    delete_btn = QPushButton("Удалить эту вкладку")
    # delete_btn.clicked.connect(lambda: remove_tab(form.tabWidget.currentIndex))
    right_layout.addWidget(delete_btn)

    # Добавляем левую и правую части в основной layout
    main_layout.addWidget(left_widget, 3)  # коэффициент растяжения 3
    main_layout.addWidget(right_widget, 1)  # коэффициент растяжения 1

    # Добавляем новую вкладку
    tab_index = form.tabWidget.addTab(new_widget, os.path.basename(filepath))

    # Переключаемся на новую вкладку
    form.tabWidget.setCurrentIndex(tab_index)

    # Сохраняем ссылки на виджеты, если нужно
    new_widget.code_area = code_area
    new_widget.text_area = text_area
    new_widget.datetime_edit = datetime_edit
    new_widget.header_edit = header_edit
    new_widget.public_btn = public_btn


def remove_tab(index):
    """Удаляет вкладку по индексу"""
    if form.tabWidget.count() > 1:  # Оставляем хотя бы одну вкладку
        form.tabWidget.removeTab(index)


# подключаем файл, полученный в QtDesigner
Form, Window = uic.loadUiType("main_window.ui")
app = QApplication([])
window, form = Window(), Form()
form.setupUi(window)
window.show()

action_new_tab = window.findChild(QAction, "actionnewTab")
action_open = window.findChild(QAction, "action_open")
action_open.triggered.connect(lambda: open_file(window))
if action_new_tab:
    action_new_tab.triggered.connect(add_new_tab)
else:
    print("Действие actionnewTab не найдено")


def close_tab_handler(index):
    """Обработчик нажатия на крестик вкладки"""
    print(f"Закрытие вкладки с индексом: {index}")

    # Проверяем, можно ли закрыть вкладку
    if form.tabWidget.count() > 1:  # Оставляем хотя бы одну вкладку
        # Можно добавить проверку на несохраненные изменения
        widget = form.tabWidget.widget(index)
        tab_name = form.tabWidget.tabText(index)

        print(f"Закрываю вкладку: '{tab_name}'")
        form.tabWidget.removeTab(index)
    else:
        print("Нельзя закрыть последнюю вкладку")


form.tabWidget.tabCloseRequested.connect(close_tab_handler)

# запускаем окно программы
app.exec()
