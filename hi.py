"""
Enhanced Turing Machine Text Editor (Final Version)
---------------------------------------------------
Simulates a Turing-like text editor with:
Undo, Redo, Replace, Clear, Mode Switch, Movement, and Save/Load.
"""

from copy import deepcopy

class TuringEditor:
    def __init__(self, tape_size=300):
        self.tape = ["_"] * tape_size
        self.head = 0
        self.state = "q0"
        self.mode = "insert"  # or "overwrite"
        self.undo_stack = []
        self.redo_stack = []

    # -----------------------
    # Utility Helpersty
    # -----------------------
    def _visible_length(self):
        last_nonblank = max((i for i, c in enumerate(self.tape) if c != "_"), default=-1)
        return max(last_nonblank + 1, self.head + 1)

    def display_tape(self):
        vis_len = self._visible_length()
        visible = "".join(self.tape[:vis_len]) if vis_len > 0 else "_"
        cursor_line = " " * self.head + "^"
        print(f"\nState: {self.state} | Mode: {self.mode.upper()}")
        print("Tape :", visible)
        print("Head :", cursor_line)

    def save_state(self):
        self.undo_stack.append((deepcopy(self.tape), self.head, self.mode))
        if len(self.undo_stack) > 300:
            self.undo_stack.pop(0)

    def get_text(self):
        vis_len = self._visible_length()
        return "".join(self.tape[:vis_len]).rstrip("_")

    def clear_redo(self):
        self.redo_stack.clear()

    # -----------------------
    # Editing Operations
    # -----------------------
    def type_text(self, text):
        if not text:
            return
        self.save_state()
        self.state = "Typing"
        for ch in text:
            if self.mode == "insert":
                self.tape.insert(self.head, ch)
                self.tape.pop()  # keep same length
            else:  # overwrite mode
                self.tape[self.head] = ch
            self.head += 1
        self.clear_redo()
        self.display_tape()

    def backspace(self):
        if self.head == 0:
            print("Nothing to delete.")
            return
        self.save_state()
        self.state = "Delete"
        self.head -= 1
        deleted = self.tape[self.head]
        self.tape[self.head] = "_"
        self.clear_redo()
        print(f"Deleted '{deleted}'")
        self.display_tape()

    def move_left(self):
        self.state = "Move_Left"
        if self.head > 0:
            self.head -= 1
        self.display_tape()

    def move_right(self):
        self.state = "Move_Right"
        if self.head < len(self.tape) - 1:
            self.head += 1
        self.display_tape()

    def move_start(self):
        self.state = "Move_Start"
        self.head = 0
        self.display_tape()

    def move_end(self):
        self.state = "Move_End"
        self.head = self._visible_length() - 1
        self.display_tape()

    def undo(self):
        if not self.undo_stack:
            print("Nothing to undo.")
            return
        self.state = "Undo"
        self.redo_stack.append((deepcopy(self.tape), self.head, self.mode))
        self.tape, self.head, self.mode = self.undo_stack.pop()
        print("↩ Undo performed.")
        self.display_tape()

    def redo(self):
        if not self.redo_stack:
            print("Nothing to redo.")
            return
        self.state = "Redo"
        self.undo_stack.append((deepcopy(self.tape), self.head, self.mode))
        self.tape, self.head, self.mode = self.redo_stack.pop()
        print("↪ Redo performed.")
        self.display_tape()

    def toggle_mode(self):
        self.mode = "overwrite" if self.mode == "insert" else "insert"
        print(f"Mode changed to {self.mode.upper()}")
        self.display_tape()

    def clear_all(self):
        self.save_state()
        self.tape = ["_"] * len(self.tape)
        self.head = 0
        self.state = "Clear"
        print("Cleared all text.")
        self.display_tape()

    def replace_text(self, old, new):
        self.save_state()
        text = self.get_text().replace(old, new)
        for i, ch in enumerate(text):
            self.tape[i] = ch
        for j in range(len(text), len(self.tape)):
            self.tape[j] = "_"
        print(f"Replaced all '{old}' with '{new}'.")
        self.display_tape()

    def word_count(self):
        words = self.get_text().split()
        print(f"Word Count: {len(words)} | Character Count: {len(self.get_text())}")

    def save_to_file(self, filename):
        with open(filename, "w") as f:
            f.write(self.get_text())
        print(f"Saved to {filename}")

    def load_from_file(self, filename):
        try:
            with open(filename, "r") as f:
                content = f.read()
            self.save_state()
            self.tape = list(content) + ["_"] * (len(self.tape) - len(content))
            self.head = len(content)
            print(f"Loaded {len(content)} characters from {filename}")
            self.display_tape()
        except FileNotFoundError:
            print("File not found.")

# ----------------------------
# CLI Driver
# ----------------------------
def run_editor():
    ed = TuringEditor()
    print("""
🧠 Turing Machine Text Editor (Final Version)
Commands:
  type <text>        -> insert or overwrite text
  del                -> backspace
  left/right/start/end -> move cursor
  mode               -> toggle insert/overwrite
  undo / redo        -> undo or redo changes
  replace <old> <new>-> replace occurrences
  clear              -> clear all text
  count              -> show word and character count
  save <file>        -> save to file
  load <file>        -> load from file
  show               -> display tape
  exit               -> quit
""")
    while True:
        try:
            cmd = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting editor.")
            break
        if not cmd:
            continue
        parts = cmd.split()
        c = parts[0].lower()

        try:
            if c == "type": ed.type_text(" ".join(parts[1:]))
            elif c == "del": ed.backspace()
            elif c == "left": ed.move_left()
            elif c == "right": ed.move_right()
            elif c == "start": ed.move_start()
            elif c == "end": ed.move_end()
            elif c == "mode": ed.toggle_mode()
            elif c == "undo": ed.undo()
            elif c == "redo": ed.redo()
            elif c == "replace" and len(parts) == 3: ed.replace_text(parts[1], parts[2])
            elif c == "clear": ed.clear_all()
            elif c == "count": ed.word_count()
            elif c == "save" and len(parts) == 2: ed.save_to_file(parts[1])
            elif c == "load" and len(parts) == 2: ed.load_from_file(parts[1])
            elif c == "show": ed.display_tape()
            elif c == "exit": 
                print("✅ Final Text:", ed.get_text())
                break
            else:
                print("Unknown or invalid command.")
        except Exception as e:
            print("⚠ Error:", e)

if __name__ == "__main__":
    run_editor()