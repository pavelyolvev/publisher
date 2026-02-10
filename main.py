import os
from tkinter import *
from tkinter import ttk, filedialog, scrolledtext, messagebox
from tkcalendar import DateEntry

show_text = False

root = Tk()
root.title("Publisher v0.1.1")
root.geometry("800x600")
root.option_add("*tearOff", FALSE)

notebook = ttk.Notebook()
notebook.pack(expand=True, fill=BOTH)

show_code = BooleanVar()

main_menu = Menu()
file_menu = Menu()
view_menu = Menu()
settings_menu = Menu()
word_press_menu = Menu()

file_menu.add_command(label="Сохранить")
file_menu.add_command(label="Закрыть все")
file_menu.add_separator()
file_menu.add_command(label="Выход")

word_press_menu.add_command(label="Статус:")
word_press_menu.add_separator()
word_press_menu.add_command(label="Войти в аккаунт")
word_press_menu.add_command(label="Выйти из аккаунта")


def on_clc():
    print(show_code.get())
    return


def open_file():
    global filepath
    filepath = filedialog.askopenfilename()
    if filepath != "":
        if check_if_doc:
            notebook.add(create_frame(notebook), text=f"{os.path.basename(filepath)}")
            # read_doc()


def check_if_doc():  # заглушка
    return True


file_menu.add_command(label="Открыть", command=open_file)


def close_current_tab():
    notebook.forget("current")


def create_frame(notebook):
    def get_selected_date():
        """Retrieves the selected date and prints it to the console."""
        selected_date = cal.get()
        print(f"Selected date: {selected_date}")

    frame_main = ttk.Frame(notebook)
    frame_left = ttk.Frame(frame_main, borderwidth=1, relief=SOLID, padding=[8, 10])
    frame_text = ttk.Frame(frame_main, borderwidth=1, relief=SOLID, padding=[8, 10])
    frame_tools = ttk.Frame(frame_main, borderwidth=1, relief=SOLID, padding=[8, 10])
    frame = ttk.Frame(frame_main, borderwidth=1, relief=SOLID, padding=[8, 10])

    name_label = ttk.Label(frame, text="Заголовок:")
    name_label.pack(anchor=NW)

    name_entry = ttk.Entry(frame, text="temp")
    name_entry.pack(anchor=NW)

    name_label = ttk.Label(frame, text="Дата публикации:")
    name_label.pack(anchor=NW)

    cal = DateEntry(frame, width=16, background="darkblue",
                    foreground="white", borderwidth=2,
                    date_pattern="dd.mm.yyyy")
    cal.pack(pady=20)

    button = ttk.Button(frame, text="Get Selected Date", command=get_selected_date)
    button.pack(pady=10)

    text_area = scrolledtext.ScrolledText(frame_left, wrap=WORD, font=("Times New Roman", 15))
    code_area = scrolledtext.ScrolledText(frame_left, wrap=WORD, font=("Courier New", 15))

    text_area.grid(column=0, row=0)
    code_area.grid(column=1, row=0)

    tab_cls_btn = ttk.Button(frame_main, text="Закрыть вкладку", command=close_current_tab)
    tab_cls_btn.pack(anchor=NW, side=TOP)


    frame.pack(side=RIGHT, fill=Y, expand=True)
    frame_left.pack(anchor=W, fill=Y, expand=True)

    frame_main.pack(fill=BOTH, expand=True)
    return frame_main


view_menu.add_checkbutton(label="Отоброжать HTML код", variable=show_code, command=on_clc)
view_menu.add_checkbutton(label="Отоброжать Текст", variable=show_text, state='disabled')

settings_menu.add_cascade(label="WordPress", menu=word_press_menu)

main_menu.add_cascade(label="Файл", menu=file_menu)
main_menu.add_cascade(label="Вид", menu=view_menu)
main_menu.add_cascade(label="Настройки", menu=settings_menu)

notebook.add(create_frame(notebook), text="Test_frame")
notebook.add(create_frame(notebook), text="Test_frame2")

root.config(menu=main_menu)
root.mainloop()
