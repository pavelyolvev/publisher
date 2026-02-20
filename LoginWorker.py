from PyQt6.QtCore import QThread, pyqtSignal, QObject
import time

# Импортируем модуль, но не конкретные функции из mainqt
from wordpress_module import WordPressAPI

class LoginWorker(QObject):
    """Рабочий класс для выполнения подключения в отдельном потоке"""
    finished = pyqtSignal(bool, str)  # сигнал: успех, сообщение
    progress = pyqtSignal(str)  # сигнал для обновления статуса

    def __init__(self, login_data):
        super().__init__()
        self.login_data = login_data
        self.wp = None

    def run(self):
        """Метод, который выполняется в потоке"""
        try:
            # Имитация процесса подключения
            self.progress.emit("connecting")

            # Создаем экземпляр WordPressAPI
            self.wp = WordPressAPI(
                site_url=self.login_data[0],
                username=self.login_data[1],
                app_password=self.login_data[2]
            )

            # Проверка подключения
            success = self.wp.check_connection()

            if success:
                self.finished.emit(True, f"Подключено к {self.wp.base_url}")
            else:
                self.finished.emit(False, "Логин или пароль не верен или сервер недоступен")

        except Exception as e:
            self.finished.emit(False, f"Ошибка: {str(e)}")