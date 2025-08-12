#!/usr/bin/env python3
"""
Modern Task Management Application
A feature-rich task manager with modern GUI design using Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Optional
import random

class ModernTaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TaskFlow - Modern Task Manager")
        self.root.geometry("1200x700")
        
        # Modern color scheme
        self.colors = {
            'bg': '#1e1e2e',
            'sidebar': '#2a2a3e',
            'card': '#363649',
            'primary': '#7c3aed',
            'primary_hover': '#6d28d9',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'text': '#ffffff',
            'text_secondary': '#a0a0b8',
            'border': '#4a4a5e'
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Data storage
        self.tasks_file = 'tasks.json'
        self.tasks = self.load_tasks()
        self.filtered_tasks = self.tasks.copy()
        self.current_filter = 'all'
        
        # Setup custom styles
        self.setup_styles()
        
        # Create GUI
        self.create_widgets()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Center window on screen
        self.center_window()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        """Setup custom ttk styles for modern look"""
        self.style = ttk.Style()
        
        # Configure custom fonts
        self.title_font = font.Font(family="Helvetica", size=24, weight="bold")
        self.heading_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.body_font = font.Font(family="Helvetica", size=11)
        self.small_font = font.Font(family="Helvetica", size=9)
        
        # Custom button style
        self.style.configure(
            "Modern.TButton",
            background=self.colors['primary'],
            foreground=self.colors['text'],
            borderwidth=0,
            relief="flat",
            padding=(15, 10),
            font=self.body_font
        )
        self.style.map(
            "Modern.TButton",
            background=[('active', self.colors['primary_hover'])],
            foreground=[('active', self.colors['text'])]
        )
        
        # Success button style
        self.style.configure(
            "Success.TButton",
            background=self.colors['success'],
            foreground=self.colors['text'],
            borderwidth=0,
            relief="flat",
            padding=(10, 5),
            font=self.body_font
        )
        
        # Danger button style
        self.style.configure(
            "Danger.TButton",
            background=self.colors['danger'],
            foreground=self.colors['text'],
            borderwidth=0,
            relief="flat",
            padding=(10, 5),
            font=self.body_font
        )
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create sidebar
        self.create_sidebar(main_container)
        
        # Create main content area
        self.create_main_content(main_container)
    
    def create_sidebar(self, parent):
        """Create the sidebar with navigation and stats"""
        sidebar = tk.Frame(parent, bg=self.colors['sidebar'], width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))
        sidebar.pack_propagate(False)
        
        # App title
        title_frame = tk.Frame(sidebar, bg=self.colors['sidebar'])
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            title_frame,
            text="📋 TaskFlow",
            font=self.title_font,
            bg=self.colors['sidebar'],
            fg=self.colors['text']
        ).pack()
        
        # Stats section
        stats_frame = tk.Frame(sidebar, bg=self.colors['card'])
        stats_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.create_stats_widgets(stats_frame)
        
        # Filter buttons
        filter_frame = tk.Frame(sidebar, bg=self.colors['sidebar'])
        filter_frame.pack(fill=tk.X, padx=15, pady=20)
        
        tk.Label(
            filter_frame,
            text="FILTERS",
            font=self.small_font,
            bg=self.colors['sidebar'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=(0, 10))
        
        filters = [
            ("📌 All Tasks", "all"),
            ("⏳ Pending", "pending"),
            ("✅ Completed", "completed"),
            ("⚡ High Priority", "high"),
            ("📅 Due Today", "today")
        ]
        
        self.filter_buttons = {}
        for text, filter_type in filters:
            btn = self.create_filter_button(filter_frame, text, filter_type)
            self.filter_buttons[filter_type] = btn
        
        # Set initial active filter
        self.set_active_filter('all')
    
    def create_filter_button(self, parent, text, filter_type):
        """Create a filter button"""
        btn = tk.Button(
            parent,
            text=text,
            font=self.body_font,
            bg=self.colors['sidebar'],
            fg=self.colors['text'],
            bd=0,
            pady=8,
            anchor=tk.W,
            cursor="hand2",
            command=lambda: self.filter_tasks(filter_type)
        )
        btn.pack(fill=tk.X, pady=2)
        
        # Hover effects
        btn.bind("<Enter>", lambda e: btn.configure(bg=self.colors['card']))
        btn.bind("<Leave>", lambda e: btn.configure(
            bg=self.colors['primary'] if self.current_filter == filter_type else self.colors['sidebar']
        ))
        
        return btn
    
    def set_active_filter(self, filter_type):
        """Set the active filter button"""
        for f_type, btn in self.filter_buttons.items():
            if f_type == filter_type:
                btn.configure(bg=self.colors['primary'])
            else:
                btn.configure(bg=self.colors['sidebar'])
        self.current_filter = filter_type
    
    def create_stats_widgets(self, parent):
        """Create statistics widgets"""
        stats_container = tk.Frame(parent, bg=self.colors['card'])
        stats_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Total tasks
        self.total_label = self.create_stat_widget(
            stats_container, "Total Tasks", "0", self.colors['primary']
        )
        
        # Completed tasks
        self.completed_label = self.create_stat_widget(
            stats_container, "Completed", "0", self.colors['success']
        )
        
        # Pending tasks
        self.pending_label = self.create_stat_widget(
            stats_container, "Pending", "0", self.colors['warning']
        )
        
        self.update_stats()
    
    def create_stat_widget(self, parent, title, value, color):
        """Create a single stat widget"""
        frame = tk.Frame(parent, bg=self.colors['card'])
        frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            frame,
            text=title,
            font=self.small_font,
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W)
        
        value_label = tk.Label(
            frame,
            text=value,
            font=self.heading_font,
            bg=self.colors['card'],
            fg=color
        )
        value_label.pack(anchor=tk.W)
        
        return value_label
    
    def create_main_content(self, parent):
        """Create the main content area"""
        content_frame = tk.Frame(parent, bg=self.colors['bg'])
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with add task button
        header_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            header_frame,
            text="My Tasks",
            font=self.heading_font,
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        add_btn = ttk.Button(
            header_frame,
            text="+ Add New Task",
            style="Modern.TButton",
            command=self.show_add_task_dialog
        )
        add_btn.pack(side=tk.RIGHT)
        
        # Search bar
        search_frame = tk.Frame(content_frame, bg=self.colors['card'])
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        search_container = tk.Frame(search_frame, bg=self.colors['card'])
        search_container.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            search_container,
            text="🔍",
            font=self.body_font,
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.search_tasks)
        
        search_entry = tk.Entry(
            search_container,
            textvariable=self.search_var,
            font=self.body_font,
            bg=self.colors['card'],
            fg=self.colors['text'],
            bd=0,
            insertbackground=self.colors['text']
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Task list container with scrollbar
        list_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar for task list
        canvas = tk.Canvas(list_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(
            int(-1*(e.delta/120)), "units"
        ))
        
        # Display tasks
        self.display_tasks()
    
    def show_add_task_dialog(self):
        """Show dialog to add a new task"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Task")
        dialog.geometry("500x400")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250)
        y = (dialog.winfo_screenheight() // 2) - (200)
        dialog.geometry(f'+{x}+{y}')
        
        # Title
        tk.Label(
            dialog,
            text="Create New Task",
            font=self.heading_font,
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        # Form container
        form_frame = tk.Frame(dialog, bg=self.colors['bg'])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        # Task title
        tk.Label(
            form_frame,
            text="Task Title",
            font=self.body_font,
            bg=self.colors['bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=(10, 5))
        
        title_entry = tk.Entry(
            form_frame,
            font=self.body_font,
            bg=self.colors['card'],
            fg=self.colors['text'],
            bd=1,
            relief=tk.SOLID,
            insertbackground=self.colors['text']
        )
        title_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Description
        tk.Label(
            form_frame,
            text="Description",
            font=self.body_font,
            bg=self.colors['bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=(10, 5))
        
        desc_text = tk.Text(
            form_frame,
            height=4,
            font=self.body_font,
            bg=self.colors['card'],
            fg=self.colors['text'],
            bd=1,
            relief=tk.SOLID,
            insertbackground=self.colors['text']
        )
        desc_text.pack(fill=tk.X, pady=(0, 10))
        
        # Priority
        tk.Label(
            form_frame,
            text="Priority",
            font=self.body_font,
            bg=self.colors['bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=(10, 5))
        
        priority_var = tk.StringVar(value="medium")
        priority_frame = tk.Frame(form_frame, bg=self.colors['bg'])
        priority_frame.pack(fill=tk.X, pady=(0, 10))
        
        for priority in ["low", "medium", "high"]:
            tk.Radiobutton(
                priority_frame,
                text=priority.capitalize(),
                variable=priority_var,
                value=priority,
                font=self.body_font,
                bg=self.colors['bg'],
                fg=self.colors['text'],
                selectcolor=self.colors['card'],
                activebackground=self.colors['bg']
            ).pack(side=tk.LEFT, padx=10)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, pady=20, padx=30)
        
        def add_task():
            title = title_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()
            priority = priority_var.get()
            
            if not title:
                messagebox.showwarning("Warning", "Please enter a task title!")
                return
            
            task = {
                'id': len(self.tasks) + 1,
                'title': title,
                'description': description,
                'priority': priority,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'due_date': (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            }
            
            self.tasks.append(task)
            self.save_tasks()
            self.filter_tasks(self.current_filter)
            self.update_stats()
            dialog.destroy()
            
            # Show success animation
            self.show_notification("Task added successfully!", "success")
        
        ttk.Button(
            button_frame,
            text="Add Task",
            style="Modern.TButton",
            command=add_task
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Button(
            button_frame,
            text="Cancel",
            font=self.body_font,
            bg=self.colors['card'],
            fg=self.colors['text'],
            bd=0,
            padx=20,
            pady=10,
            command=dialog.destroy
        ).pack(side=tk.RIGHT)
        
        # Focus on title entry
        title_entry.focus()
    
    def display_tasks(self):
        """Display all tasks in the scrollable frame"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.filtered_tasks:
            # Show empty state
            empty_frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg'])
            empty_frame.pack(fill=tk.BOTH, expand=True, pady=50)
            
            tk.Label(
                empty_frame,
                text="📭",
                font=font.Font(size=48),
                bg=self.colors['bg'],
                fg=self.colors['text_secondary']
            ).pack()
            
            tk.Label(
                empty_frame,
                text="No tasks found",
                font=self.heading_font,
                bg=self.colors['bg'],
                fg=self.colors['text_secondary']
            ).pack(pady=10)
            
            return
        
        # Display each task
        for task in self.filtered_tasks:
            self.create_task_card(task)
    
    def create_task_card(self, task):
        """Create a task card widget"""
        # Main card frame
        card = tk.Frame(
            self.scrollable_frame,
            bg=self.colors['card'],
            relief=tk.FLAT,
            bd=1
        )
        card.pack(fill=tk.X, pady=5, padx=2)
        
        # Add hover effect
        def on_enter(e):
            card.configure(bg=self.colors['border'])
        
        def on_leave(e):
            card.configure(bg=self.colors['card'])
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # Card content
        content_frame = tk.Frame(card, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        # Top row (checkbox, title, priority)
        top_row = tk.Frame(content_frame, bg=self.colors['card'])
        top_row.pack(fill=tk.X)
        
        # Checkbox
        check_var = tk.BooleanVar(value=task['status'] == 'completed')
        check = tk.Checkbutton(
            top_row,
            variable=check_var,
            bg=self.colors['card'],
            activebackground=self.colors['card'],
            command=lambda: self.toggle_task_status(task['id'], check_var.get())
        )
        check.pack(side=tk.LEFT, padx=(0, 10))
        
        # Title
        title_label = tk.Label(
            top_row,
            text=task['title'],
            font=self.body_font if task['status'] == 'pending' else 
                 font.Font(family="Helvetica", size=11, overstrike=True),
            bg=self.colors['card'],
            fg=self.colors['text'] if task['status'] == 'pending' else self.colors['text_secondary'],
            anchor=tk.W
        )
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Priority badge
        priority_colors = {
            'low': self.colors['success'],
            'medium': self.colors['warning'],
            'high': self.colors['danger']
        }
        
        priority_label = tk.Label(
            top_row,
            text=task['priority'].upper(),
            font=self.small_font,
            bg=priority_colors[task['priority']],
            fg=self.colors['text'],
            padx=8,
            pady=2
        )
        priority_label.pack(side=tk.LEFT, padx=5)
        
        # Actions
        action_frame = tk.Frame(top_row, bg=self.colors['card'])
        action_frame.pack(side=tk.RIGHT)
        
        # Edit button
        edit_btn = tk.Button(
            action_frame,
            text="✏️",
            font=self.small_font,
            bg=self.colors['card'],
            fg=self.colors['text_secondary'],
            bd=0,
            cursor="hand2",
            command=lambda: self.edit_task(task['id'])
        )
        edit_btn.pack(side=tk.LEFT, padx=2)
        
        # Delete button
        delete_btn = tk.Button(
            action_frame,
            text="🗑️",
            font=self.small_font,
            bg=self.colors['card'],
            fg=self.colors['danger'],
            bd=0,
            cursor="hand2",
            command=lambda: self.delete_task(task['id'])
        )
        delete_btn.pack(side=tk.LEFT, padx=2)
        
        # Description (if exists)
        if task.get('description'):
            desc_label = tk.Label(
                content_frame,
                text=task['description'][:100] + "..." if len(task['description']) > 100 else task['description'],
                font=self.small_font,
                bg=self.colors['card'],
                fg=self.colors['text_secondary'],
                anchor=tk.W,
                justify=tk.LEFT
            )
            desc_label.pack(fill=tk.X, pady=(5, 0))
        
        # Bottom row (due date)
        bottom_row = tk.Frame(content_frame, bg=self.colors['card'])
        bottom_row.pack(fill=tk.X, pady=(5, 0))
        
        due_date = datetime.strptime(task['due_date'], "%Y-%m-%d")
        days_until = (due_date - datetime.now()).days
        
        due_text = f"📅 Due: {task['due_date']}"
        if days_until < 0:
            due_text += f" (Overdue by {abs(days_until)} days)"
            due_color = self.colors['danger']
        elif days_until == 0:
            due_text += " (Today)"
            due_color = self.colors['warning']
        elif days_until <= 3:
            due_text += f" ({days_until} days)"
            due_color = self.colors['warning']
        else:
            due_text += f" ({days_until} days)"
            due_color = self.colors['text_secondary']
        
        tk.Label(
            bottom_row,
            text=due_text,
            font=self.small_font,
            bg=self.colors['card'],
            fg=due_color
        ).pack(side=tk.LEFT)
    
    def toggle_task_status(self, task_id, completed):
        """Toggle task completion status"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = 'completed' if completed else 'pending'
                break
        
        self.save_tasks()
        self.filter_tasks(self.current_filter)
        self.update_stats()
        
        status = "completed" if completed else "reopened"
        self.show_notification(f"Task {status}!", "success" if completed else "info")
    
    def edit_task(self, task_id):
        """Edit a task"""
        task = next((t for t in self.tasks if t['id'] == task_id), None)
        if not task:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Task")
        dialog.geometry("500x400")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250)
        y = (dialog.winfo_screenheight() // 2) - (200)
        dialog.geometry(f'+{x}+{y}')
        
        # Title
        tk.Label(
            dialog,
            text="Edit Task",
            font=self.heading_font,
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        # Form container
        form_frame = tk.Frame(dialog, bg=self.colors['bg'])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        # Task title
        tk.Label(
            form_frame,
            text="Task Title",
            font=self.body_font,
            bg=self.colors['bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=(10, 5))
        
        title_entry = tk.Entry(
            form_frame,
            font=self.body_font,
            bg=self.colors['card'],
            fg=self.colors['text'],
            bd=1,
            relief=tk.SOLID,
            insertbackground=self.colors['text']
        )
        title_entry.insert(0, task['title'])
        title_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Description
        tk.Label(
            form_frame,
            text="Description",
            font=self.body_font,
            bg=self.colors['bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=(10, 5))
        
        desc_text = tk.Text(
            form_frame,
            height=4,
            font=self.body_font,
            bg=self.colors['card'],
            fg=self.colors['text'],
            bd=1,
            relief=tk.SOLID,
            insertbackground=self.colors['text']
        )
        desc_text.insert("1.0", task.get('description', ''))
        desc_text.pack(fill=tk.X, pady=(0, 10))
        
        # Priority
        tk.Label(
            form_frame,
            text="Priority",
            font=self.body_font,
            bg=self.colors['bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=(10, 5))
        
        priority_var = tk.StringVar(value=task['priority'])
        priority_frame = tk.Frame(form_frame, bg=self.colors['bg'])
        priority_frame.pack(fill=tk.X, pady=(0, 10))
        
        for priority in ["low", "medium", "high"]:
            tk.Radiobutton(
                priority_frame,
                text=priority.capitalize(),
                variable=priority_var,
                value=priority,
                font=self.body_font,
                bg=self.colors['bg'],
                fg=self.colors['text'],
                selectcolor=self.colors['card'],
                activebackground=self.colors['bg']
            ).pack(side=tk.LEFT, padx=10)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, pady=20, padx=30)
        
        def save_changes():
            task['title'] = title_entry.get().strip()
            task['description'] = desc_text.get("1.0", tk.END).strip()
            task['priority'] = priority_var.get()
            
            if not task['title']:
                messagebox.showwarning("Warning", "Please enter a task title!")
                return
            
            self.save_tasks()
            self.filter_tasks(self.current_filter)
            dialog.destroy()
            self.show_notification("Task updated successfully!", "success")
        
        ttk.Button(
            button_frame,
            text="Save Changes",
            style="Modern.TButton",
            command=save_changes
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Button(
            button_frame,
            text="Cancel",
            font=self.body_font,
            bg=self.colors['card'],
            fg=self.colors['text'],
            bd=0,
            padx=20,
            pady=10,
            command=dialog.destroy
        ).pack(side=tk.RIGHT)
    
    def delete_task(self, task_id):
        """Delete a task"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            self.tasks = [t for t in self.tasks if t['id'] != task_id]
            self.save_tasks()
            self.filter_tasks(self.current_filter)
            self.update_stats()
            self.show_notification("Task deleted!", "info")
    
    def filter_tasks(self, filter_type):
        """Filter tasks based on selected filter"""
        self.set_active_filter(filter_type)
        
        if filter_type == 'all':
            self.filtered_tasks = self.tasks.copy()
        elif filter_type == 'pending':
            self.filtered_tasks = [t for t in self.tasks if t['status'] == 'pending']
        elif filter_type == 'completed':
            self.filtered_tasks = [t for t in self.tasks if t['status'] == 'completed']
        elif filter_type == 'high':
            self.filtered_tasks = [t for t in self.tasks if t['priority'] == 'high']
        elif filter_type == 'today':
            today = datetime.now().strftime("%Y-%m-%d")
            self.filtered_tasks = [t for t in self.tasks if t['due_date'] == today]
        
        # Apply search filter if exists
        if self.search_var.get():
            search_term = self.search_var.get().lower()
            self.filtered_tasks = [
                t for t in self.filtered_tasks 
                if search_term in t['title'].lower() or 
                   search_term in t.get('description', '').lower()
            ]
        
        self.display_tasks()
    
    def search_tasks(self, *args):
        """Search tasks based on search input"""
        self.filter_tasks(self.current_filter)
    
    def update_stats(self):
        """Update statistics display"""
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t['status'] == 'completed'])
        pending = total - completed
        
        self.total_label.config(text=str(total))
        self.completed_label.config(text=str(completed))
        self.pending_label.config(text=str(pending))
    
    def show_notification(self, message, type="info"):
        """Show a notification popup"""
        notif = tk.Toplevel(self.root)
        notif.overrideredirect(True)
        
        # Set notification color based on type
        colors = {
            'success': self.colors['success'],
            'info': self.colors['primary'],
            'warning': self.colors['warning'],
            'danger': self.colors['danger']
        }
        bg_color = colors.get(type, self.colors['primary'])
        
        # Create notification content
        frame = tk.Frame(notif, bg=bg_color, padx=20, pady=10)
        frame.pack()
        
        tk.Label(
            frame,
            text=message,
            font=self.body_font,
            bg=bg_color,
            fg=self.colors['text']
        ).pack()
        
        # Position notification
        notif.update_idletasks()
        x = self.root.winfo_x() + self.root.winfo_width() - notif.winfo_width() - 20
        y = self.root.winfo_y() + 50
        notif.geometry(f'+{x}+{y}')
        
        # Auto-close after 2 seconds
        notif.after(2000, notif.destroy)
        
        # Fade in effect
        notif.attributes('-alpha', 0)
        for i in range(1, 11):
            notif.after(i * 20, lambda alpha=i/10: notif.attributes('-alpha', alpha))
    
    def load_tasks(self) -> List[Dict]:
        """Load tasks from JSON file"""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def on_closing(self):
        """Handle window closing event"""
        self.save_tasks()
        self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ModernTaskApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
