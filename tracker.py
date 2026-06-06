import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ========== ДАННЫЕ ==========
DATA_FILE = "data.json"

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"profile": {"weight": 70, "gender": "Мужской", "activity": "Средняя", "manual_norm": 0, "points": 0}, "log": {}}

def save():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load()

# Напитки и очки
DRINKS = {"💧 Вода": 10, "🍵 Чай": 5, "☕ Кофе": 5, "🧃 Сок": 5, "🥛 Молоко": 5}
VOLUMES = [100, 150, 200, 250, 300, 500]

# ========== ФУНКЦИИ ==========
def get_norm():
    p = data["profile"]
    if p["manual_norm"] > 0:
        return p["manual_norm"]
    norm = p["weight"] * 30
    if p["gender"] == "Женский":
        norm -= 200
    if p["activity"] == "Средняя":
        norm += 300
    elif p["activity"] == "Высокая":
        norm += 600
    return max(norm, 1500)

def get_today():
    today = datetime.now().strftime('%Y-%m-%d')
    return data["log"].get(today, {}).get("total", 0)

def add_drink(drink, amount):
    today = datetime.now().strftime('%Y-%m-%d')
    points = DRINKS[drink]
    
    if today not in data["log"]:
        data["log"][today] = {"total": 0, "points": 0, "entries": []}
    
    data["log"][today]["total"] += amount
    data["log"][today]["points"] += points
    data["log"][today]["entries"].append({"drink": drink, "amount": amount, "points": points, "time": datetime.now().strftime('%H:%M')})
    
    data["profile"]["points"] += points
    save()
    
    # Бонус за норму
    if get_today() >= get_norm() and not data["log"][today].get("bonus"):
        data["log"][today]["bonus"] = True
        data["profile"]["points"] += 50
        save()
        messagebox.showinfo("Молодец!", "Норма выполнена! +50 очков!")

def del_entry(date, idx):
    entry = data["log"][date]["entries"][idx]
    data["log"][date]["total"] -= entry["amount"]
    data["log"][date]["points"] -= entry["points"]
    data["profile"]["points"] -= entry["points"]
    data["log"][date]["entries"].pop(idx)
    if not data["log"][date]["entries"]:
        del data["log"][date]
    save()

def get_level(points):
    if points < 100: return "Новичок"
    if points < 500: return "Любитель"
    if points < 1500: return "Мастер"
    return "Гидромант"

def get_days_norm():
    n = get_norm()
    return sum(1 for d in data["log"].values() if d.get("total", 0) >= n)

def get_streak():
    n = get_norm()
    days = sorted(data["log"].keys())
    streak = max_streak = 0
    for d in days:
        if data["log"][d].get("total", 0) >= n:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak

def get_chart_data(period):
    today = datetime.now()
    if period == "week":
        return [(today - timedelta(days=i)).strftime('%d.%m') for i in range(6, -1, -1)], \
               [data["log"].get((today - timedelta(days=i)).strftime('%Y-%m-%d'), {}).get("total", 0) for i in range(6, -1, -1)]
    elif period == "month":
        labels, totals = [], []
        for w in range(4, 0, -1):
            total = 0
            for d in range(7):
                date = (today - timedelta(days=w*7 - d)).strftime('%Y-%m-%d')
                total += data["log"].get(date, {}).get("total", 0)
            labels.append(f"{w}-я нед")
            totals.append(total)
        return labels, totals
    else:
        months = ["Янв","Фев","Март","Апр","Май","Июнь","Июль","Авг","Сен","Окт","Ноя","Дек"]
        totals = []
        for m in range(11, -1, -1):
            target = datetime(today.year, today.month, 1) - timedelta(days=m*30)
            total = 0
            for d in range(1, 32):
                date = datetime(target.year, target.month, d).strftime('%Y-%m-%d')
                total += data["log"].get(date, {}).get("total", 0)
            totals.append(total)
        return months, totals

