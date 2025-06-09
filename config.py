class Config:
    DEFAULT_FONT = ("Consolas", 16)
    THEME = "dark"
    THEMES = {
        "light": {
            "background": "#FFFFFF",
            "foreground": "#000000",
            "keyword": "#0000FF",
            "builtin": "#0000FF",
            "string": "#008000",
            "comment": "#808080",
            "number": "#0000FF",
            "def_class": "#0000FF",
            "paren_matched": "#008000",
            "paren_unmatched": "#FF0000"
        },
        "dark": {
            "background": "#1E1E1E",
            "foreground": "#D4D4D4",
            "keyword": "#569CD6",
            "builtin": "#4EC9B0",
            "string": "#CE9178",
            "comment": "#6A9955",
            "number": "#B5CEA8",
            "def_class": "#DCDCAA",
            "paren_matched": "#6A9955",
            "paren_unmatched": "#FF6347"
        }
    }

config = Config()