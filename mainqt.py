import json
import os
import re
import time
from datetime import datetime

from PyQt6 import uic, QtCore
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QAction, QIcon

from ConnectionManager import ConnectionManager
from html_text_table_gen import parse_document_text_table
from html_converter import convert
from text_edit_tool_bar import add_tool_bar
from wordpress_module import WordPressAPI


# Убираем глобальный wp, будем использовать через сигналы/слоты
# wp = None

# Оставляем функции, которые не зависят от wp
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
            html_code = text_area.toHtml()
            clean_html = convert(html_code)
            code_area.setPlainText(clean_html)
        except Exception as e:
            print(f"Ошибка при получении HTML: {e}")
        finally:
            updating = False

    code_area.textChanged.connect(code_to_html)
    text_area.textChanged.connect(html_to_code)
    code_to_html()


def time_limiter(num):
    res_h = 0
    res_m = 0
    if num >= 1440:
        num = num % 1440
    res_h = num // 60
    res_m = num % 60
    return res_h, res_m


def hide_show_widget(widget, is_shown):
    widget.setHidden(not is_shown)


# Класс для хранения состояния приложения
class AppState:
    def __init__(self):
        self.wp = None
        self.thread = None
        self.worker = None
        self.connection_manager = ConnectionManager()

    def set_wp(self, wp_instance):
        """Установка WP и обновление в менеджере"""
        self.wp = wp_instance
        self.connection_manager.set_wp(wp_instance)


app_state = AppState()


def add_new_tab(filepath):
    """Добавляет новую вкладку в tabWidget с ожиданием подключения"""
    global app_state

    html, doc_date, doc_num = parse_document_text_table(filepath)
    document_date = re.findall(r'\d{2}\.\d{2}\.\d{4}', doc_date)[0]

    new_widget = QWidget()
    mainest_layout = QVBoxLayout(new_widget)

    main_widget = QWidget()
    main_layout = QHBoxLayout(main_widget)

    left_widget = QWidget()
    left_layout = QHBoxLayout(left_widget)

    code_area = QTextEdit()
    code_area.setPlaceholderText("Введите код здесь...")
    code_area.setPlainText(html)

    text_area = QTextEdit()
    text_area.setPlaceholderText("Введите текст здесь...")
    text_area.setHtml(html)

    toolbar = add_tool_bar(text_area)
    mainest_layout.addWidget(toolbar)
    mainest_layout.addWidget(main_widget)

    link_html_editors(code_area, text_area)
    left_layout.addWidget(code_area)
    left_layout.addWidget(text_area)

    right_widget = QWidget()
    right_layout = QVBoxLayout(right_widget)

    # ... (код для datetime и заголовка как раньше) ...
    datetime_lbl = QLabel("Дата и время:")
    datetime_edit = QDateTimeEdit()
    datetime_edit.setCalendarPopup(True)
    final_date = QtCore.QDate.fromString(document_date, "dd.MM.yyyy")
    time_h, time_m = time_limiter(doc_num)
    datetime_ = QtCore.QDateTime(final_date.year(), final_date.month(), final_date.day(), time_h, time_m)
    datetime_edit.setDateTime(datetime_)

    header_lbl = QLabel("Заголовок:")
    header_edit = QLineEdit()
    header_edit.setPlaceholderText("Введите заголовок...")
    date_num = doc_date.split(' ', 1)
    header_edit.setText(f"{date_num[0]} Постановление {date_num[1]}")

    # Создаем список категорий
    categories_lbl = QLabel("Рубрики:")
    categories_list = QListWidget()

    # Добавляем индикатор загрузки
    loading_label = QLabel("Загрузка рубрик...")
    loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    loading_label.hide()

    # Функция для загрузки категорий
    def load_categories():
        if not app_state.wp:
            loading_label.setText("Нет подключения к WordPress")
            return

        try:
            categories = app_state.wp.get_categories()
            categories_list.clear()

            if categories:
                loading_label.hide()
                categories_list.show()

                for category in categories:
                    if isinstance(category, dict) and 'name' in category:
                        item = QListWidgetItem(categories_list)
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        item.setCheckState(Qt.CheckState.Unchecked)
                        item.setData(32, category)
                        item.setText(category['name'])
                        if category['name'] == "Постановления":
                            item.setCheckState(Qt.CheckState.Checked)
            else:
                loading_label.setText("Не удалось загрузить рубрики")

        except Exception as e:
            loading_label.setText(f"Ошибка загрузки: {str(e)}")

    # Сохраняем функцию как атрибут виджета для вызова из update_all_tabs_categories
    new_widget.load_categories = load_categories

    def change_check_on_selection(item: QListWidgetItem):
        if item.checkState() == item.checkState().Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)

    categories_list.itemClicked.connect(change_check_on_selection)

    # Пытаемся загрузить категории с ожиданием подключения
    if app_state.wp and app_state.wp.check_connection():
        # Если уже подключены, загружаем сразу
        load_categories()
    else:
        # Показываем индикатор загрузки
        categories_list.hide()
        loading_label.show()
        loading_label.setText("Ожидание подключения к WordPress...")

        # Добавляем в очередь на загрузку после подключения
        def delayed_load():
            if app_state.wp and app_state.wp.check_connection():
                load_categories()
            else:
                loading_label.setText("Не удалось подключиться к WordPress")

        # Используем ConnectionManager для ожидания
        app_state.connection_manager.wait_for_connection(delayed_load)

    def get_checked_categories():
        checked = []
        for x in range(categories_list.count()):
            item = categories_list.item(x)
            if item.checkState() == item.checkState().Checked:
                checked.append(item.text())
        return checked

    public_btn = QPushButton("Опубликовать")
    public_btn.clicked.connect(lambda: publish(
        header_edit.text(),
        code_area.toPlainText(),
        datetime_edit.dateTime().toPyDateTime(),
        filepath,
        get_checked_categories
    ))

    # Добавляем элементы в правый layout
    right_layout.addWidget(datetime_lbl)
    right_layout.addWidget(datetime_edit)
    right_layout.addSpacing(10)
    right_layout.addWidget(header_lbl)
    right_layout.addWidget(header_edit)
    right_layout.addSpacing(20)
    right_layout.addWidget(categories_lbl)
    right_layout.addWidget(loading_label)
    right_layout.addWidget(categories_list)
    right_layout.addSpacing(20)
    right_layout.addWidget(public_btn)
    right_layout.addStretch()

    main_layout.addWidget(left_widget, 3)
    main_layout.addWidget(right_widget, 1)

    tab_index = tabWidgetHtml.addTab(new_widget, os.path.basename(filepath))
    tabWidgetHtml.setCurrentIndex(tab_index)

    # Сохраняем ссылки на виджеты
    new_widget.code_area = code_area
    new_widget.text_area = text_area
    new_widget.datetime_edit = datetime_edit
    new_widget.header_edit = header_edit
    new_widget.categories_list = categories_list
    new_widget.loading_label = loading_label
    new_widget.public_btn = public_btn


