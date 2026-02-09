import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import threading
import os

class DockerPiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DockerPi Extension")
        self.root.geometry("500x700")
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

    # --- SCHERM 2: CREATE WINDOW ---
    def show_setup_screen(self):
        self.clear_screen()
        
        # Terug knop naar dashboard
        tk.Button(self.root, text="← Back", command=self.show_dashboard, bg="#444", fg="white").pack(anchor="nw", padx=10, pady=10)

        tk.Label(self.root, text="New Container Settings", font=("Arial", 18, "bold"), fg="white", bg="#1e1e1e").pack(pady=10)

        # Formulier Frame
        form = tk.Frame(self.root, bg="#1e1e1e")
        form.pack(pady=20)

        tk.Label(form, text="Container Name:", fg="white", bg="#1e1e1e").pack()
        name_entry = tk.Entry(form, width=30)
        name_entry.insert(0, "my-app")
        name_entry.pack(pady=5)

        tk.Label(form, text="Docker Image (e.g. nginx):", fg="white", bg="#1e1e1e").pack()
        image_entry = tk.Entry(form, width=30)
        image_entry.insert(0, "nginx")
        image_entry.pack(pady=5)

        tk.Label(form, text="Port Mapping (Host:Container):", fg="white", bg="#1e1e1e").pack()
        port_entry = tk.Entry(form, width=30)
        port_entry.insert(0, "8080:80")
        port_entry.pack(pady=5)

        # Status tekst (Laden indicator)
        status_label = tk.Label(self.root, text="", fg="#FFD700", bg="#1e1e1e", font=("Arial", 10, "italic"))
        
        def start_deploy():
            c_name = name_entry.get().strip()
            c_image = image_entry.get().strip()
            c_port = port_entry.get().strip()
            
            if not c_name or not c_image:
                messagebox.showerror("Error", "Name and Image are required!")
                return

            # UI aanpassen voor laden
            create_btn.config(state="disabled", text="Processing...")
            status_label.config(text=f"Status: Pulling '{c_image}' and starting... \nThis may take a minute.")
            status_label.pack(pady=10)
            self.root.update()

            def run_docker_task():
                try:
                    cmd = ["docker", "run", "-d", "--name", c_name]
                    if c_port:
                        cmd.extend(["-p", c_port])
                    cmd.append(c_image)
                    
                    subprocess.run(cmd, check=True)
                    
                    # Bij succes terug naar dashboard
                    self.root.after(0, self.show_dashboard)
                except Exception as e:
                    # Bij fout, knop weer aanzetten en fout tonen
                    self.root.after(0, lambda: [
                        create_btn.config(state="normal", text="CREATE & START"),
                        status_label.config(text=""),
                        messagebox.showerror("Docker Error", str(e))
                    ])

            # Start in achtergrond thread
            threading.Thread(target=run_docker_task, daemon=True).start()

        create_btn = tk.Button(self.root, text="CREATE & START", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                              command=start_deploy, pady=10, width=20)
        create_btn.pack(pady=20)

    # --- SCHERM 3: DASHBOARD ---
    def show_dashboard(self):
        self.clear_screen()
        
        header_frame = tk.Frame(self.root, bg="#1e1e1e")
        header_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(header_frame, text="Your Dashboard", font=("Arial", 18, "bold"), fg="white", bg="#1e1e1e").pack(side="left")
        tk.Button(header_frame, text="Refresh ↻", command=self.show_dashboard, bg="#444", fg="white").pack(side="right")
        
        container_list = self.get_docker_containers()
        
        if not container_list:
            tk.Label(self.root, text="No containers found.", fg="#888", bg="#1e1e1e").pack(pady=50)
        else:
            for i, (c_id, name) in enumerate(container_list[:self.max_containers]):
                status = self.get_container_status(name)
                is_online = status == "running"
                
                frame = tk.Frame(self.root, bg="#2d2d2d", pady=10)
                frame.pack(fill="x", padx=20, pady=5)
                
                tk.Label(frame, text="🐳", font=("Arial", 15), bg="#3d3d3d", fg="white", width=3).pack(side="left", padx=10)
                tk.Label(frame, text=name, font=("Arial", 12, "bold"), fg="white", bg="#2d2d2d").pack(side="left")
                
                tk.Button(frame, text="Manage", command=lambda n=name: self.show_info(n)).pack(side="right", padx=10)
                tk.Label(frame, text=f"● {'Online' if is_online else 'Offline'}", 
                         fg="#4CAF50" if is_online else "#f44336", bg="#2d2d2d").pack(side="right", padx=10)

        count = min(len(container_list), 5)
        add_btn = tk.Button(self.root, text=f"Add a Container {count}/5", 
                            state="disabled" if count >= 5 else "normal",
                            command=self.show_setup_screen, bg="#333", fg="white", pady=10)
        add_btn.pack(side="bottom", fill="x", pady=20, padx=20)

    # --- HELPER FUNCTIES ---
    def get_docker_containers(self):
        try:
            output = subprocess.check_output(['docker', 'ps', '-a', '--format', '{{.ID}}|{{.Names}}']).decode()
            return [line.split('|') for line in output.strip().split('\n') if line]
        except: return []

    def get_container_status(self, name):
        try:
            return subprocess.check_output(['docker', 'inspect', '-f', '{{.State.Status}}', name]).decode().strip()
        except: return "unknown"

    def show_info(self, name):
        status = self.get_container_status(name)
        info_win = tk.Toplevel(self.root)
        info_win.title(f"Manage {name}")
        info_win.geometry("350x300")
        info_win.configure(bg="#1e1e1e")
        
        tk.Label(info_win, text=f"Container: {name}", fg="white", bg="#1e1e1e", font=("Arial", 14, "bold")).pack(pady=20)
        
        def run_cmd(cmd):
            os.system(f"docker {cmd} {name}")
            info_win.destroy()
            self.show_dashboard()

        tk.Button(info_win, text="START", width=15, bg="green", fg="white", command=lambda: run_cmd("start")).pack(pady=5)
        tk.Button(info_win, text="STOP", width=15, bg="orange", fg="white", command=lambda: run_cmd("stop")).pack(pady=5)
        tk.Button(info_win, text="DELETE", width=15, bg="red", fg="white", command=lambda: run_cmd("rm -f")).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = DockerPiApp(root)
    root.mainloop()
