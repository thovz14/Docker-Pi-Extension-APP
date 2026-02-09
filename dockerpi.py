import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os

class DockerPiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DockerPi Extension")
        self.root.geometry("500x650")
        self.root.configure(bg="#1e1e1e")
        
        self.max_containers = 5
        self.show_welcome_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- SCHERM 1: WELKOM ---
    def show_welcome_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Welcome", font=("Arial", 30, "bold"), fg="white", bg="#1e1e1e").pack(pady=(100, 10))
        tk.Label(self.root, text="DockerPi Extension APP", font=("Arial", 14), fg="#aaaaaa", bg="#1e1e1e").pack(pady=10)
        
        start_btn = tk.Button(self.root, text="Start", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", 
                              width=15, height=2, bd=0, command=self.check_initial_state)
        start_btn.pack(pady=50)

    def check_initial_state(self):
        containers = self.get_docker_containers()
        if containers:
            self.show_dashboard()
        else:
            self.show_setup_screen()

    # --- SCHERM 2: SETUP ---
    def show_setup_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Setup Containers", font=("Arial", 18, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)
        
        containers = self.get_docker_containers()
        if not containers:
            tk.Label(self.root, text="No containers found on your Pi.", fg="white", bg="#1e1e1e").pack(pady=10)
            tk.Button(self.root, text="Create Nginx Container", bg="#2196F3", fg="white", 
                      command=self.create_default_container).pack(pady=20)
        else:
            tk.Label(self.root, text="Found containers! Click to go to Dashboard.", fg="white", bg="#1e1e1e").pack(pady=10)
            tk.Button(self.root, text="Go to Dashboard", command=self.show_dashboard).pack(pady=20)

    def create_default_container(self):
        try:
            # We gebruiken een unieke naam op basis van tijd om conflicten te voorkomen
            import time
            name = f"Pi-Web-{int(time.time())}"
            subprocess.run(["docker", "run", "-d", "--name", name, "nginx"], check=True)
            messagebox.showinfo("Success", f"Container '{name}' created!")
            self.show_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create container: {e}")

    # --- SCHERM 3: DASHBOARD ---
    def show_dashboard(self):
        self.clear_screen()
        
        # Header met Refresh knop
        header_frame = tk.Frame(self.root, bg="#1e1e1e")
        header_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(header_frame, text="Your Dashboard", font=("Arial", 18, "bold"), fg="white", bg="#1e1e1e").pack(side="left")
        tk.Button(header_frame, text="Refresh ↻", command=self.show_dashboard, bg="#444", fg="white").pack(side="right")
        
        container_list = self.get_docker_containers()
        
        if not container_list:
            tk.Label(self.root, text="No containers to show.", fg="#888", bg="#1e1e1e").pack(pady=50)
        else:
            for i, (c_id, name) in enumerate(container_list[:self.max_containers]):
                status = self.get_container_status(name)
                # Verbeterde check: Docker geeft 'running', 'exited', 'paused'
                is_online = status == "running"
                color = "#4CAF50" if is_online else "#f44336"
                status_text = "Online" if is_online else "Offline"
                
                frame = tk.Frame(self.root, bg="#2d2d2d", pady=10)
                frame.pack(fill="x", padx=20, pady=5)
                
                # Emoji rondje
                tk.Label(frame, text="🐳", font=("Arial", 15), bg="#3d3d3d", fg="white", width=3).pack(side="left", padx=10)
                
                # Naam
                tk.Label(frame, text=name, font=("Arial", 12, "bold"), fg="white", bg="#2d2d2d").pack(side="left")
                
                # Info Button
                btn_info = tk.Button(frame, text="Manage", command=lambda n=name: self.show_info(n))
                btn_info.pack(side="right", padx=10)
                
                # Status Dot
                tk.Label(frame, text=f"● {status_text}", fg=color, bg="#2d2d2d", font=("Arial", 10)).pack(side="right", padx=10)

        # Footer
        count = min(len(container_list), 5)
        add_btn = tk.Button(self.root, text=f"Add a Container {count}/5", 
                            state="disabled" if count >= 5 else "normal",
                            command=self.show_setup_screen, bg="#333", fg="white", pady=10)
        add_btn.pack(side="bottom", fill="x", pady=20, padx=20)

    # --- COMMANDS & LOGICA ---
    def get_docker_containers(self):
        try:
            # Haalt alle containers op (ID en Naam)
            output = subprocess.check_output(['docker', 'ps', '-a', '--format', '{{.ID}}|{{.Names}}']).decode()
            lines = output.strip().split('\n')
            return [line.split('|') for line in lines if line]
        except:
            return []

    def get_container_status(self, name):
        try:
            # Inspect geeft de exacte status (running, exited, etc.)
            return subprocess.check_output(['docker', 'inspect', '-f', '{{.State.Status}}', name]).decode().strip()
        except:
            return "unknown"

    def show_info(self, name):
        status = self.get_container_status(name)
        info_win = tk.Toplevel(self.root)
        info_win.title(f"Manage {name}")
        info_win.geometry("350x300")
        info_win.configure(bg="#1e1e1e")
        info_win.transient(self.root) # Zorgt dat hij bovenop blijft
        
        tk.Label(info_win, text=f"Container: {name}", fg="white", bg="#1e1e1e", font=("Arial", 14, "bold")).pack(pady=20)
        
        status_lbl = tk.Label(info_win, text=f"Current Status: {status.upper()}", 
                              fg="#4CAF50" if status == "running" else "#f44336", bg="#1e1e1e")
        status_lbl.pack(pady=5)

        def run_docker_cmd(cmd):
            try:
                subprocess.run(["docker", cmd, name], check=True)
                info_win.destroy()
                self.show_dashboard() # DASHBOARD VERVERSEN
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        btn_frame = tk.Frame(info_win, bg="#1e1e1e")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="START", width=10, bg="#4CAF50", fg="white", command=lambda: run_docker_cmd("start")).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="STOP", width=10, bg="#ff9800", fg="white", command=lambda: run_docker_cmd("stop")).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="DELETE", width=22, bg="#f44336", fg="white", command=lambda: run_docker_cmd("rm -f")).grid(row=1, column=0, columnspan=2, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = DockerPiApp(root)
    root.mainloop()
