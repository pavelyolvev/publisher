import re


def check_for_empty_tags(html):
    pattern = r"\s*<strong>\s*</strong>\s*"
    return re.sub(pattern, '', html)

def convert(html):
    html = html.split(re.search(r'<body\b[^>]*>', html).group(0))[1]
    html = html.split('</body></html>')[0]
    res_html = []
    html_array = html.split('\n')
    for line in html_array:
        text_align = "justify"
        if 'align="center"' in line: text_align = "center"
        if 'align="right"' in line: text_align = "right"
        if text_align != "justify": line = line.replace(f'align="{text_align}" ', "")
        match = re.search(r'<span style="[^"]*">([^<]*)</span>', line)
        #print(match)
        if match:
            line = line.replace(match.group(0), f"<strong>{match.group(1)}</strong>")
            #print(line)
        match_style = re.search(r'<p[^>]*style="([^"]*)"', line)
        if match_style:
            line = line.replace(match_style.group(1), f"text-align: {text_align};")
            print(line)
        res_html.append(line)
    return '\n'.join(res_html)


htmll = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /><style type="text/css">
p, li { white-space: pre-wrap; }
hr { height: 1px; border-width: 0; }
li.unchecked::marker { content: "\2610"; }
li.checked::marker { content: "\2612"; }
</style></head><body style=" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;">
<p align="center" style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:700;">Постановление </span></p>
<p align="right" style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:700;">15.01.2026 № 12</span></p>
<p align="center" style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:700;">О продаже муниципального имущества</span> </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">В соответствии с Федеральным Законом от 06.10.2003 № 131-ФЗ «Об общих принципах организации местного самоуправления в Российской Федерации», Федеральным Законом от 20.03.2025 № 33-ФЗ «Об общих принципах организации местного самоуправления в единой системе публичной власти», Федеральным Законом от 21.12.2001 № 178-ФЗ «О приватизации государственного и муниципального имущества», Уставом муниципального района Похвистневский Самарской области и п. 2.8 Порядка управления и распоряжения имуществом, находящимся в собственности муниципального района Похвистневский Самарской области, Администрация муниципального района Похвистневский Самарской области </p>
<p align="center" style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:700;">П О С Т А Н О В Л Я Е Т:</span> </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">1. Комитету по управлению муниципальным имуществом Администрации муниципального района Похвистневский провести торги посредством публичного предложения по продаже помещения, назначение: нежилое, наименование: нежилое помещение, площадью 151 кв.м, с кадастровым номером 63:29:0706007:130, расположенного по адресу: Самарская область, р-н Похвистневский, с. Старый Аманак, ул. Центральная, д. 42 г, 2 этаж комнаты №№ 7,8,9,10,11,12,13,14,15,16,17,28. </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">2. Установить следующие условия приватизации муниципального имущества, указанного в пункте 1 настоящего постановления, посредством публичного предложения: </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">2.1. Начальную цену помещения – в сумме 885245 (Восемьсот восемьдесят пять тысяч двести сорок пять) руб. 90 коп. с учетом НДС (НДС 22% - 135245 (Сто тридцать пять тысяч двести сорок пять) руб. 90 коп.). </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Цена определена в соответствии с отчетом № 56 об оценке рыночной стоимости от 24.07.2025, выполненным ООО «Эксперт плюс», и составляет 750000 (Семьсот пятьдесят тысяч) руб. 00 коп. без учета НДС. </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">2.2. Величину снижения цены первоначального предложения, указанной </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">в подпункте 2.1 настоящего постановления («шаг понижения) – 88524 (Восемьдесят восемь тысяч пятьсот двадцать четыре) руб. 59 коп. </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">2.3. Минимальную цену предложения (цена отсечения) – 442622 (Четыреста сорок две тысячи шестьсот двадцать два) руб. 95 коп. </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">2.4. Открытую форму подачи предложений о цене помещения. </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">2.5. Величину повышения начальной цены (шаг аукциона) в размере 5% начальной цены продажи, указанной в подпункте 2.1 настоящего постановления, что составляет 44262 (Сорок четыре тысячи двести шестьдесят два) руб. 30 коп. </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">2.6. Задаток для участия в процедуре продажи посредством публичного предложения в размере 10% начальной цены продажи, указанной в подпункте 2.1 настоящего постановления, что составляет 88524 (Восемьдесят восемь тысяч пятьсот двадцать четыре) руб. 59 коп. </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">3. Настоящее Постановление и информационное сообщение о </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">проведении торгов посредством публичного предложения разместить на официальном сайте Российской Федерации для размещения информации о проведении торгов и на сайте Администрации муниципального района Похвистневский Самарской области в сети «Интернет». </p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">4. Контроль за выполнением настоящего Постановления возложить на руководителя Комитета по управлению муниципальным имуществом Администрации муниципального района Похвистневский О.А. Денисову. </p>
<p align="center" style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Глава района <span style=" font-weight:700;">А.В.Шахвалов</span></p>
<p align="right" style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><a href="http://pohr.ru/wps/wp-content/uploads/2026/01/12.docx.docx"><span style=" font-weight:700; text-decoration: underline; color:#0000ff;">Приложение</span></a> </p></body></html>"""

htmll2 = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /><style type="text/css">
p, li { white-space: pre-wrap; }
hr { height: 1px; border-width: 0; }
li.unchecked::marker { content: "\2610"; }
li.checked::marker { content: "\2612"; }
</style></head><body>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><!--StartFragment--><span style=" font-weight:700;">О внесении изменений в муниципальную программу «Развитие муниципальной службы в Администрации муниципального района Похвистневский Самарской области» на 2024-2028 годы</span> <!--EndFragment--></p></body></html>
"""
#ht = convert(htmll)
#print(ht)
