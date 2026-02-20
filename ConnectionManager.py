from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class ConnectionManager(QObject):
    """Менеджер для управления ожиданием подключения к WordPress"""

    # Сигнал о изменении статуса подключения
    connection_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.wp = None  # Будет установлен извне
        self.connection_established = False
        self.max_attempts = 30  # максимальное количество попыток
        self.attempt_interval = 1000  # интервал между попытками в мс (1 секунда)
        self.pending_requests = []  # список ожидающих запросов
        self.attempt_count = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connection)

    def set_wp(self, wp_instance):
        """Установка экземпляра WordPress API"""
        self.wp = wp_instance
        # Если уже есть ожидающие запросы, проверяем подключение
        if self.pending_requests:
            self.check_connection()

    def check_connection(self):
        """Проверка подключения к WordPress"""
        if self.wp and self.wp.check_connection():
            self.connection_established = True
            self.timer.stop()
            self.attempt_count = 0
            # Выполняем все ожидающие запросы
            self.process_pending_requests()
            self.connection_changed.emit(True)
            return True
        return False

    def wait_for_connection(self, callback, *args, **kwargs):
        """Ожидание подключения с последующим выполнением callback"""

        # Если уже подключены, выполняем сразу
        if self.wp and self.wp.check_connection():
            callback(*args, **kwargs)
            return

        # Добавляем в очередь ожидающих запросов
        self.pending_requests.append((callback, args, kwargs))

        # Если таймер еще не запущен, запускаем
        if not self.timer.isActive():
            self.attempt_count = 0
            self.timer.start(self.attempt_interval)

    def process_pending_requests(self):
        """Обработка всех ожидающих запросов"""
        for callback, args, kwargs in self.pending_requests:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Ошибка при выполнении отложенного запроса: {e}")

        self.pending_requests.clear()

    def cancel_all_requests(self):
        """Отмена всех ожидающих запросов"""
        self.pending_requests.clear()
        self.timer.stop()
        self.attempt_count = 0
        self.connection_changed.emit(False)