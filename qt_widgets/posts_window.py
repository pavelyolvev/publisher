from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *


def posts_widget(wp, cur_page=1):

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)  # Важно! Позволяет виджету изменять размер
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    posts_w = QWidget(scroll_area)
    # Устанавливаем стиль для нечетных столбцов
    posts_w.setStyleSheet("""
            QWidget {
                background-color: #ccc;
            }
            QLabel.odd_column {
                background-color: #e6e6e6;  /* светлее для нечетных столбцов */
                max-height: 50px;
                min-height: 20px;
            }
            QLabel.even_column {
                background-color: #d9d9d9;  /* темнее для четных столбцов */
                max-height: 50px;
                min-height: 20px;
            }
        """)

    posts_layout = QGridLayout(posts_w)
    categories_tuple_array = wp.get_category_names_with_id()
    print(categories_tuple_array)

    # Заголовки с классами
    headers = ["Номер записи", "Заголовок", "Дата публикации", "Статус", "Рубрики", "Автор", "Ссылка на запись"]
    for col, header_text in enumerate(headers, start=0):  # начинаем с колонки 1
        header = QLabel(header_text)
        # Применяем класс в зависимости от четности колонки
        if col % 2 == 1:  # нечетная колонка
            header.setProperty('class', 'odd_column')
        else:
            header.setProperty('class', 'even_column')
        posts_layout.addWidget(header, 0, col)

    posts_pages, posts = wp.get_posts_on_page(cur_page, 5)
    for i, post in enumerate(posts):
        if isinstance(post, dict):
            title = post['title']
            if isinstance(title, dict):
                add_post_widget(posts_layout, i + 1, categories_tuple_array, str(post['id']), post['date'],
                                post['status'], post['link'], post['categories'],
                                str(post['author']), title['rendered'][:50])

    # posts_layout.addWidget(QLabel(""), len(posts)+1, 0, 0, 6, Qt.AlignmentFlag.AlignCenter)
    # posts_layout.addWidget(QLabel("первая.. 1 2 3 4 5... последняя"), len(posts)+2, 0, 0, 6, Qt.AlignmentFlag.AlignCenter)
    scroll_area.setWidget(posts_w)
    return scroll_area


def add_post_widget(posts_layout, row, categories_tuple_array, id, date, status, link, categories, author, title):
    # Создаем виджеты по отдельности для большей ясности
    id_w = QLabel(id)
    title_w = QLabel(title)
    date_w = QLabel(date)
    status_w = QLabel(status)
    categories_w = QLabel(get_categories_array(categories_tuple_array, categories))
    author_w = QLabel(author)

    categories_w.setWordWrap(True)
    categories_w.setMinimumWidth(100)
    # Специальная обработка для ссылки
    link_w = QTextBrowser()
    link_w.setHtml(f'<a href="{link}">{link}</a>')
    link_w.setOpenExternalLinks(True)
    link_w.setMaximumHeight(30)
    link_w.setMaximumWidth(250)
    link_w.setMinimumWidth(250)

    # Применяем классы
    widgets = [
        (id_w, 0),
        (title_w, 1),
        (date_w, 2),
        (status_w, 3),
        (categories_w, 4),
        (author_w, 5),
        (link_w, 6)
    ]

    for widget, col in widgets:
        # Применяем класс в зависимости от четности колонки
        if col % 2 == 1:
            widget.setProperty('class', 'odd_column')
        else:
            widget.setProperty('class', 'even_column')

        # Обновляем стиль
        widget.style().unpolish(widget)
        widget.style().polish(widget)

        posts_layout.addWidget(widget, row, col)


def get_categories_array(categories_tuple_array, cat_array):
    result = []
    categories_dict = {id_a: name for id_a, name in categories_tuple_array}
    for cat in cat_array:
        result.append(categories_dict.get(cat))
    return ', '.join(result)
