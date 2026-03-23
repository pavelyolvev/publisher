import json
import os
import re
from datetime import datetime

from PyQt6 import uic, QtCore
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QAction

from qt_widgets import posts_window
from wordpress.ConnectionManager import ConnectionManager
from html.html_text_table_gen import parse_document_text_table
from html.html_converter import convert, check_for_empty_tags
from qt_widgets.text_edit_tool_bar import add_tool_bar


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
            html_code = check_for_empty_tags(html_code)
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
            clean_html = check_for_empty_tags(clean_html)
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


def hide_show_widget(tab_widget: QTabWidget, widget_name: str, is_shown: bool):
    """
    Скрывает или показывает виджет в текущей вкладке

    Args:
        tab_widget: QTabWidget, содержащий вкладки
        widget_name: имя атрибута виджета (строкой)
        is_shown: True - показать, False - скрыть
    """
    # Получаем текущую вкладку
    current_tab = tab_widget.currentWidget()

    if current_tab and hasattr(current_tab, widget_name):
        # Получаем виджет по имени атрибута
        widget = getattr(current_tab, widget_name)
        # Скрываем или показываем
        widget.setHidden(not is_shown)
    else:
        print(f"Виджет {widget_name} не найден в текущей вкладке")


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
is_online = False


def add_new_tab(filepath):
    """Добавляет новую вкладку в tabWidget с ожиданием подключения"""
    global app_state
    global is_online

    html, doc_date, doc_num = parse_document_text_table(filepath, is_online)
    if doc_date is not None:
        document_date = re.findall(r'\d{2}\.\d{2}\.\d{4}', doc_date)[0]
    else:
        doc_date = ""
        document_date = "00.00.0000"
        QMessageBox().critical(None, "Ошибка!", f"Не удалось определить дату и номер постановления. Номер постановления указан по названию файла. Файл {os.path.basename(filepath)}")

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

    toolbar = add_tool_bar(text_area, code_area)
    mainest_layout.addWidget(toolbar)
    mainest_layout.addWidget(main_widget)

    link_html_editors(code_area, text_area)
    left_layout.addWidget(code_area)
    left_layout.addWidget(text_area)

    right_widget = QWidget()
    right_layout = QVBoxLayout(right_widget)

    # ... (datetime и header как раньше) ...
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
    if doc_date != "":
        header_edit.setText(f"{date_num[0]} Постановление {date_num[1]}")
    else:
        header_edit.setText(f"ВставьтеДату Постановление № {os.path.splitext(os.path.basename(filepath))[0]}")

    # Создаем дерево категорий
    categories_lbl = QLabel("Рубрики:")
    categories_tree = QTreeWidget()
    categories_tree.setHeaderLabel("Категории")
    categories_tree.setIndentation(20)
    categories_tree.setAlternatingRowColors(True)
    categories_tree.setMinimumHeight(200)

    # Настройка размеров
    header = categories_tree.header()
    header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    header.setStretchLastSection(True)

    # Добавляем индикатор загрузки
    loading_label = QLabel("Загрузка рубрик...")
    loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    loading_label.hide()

    # Функция для построения иерархического дерева категорий
    def build_category_tree(categories):
        """Строит иерархическое дерево категорий"""
        # Создаем словарь для быстрого доступа к элементам по ID
        items_dict = {}

        # Сначала создаем все элементы
        for category in categories:
            if isinstance(category, dict) and 'name' in category:
                item = QTreeWidgetItem()
                item.setText(0, category['name'])
                # Сохраняем полный объект категории в UserRole
                item.setData(0, Qt.ItemDataRole.UserRole, category)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(0, Qt.CheckState.Unchecked)

                items_dict[category['id']] = item

        # Затем устанавливаем родительские отношения
        for category in categories:
            if isinstance(category, dict) and 'parent' in category:
                parent_id = category['parent']
                if parent_id in items_dict:
                    # Это подрубрика - добавляем к родителю
                    parent_item = items_dict[parent_id]
                    child_item = items_dict[category['id']]
                    parent_item.addChild(child_item)
                elif category['parent'] == 0:
                    # Это корневая категория - добавляем в дерево
                    categories_tree.addTopLevelItem(items_dict[category['id']])

        # Раскрываем дерево для удобства
        categories_tree.expandAll()

        # Отмечаем категорию "Постановления" по умолчанию
        for i in range(categories_tree.topLevelItemCount()):
            item = categories_tree.topLevelItem(i)
            if item.text(0) == "Постановления":
                item.setCheckState(0, Qt.CheckState.Checked)
                break

    # Функция для загрузки категорий
    def load_categories():
        if not app_state.wp:
            loading_label.setText("Нет подключения к WordPress")
            return

        try:
            categories = app_state.wp.get_categories()
            categories_tree.clear()

            if categories:
                loading_label.hide()
                categories_tree.show()
                build_category_tree(categories)
            else:
                loading_label.setText("Не удалось загрузить рубрики")

        except Exception as e:
            loading_label.setText(f"Ошибка загрузки: {str(e)}")
            print(f"Ошибка загрузки категорий: {e}")

    # Сохраняем функцию как атрибут виджета
    new_widget.load_categories = load_categories

    # Обработка изменения состояния чекбоксов
    def on_item_changed(item, column):
        """Обновляет состояние дочерних элементов при изменении родителя"""
        if column == 0:
            if item.checkState(column) == Qt.CheckState.Checked:
                # Если родитель отмечен, отмечаем всех детей
                for i in range(item.childCount()):
                    child = item.child(i)
                    child.setCheckState(0, Qt.CheckState.Checked)
            else:
                # Если родитель снят, снимаем всех детей
                for i in range(item.childCount()):
                    child = item.child(i)
                    child.setCheckState(0, Qt.CheckState.Unchecked)

            # Обновляем состояние родителя (если есть)
            parent = item.parent()
            if parent:
                update_parent_check_state(parent)

    def update_parent_check_state(parent_item):
        """Обновляет состояние родителя на основе состояния детей"""
        all_checked = True
        any_checked = False

        for i in range(parent_item.childCount()):
            child_state = parent_item.child(i).checkState(0)
            if child_state == Qt.CheckState.Unchecked:
                all_checked = False
            else:
                any_checked = True

        if all_checked:
            parent_item.setCheckState(0, Qt.CheckState.Checked)
        elif any_checked:
            # В Qt нет частичного состояния по умолчанию для чекбоксов,
            # поэтому оставляем как есть или можно установить в Checked
            parent_item.setCheckState(0, Qt.CheckState.Checked)
        else:
            parent_item.setCheckState(0, Qt.CheckState.Unchecked)

    categories_tree.itemChanged.connect(on_item_changed)

    # Обработка двойного клика для изменения состояния
    def on_item_clicked(item, column):
        current_state = item.checkState(column)
        new_state = Qt.CheckState.Unchecked if current_state == Qt.CheckState.Checked else Qt.CheckState.Checked
        item.setCheckState(column, new_state)

    categories_tree.itemDoubleClicked.connect(on_item_clicked)

    # Функция для получения ID выбранных категорий (для publish_post)
    def get_selected_category_ids():
        """
        Возвращает список ID выбранных категорий для publish_post
        """
        selected_ids = []

        def collect_ids(item):
            if item.checkState(0) == Qt.CheckState.Checked:
                category_data = item.data(0, Qt.ItemDataRole.UserRole)
                if category_data and 'id' in category_data:
                    cat_id = category_data['id']
                    if cat_id not in selected_ids:
                        selected_ids.append(cat_id)

            for i in range(item.childCount()):
                collect_ids(item.child(i))

        # Собираем ID со всех уровней
        for i in range(categories_tree.topLevelItemCount()):
            collect_ids(categories_tree.topLevelItem(i))

        # Для отладки
        print(f"Выбранные ID категорий: {selected_ids}")

        return selected_ids

    # Функция для получения названий выбранных категорий (для отображения)
    def get_selected_category_names():
        """Возвращает список названий выбранных категорий"""
        selected_names = []

        def collect_names(item):
            if item.checkState(0) == Qt.CheckState.Checked:
                selected_names.append(item.text(0))

            for i in range(item.childCount()):
                collect_names(item.child(i))

        for i in range(categories_tree.topLevelItemCount()):
            collect_names(categories_tree.topLevelItem(i))

        return selected_names

    # Функция для получения подробной информации о выбранных категориях
    def get_selected_categories_info():
        """Возвращает список словарей с полной информацией о выбранных категориях"""
        selected_categories = []

        def collect_info(item):
            if item.checkState(0) == Qt.CheckState.Checked:
                category_data = item.data(0, Qt.ItemDataRole.UserRole)
                if category_data:
                    selected_categories.append(category_data)

            for i in range(item.childCount()):
                collect_info(item.child(i))

        for i in range(categories_tree.topLevelItemCount()):
            collect_info(categories_tree.topLevelItem(i))

        return selected_categories

    # Подключаемся к WordPress
    if app_state.wp and app_state.wp.check_connection():
        load_categories()
    else:
        categories_tree.hide()
        loading_label.show()
        loading_label.setText("Ожидание подключения к WordPress...")

        def delayed_load():
            if app_state.wp and app_state.wp.check_connection():
                load_categories()
            else:
                loading_label.setText("Не удалось подключиться к WordPress")

        app_state.connection_manager.wait_for_connection(delayed_load)

    public_btn = QPushButton("Опубликовать")

    # Обновляем лямбда-функцию для использования ID категорий
    public_btn.clicked.connect(lambda: publish(
        header_edit.text(),
        code_area.toPlainText(),
        datetime_edit.dateTime().toPyDateTime(),
        filepath,
        get_selected_category_ids  # Передаем функцию, возвращающую список ID
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
    right_layout.addWidget(categories_tree)
    right_layout.addSpacing(20)

    # Добавляем информационную метку о выбранных категориях (опционально)
    selected_info = QLabel()
    selected_info.setWordWrap(True)
    selected_info.setMaximumHeight(60)
    selected_info.setStyleSheet("color: gray; font-size: 10px;")

    def update_selected_info():
        names = get_selected_category_names()
        if names:
            selected_info.setText(f"Выбрано: {', '.join(names)}")
        else:
            selected_info.setText("Ничего не выбрано")

    # Подключаем обновление информации при изменении
    categories_tree.itemChanged.connect(lambda: update_selected_info())

    right_layout.addWidget(selected_info)
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
    new_widget.categories_tree = categories_tree
    new_widget.loading_label = loading_label
    new_widget.public_btn = public_btn
    new_widget.selected_info = selected_info

    # Сохраняем методы для доступа к выбранным категориям
    new_widget.get_selected_category_ids = get_selected_category_ids
    new_widget.get_selected_category_names = get_selected_category_names
    new_widget.get_selected_categories_info = get_selected_categories_info


def publish(title, content, publish_datetime, filepath, get_category_ids_func):
    """
    Публикует запись в WordPress

    Args:
        title: заголовок записи
        content: содержание записи
        publish_datetime: дата и время публикации
        filepath: путь к файлу (для информации)
        get_category_ids_func: функция, возвращающая список ID выбранных категорий
    """
    global app_state

    if not app_state.wp:
        QMessageBox.warning(None, "Ошибка", "Нет подключения к WordPress")
        return

    try:
        # Получаем ID выбранных категорий
        category_ids = get_category_ids_func()

        print(f"Публикация с категориями ID: {category_ids}")

        # Определяем статус в зависимости от даты
        now = datetime.now()
        if publish_datetime > now:
            status = "future"
        else:
            status = "publish"

        # Публикуем запись
        result = app_state.wp.publish_post(
            title=title,
            content=content,
            categories=category_ids,  # Передаем список ID
            default_category="Постановления",  # Резервная категория
            status=status,
            publish_date=publish_datetime
        )

        if result:
            QMessageBox.information(None, "Успех",
                                    f"Запись успешно опубликована!\nID: {result.get('id')}\nСсылка: {result.get('link')}")
        else:
            QMessageBox.critical(None, "Ошибка", "Не удалось опубликовать запись")

    except Exception as e:
        QMessageBox.critical(None, "Ошибка", f"Ошибка при публикации: {str(e)}")
        print(f"Ошибка публикации: {e}")


def open_dialog_wp_login():
    """Открытие диалога входа в WordPress"""
    global app_state

    dialog = uic.loadUi("ui/dialog_wp_login.ui")

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

    from wordpress.LoginWorker import LoginWorker

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
    global is_online

    if success:
        # Сохраняем wp из worker через специальный метод
        app_state.set_wp(app_state.worker.wp)

        # Сохраняем данные в файл
        with open("wpdata.wp", "w") as f:
            json.dump(app_state.worker.login_data, f)

        is_online = True
        QMessageBox.information(window, "Вход выполнен", message)
        update_menu_status("connected")

        # Принудительно проверяем подключение и обрабатываем ожидающие запросы
        app_state.connection_manager.check_connection()

        cur_page = 1

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        tool_widget = QWidget()
        tool_layout = QHBoxLayout(tool_widget)

        cur_page_lbl = QLabel(f"Страница {cur_page}")
        refresh_btn = QPushButton("Обновить")
        tool_layout.addWidget(cur_page_lbl)
        tool_layout.addStretch()  # сдвигаем кнопку вправо
        tool_layout.addWidget(refresh_btn)

        main_layout.addWidget(tool_widget)

        # Создаем контейнер для виджета с постами
        posts_container = QWidget()
        posts_container_layout = QVBoxLayout(posts_container)
        posts_container.setObjectName("posts_container")  # для удобства поиска

        # Создаем и добавляем начальный виджет с постами
        current_posts_widget = posts_window.posts_widget(app_state.wp, cur_page)
        current_posts_widget.setObjectName("posts_widget_main")
        posts_container_layout.addWidget(current_posts_widget)

        main_layout.addWidget(posts_container)

        def refresh_posts():
            # Находим старый виджет с постами
            old_widget = posts_container.findChild(QWidget, "posts_widget_main")

            if old_widget:
                # Удаляем старый виджет
                old_widget.deleteLater()

            # Создаем новый виджет с постами
            new_posts_widget = posts_window.posts_widget(app_state.wp)
            new_posts_widget.setObjectName("posts_widget_main")

            # Добавляем новый виджет в контейнер
            posts_container_layout.addWidget(new_posts_widget)

            # Опционально: показываем сообщение об успешном обновлении
            print("Данные обновлены")

        refresh_btn.clicked.connect(refresh_posts)

        # Добавляем main_widget в tab_posts
        tab_posts = window.findChild(QWidget, "tab_posts")
        if tab_posts:
            tab_posts_layout = QVBoxLayout(tab_posts)
            tab_posts_layout.addWidget(main_widget)

        # Обновляем все открытые вкладки
        update_all_tabs_categories()

    else:
        is_online = False
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


def login_on_load():
    path = "wpdata.wp"
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
Form, Window = uic.loadUiType("ui/main_window.ui")
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
action_html = window.findChild(QAction, "action_HTML")
action_text = window.findChild(QAction, "action_text")
action_wp_dialog = window.findChild(QAction, "action_open_wp_dialog")
action_reconnect = window.findChild(QAction, "action_reconnect")

# Подключение сигналов
if action_wp_dialog:
    action_wp_dialog.triggered.connect(open_dialog_wp_login)
if action_open:
    action_open.triggered.connect(lambda: open_file(window))
if action_html:
    action_html.toggled.connect(lambda checked: hide_show_widget(tabWidgetHtml, "code_area", checked))
if action_text:
    action_text.toggled.connect(lambda checked: hide_show_widget(tabWidgetHtml, "text_area", checked))
if action_reconnect:
    action_reconnect.triggered.connect(login_on_load)

tabWidgetHtml.tabCloseRequested.connect(close_tab_handler)

# Показываем окно
window.show()

# Пытаемся загрузить сохраненные данные
#login_on_load()

# Добавляем тестовую вкладку
#add_new_tab("C:/Users/brylo/OneDrive/Desktop/publisher/py/37.docx")

# Запуск приложения
app.exec()