def publish(title, content, datetime, file, categories=None):
    """Публикация поста"""
    global app_state

    if not app_state.wp or not app_state.wp.check_connection():
        QMessageBox.critical(window, "Ошибка", "Нет подключения к WordPress")
        return

    print("date to publish: " + datetime.strftime("%Y-%m-%d %H:%M:%S"))
    upload = app_state.wp.upload_media(file)
    if upload:
        print(upload)
        if isinstance(upload, dict) and 'guid' in upload:
            guid = upload['guid']
            if isinstance(guid, dict) and 'raw' in guid:
                url = guid['raw']
                print(url)
                post = app_state.wp.publish_post(
                    title=title,
                    content=content.format(url),
                    categories=categories,
                    status="publish",
                    publish_date=datetime
                )
                if post:
                    QMessageBox.information(window, "Успех", "Пост опубликован")


def open_dialog_wp_login():
    """Открытие диалога входа в WordPress"""
    global app_state

    dialog = uic.loadUi("dialog_wp_login.ui")

    def on_login():
        data = [
            dialog.le_url.text(),
            dialog.le_login.text(),
            dialog.le_password.text()
        ]

        # Запускаем подключение в потоке
        start_login_thread(data)
        dialog.accept()

    button_box = dialog.findChild(QDialogButtonBox, "buttonBox")
    if button_box:
        button_box.accepted.connect(on_login)

    if hasattr(dialog, 'btn_login_wp'):
        dialog.btn_login_wp.clicked.connect(on_login)

    dialog.exec()


def check_wp_login():
    """Проверка статуса подключения"""
    global app_state

    if app_state.wp and app_state.wp.check_connection():
        QMessageBox.information(
            window,
            "Вход выполнен",
            f"Вход выполнен. Подключено к {app_state.wp.base_url}"
        )
    else:
        QMessageBox.critical(
            window,
            "Ошибка входа",
            "Логин или пароль не верен или сервер недоступен"
        )


def start_login_thread(login_data):
    """Запуск потока для подключения"""
    global app_state

    from LoginWorker import LoginWorker

    # Создаем поток
    app_state.thread = QThread()
    # Создаем рабочий объект
    app_state.worker = LoginWorker(login_data)
    # Перемещаем рабочий объект в поток
    app_state.worker.moveToThread(app_state.thread)

    # Подключаем сигналы
    app_state.thread.started.connect(app_state.worker.run)
    app_state.worker.finished.connect(on_login_finished)
    app_state.worker.progress.connect(update_menu_status)
    app_state.worker.finished.connect(app_state.thread.quit)
    app_state.worker.finished.connect(app_state.worker.deleteLater)
    app_state.thread.finished.connect(app_state.thread.deleteLater)

    # Запускаем поток
    app_state.thread.start()


