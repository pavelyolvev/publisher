from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth


class WordPressAPI:
    def __init__(self, site_url, username, app_password):
        self.base_url = site_url.rstrip('/')
        self.auth = HTTPBasicAuth(username, app_password)
        self.headers = {'Accept': 'application/json'}

    def _rest_url(self, endpoint):
        """Формирует правильный URL для REST API в режиме ?p=123"""
        return f"{self.base_url}/index.php?rest_route=/{endpoint.lstrip('/')}"

    def check_connection(self):
        """Проверка подключения к WordPress"""
        try:
            response = requests.get(
                self._rest_url("wp/v2/users/me"),
                auth=self.auth,
                headers=self.headers
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Ошибка: {e}")
            return False

    def get_pages(self):
        """Получить все страницы"""
        response = requests.get(
            self._rest_url("wp/v2/pages"),
            auth=self.auth,
            headers=self.headers
        )
        return response.json()

    def get_posts(self):
        """Получить все записи"""
        response = requests.get(
            self._rest_url("wp/v2/posts"),
            auth=self.auth,
            headers=self.headers
        )
        return response.json()

    def get_post(self, post_id):
        """Получить конкретную запись по ID"""
        response = requests.get(
            self._rest_url(f"wp/v2/posts/{post_id}"),
            auth=self.auth,
            headers=self.headers
        )
        return response.json()

    def _request(self, method, endpoint, **kwargs):
        """Универсальный метод для запросов"""
        url = self._rest_url(endpoint)
        response = requests.request(method, url, auth=self.auth, headers=self.headers, **kwargs)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"❌ Ошибка {method} {endpoint}: {response.status_code}")
            print(response.text)
            return None

    # ============== РАБОТА С РУБРИКАМИ ==============

    def get_categories(self):
        """Получить все рубрики"""
        result = self._request('GET', 'wp/v2/categories')
        return result if isinstance(result, list) else []

    def get_category_id_by_name(self, category_name):
        """Найти ID рубрики по названию"""
        categories = self.get_categories()
        for cat in categories:
            # Проверяем, что cat - это словарь
            if isinstance(cat, dict) and 'name' in cat:
                if cat['name'].lower() == category_name.lower():
                    return cat['id']
        return None

    def create_category(self, category_name, parent_id=0):
        """Создать новую рубрику"""
        data = {
            'name': category_name,
            'parent': parent_id
        }
        return self._request('POST', 'wp/v2/categories', json=data)

    def ensure_category(self, category_name):
        """Получить ID рубрики, создать если не существует"""
        cat_id = self.get_category_id_by_name(category_name)
        if cat_id:
            return cat_id

        # Создаём новую рубрику
        result = self.create_category(category_name)
        if result and 'id' in result:
            print(f"✅ Создана новая рубрика: {category_name} (ID: {result['id']})")
            return result['id']
        return None

    # ============== ПУБЛИКАЦИЯ ЗАПИСЕЙ ==============

    def publish_post(self,
                     title,
                     content,
                     categories=None,
                     default_category="Без рубрики",
                     status="publish",
                     publish_date=None,  # Если None - публикуется сразу
                     excerpt="",
                     slug="",
                     featured_media=0,
                     comment_status="open",
                     ping_status="open"
                     ):

        # 1. Получаем ID рубрики по умолчанию
        default_id = self.ensure_category(default_category)
        if not default_id:
            print(f"❌ Не удалось создать/найти рубрику по умолчанию: {default_category}")
            return None

        # 2. Обработка рубрик
        category_ids = [default_id]

        if categories:
            for cat in categories:
                if isinstance(cat, int):
                    if cat not in category_ids:
                        category_ids.append(cat)
                elif isinstance(cat, str):
                    cat_id = self.ensure_category(cat)
                    if cat_id and cat_id not in category_ids:
                        category_ids.append(cat_id)

        # 3. Подготовка данных записи
        post_data = {
            'title': title,
            'content': content,
            'status': status,
            'categories': category_ids,
            'excerpt': excerpt,
            'comment_status': comment_status,
            'ping_status': ping_status
        }

        # 4. Добавляем дату ТОЛЬКО если она явно указана
        if publish_date:
            if isinstance(publish_date, datetime):
                post_data['date'] = publish_date.isoformat()
            else:
                post_data['date'] = publish_date

        # 5. Добавляем slug, если указан
        if slug:
            post_data['slug'] = slug

        # 6. Добавляем миниатюру, если указана
        if featured_media:
            post_data['featured_media'] = featured_media

        # 7. Отправка запроса
        result = self._request('POST', 'wp/v2/posts', json=post_data)

        if result:
            status_text = "✅" if result.get('status') == 'publish' else "⏳"
            print(f"{status_text} Запись создана: {result.get('title', {}).get('rendered', title)}")
            print(f"   ID: {result.get('id')}")
            print(f"   Статус: {result.get('status')}")
            print(f"   Ссылка: {result.get('link')}")
            return result
        else:
            print("❌ Ошибка публикации записи")
            return None

# ============== ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ==============

# Подключение к сайту
wp = WordPressAPI(
    site_url="http://localhost/wordpress",
    username="pavelyolvev",
    app_password="sP1o sA5h UlIo BUhO r3KJ UtXu"
)

# ПРИМЕР 1: Простая публикация (сейчас, рубрика по умолчанию)
print("\n📝 ПРИМЕР 1: Простая публикация")
post1 = wp.publish_post(
    title="Моя первая запись из Python",
    content="<p>Это содержимое записи, созданной через REST API.</p>"
)

# ПРИМЕР 2: Публикация с указанием рубрик
print("\n📝 ПРИМЕР 2: Публикация с рубриками")
post2 = wp.publish_post(
    title="Новости технологий",
    content="<p>Сегодня в мире технологий произошло важное событие.</p>",
    categories=["Новости", "Технологии"],  # Названия рубрик
    default_category="Разное"
)

# ПРИМЕР 3: Публикация в будущем
print("\n📝 ПРИМЕР 3: Отложенная публикация")
from datetime import datetime, timedelta
future_date = datetime.now() + timedelta(days=1)
post3 = wp.publish_post(
    title="Завтрашняя новость",
    content="<p>Эта запись опубликуется завтра.</p>",
    categories=["Анонсы"],
    status="future",
    publish_date=future_date
)

# ПРИМЕР 4: Черновик
print("\n📝 ПРИМЕР 4: Черновик")
post4 = wp.publish_post(
    title="Черновик статьи",
    content="<p>Я еще работаю над этой статьей.</p>",
    categories=["Черновики"],
    status="draft",
    excerpt="Краткое описание статьи"
)

# ПРОВЕРКА: Все рубрики
print("\n📂 Все рубрики на сайте:")
categories = wp.get_categories()
for cat in categories:
    print(f"  - {cat['name']} (ID: {cat['id']}, записей: {cat['count']})")