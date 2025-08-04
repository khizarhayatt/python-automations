import tkinter as tk
from tkinter import messagebox, ttk
import schedule
import time
import threading
from plyer import notification
import pygame
import os
from datetime import datetime, timedelta

class BreakReminder:
    def __init__(self, root):
        self.root = root
        self.root.title("🍱 Break Reminder")
        self.root.geometry("400x500")
        self.root.configure(bg='#2C3E50')
        self.root.resizable(False, True)
        
        # Initialize pygame for sound
        pygame.mixer.init()
        
        # App state
        self.is_running = False
        self.break_thread = None
        self.next_break_time = None
        
        # Default settings
        self.work_duration = 1  # minutes
        self.break_duration = 5   # minutes
        self.long_break_duration = 15  # minutes
        self.sessions_until_long_break = 4
        self.current_session = 0
        self.enable_sound = True
        self.enable_notifications = True
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#34495E', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🍱 Break Reminder",
            font=("Segoe UI", 16, "bold"),
            bg='#34495E',
            fg='#ECF0F1'
        )
        title_label.pack(pady=15)
        
        # Main content area
        main_frame = tk.Frame(self.root, bg='#2C3E50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Timer settings
        settings_frame = tk.LabelFrame(
            main_frame,
            text="⚙️ Timer Settings",
            font=("Segoe UI", 12, "bold"),
            bg='#2C3E50',
            fg='#ECF0F1',
            bd=2,
            relief='raised'
        )
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Work duration
        work_frame = tk.Frame(settings_frame, bg='#2C3E50')
        work_frame.pack(fill=tk.X, padx=10, pady=8)
        
        tk.Label(work_frame, text="Work Duration:", font=("Segoe UI", 10), 
                bg='#2C3E50', fg='#BDC3C7').pack(side=tk.LEFT)
        
        self.work_var = tk.StringVar(value=str(self.work_duration))
        work_spinbox = tk.Spinbox(work_frame, from_=5, to=120, width=5, 
                                 textvariable=self.work_var, font=("Segoe UI", 10))
        work_spinbox.pack(side=tk.RIGHT)
        
        tk.Label(work_frame, text="minutes", font=("Segoe UI", 10), 
                bg='#2C3E50', fg='#BDC3C7').pack(side=tk.RIGHT, padx=(5, 10))
        
        # Short break duration
        break_frame = tk.Frame(settings_frame, bg='#2C3E50')
        break_frame.pack(fill=tk.X, padx=10, pady=8)
        
        tk.Label(break_frame, text="Short Break:", font=("Segoe UI", 10), 
                bg='#2C3E50', fg='#BDC3C7').pack(side=tk.LEFT)
        
        self.break_var = tk.StringVar(value=str(self.break_duration))
        break_spinbox = tk.Spinbox(break_frame, from_=1, to=30, width=5, 
                                  textvariable=self.break_var, font=("Segoe UI", 10))
        break_spinbox.pack(side=tk.RIGHT)
        
        tk.Label(break_frame, text="minutes", font=("Segoe UI", 10), 
                bg='#2C3E50', fg='#BDC3C7').pack(side=tk.RIGHT, padx=(5, 10))
        
        # Long break duration
        long_break_frame = tk.Frame(settings_frame, bg='#2C3E50')
        long_break_frame.pack(fill=tk.X, padx=10, pady=8)
        
        tk.Label(long_break_frame, text="Long Break:", font=("Segoe UI", 10), 
                bg='#2C3E50', fg='#BDC3C7').pack(side=tk.LEFT)
        
        self.long_break_var = tk.StringVar(value=str(self.long_break_duration))
        long_break_spinbox = tk.Spinbox(long_break_frame, from_=10, to=60, width=5, 
                                       textvariable=self.long_break_var, font=("Segoe UI", 10))
        long_break_spinbox.pack(side=tk.RIGHT)
        
        tk.Label(long_break_frame, text="minutes", font=("Segoe UI", 10), 
                bg='#2C3E50', fg='#BDC3C7').pack(side=tk.RIGHT, padx=(5, 10))
        
        # Notification settings
        notif_frame = tk.LabelFrame(
            main_frame,
            text="🔔 Notification Settings",
            font=("Segoe UI", 12, "bold"),
            bg='#2C3E50',
            fg='#ECF0F1',
            bd=2,
            relief='raised'
        )
        notif_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Checkboxes
        self.sound_var = tk.BooleanVar(value=self.enable_sound)
        sound_check = tk.Checkbutton(
            notif_frame,
            text="🔊 Enable Sound Alerts",
            variable=self.sound_var,
            font=("Segoe UI", 10),
            bg='#2C3E50',
            fg='#ECF0F1',
            activebackground='#34495E',
            selectcolor='#2C3E50'
        )
        sound_check.pack(anchor=tk.W, padx=10, pady=5)
        
        self.notif_var = tk.BooleanVar(value=self.enable_notifications)
        notif_check = tk.Checkbutton(
            notif_frame,
            text="💬 Enable Pop-up Notifications",
            variable=self.notif_var,
            font=("Segoe UI", 10),
            bg='#2C3E50',
            fg='#ECF0F1',
            activebackground='#34495E',
            selectcolor='#2C3E50'
        )
        notif_check.pack(anchor=tk.W, padx=10, pady=5)
        
        # Status display
        status_frame = tk.LabelFrame(
            main_frame,
            text="📊 Status",
            font=("Segoe UI", 12, "bold"),
            bg='#2C3E50',
            fg='#ECF0F1',
            bd=2,
            relief='raised'
        )
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_label = tk.Label(
            status_frame,
            text="🔴 Not Running",
            font=("Segoe UI", 12, "bold"),
            bg='#2C3E50',
            fg='#E74C3C'
        )
        self.status_label.pack(pady=10)
        
        self.session_label = tk.Label(
            status_frame,
            text="Sessions completed: 0",
            font=("Segoe UI", 10),
            bg='#2C3E50',
            fg='#BDC3C7'
        )
        self.session_label.pack(pady=(0, 5))
        
        self.next_break_label = tk.Label(
            status_frame,
            text="Next break: Not scheduled",
            font=("Segoe UI", 10),
            bg='#2C3E50',
            fg='#BDC3C7'
        )
        self.next_break_label.pack(pady=(0, 10))
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg='#2C3E50')
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = tk.Button(
            button_frame,
            text="▶️ Start Reminders",
            command=self.start_reminders,
            font=("Segoe UI", 12, "bold"),
            bg='#27AE60',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        self.stop_button = tk.Button(
            button_frame,
            text="⏹️ Stop",
            command=self.stop_reminders,
            font=("Segoe UI", 12, "bold"),
            bg='#E74C3C',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
        
        # Test button
        test_button = tk.Button(
            main_frame,
            text="🧪 Test Notification",
            command=self.test_notification,
            font=("Segoe UI", 10),
            bg='#3498DB',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        test_button.pack(fill=tk.X)
        
    def start_reminders(self):
        """Start the break reminder system"""
        try:
            # Update settings from UI
            self.work_duration = int(self.work_var.get())
            self.break_duration = int(self.break_var.get())
            self.long_break_duration = int(self.long_break_var.get())
            self.enable_sound = self.sound_var.get()
            self.enable_notifications = self.notif_var.get()
            
            self.is_running = True
            self.current_session = 0
            
            # Update UI
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="🟢 Running", fg='#27AE60')
            
            # Schedule first break
            self.schedule_next_break()
            
            # Start background thread
            self.break_thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.break_thread.start()
            
            self.show_notification("Break Reminder Started", 
                                 f"Your first break is scheduled in {self.work_duration} minutes!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all duration fields.")
    
    def stop_reminders(self):
        """Stop the break reminder system"""
        self.is_running = False
        schedule.clear()
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="🔴 Stopped", fg='#E74C3C')
        self.next_break_label.config(text="Next break: Not scheduled")
        
        self.show_notification("Break Reminder Stopped", "Take care of yourself! 💙")
    
    def schedule_next_break(self):
        """Schedule the next break notification"""
        # Clear existing schedules
        schedule.clear()
        
        # Calculate next break time
        self.next_break_time = datetime.now() + timedelta(minutes=self.work_duration)
        
        # Schedule the break
        schedule.every(self.work_duration).minutes.do(self.trigger_break)
        
        # Update UI
        time_str = self.next_break_time.strftime("%I:%M %p")
        self.next_break_label.config(text=f"Next break: {time_str}")
    
    def trigger_break(self):
        """Trigger a break notification"""
        self.current_session += 1
        
        # Determine break type
        if self.current_session % self.sessions_until_long_break == 0:
            break_type = "Long Break"
            duration = self.long_break_duration
            emoji = "🍽️"
        else:
            break_type = "Short Break"
            duration = self.break_duration
            emoji = "☕"
        
        # Update session counter
        self.session_label.config(text=f"Sessions completed: {self.current_session}")
        
        # Show break notification
        title = f"{emoji} Time for a {break_type}!"
        message = f"You've worked for {self.work_duration} minutes.\nTake a {duration}-minute break and recharge! 🔋"
        
        self.show_break_popup(title, message, break_type, duration)
        
        # Play sound if enabled
        if self.enable_sound:
            self.play_break_sound()
        
        # Schedule next break
        if self.is_running:
            self.schedule_next_break()
        
        return schedule.CancelJob  # Cancel this specific job
    
    def show_break_popup(self, title, message, break_type, duration):
        """Show a break reminder popup window"""
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("350x250")
        popup.configure(bg='#E8F6F3')
        popup.resizable(False, False)
        
        # Center the popup
        popup.transient(self.root)
        popup.grab_set()
        
        # Icon and title
        icon_label = tk.Label(
            popup,
            text="🍱" if "Long" in break_type else "☕",
            font=("Segoe UI Emoji", 48),
            bg='#E8F6F3'
        )
        icon_label.pack(pady=20)
        
        title_label = tk.Label(
            popup,
            text=title,
            font=("Segoe UI", 16, "bold"),
            bg='#E8F6F3',
            fg='#2C3E50'
        )
        title_label.pack()
        
        message_label = tk.Label(
            popup,
            text=message,
            font=("Segoe UI", 11),
            bg='#E8F6F3',
            fg='#34495E',
            justify=tk.CENTER
        )
        message_label.pack(pady=15)
        
        # Buttons
        button_frame = tk.Frame(popup, bg='#E8F6F3')
        button_frame.pack(pady=10)
        
        ok_button = tk.Button(
            button_frame,
            text="✅ Got it!",
            command=popup.destroy,
            font=("Segoe UI", 10, "bold"),
            bg='#27AE60',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        ok_button.pack(side=tk.LEFT, padx=5)
        
        snooze_button = tk.Button(
            button_frame,
            text="😴 Snooze 5min",
            command=lambda: self.snooze_break(popup),
            font=("Segoe UI", 10),
            bg='#F39C12',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        snooze_button.pack(side=tk.LEFT, padx=5)
        
        # Auto-close after 30 seconds
        popup.after(30000, popup.destroy)
    
    def snooze_break(self, popup):
        """Snooze the break for 5 minutes"""
        popup.destroy()
        schedule.clear()
        schedule.every(5).minutes.do(self.trigger_break)
        
        # Update next break time
        self.next_break_time = datetime.now() + timedelta(minutes=5)
        time_str = self.next_break_time.strftime("%I:%M %p")
        self.next_break_label.config(text=f"Next break: {time_str} (snoozed)")
    
    def show_notification(self, title, message):
        """Show system notification"""
        if self.enable_notifications:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Break Reminder",
                    timeout=10
                )
            except Exception:
                pass  # Fail silently if notifications aren't supported
    
    def play_break_sound(self):
        """Play break notification sound"""
        try:
            # Create a simple beep sound
            frequency = 800  # Hz
            duration = 0.3   # seconds
            sample_rate = 22050
            frames = int(duration * sample_rate)
            
            # Generate sine wave
            import numpy as np
            wave = np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames))
            wave = (wave * 32767).astype(np.int16)
            
            # Convert to stereo
            stereo_wave = np.array([wave, wave]).T
            
            # Play sound
            sound = pygame.sndarray.make_sound(stereo_wave)
            sound.play()
            
        except Exception:
            # Fallback: system beep
            print('\a')  # Terminal bell
    
    def test_notification(self):
        """Test the notification system"""
        self.show_notification("🧪 Test Notification", "This is a test notification! Your system is working correctly. 🎉")
        
        if self.sound_var.get():
            self.play_break_sound()
    
    def run_scheduler(self):
        """Run the scheduler in background thread"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)

def main():
    root = tk.Tk()
    app = BreakReminder(root)
    root.mainloop()

if __name__ == "__main__":
    main()
