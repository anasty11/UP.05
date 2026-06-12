import tkinter as tk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Трекер жидкости")
        self.root.geometry("400x650")
        self.root.configure(bg="#E8F4FD")

        # Верхние бейджи
        self.days_lbl = tk.Label(root, text="Дни нормы: 0", font=("Arial", 9, "bold"), bg="white", fg="#333")
        self.days_lbl.place(x=15, y=15, width=100, height=35)
        self.points_lbl = tk.Label(root, text="Капли: 0", font=("Arial", 9, "bold"), bg="white", fg="#333")
        self.points_lbl.place(x=285, y=15, width=100, height=35)
        
        # Круг
        self.canvas = tk.Canvas(root, width=200, height=200, bg="#E8F4FD", highlightthickness=0)
        self.canvas.place(x=100, y=80)

         # Уровень
        self.level_lbl = tk.Label(root, text="Уровень: Новичок", font=("Arial", 12, "bold"), bg="#E8F4FD", fg="#2196F3")
        self.level_lbl.place(x=145, y=295)
        
        # Кнопки
        tk.Button(root, text="➕ Добавить", font=("Arial", 14, "bold"), bg="white", fg="#333", relief="ridge", bd=2).place(x=110, y=330, width=180, height=45)
        tk.Button(root, text="История", font=("Arial", 10, "bold"), bg="white", fg="#333", relief="ridge", bd=2).place(x=20, y=550, width=110, height=40)
        tk.Button(root, text="Настройки", font=("Arial", 10, "bold"), bg="white", fg="#333", relief="ridge", bd=2).place(x=145, y=550, width=110, height=40)
        tk.Button(root, text="Статистика", font=("Arial", 10, "bold"), bg="white", fg="#333", relief="ridge", bd=2).place(x=270, y=550, width=110, height=40)
        

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()