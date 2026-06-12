import tkinter as tk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Трекер жидкости")
        self.root.geometry("400x650")
        self.root.configure(bg="#E8F4FD")

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()