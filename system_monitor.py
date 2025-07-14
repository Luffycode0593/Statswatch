import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import threading
import time
from datetime import datetime
import platform
import os
import sys

try:
    import screeninfo
except ImportError:
    screeninfo = None

class SystemMonitor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Moniteur Système - PC Stats")
        self.root.geometry("1200x800")
        self.theme = 'dark'  # 'dark' ou 'light'
        self.lang = 'fr'     # 'fr' ou 'en'
        self.colors = self.get_theme_colors()
        
        # Configuration
        self.show_vps = tk.BooleanVar(value=True)
        self.show_temps = tk.BooleanVar(value=True)
        self.show_components = tk.BooleanVar(value=True)
        self.show_memory = tk.BooleanVar(value=True)
        self.show_global = tk.BooleanVar(value=True)
        
        # Overlay benchmark
        self.overlay_active = False
        self.overlay_window = None
        
        self.setup_ui()
        self.start_monitoring()
        
    def get_theme_colors(self):
        if self.theme == 'dark':
            return {
                'bg': '#2b2b2b',
                'panel': '#3c3c3c',
                'widget': '#404040',
                'text': 'white',
                'button_bg': '#2196F3',
                'button_fg': '#fff',
                'button2_bg': '#00C851',
                'button2_fg': '#fff',
                'settings_bg': '#222',
                'settings_fg': '#fff',
            }
        else:
            return {
                'bg': '#f5f5f5',
                'panel': '#e0e0e0',
                'widget': '#fafafa',
                'text': '#222',
                'button_bg': '#1976D2',
                'button_fg': '#fff',
                'button2_bg': '#43A047',
                'button2_fg': '#fff',
                'settings_bg': '#fff',
                'settings_fg': '#222',
            }
    
    def setup_ui(self):
        self.root.configure(bg=self.colors['bg'])
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TFrame', background=self.colors['bg'])
        style.configure('Custom.TLabel', background=self.colors['bg'], foreground=self.colors['text'])
        
        # Panel de configuration (haut gauche)
        config_frame = tk.Frame(self.root, bg=self.colors['panel'], relief='raised', bd=2)
        config_frame.place(x=10, y=10, width=300, height=250)
        
        tk.Label(config_frame, text=self.tr("⚙️ Configuration"), font=('Arial', 14, 'bold'), 
                bg=self.colors['panel'], fg=self.colors['text']).pack(pady=10)
        
        tk.Checkbutton(config_frame, text=self.tr("Afficher VPS/CPU"), variable=self.show_vps,
                      bg=self.colors['panel'], fg=self.colors['text'], selectcolor=self.colors['bg'], font=('Arial', 10)).pack(anchor='w', padx=15, pady=2)
        tk.Checkbutton(config_frame, text=self.tr("Afficher Températures"), variable=self.show_temps,
                      bg=self.colors['panel'], fg=self.colors['text'], selectcolor=self.colors['bg'], font=('Arial', 10)).pack(anchor='w', padx=15, pady=2)
        tk.Checkbutton(config_frame, text=self.tr("Afficher Composants"), variable=self.show_components,
                      bg=self.colors['panel'], fg=self.colors['text'], selectcolor=self.colors['bg'], font=('Arial', 10)).pack(anchor='w', padx=15, pady=2)
        tk.Checkbutton(config_frame, text=self.tr("Afficher Mémoire"), variable=self.show_memory,
                      bg=self.colors['panel'], fg=self.colors['text'], selectcolor=self.colors['bg'], font=('Arial', 10)).pack(anchor='w', padx=15, pady=2)
        tk.Checkbutton(config_frame, text=self.tr("Infos Globales"), variable=self.show_global,
                      bg=self.colors['panel'], fg=self.colors['text'], selectcolor=self.colors['bg'], font=('Arial', 10)).pack(anchor='w', padx=15, pady=2)
        
        # Widgets de monitoring (inchangés)
        self.create_monitoring_widgets()
        
        # Boutons en bas à droite
        self.create_bottom_buttons()

        # Label signature en bas à droite
        signature = tk.Label(self.root, text="Created by Luffy | Contact: luffy._.f (Discord)",
                            font=("Arial", 9, "italic"), fg="#888", bg=self.colors['bg'])
        signature.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-5)
        
    def create_bottom_buttons(self):
        # Frame pour les boutons en bas à droite
        bottom_frame = tk.Frame(self.root, bg=self.colors['bg'])
        bottom_frame.place(relx=1.0, rely=1.0, anchor='se', x=-30, y=-30)
        
        # Rafraîchir
        refresh_btn = tk.Button(
            bottom_frame, text=self.tr("🔄 Rafraîchir"), command=self.refresh_all,
            bg=self.colors['button_bg'], fg=self.colors['button_fg'], font=('Arial', 14, 'bold'), width=13, height=2, bd=4, relief='raised', cursor='hand2', activebackground=self.colors['button_bg'], activeforeground=self.colors['button_fg']
        )
        refresh_btn.grid(row=0, column=0, padx=10, pady=5)
        
        # Overlay
        overlay_btn = tk.Button(
            bottom_frame, text=self.tr("🏁 Overlay"), command=self.open_overlay_config,
            bg=self.colors['button2_bg'], fg=self.colors['button2_fg'], font=('Arial', 14, 'bold'), width=13, height=2, bd=4, relief='raised', cursor='hand2', activebackground=self.colors['button2_bg'], activeforeground=self.colors['button2_fg']
        )
        overlay_btn.grid(row=0, column=1, padx=10, pady=5)
        
        # Paramètres
        settings_btn = tk.Button(
            bottom_frame, text="⚙️", command=self.open_settings,
            bg=self.colors['settings_bg'], fg=self.colors['settings_fg'], font=('Arial', 18, 'bold'), width=3, height=2, bd=4, relief='raised', cursor='hand2', activebackground=self.colors['panel'], activeforeground=self.colors['text']
        )
        settings_btn.grid(row=0, column=2, padx=10, pady=5)

    def open_overlay_config(self):
        # Fenêtre de config overlay
        win = tk.Toplevel(self.root)
        win.title(self.tr("Configuration Overlay"))
        win.geometry("320x260")
        win.configure(bg=self.colors['settings_bg'])
        win.resizable(False, False)
        
        tk.Label(win, text=self.tr("Choisissez les infos à afficher dans l'overlay :"), font=('Arial', 12, 'bold'), bg=self.colors['settings_bg'], fg=self.colors['settings_fg']).pack(pady=10)
        
        # Variables de config overlay
        self.overlay_show_fps = tk.BooleanVar(value=getattr(self, 'overlay_show_fps', True))
        self.overlay_show_cpu = tk.BooleanVar(value=getattr(self, 'overlay_show_cpu', True))
        self.overlay_show_network = tk.BooleanVar(value=getattr(self, 'overlay_show_network', False))
        self.overlay_show_temp = tk.BooleanVar(value=getattr(self, 'overlay_show_temp', True))
        
        tk.Checkbutton(win, text="FPS", variable=self.overlay_show_fps, font=('Arial', 11), bg=self.colors['settings_bg'], fg=self.colors['settings_fg'], selectcolor=self.colors['panel']).pack(anchor='w', padx=30, pady=2)
        tk.Checkbutton(win, text=self.tr("Processeur (CPU)"), variable=self.overlay_show_cpu, font=('Arial', 11), bg=self.colors['settings_bg'], fg=self.colors['settings_fg'], selectcolor=self.colors['panel']).pack(anchor='w', padx=30, pady=2)
        tk.Checkbutton(win, text=self.tr("Réseau"), variable=self.overlay_show_network, font=('Arial', 11), bg=self.colors['settings_bg'], fg=self.colors['settings_fg'], selectcolor=self.colors['panel']).pack(anchor='w', padx=30, pady=2)
        tk.Checkbutton(win, text=self.tr("Températures"), variable=self.overlay_show_temp, font=('Arial', 11), bg=self.colors['settings_bg'], fg=self.colors['settings_fg'], selectcolor=self.colors['panel']).pack(anchor='w', padx=30, pady=2)
        
        def launch_overlay():
            win.destroy()
            self.toggle_overlay()
        
        tk.Button(win, text=self.tr("Afficher l'overlay"), command=launch_overlay, font=('Arial', 12, 'bold'), bg=self.colors['button2_bg'], fg=self.colors['button2_fg'], width=18, height=1).pack(pady=18)

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title(self.tr("Paramètres"))
        win.geometry("350x220")
        win.configure(bg=self.colors['settings_bg'])
        win.resizable(False, False)
        
        tk.Label(win, text=self.tr("Paramètres de l'application"), font=('Arial', 14, 'bold'), bg=self.colors['settings_bg'], fg=self.colors['settings_fg']).pack(pady=10)
        
        # Choix de la langue
        tk.Label(win, text=self.tr("Langue :"), font=('Arial', 12), bg=self.colors['settings_bg'], fg=self.colors['settings_fg']).pack(anchor='w', padx=20, pady=5)
        lang_var = tk.StringVar(value=self.lang)
        langs = [('fr', 'Français'), ('en', 'English')]
        for code, label in langs:
            tk.Radiobutton(win, text=label, variable=lang_var, value=code, font=('Arial', 11), bg=self.colors['settings_bg'], fg=self.colors['settings_fg'], selectcolor=self.colors['panel']).pack(anchor='w', padx=40)
        
        # Choix du thème
        tk.Label(win, text=self.tr("Thème :"), font=('Arial', 12), bg=self.colors['settings_bg'], fg=self.colors['settings_fg']).pack(anchor='w', padx=20, pady=5)
        theme_var = tk.StringVar(value=self.theme)
        themes = [('dark', self.tr('Sombre')), ('light', self.tr('Clair'))]
        for code, label in themes:
            tk.Radiobutton(win, text=label, variable=theme_var, value=code, font=('Arial', 11), bg=self.colors['settings_bg'], fg=self.colors['settings_fg'], selectcolor=self.colors['panel']).pack(anchor='w', padx=40)
        
        def apply_settings():
            self.lang = lang_var.get()
            self.theme = theme_var.get()
            self.colors = self.get_theme_colors()
            win.destroy()
            self.root.destroy()
            # Relancer l'appli avec le nouveau thème/langue
            os.execl(sys.executable, sys.executable, *sys.argv)
        
        tk.Button(win, text=self.tr("Appliquer"), command=apply_settings, font=('Arial', 12, 'bold'), bg=self.colors['button_bg'], fg=self.colors['button_fg'], width=12, height=1).pack(pady=15)
    
    def tr(self, text):
        # Simple traduction FR/EN
        translations = {
            'fr': {
                "⚙️ Configuration": "⚙️ Configuration",
                "Afficher VPS/CPU": "Afficher VPS/CPU",
                "Afficher Températures": "Afficher Températures",
                "Afficher Composants": "Afficher Composants",
                "Afficher Mémoire": "Afficher Mémoire",
                "Infos Globales": "Infos Globales",
                "🔄 Rafraîchir": "🔄 Rafraîchir",
                "🏁 Overlay": "🏁 Overlay",
                "Paramètres": "Paramètres",
                "Paramètres de l'application": "Paramètres de l'application",
                "Langue :": "Langue :",
                "Thème :": "Thème :",
                "Sombre": "Sombre",
                "Clair": "Clair",
                "Appliquer": "Appliquer",
            },
            'en': {
                "⚙️ Configuration": "⚙️ Settings",
                "Afficher VPS/CPU": "Show VPS/CPU",
                "Afficher Températures": "Show Temperatures",
                "Afficher Composants": "Show Components",
                "Afficher Mémoire": "Show Memory",
                "Infos Globales": "Global Info",
                "🔄 Rafraîchir": "🔄 Refresh",
                "🏁 Overlay": "🏁 Overlay",
                "Paramètres": "Settings",
                "Paramètres de l'application": "Application Settings",
                "Langue :": "Language:",
                "Thème :": "Theme:",
                "Sombre": "Dark",
                "Clair": "Light",
                "Appliquer": "Apply",
            }
        }
        return translations[self.lang].get(text, text)

    def toggle_overlay(self):
        if not self.overlay_active:
            self.show_overlay()
        else:
            self.hide_overlay()
            
    def show_overlay(self):
        self.overlay_active = True
        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.overrideredirect(True)
        self.overlay_window.attributes('-topmost', True)
        self.overlay_window.attributes('-alpha', 0.92)
        self.overlay_window.configure(bg='#181f18')
        self.overlay_window.geometry("350x160+20+20")
        # Nettoyage
        for widget in self.overlay_window.winfo_children():
            widget.destroy()
        # Affichage dynamique selon config
        self.overlay_labels = []
        if getattr(self, 'overlay_show_fps', False):
            self.overlay_fps = tk.Label(self.overlay_window, text="", font=('Consolas', 15, 'bold'), bg='#181f18', fg='#00C851')
            self.overlay_fps.pack(anchor='w', padx=15, pady=2)
            self.overlay_labels.append('fps')
        if getattr(self, 'overlay_show_cpu', False):
            self.overlay_cpu = tk.Label(self.overlay_window, text="", font=('Consolas', 15, 'bold'), bg='#181f18', fg='#2196F3')
            self.overlay_cpu.pack(anchor='w', padx=15, pady=2)
            self.overlay_freq = tk.Label(self.overlay_window, text="", font=('Consolas', 12), bg='#181f18', fg='#4CAF50')
            self.overlay_freq.pack(anchor='w', padx=15, pady=2)
            self.overlay_labels.append('cpu')
        if getattr(self, 'overlay_show_network', False):
            self.overlay_network = tk.Label(self.overlay_window, text="", font=('Consolas', 13, 'bold'), bg='#181f18', fg='#FF9800')
            self.overlay_network.pack(anchor='w', padx=15, pady=2)
            self.overlay_labels.append('network')
        if getattr(self, 'overlay_show_temp', False):
            self.overlay_cpu_temp = tk.Label(self.overlay_window, text="", font=('Consolas', 13, 'bold'), bg='#181f18', fg='#FF5722')
            self.overlay_cpu_temp.pack(anchor='w', padx=15, pady=2)
            self.overlay_gpu_temp = tk.Label(self.overlay_window, text="", font=('Consolas', 13, 'bold'), bg='#181f18', fg='#FF9800')
            self.overlay_gpu_temp.pack(anchor='w', padx=15, pady=2)
            self.overlay_labels.append('temp')
        # Fermer overlay sur clic droit
        self.overlay_window.bind('<Button-3>', lambda e: self.hide_overlay())
        self.log_message("✅ Overlay activé (toujours visible sur le PC)")
        self.update_overlay_info()
        
    def hide_overlay(self):
        if self.overlay_window:
            self.overlay_window.destroy()
            self.overlay_window = None
        self.overlay_active = False
        self.log_message("❌ Overlay désactivé")
        
    def update_overlay_info(self):
        if not self.overlay_active or not self.overlay_window:
            return
        try:
            # FPS réel = taux de rafraîchissement de l'écran principal
            if hasattr(self, 'overlay_fps'):
                hz = None
                if screeninfo:
                    try:
                        monitors = screeninfo.get_monitors()
                        if monitors:
                            hz = getattr(monitors[0], 'hz', None)
                    except Exception:
                        hz = None
                if hz is None:
                    # Méthode alternative pour Windows
                    try:
                        import ctypes
                        user32 = ctypes.windll.user32
                        user32.SetProcessDPIAware()
                        dc = ctypes.windll.gdi32.CreateDCW("DISPLAY", None, None, None)
                        hz = ctypes.windll.gdi32.GetDeviceCaps(dc, 116)
                        ctypes.windll.gdi32.DeleteDC(dc)
                    except Exception:
                        hz = None
                if hz:
                    self.overlay_fps.config(text=f"Taux de rafraîchissement : {hz} Hz")
                else:
                    self.overlay_fps.config(text="Taux de rafraîchissement : N/A")
            # CPU
            if hasattr(self, 'overlay_cpu'):
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_freq = psutil.cpu_freq()
                self.overlay_cpu.config(text=f"CPU : {cpu_percent:.1f}%")
                self.overlay_freq.config(text=f"Fréquence : {cpu_freq.current:.0f} MHz")
            # Réseau
            if hasattr(self, 'overlay_network'):
                net_io = psutil.net_io_counters()
                sent_mb = net_io.bytes_sent / (1024**2)
                recv_mb = net_io.bytes_recv / (1024**2)
                self.overlay_network.config(text=f"Réseau : {sent_mb:.1f} Mo envoyés / {recv_mb:.1f} Mo reçus")
            # Températures
            if hasattr(self, 'overlay_cpu_temp') or hasattr(self, 'overlay_gpu_temp'):
                temps = psutil.sensors_temperatures()
                cpu_temp_found = False
                gpu_temp_found = False
                if temps:
                    for name, entries in temps.items():
                        if name == 'coretemp':
                            for entry in entries:
                                if 'Package id 0' in entry.label or 'Core 0' in entry.label:
                                    self.overlay_cpu_temp.config(text=f"CPU Temp : {entry.current:.1f}°C")
                                    cpu_temp_found = True
                                    break
                        elif 'gpu' in name.lower():
                            for entry in entries:
                                self.overlay_gpu_temp.config(text=f"GPU Temp : {entry.current:.1f}°C")
                                gpu_temp_found = True
                                break
                if hasattr(self, 'overlay_cpu_temp') and not cpu_temp_found:
                    self.overlay_cpu_temp.config(text="CPU Temp : N/A")
                if hasattr(self, 'overlay_gpu_temp') and not gpu_temp_found:
                    self.overlay_gpu_temp.config(text="GPU Temp : N/A")
        except Exception as e:
            self.log_message(f"❌ Erreur overlay: {e}")
        # Rafraîchir toutes les 2 secondes
        if self.overlay_active:
            self.overlay_window.after(2000, self.update_overlay_info)
        
    def create_monitoring_widgets(self):
        # CPU/VPS Widget
        self.cpu_frame = tk.Frame(self.root, bg=self.colors['widget'], relief='raised', bd=2)
        self.cpu_frame.place(x=320, y=10, width=280, height=200)
        
        self.cpu_label = tk.Label(self.cpu_frame, text="🖥️ CPU/VPS", font=('Arial', 12, 'bold'),
                                 bg=self.colors['widget'], fg=self.colors['text'])
        self.cpu_label.pack(pady=5)
        
        self.cpu_usage = tk.Label(self.cpu_frame, text="Utilisation: 0%", font=('Arial', 10),
                                 bg=self.colors['widget'], fg='#4CAF50')
        self.cpu_usage.pack()
        
        self.cpu_freq = tk.Label(self.cpu_frame, text="Fréquence: 0 MHz", font=('Arial', 10),
                                bg=self.colors['widget'], fg='#2196F3')
        self.cpu_freq.pack()
        
        self.cpu_cores = tk.Label(self.cpu_frame, text="Cœurs: 0", font=('Arial', 10),
                                 bg=self.colors['widget'], fg='#FF9800')
        self.cpu_cores.pack()
        
        # Mémoire Widget
        self.memory_frame = tk.Frame(self.root, bg=self.colors['widget'], relief='raised', bd=2)
        self.memory_frame.place(x=610, y=10, width=280, height=200)
        
        self.memory_label = tk.Label(self.memory_frame, text="💾 Mémoire", font=('Arial', 12, 'bold'),
                                    bg=self.colors['widget'], fg=self.colors['text'])
        self.memory_label.pack(pady=5)
        
        self.memory_usage = tk.Label(self.memory_frame, text="Utilisation: 0%", font=('Arial', 10),
                                    bg=self.colors['widget'], fg='#4CAF50')
        self.memory_usage.pack()
        
        self.memory_total = tk.Label(self.memory_frame, text="Total: 0 GB", font=('Arial', 10),
                                    bg=self.colors['widget'], fg='#2196F3')
        self.memory_total.pack()
        
        self.memory_available = tk.Label(self.memory_frame, text="Disponible: 0 GB", font=('Arial', 10),
                                        bg=self.colors['widget'], fg='#FF9800')
        self.memory_available.pack()
        
        # Disque Widget
        self.disk_frame = tk.Frame(self.root, bg=self.colors['widget'], relief='raised', bd=2)
        self.disk_frame.place(x=900, y=10, width=280, height=200)
        
        self.disk_label = tk.Label(self.disk_frame, text="💿 Disque", font=('Arial', 12, 'bold'),
                                  bg=self.colors['widget'], fg=self.colors['text'])
        self.disk_label.pack(pady=5)
        
        self.disk_usage = tk.Label(self.disk_frame, text="Utilisation: 0%", font=('Arial', 10),
                                  bg=self.colors['widget'], fg='#4CAF50')
        self.disk_usage.pack()
        
        self.disk_total = tk.Label(self.disk_frame, text="Total: 0 GB", font=('Arial', 10),
                                  bg=self.colors['widget'], fg='#2196F3')
        self.disk_total.pack()
        
        self.disk_free = tk.Label(self.disk_frame, text="Libre: 0 GB", font=('Arial', 10),
                                 bg=self.colors['widget'], fg='#FF9800')
        self.disk_free.pack()
        
        # Températures Widget
        self.temp_frame = tk.Frame(self.root, bg=self.colors['widget'], relief='raised', bd=2)
        self.temp_frame.place(x=10, y=270, width=280, height=200)
        
        self.temp_label = tk.Label(self.temp_frame, text="🌡️ Températures", font=('Arial', 12, 'bold'),
                                  bg=self.colors['widget'], fg=self.colors['text'])
        self.temp_label.pack(pady=5)
        
        self.cpu_temp = tk.Label(self.temp_frame, text="CPU: N/A", font=('Arial', 10),
                                bg=self.colors['widget'], fg='#FF5722')
        self.cpu_temp.pack()
        
        self.gpu_temp = tk.Label(self.temp_frame, text="GPU: N/A", font=('Arial', 10),
                                bg=self.colors['widget'], fg='#FF9800')
        self.gpu_temp.pack()
        
        # Réseau Widget
        self.network_frame = tk.Frame(self.root, bg=self.colors['widget'], relief='raised', bd=2)
        self.network_frame.place(x=300, y=270, width=280, height=200)
        
        self.network_label = tk.Label(self.network_frame, text="🌐 Réseau", font=('Arial', 12, 'bold'),
                                     bg=self.colors['widget'], fg=self.colors['text'])
        self.network_label.pack(pady=5)
        
        self.network_sent = tk.Label(self.network_frame, text="Envoyé: 0 MB", font=('Arial', 10),
                                    bg=self.colors['widget'], fg='#4CAF50')
        self.network_sent.pack()
        
        self.network_recv = tk.Label(self.network_frame, text="Reçu: 0 MB", font=('Arial', 10),
                                    bg=self.colors['widget'], fg='#2196F3')
        self.network_recv.pack()
        
        # Informations Globales Widget
        self.global_frame = tk.Frame(self.root, bg=self.colors['widget'], relief='raised', bd=2)
        self.global_frame.place(x=590, y=270, width=280, height=200)
        
        self.global_label = tk.Label(self.global_frame, text="ℹ️ Infos Globales", font=('Arial', 12, 'bold'),
                                    bg=self.colors['widget'], fg=self.colors['text'])
        self.global_label.pack(pady=5)
        
        self.os_info = tk.Label(self.global_frame, text="OS: N/A", font=('Arial', 10),
                               bg=self.colors['widget'], fg='#9C27B0')
        self.os_info.pack()
        
        self.uptime = tk.Label(self.global_frame, text="Uptime: N/A", font=('Arial', 10),
                              bg=self.colors['widget'], fg='#607D8B')
        self.uptime.pack()
        
        self.boot_time = tk.Label(self.global_frame, text="Démarrage: N/A", font=('Arial', 10),
                                 bg=self.colors['widget'], fg='#607D8B')
        self.boot_time.pack()
        
        # Zone de logs
        self.log_frame = tk.Frame(self.root, bg=self.colors['widget'], relief='raised', bd=2)
        self.log_frame.place(x=880, y=270, width=280, height=200)
        
        self.log_label = tk.Label(self.log_frame, text="📋 Logs", font=('Arial', 12, 'bold'),
                                 bg=self.colors['widget'], fg=self.colors['text'])
        self.log_label.pack(pady=5)
        
        self.log_text = tk.Text(self.log_frame, height=8, width=35, bg=self.colors['bg'], fg=self.colors['text'],
                               font=('Consolas', 8))
        self.log_text.pack(padx=5, pady=5)
        
        # Rendre les widgets cliquables
        self.make_widgets_clickable()
        
    def make_widgets_clickable(self):
        # Rendre les widgets cliquables avec des événements
        widgets = [self.cpu_frame, self.memory_frame, self.disk_frame, 
                  self.temp_frame, self.network_frame, self.global_frame]
        
        for widget in widgets:
            widget.bind('<Button-1>', self.widget_clicked)
            widget.bind('<Enter>', self.widget_hover)
            widget.bind('<Leave>', self.widget_leave)
            
    def widget_clicked(self, event):
        widget_name = event.widget.winfo_name() or "Widget"
        self.log_message(f"Widget cliqué: {widget_name}")
        
    def widget_hover(self, event):
        event.widget.configure(bg='#505050')
        
    def widget_leave(self, event):
        event.widget.configure(bg='#404040')
        
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
        # Limiter les logs à 50 lignes
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 50:
            self.log_text.delete("1.0", tk.END)
            self.log_text.insert(tk.END, '\n'.join(lines[-50:]))
            
    def update_cpu_info(self):
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count()
            
            self.cpu_usage.config(text=f"Utilisation: {cpu_percent:.1f}%")
            self.cpu_freq.config(text=f"Fréquence: {cpu_freq.current:.0f} MHz")
            self.cpu_cores.config(text=f"Cœurs: {cpu_count}")
            
        except Exception as e:
            self.log_message(f"❌ Erreur CPU: {e}")
            
    def update_memory_info(self):
        try:
            memory = psutil.virtual_memory()
            
            self.memory_usage.config(text=f"Utilisation: {memory.percent:.1f}%")
            self.memory_total.config(text=f"Total: {memory.total / (1024**3):.1f} GB")
            self.memory_available.config(text=f"Disponible: {memory.available / (1024**3):.1f} GB")
            
        except Exception as e:
            self.log_message(f"❌ Erreur Mémoire: {e}")
            
    def update_disk_info(self):
        try:
            disk = psutil.disk_usage('/')
            
            self.disk_usage.config(text=f"Utilisation: {(disk.used / disk.total) * 100:.1f}%")
            self.disk_total.config(text=f"Total: {disk.total / (1024**3):.1f} GB")
            self.disk_free.config(text=f"Libre: {disk.free / (1024**3):.1f} GB")
            
        except Exception as e:
            self.log_message(f"❌ Erreur Disque: {e}")
            
    def update_temperature_info(self):
        try:
            # Tentative de récupération des températures
            temps = psutil.sensors_temperatures()
            
            if temps:
                for name, entries in temps.items():
                    if name == 'coretemp':
                        for entry in entries:
                            if 'Package id 0' in entry.label or 'Core 0' in entry.label:
                                self.cpu_temp.config(text=f"CPU: {entry.current:.1f}°C")
                                break
                    elif 'gpu' in name.lower():
                        for entry in entries:
                            self.gpu_temp.config(text=f"GPU: {entry.current:.1f}°C")
                            break
            else:
                self.cpu_temp.config(text="CPU: N/A")
                self.gpu_temp.config(text="GPU: N/A")
                
        except Exception as e:
            self.cpu_temp.config(text="CPU: N/A")
            self.gpu_temp.config(text="GPU: N/A")
            
    def update_network_info(self):
        try:
            net_io = psutil.net_io_counters()
            
            sent_mb = net_io.bytes_sent / (1024**2)
            recv_mb = net_io.bytes_recv / (1024**2)
            
            self.network_sent.config(text=f"Envoyé: {sent_mb:.1f} MB")
            self.network_recv.config(text=f"Reçu: {recv_mb:.1f} MB")
            
        except Exception as e:
            self.log_message(f"❌ Erreur Réseau: {e}")
            
    def update_global_info(self):
        try:
            # OS Info
            os_name = platform.system()
            os_version = platform.version()
            self.os_info.config(text=f"OS: {os_name} {os_version}")
            
            # Uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            uptime_str = str(uptime).split('.')[0]  # Enlever les microsecondes
            self.uptime.config(text=f"Uptime: {uptime_str}")
            
            # Boot time
            boot_str = boot_time.strftime("%d/%m/%Y %H:%M")
            self.boot_time.config(text=f"Démarrage: {boot_str}")
            
        except Exception as e:
            self.log_message(f"❌ Erreur Infos Globales: {e}")
            
    def update_all_info(self):
        if self.show_vps.get():
            self.update_cpu_info()
        if self.show_memory.get():
            self.update_memory_info()
        if self.show_components.get():
            self.update_disk_info()
            self.update_network_info()
        if self.show_temps.get():
            self.update_temperature_info()
        if self.show_global.get():
            self.update_global_info()
            
        # Mettre à jour le benchmark si actif
        self.update_overlay_info() # Update overlay info
            
    def refresh_all(self):
        self.update_all_info()
        self.log_message("🔄 Rafraîchissement manuel effectué")
        
    def start_monitoring(self):
        def monitor_loop():
            while True:
                try:
                    self.update_all_info()
                    time.sleep(2)  # Mise à jour toutes les 2 secondes
                except Exception as e:
                    self.log_message(f"❌ Erreur monitoring: {e}")
                    time.sleep(5)
                    
        # Démarrer le monitoring dans un thread séparé
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        # Première mise à jour
        self.update_all_info()
        self.log_message("✅ Monitoring démarré")
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    import sys
    app = SystemMonitor()
    app.run() 