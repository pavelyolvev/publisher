import docx as Document
import collections
import numpy as np


def gen_html_table_simple(table):
    cell_template = "<td {} style='border-width:1px; border-style:solid;{}'>{}</td>"
    row_template = "<tr>\n{}\n</tr>"

    tab = to_py_table(table)
    tab_tr = to_py_table_tr(table)
    tab_tr_tr = [list(row) for row in zip(*tab_tr)]

    # Отладка
    print(np.array(tab))
    print(np.array(tab_tr_tr))

    final_tab = merge_matrices(tab, tab_tr_tr)
    print("_____________________________")
    print(np.array(final_tab))

    rows = len(final_tab)
    cols = len(final_tab[0]) if rows else 0
    processed = [[False] * cols for _ in range(rows)]
    html_rows = []

    for i in range(rows):
        row_cells = []
        for j in range(cols):
            if processed[i][j]:
                continue

            cell = final_tab[i][j]
            val = cell.text  # текст объекта для отображения

            # Если текст пустой - не объединяем, выводим как отдельную ячейку
            if val == "":
                row_cells.append(cell_template.format("", "", val))
                processed[i][j] = True
                continue

            # BFS для поиска связной области одинаковых объектов
            queue = collections.deque()
            queue.append((i, j))
            visited = set()

            while queue:
                x, y = queue.popleft()
                if (x, y) in visited:
                    continue
                if not (0 <= x < rows and 0 <= y < cols):
                    continue
                if processed[x][y] or final_tab[x][y] is not cell:
                    continue
                visited.add((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < rows and 0 <= ny < cols and not processed[nx][ny] and final_tab[nx][ny] is cell:
                        queue.append((nx, ny))

            if not visited:
                continue

            # Вычисляем ограничивающий прямоугольник
            min_r = min(r for r, _ in visited)
            max_r = max(r for r, _ in visited)
            min_c = min(c for _, c in visited)
            max_c = max(c for _, c in visited)
            height = max_r - min_r + 1
            width = max_c - min_c + 1

            # Проверка на прямоугольность
            if len(visited) == height * width and height * width != 1:
                # Прямоугольная область – объединяем
                attrs = []
                if height > 1:
                    attrs.append(f'rowspan="{height}"')
                    cell_style = ' vertical-align: middle;'
                if width > 1:
                    attrs.append(f'colspan="{width}"')
                    cell_style = ' text-align: center;'
                if height > 1 and width > 1:
                    cell_style = ' text - align: center; vertical-align: middle;'
                attr_str = ' ' + ' '.join(attrs) if attrs else ''

                # ТОЛЬКО для объединенных ячеек добавляем центрирование текста



                row_cells.append(cell_template.format(attr_str, cell_style, val))
                # Помечаем все клетки прямоугольника
                for r in range(min_r, max_r + 1):
                    for c in range(min_c, max_c + 1):
                        processed[r][c] = True
            else:
                # Непрямоугольная – обрабатываем по одной (без дополнительного форматирования)
                row_cells.append(cell_template.format("", "", val))
                processed[i][j] = True

        html_rows.append(row_template.format('\n'.join(row_cells)))

    full_html = "<table style='border-collapse: collapse'>\n" + "\n".join(html_rows) + "\n</table>"
    print(full_html)
    return full_html

def to_py_table(table):
    tab = []
    for row in table.rows:
        cur_row = []
        for cell in row.cells:
            cur_row.append(cell)
        tab.append(cur_row)
    return tab
def to_py_table_tr(table):
    tab = []
    for col in table.columns:
        cur_row = []
        for cell in col.cells:
            cur_row.append(cell) # .text[:15]
        tab.append(cur_row)
    return tab
def merge_matrices(mat1, mat2):
    """
    Объединяет две матрицы объектов так, что все элементы с одинаковым
    значением становятся одним объектом (с приоритетом из первой матрицы).

    Параметры:
        mat1, mat2: списки списков объектов. У каждого объекта должен быть
                    атрибут 'val', возвращающий числовое значение.

    Возвращает:
        Новую матрицу (список списков) того же размера.
    """
    # Проверка размеров (можно добавить)
    rows = len(mat1)
    cols = len(mat1[0]) if rows else 0

    # Словарь для хранения выбранного представителя для каждого значения
    representative = {}

    # Сначала проходим по первой матрице
    for i in range(rows):
        for j in range(cols):
            obj = mat1[i][j]
            val = obj.text
            if val not in representative:
                representative[val] = obj

    # Затем по второй матрице для значений, ещё не имеющих представителя
    for i in range(rows):
        for j in range(cols):
            obj = mat2[i][j]
            val = obj.text
            if val not in representative:
                representative[val] = obj

    # Формируем новую матрицу, заменяя объекты на представителей
    new_matrix = []
    for i in range(rows):
        row = []
        for j in range(cols):
            obj = mat1[i][j]          # можно взять из любой матрицы, числа совпадают
            val = obj.text
            row.append(representative[val])
        new_matrix.append(row)

    return new_matrix
"""def gen_html_table_simple(table):
    cell_template = "<td {} style='border-width:1px; border-style:solid;'>{}</td>"
    row_template = "<tr>\n{}\n</tr>"

    table_tr = transpose_table(table)

    rows_html = []
    skip = 0

    for i, row in enumerate(table.rows):
        cells_html = []
        cells = table.rows[i].cells
        cells_v = table.columns[i].cells
        print(f"row: {i}:")
        for j in range(0, len(cells)):
            span = []
            #print(cells[j])
            print(f"    cell: {j}")
            colspan = colspan_for_cell(j, i, table_tr)
            if colspan > 1:
                span.append(f'colspan={colspan}')
            if skip > 0:
                skip -= 1
                continue

            if j+1 in range(0, len(cells)) and cells[j+1] == cells[j]:
                rowspan = 1
                for c in range(j, len(cells)-1):
                    if c+1 in range(len(cells)) and cells[c+1] == cells[j]:
                        rowspan += 1
                span.append(f'rowspan={rowspan}')
                skip = rowspan - 1
            cells_html.append(cell_template.format(f"{' '.join(span)}", ' '.join(cells[j].text.split())))
        rows_html.append(row_template.format('\n'.join(cells_html)))
    table_html = f"<table style='border-collapse: collapse'>\n{''.join(rows_html)}\n</table>"

    return table_html"""

def transpose_table(old_table):

    # Определяем размеры
    old_rows = len(old_table.rows)
    old_cols = len(old_table.rows[0].cells)

    # Создаем новую таблицу с переставленными размерами
    new_table = Document().add_table(rows=old_cols, cols=old_rows)

    # Копируем данные с транспонированием
    for i in range(old_rows):
        for j in range(old_cols):
            # Получаем текст из исходной ячейки
            cell_text = old_table.rows[i].cells[j].text

            # Вставляем в транспонированную позицию
            new_table.rows[j].cells[i].text = cell_text

    # Удаляем старую таблицу (опционально)
    # Для удаления нужно работать с XML напрямую

    return new_table