# ========== ГЛАВНОЕ ОКНО ==========
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
        self.arc = None
        self.main_txt = self.canvas.create_text(100, 90, text="0/0", font=("Arial", 12, "bold"), fill="#333")
        self.percent_txt = self.canvas.create_text(100, 115, text="0%", font=("Arial", 10), fill="#666")
        
        # Уровень
        self.level_lbl = tk.Label(root, text="Уровень: Новичок", font=("Arial", 12, "bold"), bg="#E8F4FD", fg="#2196F3")
        self.level_lbl.place(x=145, y=295)
        
        # Кнопки
        tk.Button(root, text="➕ Добавить", font=("Arial", 14, "bold"), bg="white", fg="#333", command=self.add_window, relief="ridge", bd=2).place(x=110, y=330, width=180, height=45)
        tk.Button(root, text="История", font=("Arial", 10, "bold"), bg="white", fg="#333", command=self.history, relief="ridge", bd=2).place(x=20, y=550, width=110, height=40)
        tk.Button(root, text="Настройки", font=("Arial", 10, "bold"), bg="white", fg="#333", command=self.settings, relief="ridge", bd=2).place(x=145, y=550, width=110, height=40)
        tk.Button(root, text="Статистика", font=("Arial", 10, "bold"), bg="white", fg="#333", command=self.stats, relief="ridge", bd=2).place(x=270, y=550, width=110, height=40)
        
        self.update()
    
    def draw(self, percent):
        if self.arc:
            self.canvas.delete(self.arc)
        self.arc = self.canvas.create_arc(10, 10, 190, 190, start=90, extent=-(percent*3.6), outline="#4CAF50", width=15, style="arc")
    
    def update(self):
        today = get_today()
        norm = get_norm()
        percent = min(int(today/norm*100), 100) if norm > 0 else 0
        self.draw(percent)
        self.canvas.itemconfig(self.main_txt, text=f"{int(today)}/{int(norm)}")
        self.canvas.itemconfig(self.percent_txt, text=f"{percent}%")
        self.days_lbl.config(text=f"Дни нормы: {get_days_norm()}")
        self.points_lbl.config(text=f"Капли: {data['profile']['points']}")
        self.level_lbl.config(text=f"Уровень: {get_level(data['profile']['points'])}")
        self.root.after(1000, self.update)
    
    def add_window(self):
        AddWindow(self.root, self.update)
    
    def history(self):
        HistoryWindow(self.root, self.update)
    
    def settings(self):
        SettingsWindow(self.root, self.update)
    
    def stats(self):
        StatsWindow(self.root)

# ========== ОКНО ДОБАВЛЕНИЯ ==========
class AddWindow:
    def __init__(self, parent, refresh):
        self.refresh = refresh
        self.win = tk.Toplevel(parent)
        self.win.title("Добавить")
        self.win.geometry("300x500")
        self.win.configure(bg="#E8F4FD")
        
        tk.Label(self.win, text="Выберите напиток", font=("Arial", 14, "bold"), bg="#E8F4FD").pack(pady=10)
        
        self.drink = tk.StringVar(value="💧 Вода")
        for d in DRINKS:
            tk.Radiobutton(self.win, text=d, variable=self.drink, value=d, bg="#E8F4FD", font=("Arial", 11)).pack(anchor="w", padx=30)
        
        tk.Label(self.win, text="Объём (мл):", font=("Arial", 11), bg="#E8F4FD").pack(pady=(15,5))
        
        self.vol = tk.IntVar(value=200)
        vol_frame = tk.Frame(self.win, bg="#E8F4FD")
        vol_frame.pack()
        for v in VOLUMES:
            tk.Radiobutton(vol_frame, text=f"{v}", variable=self.vol, value=v, bg="#E8F4FD").pack(side="left", padx=5)
        
        tk.Label(self.win, text="Свой объём:", font=("Arial", 10), bg="#E8F4FD").pack(pady=(10,0))
        self.custom = tk.Entry(self.win, font=("Arial", 10), width=10)
        self.custom.pack()
        
        tk.Button(self.win, text="Добавить", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=self.add).pack(pady=20)
    
    def add(self):
        drink = self.drink.get()
        custom = self.custom.get()
        amount = int(custom) if custom else self.vol.get()
        if amount <= 0 or amount > 2000:
            messagebox.showerror("Ошибка", "Объём от 1 до 2000 мл")
            return
        add_drink(drink, amount)
        messagebox.showinfo("Успех", f"+{amount} мл {drink}\n+{DRINKS[drink]} очков")
        self.win.destroy()
        self.refresh()

# ========== ОКНО ИСТОРИИ ==========
class HistoryWindow:
    def __init__(self, parent, refresh):
        self.refresh = refresh
        self.win = tk.Toplevel(parent)
        self.win.title("История")
        self.win.geometry("500x550")
        self.win.configure(bg="#E8F4FD")
        
        tk.Label(self.win, text="История", font=("Arial", 16, "bold"), bg="#E8F4FD").pack(pady=10)
        
        frame = tk.Frame(self.win, bg="white")
        frame.pack(padx=15, pady=10, fill="both", expand=True)
        
        scroll = tk.Scrollbar(frame)
        scroll.pack(side="right", fill="y")
        
        self.lb = tk.Listbox(frame, font=("Arial", 10), bg="white", yscrollcommand=scroll.set)
        self.lb.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.lb.yview)
        
        tk.Button(frame, text="Удалить", font=("Arial", 11, "bold"), bg="#f44336", fg="white", command=self.delete).pack(pady=10)
        
        self.load()
    
    def load(self):
        self.lb.delete(0, tk.END)
        self.entries = []
        for date in sorted(data["log"].keys(), reverse=True):
            log = data["log"][date]
            self.lb.insert(tk.END, f"══ {date} ══ | {log['total']} мл | {log['points']} очков")
            self.entries.append(("header", date, None))
            for i, e in enumerate(log["entries"]):
                txt = f"  {e['time']} | {e['drink']} | {e['amount']} мл | +{e['points']}"
                self.lb.insert(tk.END, txt)
                self.entries.append(("entry", date, i))
    
    def delete(self):
        sel = self.lb.curselection()
        if not sel:
            return
        typ, date, idx = self.entries[sel[0]]
        if typ == "entry" and messagebox.askyesno("Удалить", "Удалить запись?"):
            del_entry(date, idx)
            self.refresh()
            self.load()

