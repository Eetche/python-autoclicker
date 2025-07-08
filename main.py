import pyautogui as pag
import os
import json
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import keyboard

SCENARIOS_PATH = "scenarios/"


if (not os.path.isdir(SCENARIOS_PATH)):
    os.mkdir(SCENARIOS_PATH)

print("Успешный запуск \n")

config = open("./config.json", 'r')
config_data = json.loads(config.read())

def newest_file(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)

recording = False
instructions = []
active = False
after_id = None

def work(intsructions_arg):
    global after_id
    global active

    if (type(intsructions_arg) == str):
        intsructions_arg = intsructions_arg.strip('[]').replace(' ', '').split(',')
        
    for i in range(len(intsructions_arg) - 1):
        intsructions_arg[i] = int(intsructions_arg[i])

    coordinates = []

    for i in intsructions_arg:
        if (intsructions_arg.index(i) % 2 == 0):
            x = i
            y = intsructions_arg[intsructions_arg.index(i) + 1]
            coordinates.append([x, y])


    def move_cursor():
        global after_id, active
        if active:
            for i in coordinates:
                if not active:  # Проверка на случай, если active изменился во время выполнения
                    break
                pag.moveTo(i[0], i[1], duration=config_data['duration'])
                pag.click()
            # Планируем следующий вызов только если active=True
            if active:
                after_id = TkRoot.after(100, move_cursor)
        else:
            # Если active=False, отменяем запланированные вызовы
            if after_id:
                TkRoot.after_cancel(after_id)
                after_id = None

    # Отменяем предыдущие запланированные вызовы, если они есть
    if after_id:
        TkRoot.after_cancel(after_id)
        after_id = None

    active = True
    move_cursor()

def stop_work():
    global active, after_id

    active = False
    print("stop work: ", active)
    if after_id:
        TkRoot.after_cancel(after_id)
        after_id = None


def key_push(key):
    global instructions
    global recording

    if (recording):
        if (key.name == "ф" or key.name == "a"):
            x = pag.position().x
            y = pag.position().y

            instructions.append(x)
            instructions.append(y)

            with open(newest_file(SCENARIOS_PATH), "w") as file:
                file.write(str(instructions))
            print(instructions)

        if (key.name == "ы" or key.name == "s"):
            recording = False

    if (key.name == "d" or key.name == "в"):
        stop_work()
        print("go stop_work()")

# UI settings

def new_scen_hand():
    global recording
    global instructions

    instructions = []

    scen_name = simpledialog.askstring("Новый сценарий", "Введите название сценария: ")

    if (scen_name != None):
        messagebox.showinfo("Новый сценарий", "Начата запись нового сценария. Нажмите A для установки точки перемещения")
        scen = open(SCENARIOS_PATH + scen_name + ".scen", "w")
        recording = True
        end_rec.pack()
        end_rec.place(x=250, y=40)

        scen.close()

TkRoot = tk.Tk()
TkRoot.title("Автокликер")
TkRoot.geometry("600x150")

TkStyle = ttk.Style(TkRoot)
TkStyle.theme_use('clam')

new_scen_btn = ttk.Button(TkRoot,
                         text="Новый сценарий",
                         command=new_scen_hand,

)

new_scen_btn.pack()
new_scen_btn.place(x=75, y=40)


def work_hand():
    global active
    worked_scen_name = simpledialog.askstring("Начать выполнение", "Введите название сценария")


    if (worked_scen_name != None and os.path.exists(SCENARIOS_PATH + worked_scen_name + ".scen")):
        with open(SCENARIOS_PATH + worked_scen_name + ".scen", "r") as file:
            instr = file.read()

            active = True

            work(instr)

work_btn = ttk.Button(TkRoot, text="Начать выполнение", command=work_hand)
work_btn.pack()
work_btn.place(x=425, y=40)

def end_recording():
    global recording

    recording = False
    end_rec.place_forget()

end_rec = ttk.Button(TkRoot, text="Закончить запись", command=end_recording)


def go_latest():
    with open(newest_file(SCENARIOS_PATH)) as file:
        work(file.read())

latest_btn = ttk.Button(TkRoot, text="Начать последний сценарий", command=go_latest)
latest_btn.pack()
latest_btn.place(x=225, y=100)

keyboard.on_press(key_push)

TkRoot.resizable(0, 0)
TkRoot.mainloop()
