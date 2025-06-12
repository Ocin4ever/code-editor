import re
import tkinter as tk
from tkinter import scrolledtext
from collections import deque
from config import config
from core.syntax import SyntaxHighlighter
from core.language_rules import LANGUAGE_INDENT_RULES

class CodeEditor(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.highlighter = SyntaxHighlighter()
        self.current_language = "python"
        self.last_char = ""
        self.last_last_char = ""
        # Piles de taille maximale 50
        self.undo_stack = deque(maxlen=50)
        self.redo_stack = deque(maxlen=50)
        self._setup_editor()
        self._bind_events()
        self.snapshot()
    
    def _setup_editor(self):
        # Récupère le thème dans config.py
        self.text = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=config.DEFAULT_FONT,
            bg=config.THEMES[config.THEME]["background"],
            fg=config.THEMES[config.THEME]["foreground"],
            insertbackground=config.THEMES[config.THEME]["foreground"],
            insertwidth=2,
            undo=True
        )
        self._configure_tags()
        self.text.pack(expand=True, fill="both")
    
    def _configure_tags(self):
        """Récupère le thème du texte dans config.py"""
        theme = config.THEMES[config.THEME]
        for tag, color in [
            ('keyword', theme['keyword']),
            ('builtin', theme['builtin']),
            ('string', theme['string']),
            ('comment', theme['comment']),
            ('number', theme['number']),
            ('paren_matched', theme['paren_matched']),
            ('paren_unmatched', theme['paren_unmatched'])
        ]:
            self.text.tag_configure(tag, foreground=color)
    
    def _bind_events(self):
        """Capture les touches pressées"""
        self.text.bind("<KeyPress>", self._on_key_press)
        self.text.bind("<KeyRelease>", self._on_key_release)
        self.text.bind("<Return>", self._handle_return)
        self.text.bind("<Tab>", self._on_tab)
        self.text.bind("<Control-z>", self._undo)
        self.text.bind("<Control-y>", self._redo)
        self.text.bind("<Control-Z>", self._undo)
        self.text.bind("<Control-Y>", self._redo)
    
    def snapshot(self):
        """
        Prend une capture du texte actuel, utile pour undo/redo
        
        Complexité temporelle : O(n)
        n : longueur du texte (lecture via get).

        Complexité spatiale : O(n)
        Stocke une copie du texte et la position du curseur.
        """

        content = self.text.get("1.0", "end-1c")
        cursor_pos = self.text.index("insert")
        if not self.undo_stack or self.undo_stack[-1] != (content, cursor_pos):
            self.undo_stack.append((content, cursor_pos))
            self.redo_stack.clear()
    
    def _undo(self, event=None):
        """
        Annule la dernière action
        
        Complexité temporelle : O(n + n + k + n * m) = O(n * m)
        delete et insert sont en O(n).
        l'appel à stack est en O(k) avec k: la taille de la pile
        highlight est appelée en (O(n * m)).
        """

        if len(self.undo_stack) > 1:
            # Déplacer l'état actuel vers redo
            current = self.undo_stack.pop()
            self.redo_stack.append(current)
            
            # Restaurer l'état précédent
            content, cursor_pos = self.undo_stack[-1]
            self.text.delete("1.0", "end")
            self.text.insert("1.0", content)
            self.text.mark_set("insert", cursor_pos)
            
            self.highlighter.highlight(self.text, self.current_language)
        return "break"
    
    def _redo(self, event=None):
        """
        Rétablit la dernière action annulée
        
        Complexité temporelle : O(n + n + k + n * m) = O(n * m)
        delete et insert sont en O(n).
        l'appel à stack est en O(k) avec k : la taille de la pile
        highlight est appelée en (O(n * m)).
        """

        if self.redo_stack:
            current = (self.text.get("1.0", "end-1c"), self.text.index("insert"))
            self.undo_stack.append(current)
            
            # Restaurer l'état redo
            content, cursor_pos = self.redo_stack.pop()
            self.text.delete("1.0", "end")
            self.text.insert("1.0", content)
            self.text.mark_set("insert", cursor_pos)
            
            self.highlighter.highlight(self.text, self.current_language)
        return "break"
    
    def _handle_return(self, event):
        """
        Gestion de l'indentation
        
        Complexité temporelle : O(n * m + k)
        re.match et get en O(k) : longueur de la ligne
        snapshot est en O(n)
        highlight est en O(n * m) avec le nb de motif (5 ici)
        """

        self.snapshot()
        cursor_pos = self.text.index("insert")
        line, col = map(int, cursor_pos.split('.'))
        
        current_line = self.text.get(f"{line}.0", "insert")
        
        rules = LANGUAGE_INDENT_RULES.get(self.current_language, {})
        indent_size = rules.get("indent_size", 4)
        
        # Calcul d'indentation de base
        base_indent = len(re.match(r'^\s*', current_line).group(0))
        
        # 1. Cas spécial : après return/break dans un bloc
        if any(current_line.lstrip().startswith(trigger) for trigger in rules.get("block_enders", [])):
            new_indent = max(0, base_indent - indent_size)
        
        # 2. Cas standard : indentation après ":"
        elif any(trigger in current_line for trigger in rules.get("indent_after", [])):
            new_indent = base_indent + indent_size
        
        # 4. Cas par défaut
        else:
            new_indent = base_indent
        
        # Appliquer le changement
        self.text.insert("insert", "\n" + " " * new_indent)
        self.highlighter.highlight(self.text, self.current_language)
        return "break"
    
    def _on_tab(self, event):
        """Rebinding de la touche tab"""
        self.snapshot()
        self.text.insert("insert", LANGUAGE_INDENT_RULES["python"]["tab_equivalent"])
        return "break"
    
    def _on_key_press(self, event):
        """Après chaque touche pressée on capture le texte"""
        if event.keysym not in ["Control_L", "Control_R", "Alt_L", "Alt_R", "Shift_L", "Shift_R"]:
            self.snapshot()
        
        cursor_pos = self.text.index("insert")
        line, col = map(int, cursor_pos.split('.'))

        self.char_before = self.text.get(f"{line}.{col-1}", f"{line}.{col}") if col > 0 else ""
        self.char_after = self.text.get(f"{line}.{col}", f"{line}.{col+1}")
    
    def _on_key_release(self, event):
        """Rebinding de la touche delete"""
        cursor_pos = self.text.index("insert")
        line, col = map(int, cursor_pos.split('.'))
        last_last_char = self.last_last_char
        last_char = self.last_char
        self.last_last_char = last_char
        self.last_char = event.keysym

        if event.keysym == "Delete":
            line_text = self.text.get(f"{line}.0", f"{line}.end")
            
            # Vérifier si on est au début d'une indentation
            if col % 4 == 0 and line_text[col:col+4] == "    ":
                self.text.delete(f"{line}.{col}", f"{line}.{col+4}")
                return "break"
        
        if event.keysym == "parenleft" and (last_char, last_last_char) != ("BackSpace", "parenleft"):
            self.text.insert(cursor_pos, ")")
            self.text.mark_set("insert", f"{line}.{col}")
        
        if event.keysym == "BackSpace":
            # Si on est entre parenthèses, supprimer aussi la fermante
            if self.char_before == "(" and self.char_after == ")":
                self.text.delete(f"{line}.{col}", f"{line}.{col+1}")
        
        self.highlighter.highlight(self.text, self.current_language)