def on_login_finished(success, message):
    """Обработка завершения попытки входа"""
    global app_state

    if success:
        # Сохраняем wp из worker через специальный метод
        app_state.set_wp(app_state.worker.wp)

        # Сохраняем данные в файл
        with open("wpdata.wp", "w") as f:
            json.dump(app_state.worker.login_data, f)

        QMessageBox.information(window, "Вход выполнен", message)
        update_menu_status("connected")

        # Принудительно проверяем подключение и обрабатываем ожидающие запросы
        app_state.connection_manager.check_connection()

        # Обновляем все открытые вкладки
        update_all_tabs_categories()

    else:
        QMessageBox.critical(window, "Ошибка входа", message)
        update_menu_status("disconnected")
        # Отменяем все ожидающие запросы
        app_state.connection_manager.cancel_all_requests()

def update_all_tabs_categories():
    """Обновление категорий во всех открытых вкладках"""
    for i in range(tabWidgetHtml.count()):
        widget = tabWidgetHtml.widget(i)
        if hasattr(widget, 'load_categories'):
            # Вызываем функцию загрузки категорий для вкладки
            widget.load_categories()


def update_all_tabs_categories():
    """Обновление категорий во всех открытых вкладках"""
    for i in range(tabWidgetHtml.count()):
        widget = tabWidgetHtml.widget(i)
        if hasattr(widget, 'categories_list') and hasattr(widget, 'loading_label'):
            # Функция загрузки для каждой вкладки
            def load_tab_categories(w=widget):
                if hasattr(w, 'categories_list') and hasattr(w, 'loading_label'):
                    # Здесь код загрузки категорий для конкретной вкладки
                    # Можно вызвать функцию, аналогичную load_categories из add_new_tab
                    pass


def update_menu_status(status):
    """Обновление статуса в меню"""
    status_texts = {
        "disconnected": "Wordpress: Отключено",
        "connecting": "Wordpress: Подключение...",
        "connected": "Wordpress: Подключено"
    }

    menu_wordpress = window.findChild(QMenu, "menuWordpress")
    if menu_wordpress:
        menu_wordpress.setTitle(status_texts.get(status, "Отключено"))


def login_on_load(path):
    """Загрузка и попытка входа при старте"""
    # Создаем файл если не существует
    if not os.path.exists(path):
        open(path, "x", encoding="utf-8")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f)

    # Читаем данные
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if content:
            data = json.loads(content)
            if data:
                # Обновляем статус в меню
                update_menu_status("connecting")
                # Запускаем подключение в отдельном потоке
                start_login_thread(data)


def close_tab_handler(index):
    """Обработчик нажатия на крестик вкладки"""
    if tabWidgetHtml.count() > 1:
        tabWidgetHtml.removeTab(index)


# Загрузка UI
Form, Window = uic.loadUiType("main_window.ui")
app = QApplication([])
window, form = Window(), Form()
form.setupUi(window)

# Настройка вкладок
form.tab_html_gen.setLayout(QVBoxLayout())
tabWidgetHtml = QTabWidget()
form.tab_html_gen.layout().addWidget(tabWidgetHtml)
tabWidgetHtml.setTabsClosable(True)
tabWidgetHtml.setMovable(True)

# Поиск действий меню
action_new_tab = window.findChild(QAction, "actionnewTab")
action_open = window.findChild(QAction, "action_open")
action_gen_html = window.findChild(QMenu, "menu_HTML")
action_wp_dialog = window.findChild(QAction, "action_open_wp_dialog")
action_status = window.findChild(QAction, "action_status")

# Подключение сигналов
if action_wp_dialog:
    action_wp_dialog.triggered.connect(open_dialog_wp_login)
if action_open:
    action_open.triggered.connect(lambda: open_file(window))
if action_gen_html:
    action_gen_html.triggered.connect(lambda: hide_show_widget(tabWidgetHtml, action_gen_html.isChecked()))
if action_status:
    action_status.triggered.connect(check_wp_login)

tabWidgetHtml.tabCloseRequested.connect(close_tab_handler)

# Показываем окно
window.show()

# Пытаемся загрузить сохраненные данные
login_on_load("wpdata.wp")

# Добавляем тестовую вкладку
add_new_tab("C:/Users/brylo/OneDrive/Desktop/publisher/py/37.docx")

# Запуск приложения
app.exec()