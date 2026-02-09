import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import threading
import os

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, color="#4CAF50", width=200, height=45, radius=25):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self.command = command
        self.color = color
        
        # Teken de afgeronde vorm
        self.rect = self.create_rounded_rect(0, 0, width, height, radius, fill=color)
        self.text = self.create_text(width/2, height/2, text=text, fill="white", font=("Fredoka", 12, "bold"))
        
        # Events
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", lambda e: self.itemconfig(self.rect, fill=self.lighten(color)))
        self.bind("<Leave>", lambda e: self.itemconfig(self.rect, fill=color))

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def lighten(self, hex):
        # Simpele highlight effect
        return hex # Voor nu houden we het simpel, maar je kunt hier RGB codes aanpassen

class DockerPiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DockerPi Extension")
        self.root.geometry("500x750")
        self.root.configure(bg="#121212") # Iets donkerder modern thema
        
        self.max_containers = 5
        self.show_welcome_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_welcome_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Welcome", font=("Fredoka", 40, "bold"), fg="white", bg="#121212").pack(pady=(120, 10))
        tk.Label(self.root, text="DockerPi Extension APP", font=("Fredoka", 16), fg="#888888", bg="#121212").pack(pady=10)
        
        RoundedButton(self.root, "Start Journey", self.check_initial_state, color="#4CAF50", width=220).pack(pady=60)

    def check_initial_state(self):
        containers = self.get_docker_containers()
        self.show_dashboard() if containers else self.show_setup_screen()

    def show_setup_screen(self):
        self.clear_screen()
        # Back button
        btn_back = tk.Button(self.root, text="←", font=("Fredoka", 14), fg="white", bg="#121212", bd=0, command=self.show_dashboard)
        btn_back.pack(anchor="nw", padx=20, pady=20)

        tk.Label(self.root, text="New Container", font=("Fredoka", 22, "bold"), fg="white", bg="#121212").pack(pady=10)

        form = tk.Frame(self.root, bg="#121212")
        form.pack(pady=20)

        def create_entry(label_text, default):
            tk.Label(form, text=label_text, font=("Fredoka", 11), fg="#aaa", bg="#121212").pack(anchor="w")
            e = tk.Entry(form, font=("Fredoka", 12), bg="#1e1e1e", fg="white", insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#333")
            e.insert(0, default)
            e.pack(fill="x", pady=(5, 15), ipady=8)
            return e

        name_e = create_entry("Container Name", "my-pi-server")
        image_e = create_entry("Docker Image", "nginx")
        port_e = create_entry("Port Mapping (Host:Container)", "8080:80")

        status_label = tk.Label(self.root, text="", font=("Fredoka", 10), fg="#FFD700", bg="#121212")

        def start_deploy():
            status_label.config(text="Deploying... checking Docker images")
            status_label.pack(pady=5)
            self.root.update()
            
            def run():
                try:
                    cmd = ["docker", "run", "-d", "--name", name_e.get()]
                    if port_e.get(): cmd.extend(["-p", port_e.get()])
                    cmd.append(image_e.get())
                    subprocess.run(cmd, check=True)
                    self.root.after(0, self.show_dashboard)
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

            threading.Thread(target=run, daemon=True).start()

        RoundedButton(self.root, "Create & Launch", start_deploy, color="#2196F3", width=250).pack(pady=20)

    def show_dashboard(self):
        self.clear_screen()
        
        header = tk.Frame(self.root, bg="#121212")
        header.pack(fill="x", padx=25, pady=(30, 20))
        
        tk.Label(header, text="Dashboard", font=("Fredoka", 24, "bold"), fg="white", bg="#121212").pack(side="left")
        # Kleine ronde refresh knop
        RoundedButton(header, "↻", self.show_dashboard, color="#333", width=40, height=40).pack(side="right")
        
        container_list = self.get_docker_containers()
        
        for i, (c_id, name) in enumerate(container_list[:self.max_containers]):
            status = self.get_container_status(name)
            is_online = status == "running"
            
            # Container Card
            card = tk.Frame(self.root, bg="#1e1e1e", padx=15, pady=10)
            card.pack(fill="x", padx=20, pady=8)
            
            # Badge
            tk.Label(card, text="🐳", font=("Arial", 16), bg="#2d2d2d", fg="white", padx=10).pack(side="left", padx=(0, 15))
            
            name_label = tk.Label(card, text=name, font=("Fredoka", 13, "bold"), fg="white", bg="#1e1e1e")
            name_label.pack(side="left")
            
            # Status dot en Manage knop
            RoundedButton(card, "Manage", lambda n=name: self.show_info(n), color="#333", width=80, height=35).pack(side="right", padx=5)
            color = "#4CAF50" if is_online else "#f44336"
            tk.Label(card, text="●", fg=color, bg="#1e1e1e", font=("Arial", 14)).pack(side="right", padx=5)

        # Bottom Add Button
        footer = tk.Frame(self.root, bg="#121212")
        footer.pack(side="bottom", fill="x", pady=30)
        RoundedButton(footer, f"Add Container {min(len(container_list), 5)}/5", self.show_setup_screen, color="#4CAF50", width=300).pack()

    def get_docker_containers(self):
        try:
            out = subprocess.check_output(['docker', 'ps', '-a', '--format', '{{.ID}}|{{.Names}}']).decode()
            return [line.split('|') for line in out.strip().split('\n') if line]
        except: return []

    def get_container_status(self, name):
        try:
            return subprocess.check_output(['docker', 'inspect', '-f', '{{.State.Status}}', name]).decode().strip()
        except: return "unknown"

    def show_info(self, name):
        info_win = tk.Toplevel(self.root)
        info_win.geometry("350x350")
        info_win.configure(bg="#1e1e1e")
        
        tk.Label(info_win, text=name, font=("Fredoka", 18, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)
        
        def run_c(cmd):
            os.system(f"docker {cmd} {name}")
            info_win.destroy()
            self.show_dashboard()

        RoundedButton(info_win, "START", lambda: run_c("start"), color="#4CAF50").pack(pady=10)
        RoundedButton(info_win, "STOP", lambda: run_c("stop"), color="#FF9800").pack(pady=10)
        RoundedButton(info_win, "DELETE", lambda: run_c("rm -f"), color="#F44336").pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    # Forceer Fredoka font (als het systeem het nog niet heeft, valt hij terug op sans-serif)
    app = DockerPiApp(root)
    root.mainloop()
