from PyQt6.QtCore import QObject, QTimer, pyqtSignal
import time


class ConnectionManager(QObject):
    """Менеджер для управления ожиданием подключения к WordPress"""

    # Сигналы
    connection_changed = pyqtSignal(bool)
    connection_error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.wp = None
        self.connection_established = False
        self.max_attempts = 5  # уменьшаем количество попыток
        self.attempt_interval = 3000  # увеличиваем интервал до 3 секунд
        self.timeout = 5  # таймаут подключения в секундах
        self.pending_requests = []
        self.attempt_count = 0
        self.is_checking = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connection)

    def set_wp(self, wp_instance):
        """Установка экземпляра WordPress API"""
        self.wp = wp_instance

    def check_connection(self):
        """Проверка подключения к WordPress с таймаутом"""
        if self.is_checking:
            return False

        self.is_checking = True

        try:
            if self.wp:
                # Устанавливаем таймаут для запроса
                import socket
                socket.setdefaulttimeout(self.timeout)

                # Пытаемся подключиться
                result = self.wp.check_connection()

                if result:
                    self.connection_established = True
                    self.timer.stop()
                    self.attempt_count = 0
                    self.process_pending_requests()
                    self.connection_changed.emit(True)
                    self.is_checking = False
                    return True
                else:
                    self.handle_connection_failure()
            else:
                self.handle_connection_failure()

        except Exception as e:
            error_msg = str(e)
            print(f"Ошибка подключения: {error_msg}")
            self.connection_error.emit(error_msg)
            self.handle_connection_failure()

        self.is_checking = False
        return False

    def handle_connection_failure(self):
        """Обработка неудачного подключения"""
        self.attempt_count += 1

        if self.attempt_count >= self.max_attempts:
            print(f"Превышено максимальное количество попыток ({self.max_attempts})")
            self.timer.stop()
            self.attempt_count = 0
            self.connection_established = False
            self.connection_changed.emit(False)

            # Уведомляем об ошибке все ожидающие запросы
            self.notify_pending_requests_error(
                "Не удалось подключиться к WordPress. Проверьте:\n"
                "1. Запущен ли локальный сервер\n"
                "2. Правильность URL\n"
                "3. Доступность порта 80"
            )

    def wait_for_connection(self, callback, error_callback=None, *args, **kwargs):
        """Ожидание подключения с выполнением callback"""

        # Проверяем подключение
        if self.wp:
            try:
                if self.wp.check_connection():
                    callback(*args, **kwargs)
                    return
            except:
                pass

        # Добавляем в очередь с обработчиком ошибки
        self.pending_requests.append((callback, error_callback, args, kwargs))

        # Запускаем таймер если не активен
        if not self.timer.isActive() and self.attempt_count < self.max_attempts:
            self.attempt_count = 0
            self.timer.start(self.attempt_interval)

    def process_pending_requests(self):
        """Обработка успешных запросов"""
        for callback, error_callback, args, kwargs in self.pending_requests:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Ошибка при выполнении отложенного запроса: {e}")
                if error_callback:
                    error_callback(str(e))

        self.pending_requests.clear()

    def notify_pending_requests_error(self, error_message):
        """Уведомление об ошибке все ожидающие запросы"""
        for callback, error_callback, args, kwargs in self.pending_requests:
            if error_callback:
                try:
                    error_callback(error_message)
                except Exception as e:
                    print(f"Ошибка в error_callback: {e}")

        self.pending_requests.clear()

    def cancel_all_requests(self):
        """Отмена всех запросов"""
        self.pending_requests.clear()
        self.timer.stop()
        self.attempt_count = 0
        self.is_checking = False
        self.connection_changed.emit(False)