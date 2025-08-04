import tkinter as tk
from tkinter import messagebox, filedialog
import os
from datetime import datetime

class StickyNotePad:
    def __init__(self, root):
        self.root = root
        self.root.title("📝 Sticky Notepad")
        self.root.geometry("350x450")
        self.root.configure(bg='#FFF9C4')  # Light yellow sticky note color
        self.root.resizable(True, True)
        
        # Create notes directory if it doesn't exist
        self.notes_dir = os.path.join(os.path.expanduser("~"), "QuickNotes")
        if not os.path.exists(self.notes_dir):
            os.makedirs(self.notes_dir)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Top button bar - transparent and minimal
        top_frame = tk.Frame(self.root, bg='#FFF9C4', height=60)
        top_frame.pack(fill=tk.X, padx=10, pady=8)
        top_frame.pack_propagate(False)
        
        # Title on the left
        title_label = tk.Label(
            top_frame, 
            text="Sticky Notepad", 
            font=("Segoe UI", 10, "bold"), 
            bg='#FFF9C4',
            fg='#333'
        )
        title_label.pack(side=tk.LEFT, padx=10, pady=15)
        
        # Emoji buttons on the right - smaller size with more padding
        save_btn = tk.Button(
            top_frame,
            text="💾",
            command=self.save_note,
            font=("Segoe UI Emoji", 16),
            bg='#FFF9C4',
            fg='#333',
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=8,
            cursor='hand2'
        )
        save_btn.pack(side=tk.RIGHT, padx=12, pady=15)
        
        clear_btn = tk.Button(
            top_frame,
            text="🗑️",
            command=self.clear_text,
            font=("Segoe UI Emoji", 16),
            bg='#FFF9C4',
            fg='#333',
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=8,
            cursor='hand2'
        )
        clear_btn.pack(side=tk.RIGHT, padx=12, pady=15)
        
        folder_btn = tk.Button(
            top_frame,
            text="📂",
            command=self.open_notes_folder,
            font=("Segoe UI Emoji", 16),
            bg='#FFF9C4',
            fg='#333',
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=8,
            cursor='hand2'
        )
        folder_btn.pack(side=tk.RIGHT, padx=12, pady=15)
        
        # Text area - main note area (no frame, borderless)
        self.text_area = tk.Text(
            self.root,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg='#FFF9C4',  # Sticky note yellow
            fg='#333',
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=10,
            insertbackground='#333',  # Cursor color
            selectbackground='#FFE082'  # Selection color
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 30))
        
        # Bottom status bar - minimal
        bottom_frame = tk.Frame(self.root, bg='#FFF9C4', height=25)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        bottom_frame.pack_propagate(False)
        
        # Subtle status text
        self.status_label = tk.Label(
            bottom_frame,
            text="Ready",
            font=("Segoe UI", 8),
            bg='#FFF9C4',
            fg='#666'
        )
        self.status_label.pack(pady=5)
        
        # Focus on text area
        self.text_area.focus()
        
        # Bind Ctrl+S for quick save
        self.root.bind('<Control-s>', lambda e: self.save_note())
        
        # Add hover effects to buttons
        self.add_hover_effects()
    
    def add_hover_effects(self):
        """Add hover effects to transparent buttons"""
        def on_enter(e):
            e.widget.config(bg='#FFE082')  # Lighter yellow on hover
        
        def on_leave(e):
            e.widget.config(bg='#FFF9C4')  # Back to transparent
        
        # Find all buttons and add hover effects
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        child.bind('<Enter>', on_enter)
                        child.bind('<Leave>', on_leave)
    
    def generate_filename(self, content):
        """Generate human-readable filename from content and date"""
        # Get first few words from content
        words = content.split()[:4]  # First 4 words
        first_words = ' '.join(words)
        
        # Clean up the words for filename (remove special characters)
        import re
        clean_words = re.sub(r'[^\w\s-]', '', first_words)
        clean_words = re.sub(r'\s+', '_', clean_words.strip())
        
        # Limit length
        if len(clean_words) > 30:
            clean_words = clean_words[:30]
        
        # Add human-readable date
        date_str = datetime.now().strftime("%b_%d_%Y")  # e.g., "Aug_03_2025"
        
        # Combine words with date
        if clean_words:
            filename = f"{clean_words}_{date_str}.txt"
        else:
            filename = f"note_{date_str}.txt"
        
        return filename
    
    def save_note(self):
        """Save note with human-readable filename"""
        content = self.text_area.get("1.0", tk.END).strip()
        
        if not content:
            self.status_label.config(text="⚠️ Nothing to save")
            self.root.after(2000, lambda: self.status_label.config(text="Ready"))
            return
        
        # Generate human-readable filename
        filename = self.generate_filename(content)
        filepath = os.path.join(self.notes_dir, filename)
        
        # Check if file already exists and modify filename if needed
        counter = 1
        original_filename = filename
        while os.path.exists(filepath):
            name, ext = os.path.splitext(original_filename)
            filename = f"{name}_{counter}{ext}"
            filepath = os.path.join(self.notes_dir, filename)
            counter += 1
        
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            
            self.status_label.config(text=f"✅ Saved!")
            self.root.after(2000, lambda: self.status_label.config(text="Ready"))
            
        except Exception as e:
            self.status_label.config(text="❌ Save failed")
            self.root.after(2000, lambda: self.status_label.config(text="Ready"))
    
    def open_notes_folder(self):
        """Open the notes folder in file explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(self.notes_dir)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{self.notes_dir}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{self.notes_dir}"')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {str(e)}")
    
    def clear_text(self):
        """Clear the text area"""
        if self.text_area.get("1.0", tk.END).strip():
            self.text_area.delete("1.0", tk.END)
            self.text_area.focus()
            self.status_label.config(text="🗑️ Cleared")
            self.root.after(2000, lambda: self.status_label.config(text="Ready"))

def main():
    root = tk.Tk()
    app = StickyNotePad(root)
    root.mainloop()

if __name__ == "__main__":
    main()
