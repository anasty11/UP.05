        self.level_lbl.place(x=145, y=295)
        
        # Кнопки
        tk.Button(root, text="➕ Добавить", font=("Arial", 14, "bold"), bg="white", fg="#333", relief="ridge", bd=2).place(x=110, y=330, width=180, height=45)
        tk.Button(root, text="История", font=("Arial", 10, "bold"), bg="white", fg="#333", relief="ridge", bd=2).place(x=20, y=550, width=110, height=40)
        tk.Button(root, text="Настройки", font=("Arial", 10, "bold"), bg="white", fg="#333", relief="ridge", bd=2).place(x=145, y=550, width=110, height=40)
        tk.Button(root, text="Статистика", font=("Arial", 10, "bold"), bg="white", fg="#333", relief="ridge", bd=2).place(x=270, y=550, width=110, height=40)
        
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

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()