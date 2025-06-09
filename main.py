from ui.editor import CodeEditor
import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Éditeur Python")
    root.geometry("800x600")
    
    editor = CodeEditor(root)
    editor.pack(expand=True, fill='both')
    
    root.mainloop()

if __name__ == "__main__":
    main()