from PyQt6.QtCore import QObject, pyqtSignal
import time
import socket

from wordpress.wordpress_module import WordPressAPI


class LoginWorker(QObject):
    """Рабочий класс для выполнения подключения в отдельном потоке"""
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)

    def __init__(self, login_data):
        super().__init__()
        self.login_data = login_data
        self.wp = None

    def run(self):
        """Метод, который выполняется в потоке"""
        try:
            self.progress.emit("connecting")

            # Устанавливаем глобальный таймаут для сокетов
            socket.setdefaulttimeout(10)

            # Создаем экземпляр WordPressAPI
            self.wp = WordPressAPI(
                site_url=self.login_data[0],
                username=self.login_data[1],
                app_password=self.login_data[2]
            )

            # Проверка подключения с таймаутом
            success = self.check_connection_with_timeout()

            if success:
                self.finished.emit(True, f"Подключено к {self.wp.base_url}")
            else:
                self.finished.emit(False, "Логин или пароль не верен или сервер недоступен")

        except socket.timeout:
            self.finished.emit(False, "Таймаут подключения. Сервер не отвечает")
        except ConnectionRefusedError:
            self.finished.emit(False, "Подключение отклонено. Проверьте, запущен ли сервер")
        except Exception as e:
            self.finished.emit(False, f"Ошибка: {str(e)}")

    def check_connection_with_timeout(self):
        """Проверка подключения с таймаутом"""
        try:
            return self.wp.check_connection()
        except Exception as e:
            print(f"Ошибка при проверке подключения: {e}")
            return False