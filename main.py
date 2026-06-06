if __name__ == "__main__":
import tkinter as tk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Мое приложение")
        self.root.geometry("400x300")
        
        label = tk.Label(root, text="Привет, мир!")
        label.pack()

root = tk.Tk()
App(root)
root.mainloop()