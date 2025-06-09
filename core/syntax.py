import re

class SyntaxHighlighter:
    def __init__(self):
        # Règles
        self.patterns = {
            "python": [
                (r'\b(def|class|if|else|elif|for|while|return|import|from|as|with)\b', 'keyword'),
                (r'\b(print|len|range|str|int|list|dict)\b', 'builtin'),
                (r'"[^"]*"|\'[^\']*\'', 'string'),
                (r'#[^\n]*', 'comment'),
                (r'\b\d+\b', 'number')
            ]
        }
    
    def highlight(self, text_widget, language):
        """Coloration basique"""
        if language not in self.patterns:
            return
            
        text = text_widget.get("1.0", "end-1c")
        for tag in text_widget.tag_names():
            text_widget.tag_remove(tag, "1.0", "end")
        
        for pattern, tag in self.patterns[language]:
            for match in re.finditer(pattern, text):
                start = f"1.0 + {match.start()}c"
                end = f"1.0 + {match.end()}c"
                text_widget.tag_add(tag, start, end)
                # Ajout de la coloration des parenthèses
        self._highlight_parens(text_widget, text)
    
    def _highlight_parens(self, text_widget, text):
        """Coloration des parenthèses selon leur état (fermées ou non)"""
        stack = []
        for i, char in enumerate(text):
            if char == '(':
                stack.append(i)
            elif char == ')':
                if stack:
                    start = stack.pop()
                    # Parenthèse fermée correctement
                    text_widget.tag_add('paren_matched', f"1.0 + {start}c", f"1.0 + {start+1}c")
                    text_widget.tag_add('paren_matched', f"1.0 + {i}c", f"1.0 + {i+1}c")
                else:
                    # Parenthèse fermante sans ouvrante
                    text_widget.tag_add('paren_unmatched', f"1.0 + {i}c", f"1.0 + {i+1}c")
        
        # Parenthèses ouvrantes non fermées
        for start in stack:
            text_widget.tag_add('paren_unmatched', f"1.0 + {start}c", f"1.0 + {start+1}c")