# ========== ОКНО НАСТРОЕК ==========
class SettingsWindow:
    def __init__(self, parent, refresh):
        self.refresh = refresh
        self.win = tk.Toplevel(parent)
        self.win.title("Настройки")
        self.win.geometry("350x450")
        self.win.configure(bg="#E8F4FD")
        
        tk.Label(self.win, text="Настройки", font=("Arial", 16, "bold"), bg="#E8F4FD").pack(pady=10)
        
        frame = tk.Frame(self.win, bg="white")
        frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        p = data["profile"]
        
        tk.Label(frame, text="Вес (кг):", bg="white").grid(row=0, column=0, pady=5, sticky="w")
        self.weight = tk.Entry(frame, width=10)
        self.weight.grid(row=0, column=1)
        self.weight.insert(0, p["weight"])
        
        tk.Label(frame, text="Активность:", bg="white").grid(row=1, column=0, pady=5, sticky="w")
        self.act = tk.StringVar(value=p["activity"])
        for i, a in enumerate(["Низкая", "Средняя", "Высокая"]):
            tk.Radiobutton(frame, text=a, variable=self.act, value=a, bg="white").grid(row=1, column=i+1)
        
        tk.Label(frame, text="Пол:", bg="white").grid(row=2, column=0, pady=5, sticky="w")
        self.gender = tk.StringVar(value=p["gender"])
        tk.Radiobutton(frame, text="М", variable=self.gender, value="Мужской", bg="white").grid(row=2, column=1)
        tk.Radiobutton(frame, text="Ж", variable=self.gender, value="Женский", bg="white").grid(row=2, column=2)
        
        tk.Label(frame, text="Ручная норма (0=авто):", bg="white").grid(row=3, column=0, pady=10, sticky="w")
        self.manual = tk.Entry(frame, width=10)
        self.manual.grid(row=3, column=1)
        self.manual.insert(0, p["manual_norm"])
        
        tk.Button(frame, text="Сохранить", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=self.save).grid(row=4, column=0, columnspan=3, pady=20)
    
    def save(self):
        try:
            data["profile"]["weight"] = float(self.weight.get())
            data["profile"]["gender"] = self.gender.get()
            data["profile"]["activity"] = self.act.get()
            data["profile"]["manual_norm"] = int(self.manual.get())
            save()
            self.refresh()
            self.win.destroy()
            messagebox.showinfo("Успех", "Настройки сохранены")
        except:
            messagebox.showerror("Ошибка", "Введите корректные значения")

# ========== ОКНО СТАТИСТИКИ ==========
class StatsWindow:
    def __init__(self, parent):
        self.win = tk.Toplevel(parent)
        self.win.title("Статистика")
        self.win.geometry("700x600")
        self.win.configure(bg="#E8F4FD")
        
        tk.Label(self.win, text="Статистика", font=("Arial", 16, "bold"), bg="#E8F4FD").pack(pady=10)
        
        frame = tk.Frame(self.win, bg="white")
        frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.period = tk.StringVar(value="week")
        pframe = tk.Frame(frame, bg="white")
        pframe.pack(pady=10)
        for t, v in [("Неделя", "week"), ("Месяц", "month"), ("Год", "year")]:
            tk.Radiobutton(pframe, text=t, variable=self.period, value=v, bg="white", command=self.draw).pack(side="left", padx=10)
        
        self.fig = plt.Figure(figsize=(6, 3.5), dpi=80, facecolor="white")
        self.canvas = FigureCanvasTkAgg(self.fig, frame)
        self.canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)
        
        self.days_lbl = tk.Label(frame, text="", font=("Arial", 11), bg="white")
        self.days_lbl.pack()
        self.streak_lbl = tk.Label(frame, text="", font=("Arial", 11), bg="white")
        self.streak_lbl.pack()
        
        tk.Button(frame, text="Назад", font=("Arial", 12, "bold"), bg="white", fg="#64B5F6", command=self.win.destroy).pack(pady=10)
        self.draw()
    
    def draw(self):
        labels, values = get_chart_data(self.period.get())
        norm = get_norm()
        
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        bars = ax.bar(labels, values, color="#4CAF50")
        ax.axhline(y=norm, color="red", linestyle="--", label=f"Норма: {int(norm)} мл")
        ax.set_title("Потребление жидкости")
        ax.set_ylabel("мл")
        ax.legend()
        for b, v in zip(bars, values):
            if v > 0:
                ax.text(b.get_x()+b.get_width()/2, b.get_height()+10, str(int(v)), ha='center', fontsize=8)
        if self.period.get() == "year":
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
        self.fig.subplots_adjust(bottom=0.15)
        self.canvas.draw()
        
        self.days_lbl.config(text=f"Дни с нормой: {get_days_norm()}")
        self.streak_lbl.config(text=f"Макс серия: {get_streak()} дней")

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()