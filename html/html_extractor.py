import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class HTMLConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("HTML Converter")
        self.setGeometry(100, 100, 800, 600)

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)

        # Основной layout
        layout = QVBoxLayout(central)

        # Метка
        label = QLabel("Введите HTML код:")
        layout.addWidget(label)

        # QTextEdit для ввода HTML
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Вставьте HTML код сюда...")
        self.text_edit.setFontFamily("Courier New")
        layout.addWidget(self.text_edit)

        # Кнопка сохранения
        save_btn = QPushButton("Сохранить в HTML файл")
        save_btn.clicked.connect(self.save_html)
        layout.addWidget(save_btn)

        # Статус бар
        self.status_label = QLabel("Готов")
        self.statusBar().addWidget(self.status_label)

        # Пример HTML
        example_html = """<p style="text-align: center;"><strong>Постановление </strong></p>
<p style="text-align: right;"><strong>20.01.2026 № 37</strong></p>
<p style="text-align: center;"><strong>О внесении изменений в муниципальную программу «Развитие муниципальной службы в Администрации муниципального района Похвистневский Самарской области» на 2024-2028 годы </strong></p>
<p style="text-align: justify;">В соответствии со статьей 179 Бюджетного кодекса Российской Федерации, Постановлением Администрации муниципального района Похвистневский Самарской области от 19.03.2019 № 193 «Об утверждении Порядка разработки, реализации и оценки эффективности муниципальных программ муниципального района Похвистневский Самарской области», решением Собрания представителей муниципального района Похвистневский от 29.12.2025 №20 «О внесении изменений в Решение Собрания представителей муниципального района Похвистневский «О бюджете муниципального района Похвистневский Самарской области на 2025 и на плановый период 2026 и 2027 годов», Администрация муниципального района Похвистневский Самарской области</p>
<p style="text-align: center;"><strong>П О С Т А Н О В Л Я Е Т:</strong></p>
<p style="text-align: justify;">1. Внести в муниципальную программу «Развитие муниципальной службы в Администрации муниципального района Похвистневский Самарской области» на 2024-2028 годы, утвержденную Постановлением Администрации района от 22.08.2023 № 569 следующие изменения:
1.1. В паспорте муниципальной Программы «Развитие муниципальной службы в Администрации муниципального района Похвистневский Самарской области» на 2024-2028 годы раздел «Объемы бюджетных ассигнований муниципальной программы» изложить в новой редакции:</p>
<table>
<tr>
<td>Объемы бюджетных ассигнований муниципальной программы</td>
<td>Общий объем финансирования из бюджета муниципального района Похвистневский Самарской области составляет 198,9 тысяч рублей, в том числе по годам: в 2024 году – 0,0 тысяч рублей; в 2025 году – 48,9 тысяч рублей в 2026 году – 50,0 тысяч рублей в 2027 году – 50,0 тысяч рублей в 2028 году – 50,0 тысяч рублей</td>
</tr>
</table>
<p style="text-align: justify;">1.2. В текстовой части муниципальной программы раздел 4. «Ресурсное обеспечение реализации муниципальной программы» слова «Общий объем финансирования программных мероприятий составляет 250 тысяч рублей, по 50 тысяч рублей ежегодно», заменить словами: «Общий объем финансирования программных мероприятий составляет 198,9 тысяч рублей, в том числе по годам:
в 2024 году – 0 тыс. рублей;
в 2025 году – 48,9 тыс. рублей;
в 2026 году – 50 тыс. рублей;
в 2027 году – 50 тыс. рублей;
в 2028 году – 50 тыс. рублей.
1.3. Приложение 3 «Объем финансовых ресурсов для реализации муниципальной программы «Развитие муниципальной службы в Администрации муниципального района Похвистневский Самарской области» на 2024-2028 годы изложить в новой редакции (Приложение прилагается).
2. Контроль за исполнением настоящего Постановления возложить на руководителя аппарата Администрации района.
3. Настоящее Постановление вступает в силу со дня его подписания и подлежит размещению на сайте Администрации муниципального района Похвистневский Самарской области в сети Интернет.</p>
<p style="text-align: center;">Глава района   <strong>А.В.Шахвалов</strong></p>
<p style="text-align: right;"><strong><a href="http://pohr.ru/wps/wp-content/uploads/2026/02/37.docx">Приложение</a></strong></p>
"""

        self.text_edit.setHtml(example_html)

    def extract_pure_html(self, qt_html):
        """
        Извлекает чистый HTML из QTextEdit без изменений
        """
        # Получаем HTML из QTextEdit
        html = self.text_edit.toHtml()
        return html

    def save_html(self):
        # Получаем чистый HTML БЕЗ каких-либо изменений
        pure_html = self.extract_pure_html(None)

        if not pure_html.strip():
            QMessageBox.warning(self, "Предупреждение", "HTML код пуст!")
            return

        # Диалог сохранения файла
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить HTML файл",
            "",
            "HTML Files (*.html);;All Files (*)"
        )

        if filename:
            try:
                # Добавляем расширение .html если его нет
                if not filename.endswith('.html'):
                    filename += '.html'

                # Сохраняем HTML в файл БЕЗ ИЗМЕНЕНИЙ
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(pure_html)

                self.status_label.setText(f"Файл сохранен: {filename}")
                QMessageBox.information(self, "Успех", f"HTML файл сохранен:\n{filename}")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
                self.status_label.setText("Ошибка сохранения")


def main():
    app = QApplication(sys.argv)
    converter = HTMLConverter()
    converter.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()