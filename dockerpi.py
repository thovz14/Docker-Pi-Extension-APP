import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os

class DockerPiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DockerPi Extension")
        self.root.geometry("500x600")
        self.root.configure(bg="#1e1e1e")
        
        self.containers_in_dashboard = []
        self.max_containers = 5

        # Start Scherm 1
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
        # Check of er al containers bestaan
        containers = self.get_docker_containers()
        if containers:
            self.show_dashboard()
        else:
            self.show_setup_screen()

    # --- SCHERM 2: ZOEKEN OF MAKEN ---
    def show_setup_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Setup Containers", font=("Arial", 18, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)
        
        containers = self.get_docker_containers()
        
        if not containers:
            tk.Label(self.root, text="No containers found on your Pi.", fg="white", bg="#1e1e1e").pack(pady=10)
            create_btn = tk.Button(self.root, text="Create Hello-World Container", bg="#2196F3", fg="white", 
                                   command=self.create_default_container)
            create_btn.pack(pady=20)
        else:
            tk.Label(self.root, text="Found containers! Select one to add:", fg="white", bg="#1e1e1e").pack(pady=10)
            for c_id, name in containers:
                btn = tk.Button(self.root, text=f"Add {name}", command=lambda n=name: self.add_to_dashboard(n))
                btn.pack(pady=5, fill='x', padx=50)

    def create_default_container(self):
        try:
            subprocess.run(["docker", "run", "-d", "--name", "Pi-Webserver", "nginx"], check=True)
            messagebox.showinfo("Success", "Container 'Pi-Webserver' created!")
            self.show_dashboard()
        except Exception as e:
            messagebox.showerror("Error", "Is Docker installed and do you have permissions?")

    # --- SCHERM 3: DASHBOARD ---
    def show_dashboard(self):
        self.clear_screen()
        tk.Label(self.root, text="Your Containers", font=("Arial", 18, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)
        
        container_list = self.get_docker_containers()
        
        # Laat alleen de containers zien die in het dashboard 'zitten' (max 5)
        for i, (c_id, name) in enumerate(container_list[:self.max_containers]):
            status = self.get_container_status(name)
            color = "#4CAF50" if "Up" in status else "#f44336"
            
            frame = tk.Frame(self.root, bg="#2d2d2d", pady=10)
            frame.pack(fill="x", padx=20, pady=5)
            
            # Emoji in rondje (simulatie met label)
            tk.Label(frame, text="🐳", font=("Arial", 15), bg="#3d3d3d", fg="white", width=3).pack(side="left", padx=10)
            
            # Naam en Status
            tk.Label(frame, text=name, font=("Arial", 12, "bold"), fg="white", bg="#2d2d2d").pack(side="left")
            
            btn_info = tk.Button(frame, text="Info", command=lambda n=name: self.show_info(n))
            btn_info.pack(side="right", padx=10)
            
            status_dot = tk.Label(frame, text="● " + ("Online" if "Up" in status else "Offline"), 
                                  fg=color, bg="#2d2d2d", font=("Arial", 10))
            status_dot.pack(side="right", padx=10)

        # Footer knop
        count = min(len(container_list), 5)
        add_btn = tk.Button(self.root, text=f"Add a Container {count}/5", state="disabled" if count >= 5 else "normal",
                            command=self.show_setup_screen, bg="#444", fg="white")
        add_btn.pack(side="bottom", fill="x", pady=20, padx=20)

    # --- COMMANDS ---
    def get_docker_containers(self):
        try:
            output = subprocess.check_output(['docker', 'ps', '-a', '--format', '{{.ID}}|{{.Names}}']).decode()
            lines = output.strip().split('\n')
            return [line.split('|') for line in lines if line]
        except:
            return []

    def get_container_status(self, name):
        try:
            return subprocess.check_output(['docker', 'inspect', '-f', '{{.State.Status}}', name]).decode().strip()
        except:
            return "unknown"

    def show_info(self, name):
        status = self.get_container_status(name)
        info_win = tk.Toplevel(self.root)
        info_win.title(f"Manage {name}")
        info_win.geometry("300x250")
        info_win.configure(bg="#1e1e1e")
        
        tk.Label(info_win, text=f"Container: {name}", fg="white", bg="#1e1e1e", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(info_win, text=f"Status: {status}", fg="#aaa", bg="#1e1e1e").pack(pady=5)
        
        tk.Button(info_win, text="START", width=15, bg="green", fg="white", 
                  command=lambda: [os.system(f"docker start {name}"), info_win.destroy(), self.show_dashboard()]).pack(pady=5)
        tk.Button(info_win, text="STOP", width=15, bg="orange", fg="white", 
                  command=lambda: [os.system(f"docker stop {name}"), info_win.destroy(), self.show_dashboard()]).pack(pady=5)
        tk.Button(info_win, text="DELETE", width=15, bg="red", fg="white", 
                  command=lambda: [os.system(f"docker rm -f {name}"), info_win.destroy(), self.show_dashboard()]).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = DockerPiApp(root)
    root.mainloop()
