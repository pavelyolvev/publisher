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
<p style="text-align: right;"><strong>15.01.2026 № 12</strong></p>
<p style="text-align: center;"><strong>О продаже муниципального имущества</strong></p>
 <p style="text-align: justify;">В соответствии с Федеральным Законом от 06.10.2003 № 131-ФЗ «Об общих принципах организации местного самоуправления в Российской Федерации», Федеральным Законом от 20.03.2025 № 33-ФЗ «Об общих принципах организации местного самоуправления в единой системе публичной власти», Федеральным Законом от 21.12.2001 № 178-ФЗ «О приватизации государственного и муниципального имущества», Уставом муниципального района Похвистневский Самарской области и п. 2.8 Порядка управления и распоряжения имуществом, находящимся в собственности муниципального района Похвистневский Самарской области, Администрация муниципального района Похвистневский Самарской области</p>
 <p style="text-align: center;"><strong>П О С Т А Н О В Л Я Е Т:</strong></p>
 <p style="text-align: justify;">1. Комитету по управлению муниципальным имуществом Администрации муниципального района Похвистневский провести торги посредством публичного предложения по продаже помещения, назначение: нежилое, наименование: нежилое помещение, площадью 151 кв.м, с кадастровым номером 63:29:0706007:130, расположенного по адресу: Самарская область, р-н Похвистневский, с. Старый Аманак, ул. Центральная, д. 42 г, 2 этаж комнаты №№ 7,8,9,10,11,12,13,14,15,16,17,28.</p>
 <p style="text-align: justify;">2. Установить следующие условия приватизации муниципального имущества, указанного в пункте 1 настоящего постановления, посредством публичного предложения:</p>
 <p style="text-align: justify;">2.1. Начальную цену помещения – в сумме 885245 (Восемьсот восемьдесят пять тысяч двести сорок пять) руб. 90 коп. с учетом НДС (НДС 22% - 135245 (Сто тридцать пять тысяч двести сорок пять) руб. 90 коп.).</p>
 <p style="text-align: justify;">Цена определена в соответствии с отчетом № 56 об оценке рыночной стоимости от 24.07.2025, выполненным ООО «Эксперт плюс», и составляет 750000 (Семьсот пятьдесят тысяч) руб. 00 коп. без учета НДС.</p>
 <p style="text-align: justify;">2.2. Величину снижения цены первоначального предложения, указанной</p>
 <p style="text-align: justify;">в подпункте 2.1 настоящего постановления («шаг понижения) – 88524 (Восемьдесят восемь тысяч пятьсот двадцать четыре) руб. 59 коп.</p>
 <p style="text-align: justify;">2.3. Минимальную цену предложения (цена отсечения) – 442622 (Четыреста сорок две тысячи шестьсот двадцать два) руб. 95 коп.</p>
 <p style="text-align: justify;">2.4. Открытую форму подачи предложений о цене помещения.</p>
 <p style="text-align: justify;">2.5. Величину повышения начальной цены (шаг аукциона) в размере 5% начальной цены продажи, указанной в подпункте 2.1 настоящего постановления, что составляет 44262 (Сорок четыре тысячи двести шестьдесят два) руб. 30 коп.</p>
 <p style="text-align: justify;">2.6. Задаток для участия в процедуре продажи посредством публичного предложения в размере 10% начальной цены продажи, указанной в подпункте 2.1 настоящего постановления, что составляет 88524 (Восемьдесят восемь тысяч пятьсот двадцать четыре) руб. 59 коп.</p>
 <p style="text-align: justify;">3. Настоящее Постановление и информационное сообщение о</p>
 <p style="text-align: justify;">проведении торгов посредством публичного предложения разместить на официальном сайте Российской Федерации для размещения информации о проведении торгов и на сайте Администрации муниципального района Похвистневский Самарской области в сети «Интернет».</p>
 <p style="text-align: justify;">4. Контроль за выполнением настоящего Постановления возложить на руководителя Комитета по управлению муниципальным имуществом Администрации муниципального района Похвистневский О.А. Денисову.</p>
 <p style="text-align: center;">Глава района   <strong>А.В.Шахвалов</strong></p>
<p style="text-align: right;"><strong><a href="http://pohr.ru/wps/wp-content/uploads/2026/01/12.docx.docx">Приложение</a></strong></p>
"""

        self.text_edit.setText(example_html)

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