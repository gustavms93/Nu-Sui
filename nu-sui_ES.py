from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

# Application Constants
APP_TITLE = "Ñu-sui: aprende a usar las velocidades de tu bici"
DEFAULT_WINDOW_SIZE = "1200x800"
DEFAULT_FONT_SIZE = 9
DEFAULT_CADENCE = 80

# Cycling-specific Constants
MIN_CADENCE = 60
MAX_CADENCE = 100
OPTIMAL_CADENCE_MIN = 80
OPTIMAL_CADENCE_MAX = 90
MIN_TEETH = 11
MAX_TEETH = 53

# UI Constants
PADDING = 10
LARGE_PADDING = 20
CHART_SIZE = (10, 6)

# Configuración general para gráficos
matplotlib.rcParams.update({'font.size': DEFAULT_FONT_SIZE})

# Diccionario para almacenar los tamaños de rueda y su circunferencia correspondiente en metros
wheel_sizes = {
    "700x18C": 2.07,
    "700x19C": 2.08,
    "700x20C": 2.086,
    "700x23C": 2.096,
    "700x25C": 2.105,
    "700x26C": 2.115,
    "700C": 2.13,
    "700x28C": 2.136,
    "700x30C": 2.146,
    "700x32C": 2.155,
    "700x35C": 2.168,
    "700x38C": 2.18,
    "700x40C": 2.2,
    "700x44C": 2.235,
    "700x45C": 2.242,
    "700x47C": 2.268,
    "650x20C": 1.938,
    "650x23C": 1.944,
    "650x35A": 2.09,
    "650x38B": 2.105,
    "650x38A": 2.125,
    "12x1.75": 0.935,
    "12x1.95": 0.94,
    "14x1.50": 1.02,
    "14x1.75": 1.055,
    "16x1.50": 1.185,
    "16x1.75": 1.195,
    "16x2.00": 1.245,
    "16x1-1/8": 1.29,
    "16x1-3/8": 1.3,
    "18x1.50": 1.34,
    "18x1.75": 1.35,
    "20x1.25": 1.45,
    "20x1.35": 1.46,
    "20x1.50": 1.49,
    "20x1.75": 1.515,
    "20x1.95": 1.565,
    "20x1-1/8": 1.545,
    "20x1-3/8": 1.615,
    "22x1-3/8": 1.77,
    "22x1-1/2": 1.785,
    "24x3/4": 1.785,
    "24x1": 1.753,
    "24x1-1/8": 1.795,
    "24x1-1/4": 1.905,
    "24x1.75": 1.89,
    "24x2.00": 1.925,
    "24x2.125": 1.965,
    "26x7/8": 1.92,
    "26x1.25": 1.95,
    "26x1.40": 2.005,
    "26x1.50": 2.01,
    "26x1.75": 2.023,
    "26x1.95": 2.05,
    "26x2.00": 2.055,
    "26x2.1": 2.068,
    "26x2.125": 2.07,
    "26x2.35": 2.083,
    "26x3.00": 2.17,
    "26x1-1.0": 1.913,
    "26x1": 1.952,
    "26x1-1/8": 1.97,
    "26x1-3/8": 2.068,
    "26x1-1/2": 2.1,
    "27x1": 2.145,
    "27x1-1/8": 2.155,
    "27x1-1/4": 2.161,
    "27x1-3/8": 2.169,
    "27.5x1.50": 2.079,
    "27.5x1.95": 2.09,
    "27.5x2.10": 2.148,
    "27.5x2.25": 2.182,
    "29x2.25": 2.281,
    "29x2.1": 2.288,
    "29x2.2": 2.298,
    "29x2.3": 2.326
}

def handle_errors(func):
    """Decorator for handling errors in GUI methods"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error en {func.__name__}: {str(e)}"
            )
            return None
    return wrapper

@dataclass
class BikeType:
    """Data class for bike type configuration"""
    name: str
    value: str
    platos: List[int]
    pinones: List[int]

class NuSui:
    def __init__(self, root: tk.Tk) -> None:
        """Initialize the application"""
        self.root = root
        self.setup_main_window()
        self.initialize_variables()
        self.create_ui()
        
    def setup_main_window(self) -> None:
        """Configure the main window"""
        self.root.title(APP_TITLE)
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        # Configure matplotlib
        matplotlib.rcParams.update({'font.size': DEFAULT_FONT_SIZE})
        
    def initialize_variables(self) -> None:
        """Initialize class variables"""
        self.crankset_teeth: List[int] = []
        self.cassette_teeth: List[int] = []
        self.wheel_sizes: Dict[str, float] = wheel_sizes
        self.modo_tecnico = tk.BooleanVar(value=False)
        self.debug_var = tk.BooleanVar(value=False)
        
    def setup_scrollable_frame(self, parent, setup_function):
        """
        Crea un marco con scroll dentro del parent y ejecuta la función setup_function
        dentro del marco scrollable
        
        Args:
            parent: Frame contenedor
            setup_function: Función que configura el contenido
        """
        # Crear un canvas para contener el frame scrollable
        canvas = tk.Canvas(parent)
        canvas.pack(side="left", fill="both", expand=True)
        
        # Añadir scrollbar vertical
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar canvas para usar scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Crear frame interior para el contenido
        inner_frame = ttk.Frame(canvas)
        
        # Crear ventana en el canvas para mostrar el frame
        canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        # Función para ajustar el tamaño del canvas al cambiar el tamaño del frame
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Función para ajustar el ancho de la ventana del canvas al cambiar el tamaño
        def configure_canvas_window(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        # Vincular eventos
        inner_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_canvas_window)
        
        # Permitir scroll con la rueda del ratón
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Ejecutar la función de configuración proporcionada en el frame scrollable
        if setup_function:
            setup_function(inner_frame)
        
        return inner_frame
        
    def create_ui(self):
        # Añadir botón para cambiar de modo en la parte superior
        mode_frame = ttk.Frame(self.root)
        mode_frame.pack(fill="x", padx=PADDING, pady=PADDING)
        
        ttk.Label(mode_frame, text="Modo:").pack(side="left", padx=PADDING)
        
        ttk.Radiobutton(mode_frame, text="Principiante", 
                       variable=self.modo_tecnico, value=False,
                       command=self.cambiar_modo).pack(side="left", padx=PADDING)
        
        ttk.Radiobutton(mode_frame, text="Deportivo/Técnico", 
                       variable=self.modo_tecnico, value=True,
                       command=self.cambiar_modo).pack(side="left", padx=PADDING)
        
        # Botón para mostrar debug
        self.debug_var = tk.BooleanVar(value=False)
        self.debug_check = ttk.Checkbutton(mode_frame, text="Mostrar debug",
                                      variable=self.debug_var)
        self.debug_check.pack(side="right", padx=PADDING)
        
        # Crear barra de menú con ayuda
        self.create_menu()
        
        # Crear pestañas principales
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Pestaña de bienvenida y conceptos básicos - CON SCROLL
        self.welcome_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.welcome_tab, text="Introducción")
        # Añadir canvas con scrollbar para la pestaña de bienvenida
        self.setup_scrollable_frame(self.welcome_tab, self.setup_welcome_tab)
        
        # Pestaña de configuración - CON SCROLL
        self.config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.config_tab, text="Mi Bicicleta")
        self.setup_scrollable_frame(self.config_tab, self.setup_config_tab)
        
        # Pestaña de visualización - CON SCROLL
        self.visual_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.visual_tab, text="Visualización")
        # El contenido se añadirá después con visualize_bike()
        
        # Pestaña de recomendaciones - CON SCROLL
        self.recom_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.recom_tab, text="¿Qué marcha usar?")
        self.setup_scrollable_frame(self.recom_tab, self.setup_recom_tab)
        
        # Pestaña de análisis técnico - CON SCROLL
        self.tech_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tech_tab, text="Análisis Técnico")
        self.setup_scrollable_frame(self.tech_tab, self.setup_tech_tab)
        
        # Inicialmente ocultar la pestaña técnica en modo principiante
        self.cambiar_modo()
    
    def cambiar_modo(self):
        """Cambia entre modo principiante y modo deportivo/técnico"""
        if self.modo_tecnico.get():
            # Cambiar a modo técnico
            self.notebook.tab(4, state="normal")  # Mostrar pestaña técnica
            # Actualizar visualizaciones y recomendaciones si ya existen datos
            if self.crankset_teeth and self.cassette_teeth:
                self.visualize_bike()
                # Actualizar pestaña técnica
                self.update_tech_tab()
        else:
            # Cambiar a modo principiante
            self.notebook.tab(4, state="hidden")  # Ocultar pestaña técnica
    
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # Menú de ayuda
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Conceptos básicos", command=self.show_basic_concepts)
        help_menu.add_command(label="Cómo usar la app", command=self.show_app_help)
        help_menu.add_command(label="Acerca de", command=self.show_about)
        
        menu_bar.add_cascade(label="Ayuda", menu=help_menu)
        self.root.config(menu=menu_bar)
    
    def setup_welcome_tab(self, parent):
        # Título
        ttk.Label(parent, text="Ñu-sui: ¡Aprende a usar las marchas de tu bicicleta!", 
                 font=("Arial", 16, "bold")).pack(pady=LARGE_PADDING)
        
        # Explicación simple
        intro_text = """
        ¡POR FAVOR! Si te gusta la aplicación, toda donación es bienvenida.
        Esto es parte de un proyecto personal, sin fines de lucro.

        Puedes donar vía PayPal: https://paypal.me/gimondragon?country.x=MX&locale.x=es_XC
        Código hecho originalmente por: Gustavo Mondragón. Puedes seguirme en redes:
        - Twitter/X: @GustavMondragon
        - Instagram: @gmondragons
        
        ¡Hola! Esta app te ayudará a comprender cómo usar las velocidades de tu bicicleta.
        
        Aprender a usar bien las marchas te permitirá:
        • Pedalear con menos esfuerzo
        • Mantener una velocidad cómoda
        • Subir pendientes más fácilmente
        • Evitar el desgaste prematuro de tu bicicleta
        
        Es como elegir la marcha correcta en un coche, pero para tu bicicleta.
        """
        
        intro_label = scrolledtext.ScrolledText(parent, wrap=tk.WORD, width=70, height=10)
        intro_label.pack(pady=PADDING, padx=LARGE_PADDING)
        intro_label.insert(tk.END, intro_text)
        intro_label.config(state="disabled")
        
        # Imágenes explicativas (se deben agregar imágenes reales)
        concepts_frame = ttk.LabelFrame(parent, text="Conceptos básicos")
        concepts_frame.pack(fill="both", expand=True, padx=LARGE_PADDING, pady=PADDING)
        
        # Aquí agregaríamos imágenes con explicaciones
        # Por ahora usaremos solo texto como ejemplo
        
        basic_concepts = [
            {
                "title": "¿Qué son las marchas?",
                "text": "Las marchas son combinaciones de 'platos' (adelante) y 'piñones' (atrás) que determinan cuánto avanza tu bicicleta con cada pedalada."
            },
            {
                "title": "Platos (adelante)",
                "text": "Son los discos dentados unidos a los pedales. Los más grandes son para ir rápido en terreno plano, los más pequeños para subir cuestas."
            },
            {
                "title": "Piñones (atrás)",
                "text": "Son los discos dentados en la rueda trasera. Los más pequeños son para velocidad, los más grandes para facilitar el pedaleo en subidas."
            },
            {
                "title": "Cadencia",
                "text": "Es la velocidad a la que pedaleas (revoluciones por minuto). Lo ideal es mantener entre 70-90 RPM para la mayoría de ciclistas."
            }
        ]
        
        for i, concept in enumerate(basic_concepts):
            frame = ttk.Frame(concepts_frame)
            frame.grid(row=i//2, column=i%2, padx=LARGE_PADDING, pady=PADDING, sticky="nsew")
            
            ttk.Label(frame, text=concept["title"], font=("Arial", 12, "bold")).pack(anchor="w")
            ttk.Label(frame, text=concept["text"], wraplength=400).pack(anchor="w", pady=PADDING)
        
        # Botón para comenzar
        ttk.Button(parent, text="¡Vamos a configurar mi bicicleta!", 
                  command=lambda: self.notebook.select(1)).pack(pady=LARGE_PADDING)
    
    def setup_config_tab(self, parent):
        # Título
        ttk.Label(parent, text="Configuración de tu bicicleta", 
                 font=("Arial", 14, "bold")).pack(pady=PADDING)
        
        # Explicación
        ttk.Label(parent, text="Vamos a configurar tu bicicleta paso a paso. Si no sabes algún dato, puedes usar los valores predeterminados.",
                 wraplength=800).pack(pady=PADDING)
        
        # Panel principal
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=LARGE_PADDING, pady=PADDING)
        
        # Panel izquierdo - Selección de tipo de bicicleta
        left_frame = ttk.LabelFrame(main_frame, text="Tipo de bicicleta")
        left_frame.pack(side="left", fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        ttk.Label(left_frame, text="Selecciona el tipo de bicicleta que tienes:").pack(pady=PADDING)
        
        # Variables para tipo de bicicleta
        self.bike_type_var = tk.StringVar(value="mtb")
        
        # Opciones de tipo con imágenes y configuraciones predefinidas
        bike_types = [
            {"name": "MTB (Montaña)", "value": "mtb", "platos": [24, 34, 42], "piñones": [14, 16, 18, 20, 22, 24, 34]},
            {"name": "Carretera", "value": "road", "platos": [34, 50], "piñones": [14, 16, 18, 20, 22, 24, 28]},
            {"name": "Urbana/Paseo", "value": "urban", "platos": [24, 34, 42], "piñones": [14, 16, 18, 20, 22, 24, 28]},
            {"name": "Personalizada", "value": "custom", "platos": [], "piñones": []}
        ]
        
        for bike in bike_types:
            ttk.Radiobutton(left_frame, text=bike["name"], value=bike["value"], 
                          variable=self.bike_type_var,
                          command=lambda b=bike: self.select_bike_type(b)).pack(anchor="w", pady=PADDING, padx=LARGE_PADDING)
        
        # Panel derecho - Configuración detallada
        self.right_frame = ttk.LabelFrame(main_frame, text="Configuración detallada")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Selección de tamaño de rueda
        ttk.Label(self.right_frame, text="Tamaño de rueda:").pack(anchor="w", pady=PADDING)
        self.wheel_size_var = tk.StringVar(value="26x2.1")  # Valor predeterminado
        
        # Agrupar tamaños de rueda por categorías para facilitar la selección
        wheel_categories = {
            "MTB": ["26x1.95", "26x2.1", "26x2.35", "27.5x2.10", "27.5x2.25", "29x2.1", "29x2.25"],
            "Carretera": ["700x23C", "700x25C", "700x28C", "700C"],
            "Urbana": ["700x35C", "700x38C", "700x40C", "26x1.75"],
            "Personalizada": list(wheel_sizes.keys())  # Use all available wheel sizes from the dictionary
        }
        
        self.wheel_combo = ttk.Combobox(self.right_frame, textvariable=self.wheel_size_var, width=30)
        self.wheel_combo.pack(anchor="w", pady=PADDING, padx=LARGE_PADDING)
        
        # Actualizar las opciones de rueda según el tipo de bicicleta seleccionado
        self.wheel_combo['values'] = wheel_categories["MTB"]  # Valor predeterminado
        
        # Cadencia predeterminada
        ttk.Label(self.right_frame, text="Cadencia habitual (pedaladas por minuto):").pack(anchor="w", pady=PADDING)
        self.cadencia_var = tk.StringVar(value=str(DEFAULT_CADENCE))  # Valor predeterminado para principiantes
        
        cadencia_frame = ttk.Frame(self.right_frame)
        cadencia_frame.pack(anchor="w", fill="x", pady=PADDING, padx=LARGE_PADDING)
        
        ttk.Scale(cadencia_frame, from_=MIN_CADENCE, to=MAX_CADENCE, orient="horizontal", 
                variable=self.cadencia_var, length=200,
                command=lambda s: self.cadencia_var.set(str(int(float(s))))).pack(side="left")
        
        ttk.Label(cadencia_frame, textvariable=self.cadencia_var).pack(side="left", padx=PADDING)
        ttk.Label(cadencia_frame, text="RPM").pack(side="left")
        
        # Explicación de cadencia
        cadencia_info = ttk.Label(self.right_frame, text="Una cadencia de 70-90 RPM es adecuada para la mayoría de ciclistas.", 
                               font=("Arial", 9, "italic"))
        cadencia_info.pack(anchor="w", padx=LARGE_PADDING)
        
        # Botón para configurar manualmente
        self.manual_config_button = ttk.Button(self.right_frame, text="Configurar manualmente",
                                            command=self.setup_custom_gears)
        self.manual_config_button.pack(anchor="w", pady=LARGE_PADDING, padx=LARGE_PADDING)
        
        # Botón para visualizar
        self.visualize_button = ttk.Button(parent, text="Visualizar mi bicicleta", 
                                        command=self.visualize_bike)
        self.visualize_button.pack(pady=LARGE_PADDING)
        
        # Seleccionar tipo MTB por defecto
        self.select_bike_type(bike_types[0])

    @handle_errors
    def setup_custom_gears(self):
        """Abre una ventana emergente para configurar manualmente los platos y piñones"""
        custom_window = tk.Toplevel(self.root)
        custom_window.title("Configuración manual de marchas")
        custom_window.geometry("500x400")
        custom_window.grab_set()  # Modal window
        
        ttk.Label(custom_window, text="Configura los dientes de platos y piñones", 
                 font=("Arial", 12, "bold")).pack(pady=PADDING)
        
        # Frame principal con dos columnas
        main_frame = ttk.Frame(custom_window)
        main_frame.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Columna izquierda - Platos
        left_frame = ttk.LabelFrame(main_frame, text="Platos (delanteros)")
        left_frame.pack(side="left", fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        ttk.Label(left_frame, text="Introduce el número de dientes separados por comas:").pack(pady=PADDING)
        
        # Valores por defecto si ya existe configuración
        platos_default = ",".join(map(str, self.crankset_teeth)) if self.crankset_teeth else ""
        self.platos_entry = ttk.Entry(left_frame)
        self.platos_entry.pack(padx=PADDING, pady=PADDING, fill="x")
        self.platos_entry.insert(0, platos_default)
        
        ttk.Label(left_frame, text="Ejemplo: 24,34,42 para triple plato\no 34,50 para doble plato", 
                 font=("Arial", 9, "italic")).pack(pady=PADDING)
        
        # Columna derecha - Piñones
        right_frame = ttk.LabelFrame(main_frame, text="Piñones (traseros)")
        right_frame.pack(side="right", fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        ttk.Label(right_frame, text="Introduce el número de dientes separados por comas:").pack(pady=PADDING)
        
        # Valores por defecto si ya existe configuración
        piñones_default = ",".join(map(str, self.cassette_teeth)) if self.cassette_teeth else ""
        self.piñones_entry = ttk.Entry(right_frame)
        self.piñones_entry.pack(padx=PADDING, pady=PADDING, fill="x")
        self.piñones_entry.insert(0, piñones_default)
        
        ttk.Label(right_frame, text="Ejemplo: 11,12,14,16,18,21,24,28,32,36\npara un cassette de 10 velocidades", 
                 font=("Arial", 9, "italic")).pack(pady=PADDING)
        
        # Botones de acción
        button_frame = ttk.Frame(custom_window)
        button_frame.pack(fill="x", padx=PADDING, pady=PADDING)
        
        ttk.Button(button_frame, text="Cancelar", 
                  command=custom_window.destroy).pack(side="left", padx=PADDING)
        
        ttk.Button(button_frame, text="Guardar configuración", 
                  command=lambda: self.save_custom_gears(custom_window)).pack(side="right", padx=PADDING)

    @handle_errors
    def save_custom_gears(self, window):
        """Guarda la configuración manual de marchas y cierra la ventana"""
        try:
            # Procesar platos
            platos_text = self.platos_entry.get().strip()
            if platos_text:
                self.crankset_teeth = [int(x.strip()) for x in platos_text.split(',')]
            else:
                self.crankset_teeth = []
                
            # Procesar piñones
            piñones_text = self.piñones_entry.get().strip()
            if piñones_text:
                self.cassette_teeth = [int(x.strip()) for x in piñones_text.split(',')]
            else:
                self.cassette_teeth = []
                
            # Validar configuración
            if not self.crankset_teeth or not self.cassette_teeth:
                raise ValueError("Debes configurar al menos un plato y un piñón")
                
            # Ordenar dientes de menor a mayor (piñones) y de mayor a menor (platos)
            self.cassette_teeth.sort()  # Menor a mayor para piñones
            self.crankset_teeth.sort(reverse=True)  # Mayor a menor para platos
            
            # Cerrar ventana
            window.destroy()
            messagebox.showinfo("Configuración guardada", "Configuración de marchas guardada correctamente")
            
        except ValueError as e:
            messagebox.showwarning("Error en configuración", str(e))
    
    @handle_errors
    def select_bike_type(self, bike_type: Dict[str, Union[str, List[int]]]) -> None:
        """
        Update bike configuration based on selected type
        
        Args:
            bike_type: Dictionary containing bike configuration
        """
        # Validate input
        required_keys = ["value", "platos", "piñones"]
        if not all(key in bike_type for key in required_keys):
            raise ValueError("Invalid bike type configuration")
            
        # Update values
        self.crankset_teeth = bike_type["platos"].copy()
        self.cassette_teeth = bike_type["piñones"].copy()
        
        # Ordenar dientes de menor a mayor (piñones) y de mayor a menor (platos)
        self.cassette_teeth.sort()  # Menor a mayor para piñones
        self.crankset_teeth.sort(reverse=True)  # Mayor a menor para platos
        
        # Update wheel options based on bike type
        wheel_options = {
            "mtb": ("26x2.1", ["26x2.1", "26x2.35", "27.5x2.10", "27.5x2.25", "29x2.1", "29x2.25", "29x2.3"]),
            "road": ("700x25C", ["700x23C", "700x25C", "700x28C", "700C"]),
            "urban": ("700x35C", ["700x35C", "700x38C", "700x40C", "26x1.75"]),
            "custom": ("700C", list(wheel_sizes.keys()))  # Add this line to include all wheel sizes for custom
        }
        
        bike_value = bike_type["value"]
        if bike_value in wheel_options:
            default_size, sizes = wheel_options[bike_value]
            self.wheel_combo['values'] = sizes
            self.wheel_size_var.set(default_size)
            
        # Handle custom configuration
        if bike_value == "custom":
            self.manual_config_button.state(['!disabled'])
            self.crankset_teeth = []
            self.cassette_teeth = []
        else:
            self.manual_config_button.state(['disabled'])

    @handle_errors
    def validate_gear_configuration(self) -> bool:
        """
        Validate the current gear configuration
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not self.crankset_teeth or not self.cassette_teeth:
            messagebox.showwarning(
                "Datos insuficientes",
                "Por favor, selecciona un tipo de bicicleta o configura manualmente."
            )
            return False
            
        # Validate teeth numbers
        try:
            for teeth in self.crankset_teeth + self.cassette_teeth:
                if not isinstance(teeth, int):
                    raise ValueError(f"Invalid teeth value: {teeth}")
                if not MIN_TEETH <= teeth <= MAX_TEETH:
                    raise ValueError(f"Teeth value out of range: {teeth}")
            return True
        except ValueError as e:
            messagebox.showwarning(
                "Configuración inválida",
                str(e)
            )
            return False

    @handle_errors
    def calculate_gear_ratio(self, chainring: int, sprocket: int) -> float:
        """
        Calculate gear ratio between chainring and sprocket
        
        Args:
            chainring (int): Number of teeth in the chainring
            sprocket (int): Number of teeth in the sprocket
            
        Returns:
            float: Gear ratio
        """
        if sprocket == 0:
            raise ValueError("Sprocket cannot have 0 teeth")
        return chainring / sprocket
        
    def is_chain_crossing(self, chainring_idx: int, sprocket_idx: int) -> Tuple[bool, Optional[str]]:
        """
        Determina si una combinación de plato y piñón cruza la cadena
        
        Args:
            chainring_idx: Índice del plato (0 para el más grande)
            sprocket_idx: Índice del piñón (0 para el más pequeño)
            
        Returns:
            bool: True si la combinación cruza la cadena, False en caso contrario
            str: Mensaje describiendo el problema, o None si no hay cruce
        """
        num_chainrings = len(self.crankset_teeth)
        num_sprockets = len(self.cassette_teeth)
        
        # Si solo hay un plato, no hay cruce posible
        if num_chainrings <= 1:
            return False, None
            
        # Debug info
        if hasattr(self, 'debug_var') and self.debug_var.get():
            print(f"Checking chain crossing for plato idx={chainring_idx} with piñón idx={sprocket_idx}")
            print(f"Platos={self.crankset_teeth}, Piñones={self.cassette_teeth}")
        
        # Ajustar la lógica de cruce de cadena según el número de platos y piñones
        if num_chainrings == 2:  # Doble plato
            # Para doble plato, considerar 35% de los piñones como extremos
            extreme_count = max(2, round(num_sprockets * 0.35))
            
            # Debug info
            if hasattr(self, 'debug_var') and self.debug_var.get():
                print(f"Doble plato: extreme_count={extreme_count}")
            
            # Plato grande con piñones grandes
            if chainring_idx == 0 and sprocket_idx >= num_sprockets - extreme_count:
                return True, "Plato grande con piñón grande: aumenta el desgaste y reduce la eficiencia"
            
            # Plato pequeño con piñones pequeños
            if chainring_idx == num_chainrings - 1 and sprocket_idx < extreme_count:
                return True, "Plato pequeño con piñón pequeño: aumenta el desgaste y reduce la eficiencia"
                
        elif num_chainrings == 3:  # Triple plato
            # Más restrictivo con triples: 40% de los piñones son extremos
            extreme_count_large = max(2, round(num_sprockets * 0.4))
            extreme_count_small = max(2, round(num_sprockets * 0.4))
            
            medium_extreme_large = max(1, round(num_sprockets * 0.15))
            medium_extreme_small = max(1, round(num_sprockets * 0.15))
            
            # Debug info
            if hasattr(self, 'debug_var') and self.debug_var.get():
                print(f"Triple plato: extreme_count_large={extreme_count_large}, "
                     f"extreme_count_small={extreme_count_small}, "
                     f"medium_extreme_large={medium_extreme_large}, "
                     f"medium_extreme_small={medium_extreme_small}")
            
            # Plato grande con piñones grandes
            if chainring_idx == 0 and sprocket_idx >= num_sprockets - extreme_count_large:
                return True, "Plato grande con piñón grande: aumenta el desgaste y reduce la eficiencia"
            
            # Plato pequeño con piñones pequeños
            if chainring_idx == num_chainrings - 1 and sprocket_idx < extreme_count_small:
                return True, "Plato pequeño con piñón pequeño: aumenta el desgaste y reduce la eficiencia"
            
            # Para el plato mediano, también hay restricciones pero menos severas
            if chainring_idx == 1 and (sprocket_idx >= num_sprockets - medium_extreme_large or 
                                    sprocket_idx < medium_extreme_small):
                return True, "Plato mediano con piñón extremo: puede causar desgaste"
        
        # Para otros casos (número de platos inusuales), usar una regla general
        else:
            # Regla general: 30% de los piñones en cada extremo
            extreme_count = max(1, round(num_sprockets * 0.3))
            
            # Plato grande con piñones grandes
            if chainring_idx == 0 and sprocket_idx >= num_sprockets - extreme_count:
                return True, "Plato grande con piñón grande: aumenta el desgaste y reduce la eficiencia"
            
            # Plato pequeño con piñones pequeños
            if chainring_idx == num_chainrings - 1 and sprocket_idx < extreme_count:
                return True, "Plato pequeño con piñón pequeño: aumenta el desgaste y reduce la eficiencia"
            
            # Para platos intermedios en configuraciones de más de 2 platos
            if len(self.crankset_teeth) > 2 and 0 < chainring_idx < len(self.crankset_teeth) - 1:
                # Solo los extremos para platos intermedios
                if sprocket_idx == 0 or sprocket_idx >= num_sprockets - 1:
                    return True, "Plato intermedio con piñón extremo: puede causar desgaste"
        
        return False, None
    
    @handle_errors
    def calculate_speed(self, gear_ratio: float, cadence: int) -> float:
        """Calculate speed in km/h"""
        wheel_circum = self.wheel_sizes[self.wheel_size_var.get()]
        return (gear_ratio * wheel_circum * cadence * 60) / 1000

    def calculate_power_estimate(self, speed: float, slope: float = 0.0) -> float:
        """Calculate estimated power output"""
        k = 0.004  # Simplified aerodynamic coefficient
        k_adjusted = k * (1 + slope/100)
        return k_adjusted * (speed ** 3)

    @handle_errors
    def visualize_bike(self):
        """Visualiza la configuración de la bicicleta y crea gráficos"""
        # Validar configuración
        if not self.validate_gear_configuration():
            return
            
        # Si el modo debug está activado, mostrar una tabla de cruce de cadena
        if self.debug_var.get():
            self.show_chain_crossing_debug()
        
        # Limpiar pestaña de visualización
        for widget in self.visual_tab.winfo_children():
            widget.destroy()
        
        # Crear un frame scrollable para la pestaña de visualización
        scrollable_frame = self.setup_scrollable_frame(self.visual_tab, None)
        
        # Obtener parámetros
        cadence = int(self.cadencia_var.get())
        wheel_size = self.wheel_size_var.get()
        
        # Crear estructura de pestañas para visualizaciones
        visual_notebook = ttk.Notebook(scrollable_frame)
        visual_notebook.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Pestaña de tabla de marchas
        table_tab = ttk.Frame(visual_notebook)
        visual_notebook.add(table_tab, text="Tabla de marchas")
        self.create_gear_table(table_tab, cadence)
        
        # Pestaña de gráfico de velocidades
        chart_tab = ttk.Frame(visual_notebook)
        visual_notebook.add(chart_tab, text="Gráfico de velocidades")
        self.create_speed_chart(chart_tab, cadence)
        
        # Pestaña de desarrollo
        dev_tab = ttk.Frame(visual_notebook)
        visual_notebook.add(dev_tab, text="Desarrollo")
        self.create_development_chart(dev_tab)
        
        # Actualizar pestaña de recomendaciones - recrear con scroll
        for widget in self.recom_tab.winfo_children():
            widget.destroy()
        self.setup_scrollable_frame(self.recom_tab, self.setup_recom_tab)
        
        # Actualizar pestaña técnica si estamos en modo técnico
        if self.modo_tecnico.get():
            for widget in self.tech_tab.winfo_children():
                widget.destroy()
            self.setup_scrollable_frame(self.tech_tab, self.setup_tech_tab)
        
        # Cambiar a pestaña de visualización
        self.notebook.select(2)  # Índice 2 = pestaña de visualización
        
    def show_chain_crossing_debug(self):
        """Muestra una ventana de debug con la matriz de cruce de cadena"""
        debug_window = tk.Toplevel(self.root)
        debug_window.title("Debug: Matriz de cruce de cadena")
        debug_window.geometry("700x500")
        
        # Frame con scroll para acomodar matrices más grandes
        canvas = tk.Canvas(debug_window)
        scrollbar = ttk.Scrollbar(debug_window, orient="vertical", command=canvas.yview)
        scrollbar_h = ttk.Scrollbar(debug_window, orient="horizontal", command=canvas.xview)
        
        frame = ttk.Frame(canvas)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        scrollbar_h.pack(side="bottom", fill="x")
        
        canvas.configure(yscrollcommand=scrollbar.set, xscrollcommand=scrollbar_h.set)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Título
        ttk.Label(frame, text="Matriz de cruce de cadena (X = cruce, O = seguro)", 
                 font=("Arial", 12, "bold")).pack(pady=PADDING)
        
        # Panel de información
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill="x", pady=PADDING)
        
        ttk.Label(info_frame, text=f"Platos: {self.crankset_teeth}", 
                font=("Arial", 10)).pack(anchor="w", pady=2)
        ttk.Label(info_frame, text=f"Piñones: {self.cassette_teeth}", 
                font=("Arial", 10)).pack(anchor="w", pady=2)
        
        # Mostrar parámetros usados para el cálculo según tipo de bicicleta
        if len(self.crankset_teeth) == 3:
            num_sprockets = len(self.cassette_teeth)
            extreme_count_large = max(2, round(num_sprockets * 0.4))
            extreme_count_small = max(2, round(num_sprockets * 0.4))
            medium_extreme_large = max(1, round(num_sprockets * 0.15))
            medium_extreme_small = max(1, round(num_sprockets * 0.15))
            
            ttk.Label(info_frame, text=f"Triple plato: Cruces en plato grande: {extreme_count_large} piñones grandes", 
                    font=("Arial", 9, "italic")).pack(anchor="w", pady=1)
            ttk.Label(info_frame, text=f"Triple plato: Cruces en plato pequeño: {extreme_count_small} piñones pequeños", 
                    font=("Arial", 9, "italic")).pack(anchor="w", pady=1)
            ttk.Label(info_frame, text=f"Triple plato: Cruces en plato mediano: {medium_extreme_small} piñones pequeños y {medium_extreme_large} piñones grandes", 
                    font=("Arial", 9, "italic")).pack(anchor="w", pady=1)
        elif len(self.crankset_teeth) == 2:
            num_sprockets = len(self.cassette_teeth)
            extreme_count = max(2, round(num_sprockets * 0.35))
            
            ttk.Label(info_frame, text=f"Doble plato: Cruces en plato grande: {extreme_count} piñones grandes", 
                    font=("Arial", 9, "italic")).pack(anchor="w", pady=1)
            ttk.Label(info_frame, text=f"Doble plato: Cruces en plato pequeño: {extreme_count} piñones pequeños", 
                    font=("Arial", 9, "italic")).pack(anchor="w", pady=1)
        
        # Crear tabla
        tabla_frame = ttk.Frame(frame)
        tabla_frame.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Encabezados de columna (piñones)
        ttk.Label(tabla_frame, text="Plato\\Piñón", width=10, 
                 font=("Arial", 10, "bold")).grid(row=0, column=0, padx=2, pady=2)
        
        for j, piñon in enumerate(self.cassette_teeth):
            ttk.Label(tabla_frame, text=f"{piñon}T", width=6, 
                     font=("Arial", 10, "bold")).grid(row=0, column=j+1, padx=2, pady=2)
        
        # Filas (platos)
        for i, plato in enumerate(self.crankset_teeth):
            ttk.Label(tabla_frame, text=f"{plato}T", width=10, 
                     font=("Arial", 10, "bold")).grid(row=i+1, column=0, padx=2, pady=2)
            
            for j in range(len(self.cassette_teeth)):
                # Calcular cruce directamente
                crossing, _ = self.is_chain_crossing(i, j)
                
                text = "X" if crossing else "O"
                
                # Usar Frame coloreado con Label dentro
                cell_frame = ttk.Frame(tabla_frame, width=50, height=30)
                cell_frame.grid(row=i+1, column=j+1, padx=2, pady=2)
                cell_frame.grid_propagate(False)  # Mantener tamaño
                
                if crossing:
                    label = ttk.Label(cell_frame, text=text, font=("Arial", 10, "bold"), foreground="red")
                else:
                    label = ttk.Label(cell_frame, text=text, font=("Arial", 10, "bold"), foreground="green")
                    
                label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Panel de explicación
        explanation = """
        Esta matriz muestra qué combinaciones de plato y piñón causan 'cruce de cadena'.
        
        Las combinaciones marcadas con X deben evitarse durante periodos prolongados porque:
        - Aumentan el desgaste de la cadena, platos, piñones y desviador
        - Reducen la eficiencia de pedaleo
        - Aumentan el riesgo de que la cadena se salga o se dañe
        
        Reglas generales:
        - Para plato grande: evitar piñones grandes
        - Para plato pequeño: evitar piñones pequeños
        - Para plato mediano: evitar los piñones extremos
        """
        
        explanation_frame = ttk.LabelFrame(frame, text="Explicación")
        explanation_frame.pack(fill="x", padx=PADDING, pady=PADDING)
        
        ttk.Label(explanation_frame, text=explanation, justify="left", wraplength=650).pack(padx=PADDING, pady=PADDING)
        
        # Botón para cerrar
        ttk.Button(frame, text="Cerrar", 
                  command=debug_window.destroy).pack(pady=PADDING)

    @handle_errors
    def create_gear_table(self, parent, cadence):
        """Crea una tabla con todas las marchas y sus velocidades, ocultando cruces de cadena"""
        # Frame contenedor con scroll
        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Crear un título explicativo
        ttk.Label(container, text=f"Velocidades estimadas (km/h) a {cadence} RPM", 
                 font=("Arial", 12, "bold")).pack(pady=PADDING)
        
        # Crear tabla con treeview
        columns = ["Plato"] + [f"{teeth}" for teeth in self.cassette_teeth]
        
        tree = ttk.Treeview(container, columns=columns, show="headings", height=len(self.crankset_teeth))
        tree.pack(fill="both", expand=True)
        
        # Configurar columnas
        tree.heading("Plato", text="Plato")
        for teeth in self.cassette_teeth:
            tree.heading(f"{teeth}", text=f"{teeth}")
            tree.column(f"{teeth}", width=60, anchor="center")
        
        # Contador de combinaciones con cruce de cadena
        crossing_count = 0
        total_combinations = len(self.crankset_teeth) * len(self.cassette_teeth)
        
        # Llenar tabla con velocidades
        for i, chainring in enumerate(self.crankset_teeth):
            row_values = [f"{chainring}T"]
            for j, sprocket in enumerate(self.cassette_teeth):
                gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
                speed = self.calculate_speed(gear_ratio, cadence)
                
                # Comprobar si esta combinación cruza la cadena
                crossing, _ = self.is_chain_crossing(i, j)
                
                if crossing:
                    # Marcar celdas con cruce de cadena
                    row_values.append("---")
                    crossing_count += 1
                else:
                    row_values.append(f"{speed:.1f}")
            
            tree.insert("", "end", values=row_values)
        
        # Añadir leyenda
        ttk.Label(container, text="Las velocidades están calculadas con el tamaño de rueda: " + 
                 f"{self.wheel_size_var.get()} ({self.wheel_sizes[self.wheel_size_var.get()]}m de circunferencia)",
                 font=("Arial", 9, "italic")).pack(pady=(PADDING, 0))
        
        # Añadir aviso sobre cruce de cadena
        warning_frame = ttk.Frame(container)
        warning_frame.pack(fill="x", pady=PADDING)
        
        warning_icon = ttk.Label(warning_frame, text="⚠️", font=("Arial", 12))
        warning_icon.pack(side="left", padx=(0, PADDING))
        
        warning_text = f"No se muestran las velocidades para {crossing_count} de {total_combinations} combinaciones porque causan 'cruce de cadena', "
        warning_text += "lo que aumenta el desgaste de los componentes y reduce la eficiencia. "
        warning_text += "Estas combinaciones están marcadas con '---'."
        
        warning_label = ttk.Label(warning_frame, text=warning_text, 
                                wraplength=600, justify="left")
        warning_label.pack(side="left", fill="x", expand=True)

    @handle_errors
    def create_speed_chart(self, parent, cadence):
        """Crea un gráfico de líneas con las velocidades para cada marcha, indicando cruces de cadena"""
        # Crear figura
        fig, ax = plt.subplots(figsize=CHART_SIZE)
        
        # Preparar datos
        for i, chainring in enumerate(self.crankset_teeth):
            speeds = []
            crosses = []  # Para marcar los puntos que cruzan la cadena
            
            for j, sprocket in enumerate(self.cassette_teeth):
                gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
                speed = self.calculate_speed(gear_ratio, cadence)
                speeds.append(speed)
                
                # Verificar si esta combinación cruza la cadena
                crossing, _ = self.is_chain_crossing(i, j)
                crosses.append(crossing)
            
            # Graficar línea principal (todos los puntos)
            line, = ax.plot(self.cassette_teeth, speeds, '-', color=f'C{i}', label=f"Plato {chainring}T")
            
            # Añadir puntos "seguros" (sin cruce) en color sólido
            safe_x = [self.cassette_teeth[j] for j in range(len(self.cassette_teeth)) if not crosses[j]]
            safe_y = [speeds[j] for j in range(len(speeds)) if not crosses[j]]
            ax.plot(safe_x, safe_y, 'o', color=f'C{i}')
            
            # Añadir puntos "peligrosos" (con cruce) en otro estilo
            cross_x = [self.cassette_teeth[j] for j in range(len(self.cassette_teeth)) if crosses[j]]
            cross_y = [speeds[j] for j in range(len(speeds)) if crosses[j]]
            if cross_x:  # Solo si hay puntos peligrosos
                ax.plot(cross_x, cross_y, 'x', color=f'C{i}', markersize=8, alpha=0.7)
        
        # Configurar gráfico
        ax.set_xlabel('Dientes del piñón')
        ax.set_ylabel('Velocidad (km/h)')
        ax.set_title(f'Velocidades a {cadence} RPM')
        ax.grid(True)
        ax.legend()
        
        # Si estamos en modo principiante, simplificar el gráfico
        if not self.modo_tecnico.get():
            ax.set_xlabel('Piñones (de más rápido a más fácil)')
            # Simplificar etiquetas del eje X
            ax.set_xticks(range(len(self.cassette_teeth)))
            ax.set_xticklabels([f"{i+1}" for i in range(len(self.cassette_teeth))])
        
        # Crear canvas para mostrar el gráfico
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Añadir leyenda para cruces de cadena
        legend_frame = ttk.Frame(parent)
        legend_frame.pack(fill="x", pady=PADDING)
        
        ttk.Label(legend_frame, text="○ = Combinaciones seguras", font=("Arial", 9)).pack(side="left", padx=PADDING)
        ttk.Label(legend_frame, text="✕ = Combinaciones con cruce de cadena (evitar)", font=("Arial", 9)).pack(side="left", padx=PADDING)

    @handle_errors
    def create_development_chart(self, parent):
        """Crea un gráfico de barras con el desarrollo de cada marcha, marcando cruces de cadena"""
        # Frame con explicación
        ttk.Label(parent, text="Desarrollo de marchas", 
                 font=("Arial", 12, "bold")).pack(pady=PADDING)
        
        ttk.Label(parent, text="El desarrollo indica la distancia recorrida en metros por cada pedalada completa.",
                 wraplength=800).pack(pady=PADDING)
        
        # Crear figura
        fig, ax = plt.subplots(figsize=CHART_SIZE)
        
        # Definir colores para cada plato
        color_map = {
            0: 'red',      # Primer plato (más grande)
            1: 'blue',     # Segundo plato
            2: 'green'     # Tercer plato (si existe)
        }
        
        # Para almacenar los datos de desarrollo por plato
        width = 0.8 / len(self.crankset_teeth)  # Ancho de barra ajustado según número de platos
        
        # Para cada plato, crear un conjunto de barras
        for i, chainring in enumerate(self.crankset_teeth):
            developments = []
            safe_markers = []  # Para marcar combinaciones seguras y cruces
            
            for j, sprocket in enumerate(self.cassette_teeth):
                gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
                development = gear_ratio * self.wheel_sizes[self.wheel_size_var.get()]
                developments.append(development)
                
                # Verificar cruce de cadena
                crossing, _ = self.is_chain_crossing(i, j)
                safe_markers.append(not crossing)  # True si es seguro, False si hay cruce
            
            # Posición de las barras para este plato
            bar_positions = [j + width*i for j in range(len(self.cassette_teeth))]
            
            # Crear barras para combinaciones seguras (sin cruce)
            safe_dev = [dev if safe else 0 for dev, safe in zip(developments, safe_markers)]
            ax.bar(bar_positions, safe_dev, width=width, color=color_map.get(i, 'gray'), 
                  label=f"Plato {chainring}T")
            
            # Crear barras para combinaciones con cruce (hatched pattern)
            cross_dev = [dev if not safe else 0 for dev, safe in zip(developments, safe_markers)]
            if any(cross_dev):  # Solo si hay alguna barra con cruce
                ax.bar(bar_positions, cross_dev, width=width, color=color_map.get(i, 'gray'), 
                      alpha=0.5, hatch='xxx')
        
        # Configurar eje X
        ax.set_xticks(range(len(self.cassette_teeth)))
        ax.set_xticklabels([f"{sprocket}T" for sprocket in self.cassette_teeth])
        
        # Configurar etiquetas y título
        ax.set_xlabel('Dientes del piñón')
        ax.set_ylabel('Desarrollo (metros/pedalada)')
        ax.set_title('Desarrollo por plato')
        ax.legend()
        
        # Ajustar layout
        fig.tight_layout()
        
        # Crear canvas para mostrar el gráfico
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Añadir leyenda para interpretar el gráfico
        note_frame = ttk.Frame(parent)
        note_frame.pack(fill="x", pady=PADDING)
        
        note_text = """
        • Las barras sólidas representan combinaciones seguras.
        • Las barras con patrón (xxx) y semitransparentes representan combinaciones con cruce de cadena.
        • Mayor desarrollo = mayor distancia recorrida por pedalada (más "duro" de pedalear).
        • Menor desarrollo = menor distancia recorrida por pedalada (más "ligero" de pedalear).
        """
        
        note_label = ttk.Label(note_frame, text=note_text, wraplength=800, justify="left")
        note_label.pack(fill="x", expand=True, padx=PADDING)
        
        # Añadir aviso sobre cruce de cadena
        warning_frame = ttk.Frame(parent)
        warning_frame.pack(fill="x", pady=PADDING)
        
        warning_icon = ttk.Label(warning_frame, text="⚠️", font=("Arial", 12))
        warning_icon.pack(side="left", padx=(0, PADDING))
        
        warning_text = "Las combinaciones marcadas con patrones (xxx) causan 'cruce de cadena', "
        warning_text += "lo que aumenta el desgaste de los componentes y reduce la eficiencia. "
        warning_text += "Se recomienda evitar estas combinaciones durante periodos prolongados."
        
        warning_label = ttk.Label(warning_frame, text=warning_text, 
                                wraplength=800, justify="left")
        warning_label.pack(side="left", fill="x", expand=True)

    @handle_errors
    def setup_recom_tab(self, parent):
        """Configura la pestaña de recomendaciones"""
        # Si no hay configuración, mostrar mensaje
        if not self.crankset_teeth or not self.cassette_teeth:
            ttk.Label(parent, text="Por favor, configura tu bicicleta primero en la pestaña 'Mi Bicicleta'",
                     font=("Arial", 12)).pack(pady=LARGE_PADDING)
            return
        
        # Crear título
        ttk.Label(parent, text="¿Qué marcha debo usar?", 
                 font=("Arial", 14, "bold")).pack(pady=PADDING)
        
        # Panel principal
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=LARGE_PADDING, pady=PADDING)
        
        # Panel izquierdo - Formulario
        form_frame = ttk.LabelFrame(main_frame, text="¿Cómo es tu ruta?")
        form_frame.pack(side="left", fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Velocidad deseada
        ttk.Label(form_frame, text="Velocidad deseada (km/h):").pack(anchor="w", pady=PADDING)
        
        self.target_speed_var = tk.StringVar(value="20")
        speed_frame = ttk.Frame(form_frame)
        speed_frame.pack(fill="x", pady=PADDING, padx=LARGE_PADDING)
        
        ttk.Scale(speed_frame, from_=5, to=50, orient="horizontal", 
                 variable=self.target_speed_var, length=200,
                 command=lambda s: self.target_speed_var.set(str(int(float(s))))).pack(side="left")
        
        ttk.Label(speed_frame, textvariable=self.target_speed_var).pack(side="left", padx=PADDING)
        ttk.Label(speed_frame, text="km/h").pack(side="left")
        
        # Pendiente
        ttk.Label(form_frame, text="Pendiente (%):").pack(anchor="w", pady=PADDING)
        
        self.slope_var = tk.StringVar(value="0")
        slope_frame = ttk.Frame(form_frame)
        slope_frame.pack(fill="x", pady=PADDING, padx=LARGE_PADDING)
        
        ttk.Scale(slope_frame, from_=-10, to=20, orient="horizontal", 
                 variable=self.slope_var, length=200,
                 command=lambda s: self.slope_var.set(str(int(float(s))))).pack(side="left")
        
        ttk.Label(slope_frame, textvariable=self.slope_var).pack(side="left", padx=PADDING)
        ttk.Label(slope_frame, text="%").pack(side="left")
        
        # Descripción de pendiente
        slope_desc = ttk.Label(form_frame, text="0% = terreno plano, valores positivos = subida, negativos = bajada", 
                             font=("Arial", 9, "italic"))
        slope_desc.pack(anchor="w", padx=LARGE_PADDING)
        
        # Botón para calcular
        ttk.Button(form_frame, text="Calcular marcha recomendada", 
                  command=self.calculate_recommended_gear).pack(pady=LARGE_PADDING)
        
        # Panel derecho - Resultados
        self.results_frame = ttk.LabelFrame(main_frame, text="Recomendación")
        self.results_frame.pack(side="right", fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Mensaje inicial
        ttk.Label(self.results_frame, text="Completa el formulario y pulsa 'Calcular' para obtener\nuna recomendación de marcha.",
                 wraplength=400).pack(pady=LARGE_PADDING)

    @handle_errors
    def calculate_recommended_gear(self):
        """Calcula y muestra la marcha recomendada según los parámetros, evitando cruces de cadena"""
        # Limpiar panel de resultados
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Obtener parámetros
        target_speed = float(self.target_speed_var.get())
        slope = float(self.slope_var.get())
        cadence = int(self.cadencia_var.get())
        
        # Calcular todas las marchas y sus velocidades, evitando cruces de cadena
        best_chainring = None
        best_sprocket = None
        min_diff = float('inf')
        
        for i, chainring in enumerate(self.crankset_teeth):
            for j, sprocket in enumerate(self.cassette_teeth):
                # Verificar si esta combinación cruza la cadena
                crossing, _ = self.is_chain_crossing(i, j)
                if crossing:
                    continue  # Saltar esta combinación
                
                gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
                speed = self.calculate_speed(gear_ratio, cadence)
                
                # Ajustar velocidad según pendiente (simplificación)
                adjusted_speed = speed * (1 - slope/100 * 0.1)
                
                # Encontrar la marcha más cercana a la velocidad deseada
                diff = abs(adjusted_speed - target_speed)
                if diff < min_diff:
                    min_diff = diff
                    best_chainring = chainring
                    best_sprocket = sprocket
        
        # Si no encontramos ninguna marcha válida (todas cruzan la cadena), buscar la menor diferencia sin importar cruces
        if best_chainring is None:
            min_diff = float('inf')
            for i, chainring in enumerate(self.crankset_teeth):
                for j, sprocket in enumerate(self.cassette_teeth):
                    gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
                    speed = self.calculate_speed(gear_ratio, cadence)
                    
                    # Ajustar velocidad según pendiente
                    adjusted_speed = speed * (1 - slope/100 * 0.1)
                    
                    diff = abs(adjusted_speed - target_speed)
                    if diff < min_diff:
                        min_diff = diff
                        best_chainring = chainring
                        best_sprocket = sprocket
                        best_i = i
                        best_j = j
            
            # Verificar si la mejor opción cruza la cadena
            crossing, crossing_message = self.is_chain_crossing(best_i, best_j)
        else:
            crossing = False
            crossing_message = None
        
        # Mostrar recomendación
        if best_chainring and best_sprocket:
            gear_ratio = self.calculate_gear_ratio(best_chainring, best_sprocket)
            actual_speed = self.calculate_speed(gear_ratio, cadence)
            
            # Título con recomendación
            ttk.Label(self.results_frame, text=f"Marcha recomendada: {best_chainring}T / {best_sprocket}T", 
                     font=("Arial", 14, "bold")).pack(pady=PADDING)
            
            # Explicación visual (simple)
            plato_idx = self.crankset_teeth.index(best_chainring) + 1
            piñon_idx = self.cassette_teeth.index(best_sprocket) + 1
            
            if len(self.crankset_teeth) == 3:  # Triple plato
                plato_desc = "pequeño" if plato_idx == 3 else ("mediano" if plato_idx == 2 else "grande")
            elif len(self.crankset_teeth) == 2:  # Doble plato
                plato_desc = "pequeño" if plato_idx == 2 else "grande"
            else:
                plato_desc = f"#{plato_idx}"
                
            ttk.Label(self.results_frame, text=f"Usa el plato {plato_desc} (de {len(self.crankset_teeth)}) y el piñón #{piñon_idx} (de {len(self.cassette_teeth)})",
                     wraplength=400).pack(pady=PADDING)
            
            # Detalles técnicos
            details_frame = ttk.Frame(self.results_frame)
            details_frame.pack(fill="x", pady=PADDING)
            
            ttk.Label(details_frame, text=f"Velocidad estimada:").grid(row=0, column=0, sticky="w", padx=PADDING)
            ttk.Label(details_frame, text=f"{actual_speed:.1f} km/h").grid(row=0, column=1, sticky="e")
            
            ttk.Label(details_frame, text=f"Relación de marchas:").grid(row=1, column=0, sticky="w", padx=PADDING)
            ttk.Label(details_frame, text=f"{gear_ratio:.2f}").grid(row=1, column=1, sticky="e")
            
            ttk.Label(details_frame, text=f"Desarrollo:").grid(row=2, column=0, sticky="w", padx=PADDING)
            development = gear_ratio * self.wheel_sizes[self.wheel_size_var.get()]
            ttk.Label(details_frame, text=f"{development:.2f} metros/pedalada").grid(row=2, column=1, sticky="e")
            
            # Mostrar advertencia si cruza la cadena
            if crossing:
                warning_frame = ttk.Frame(self.results_frame)
                warning_frame.pack(fill="x", pady=PADDING)
                
                warning_icon = ttk.Label(warning_frame, text="⚠️", font=("Arial", 12), foreground="red")
                warning_icon.pack(side="left", padx=(0, PADDING))
                
                warning_text = "ADVERTENCIA: Esta combinación cruza la cadena. "
                warning_text += "No se encontró ninguna combinación óptima que no cruce la cadena para la velocidad y pendiente indicadas. "
                warning_text += "Se recomienda usar esta marcha solo brevemente y ajustar la velocidad objetivo."
                
                warning_label = ttk.Label(warning_frame, text=warning_text, 
                                       wraplength=400, foreground="red", justify="left")
                warning_label.pack(side="left")
            
            # Consejos según pendiente
            if slope > 8:
                advice = "Para pendientes pronunciadas, mantén una cadencia alta y usa marchas más ligeras para no forzar las rodillas."
            elif slope > 0:
                advice = "Mantén una cadencia constante. Si sientes que haces demasiada fuerza, cambia a una marcha más ligera."
            elif slope < -5:
                advice = "En descensos, puedes usar marchas más duras o directamente dejar de pedalear si la velocidad es elevada."
            else:
                advice = "En llano, busca mantener una cadencia cómoda (80-90 RPM) y ajusta la marcha según el viento y tu estado físico."
            
            ttk.Label(self.results_frame, text="Consejo:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(PADDING, 0))
            ttk.Label(self.results_frame, text=advice, wraplength=400).pack(anchor="w", padx=PADDING)

    @handle_errors
    def setup_tech_tab(self, parent):
        """Configura la pestaña de análisis técnico"""
        # Título
        ttk.Label(parent, text="Análisis Técnico", 
                 font=("Arial", 14, "bold")).pack(pady=PADDING)
        
        # Explicación
        ttk.Label(parent, text="Esta pestaña contiene análisis técnicos para ciclistas experimentados.",
                 wraplength=800).pack(pady=PADDING)
        
        # Si no hay configuración, mostrar mensaje
        if not self.crankset_teeth or not self.cassette_teeth:
            ttk.Label(parent, text="Por favor, configura tu bicicleta primero en la pestaña 'Mi Bicicleta'",
                     font=("Arial", 12)).pack(pady=LARGE_PADDING)
            return
        
        # Crear notebook para técnicas de análisis
        tech_notebook = ttk.Notebook(parent)
        tech_notebook.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Pestaña de relación de marchas
        ratio_tab = ttk.Frame(tech_notebook)
        tech_notebook.add(ratio_tab, text="Relación de marchas")
        
        # Pestaña de cadencia vs potencia
        power_tab = ttk.Frame(tech_notebook)
        tech_notebook.add(power_tab, text="Cadencia vs Potencia")
        
        # Pestaña de overlap (solapamiento de marchas)
        overlap_tab = ttk.Frame(tech_notebook)
        tech_notebook.add(overlap_tab, text="Solapamiento")
        
        # Configurar cada pestaña técnica
        self.setup_ratio_tab(ratio_tab)
        self.setup_power_tab(power_tab)
        self.setup_overlap_tab(overlap_tab)

    @handle_errors
    def setup_ratio_tab(self, parent):
        """Configura la pestaña técnica de relación de marchas"""
        # Crear título
        ttk.Label(parent, text="Análisis de relación de marchas", 
                 font=("Arial", 12, "bold")).pack(pady=PADDING)
        
        # Crear gráfico
        fig, ax = plt.subplots(figsize=CHART_SIZE)
        
        # Preparar datos
        combinations = []
        ratios = []
        colors = []
        
        color_map = {
            0: 'red',      # Primer plato (más grande)
            1: 'blue',     # Segundo plato
            2: 'green'     # Tercer plato (si existe)
        }
        
        for i, chainring in enumerate(self.crankset_teeth):
            for sprocket in self.cassette_teeth:
                combinations.append(f"{chainring}/{sprocket}")
                gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
                ratios.append(gear_ratio)
                colors.append(color_map.get(i, 'gray'))
        
        # Crear gráfico de barras
        bars = ax.bar(combinations, ratios, color=colors)
        
        # Líneas de referencia de rango óptimo
        ax.axhline(y=2.5, color='gray', linestyle='--', alpha=0.5)
        ax.axhline(y=5.0, color='gray', linestyle='--', alpha=0.5)
        
        # Configurar gráfico
        ax.set_xlabel('Combinación (plato/piñón)')
        ax.set_ylabel('Relación de marchas')
        ax.set_title('Relación de marchas por combinación')
        ax.tick_params(axis='x', rotation=90)
        
        # Leyenda para colores
        legend_elements = []
        for i, chainring in enumerate(self.crankset_teeth):
            legend_elements.append(plt.Line2D([0], [0], color=color_map.get(i, 'gray'), lw=4, label=f'Plato {chainring}T'))
        legend_elements.append(plt.Line2D([0], [0], color='gray', linestyle='--', label='Rango óptimo (2.5-5.0)'))
        ax.legend(handles=legend_elements)
        
        # Ajustar layout
        fig.tight_layout()
        
        # Crear canvas para mostrar el gráfico
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Explicación técnica
        explanation = """
        La relación de marchas (gear ratio) es el número de dientes del plato dividido entre los dientes del piñón. 
        Un valor mayor indica una marcha más "dura" (para velocidad), mientras que un valor menor indica una marcha más "ligera" (para subidas).
        
        En general:
        • Valores > 5.0: Marchas muy duras para descensos o velocidad
        • Valores 2.5-5.0: Rango óptimo para uso normal
        • Valores < 2.5: Marchas ligeras para subidas
        
        El rango total de relaciones de tu bicicleta afecta directamente su versatilidad.
        """
        
        explanation_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=6)
        explanation_text.pack(fill="x", expand=False, padx=PADDING, pady=PADDING)
        explanation_text.insert(tk.END, explanation)
        explanation_text.config(state="disabled")

    @handle_errors
    def setup_power_tab(self, parent):
        """Configura la pestaña técnica de cadencia vs potencia"""
        # Crear título
        ttk.Label(parent, text="Relación entre cadencia, velocidad y potencia", 
                 font=("Arial", 12, "bold")).pack(pady=PADDING)
        
        # Crear panel para controles
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill="x", padx=PADDING, pady=PADDING)
        
        # Selector de plato/piñón
        ttk.Label(control_frame, text="Plato:").grid(row=0, column=0, padx=PADDING)
        self.power_plato_var = tk.StringVar(value=str(self.crankset_teeth[0]))
        plato_combo = ttk.Combobox(control_frame, textvariable=self.power_plato_var, 
                                   values=[str(t) for t in self.crankset_teeth], width=5)
        plato_combo.grid(row=0, column=1, padx=PADDING)
        
        ttk.Label(control_frame, text="Piñón:").grid(row=0, column=2, padx=PADDING)
        self.power_piñon_var = tk.StringVar(value=str(self.cassette_teeth[len(self.cassette_teeth)//2]))
        piñon_combo = ttk.Combobox(control_frame, textvariable=self.power_piñon_var, 
                                   values=[str(t) for t in self.cassette_teeth], width=5)
        piñon_combo.grid(row=0, column=3, padx=PADDING)
        
        ttk.Button(control_frame, text="Actualizar gráfico", 
                  command=lambda: self.update_power_chart(chart_frame)).grid(row=0, column=4, padx=LARGE_PADDING)
        
        # Frame para gráfico
        chart_frame = ttk.Frame(parent)
        chart_frame.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Crear gráfico inicial
        self.update_power_chart(chart_frame)
        
        # Explicación técnica
        explanation = """
        Este gráfico muestra la relación entre cadencia, velocidad y potencia estimada para una combinación de plato/piñón.
        
        La potencia es una estimación basada en un modelo simplificado, considerando la resistencia aerodinámica que aumenta exponencialmente con la velocidad.
        
        Observaciones clave:
        • Para una misma marcha, aumentar la cadencia aumenta linealmente la velocidad
        • La potencia necesaria aumenta exponencialmente con la velocidad
        • La cadencia óptima suele estar entre 80-90 RPM para la mayoría de ciclistas
        • A cadencias muy bajas (<60 RPM) se fuerza más las articulaciones, mientras que cadencias muy altas (>100 RPM) son menos eficientes energéticamente
        """
        
        explanation_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=8)
        explanation_text.pack(fill="x", expand=False, padx=PADDING, pady=PADDING)
        explanation_text.insert(tk.END, explanation)
        explanation_text.config(state="disabled")

    @handle_errors
    def update_power_chart(self, parent):
        """Actualiza el gráfico de potencia vs cadencia"""
        # Limpiar frame
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Obtener valores seleccionados
        try:
            chainring = int(self.power_plato_var.get())
            sprocket = int(self.power_piñon_var.get())
        except ValueError:
            messagebox.showwarning("Valor inválido", "Por favor, selecciona valores numéricos válidos")
            return
        
        # Crear figura con dos ejes Y
        fig, ax1 = plt.subplots(figsize=CHART_SIZE)
        ax2 = ax1.twinx()
        
        # Rango de cadencias a evaluar
        cadences = np.arange(60, 110, 2)
        
        # Calcular velocidades y potencias para cada cadencia
        gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
        speeds = []
        powers = []
        
        for cadence in cadences:
            speed = self.calculate_speed(gear_ratio, cadence)
            speeds.append(speed)
            powers.append(self.calculate_power_estimate(speed))
        
        # Zona óptima de cadencia
        optimal_min_idx = np.abs(cadences - OPTIMAL_CADENCE_MIN).argmin()
        optimal_max_idx = np.abs(cadences - OPTIMAL_CADENCE_MAX).argmin()
        
        # Graficar velocidad vs cadencia
        line1, = ax1.plot(cadences, speeds, 'b-', label='Velocidad')
        ax1.fill_between(cadences[optimal_min_idx:optimal_max_idx+1], 
                        0, max(speeds)*1.1, 
                        color='gray', alpha=0.1, label='Rango óptimo de cadencia')
        
        # Graficar potencia vs cadencia
        line2, = ax2.plot(cadences, powers, 'r-', label='Potencia estimada')
        
        # Configurar ejes
        ax1.set_xlabel('Cadencia (RPM)')
        ax1.set_ylabel('Velocidad (km/h)', color='b')
        ax1.tick_params(axis='y', labelcolor='b')
        
        ax2.set_ylabel('Potencia estimada (unidades relativas)', color='r')
        ax2.tick_params(axis='y', labelcolor='r')
        
        # Título
        plt.title(f'Velocidad y potencia para combinación {chainring}T / {sprocket}T')
        
        # Leyenda combinada
        lines = [line1, line2]
        labels = [line.get_label() for line in lines]
        ax1.legend(lines, labels, loc='upper left')
        
        # Ajustar layout
        fig.tight_layout()
        
        # Mostrar gráfico
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    @handle_errors
    def setup_overlap_tab(self, parent):
        """Configura la pestaña técnica de solapamiento de marchas"""
        # Crear título
        ttk.Label(parent, text="Análisis de solapamiento de marchas", 
                 font=("Arial", 12, "bold")).pack(pady=PADDING)
        
        # Crear gráfico
        fig, ax = plt.subplots(figsize=CHART_SIZE)
        
        # Preparar datos
        all_ratios = []
        colors = []
        labels = []
        
        color_map = {
            0: 'red',
            1: 'blue',
            2: 'green'
        }
        
        # Marcadores para cruces de cadena
        crosses = []
        
        # Calcular relaciones para cada plato
        for i, chainring in enumerate(self.crankset_teeth):
            ratios = []
            cross_positions = []
            for j, sprocket in enumerate(self.cassette_teeth):
                gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
                ratios.append(gear_ratio)
                
                # Verificar cruce de cadena
                crossing, _ = self.is_chain_crossing(i, j)
                cross_positions.append(crossing)
            
            # Añadir al gráfico
            line, = ax.plot(range(len(self.cassette_teeth)), ratios, '-', 
                    color=color_map.get(i, 'gray'), label=f"Plato {chainring}T")
            
            # Marcar puntos sin cruce de cadena
            safe_x = [j for j in range(len(self.cassette_teeth)) if not cross_positions[j]]
            safe_y = [ratios[j] for j in range(len(ratios)) if not cross_positions[j]]
            ax.plot(safe_x, safe_y, 'o', color=color_map.get(i, 'gray'))
            
            # Marcar puntos con cruce de cadena
            cross_x = [j for j in range(len(self.cassette_teeth)) if cross_positions[j]]
            cross_y = [ratios[j] for j in range(len(ratios)) if cross_positions[j]]
            if cross_x:
                ax.plot(cross_x, cross_y, 'x', color=color_map.get(i, 'gray'), markersize=8, alpha=0.7)
            
            # Guardar para análisis de solapamiento
            all_ratios.append(ratios)
            crosses.append(cross_positions)
        
        # Configurar gráfico
        ax.set_xlabel('Posición del piñón')
        ax.set_ylabel('Relación de marchas')
        ax.set_title('Solapamiento entre platos')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Etiquetas del eje X
        ax.set_xticks(range(len(self.cassette_teeth)))
        ax.set_xticklabels([str(t) for t in self.cassette_teeth])
        
        # Leyenda
        legend_elements = []
        for i, chainring in enumerate(self.crankset_teeth):
            legend_elements.append(plt.Line2D([0], [0], color=color_map.get(i, 'gray'), lw=2, label=f'Plato {chainring}T'))
        
        # Añadir leyenda para cruces de cadena
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='gray', linestyle='None', label='Combinación segura'))
        legend_elements.append(plt.Line2D([0], [0], marker='x', color='gray', linestyle='None', label='Cruce de cadena'))
        
        ax.legend(handles=legend_elements)
        
        # Ajustar layout
        fig.tight_layout()
        
        # Crear canvas para mostrar el gráfico
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Panel para análisis de solapamiento
        overlap_frame = ttk.LabelFrame(parent, text="Análisis de solapamiento")
        overlap_frame.pack(fill="x", padx=PADDING, pady=PADDING)
        
        # Calcular y mostrar solapamiento
        overlap_text = self.calculate_overlap_analysis(all_ratios, crosses)
        
        overlap_info = scrolledtext.ScrolledText(overlap_frame, wrap=tk.WORD, height=8)
        overlap_info.pack(fill="x", expand=False, padx=PADDING, pady=PADDING)
        overlap_info.insert(tk.END, overlap_text)
        overlap_info.config(state="disabled")

    @handle_errors
    def calculate_overlap_analysis(self, all_ratios, crosses=None):
        """
        Calcula y prepara un análisis de solapamiento de marchas
        
        Args:
            all_ratios: Lista de listas con las relaciones de cada plato
            crosses: Lista de listas con los cruces de cadena (opcional)
        """
        if len(all_ratios) <= 1:
            return "Se necesitan al menos dos platos para analizar el solapamiento."
        
        result = "Análisis de solapamiento entre platos:\n\n"
        
        # Analizar solapamiento entre platos adyacentes
        for i in range(len(all_ratios) - 1):
            plato1 = self.crankset_teeth[i]
            plato2 = self.crankset_teeth[i + 1]
            
            ratios1 = all_ratios[i]
            ratios2 = all_ratios[i + 1]
            
            # Si tenemos información de cruces, filtrar las relaciones
            if crosses:
                # Filtrar relaciones del plato 1 que no cruzan la cadena
                filtered_ratios1 = [ratios1[j] for j in range(len(ratios1)) if not crosses[i][j]]
                # Filtrar relaciones del plato 2 que no cruzan la cadena
                filtered_ratios2 = [ratios2[j] for j in range(len(ratios2)) if not crosses[i+1][j]]
                
                # Si no hay marchas válidas después de filtrar, usar las originales
                if filtered_ratios1 and filtered_ratios2:
                    min_ratio1 = min(filtered_ratios1)
                    max_ratio1 = max(filtered_ratios1)
                    min_ratio2 = min(filtered_ratios2)
                    max_ratio2 = max(filtered_ratios2)
                    
                    result += f"Entre plato {plato1}T y {plato2}T (sin cruces de cadena):\n"
                else:
                    min_ratio1 = min(ratios1)
                    max_ratio1 = max(ratios1)
                    min_ratio2 = min(ratios2)
                    max_ratio2 = max(ratios2)
                    
                    result += f"Entre plato {plato1}T y {plato2}T (incluyendo cruces de cadena):\n"
            else:
                min_ratio1 = min(ratios1)
                max_ratio1 = max(ratios1)
                min_ratio2 = min(ratios2)
                max_ratio2 = max(ratios2)
                
                result += f"Entre plato {plato1}T y {plato2}T:\n"
            
            # Calcular solapamiento
            overlap_start = max(min_ratio1, min_ratio2)
            overlap_end = min(max_ratio1, max_ratio2)
            
            if overlap_start <= overlap_end:
                overlap_pct = (overlap_end - overlap_start) / (max_ratio1 - min_ratio1) * 100
                result += f"- Rango de solapamiento: {overlap_start:.2f} a {overlap_end:.2f}\n"
                result += f"- Porcentaje de solapamiento: {overlap_pct:.1f}%\n"
                
                if overlap_pct < 10:
                    result += "- Evaluación: Solapamiento bajo. Puede haber 'saltos' grandes al cambiar de plato.\n"
                elif overlap_pct < 30:
                    result += "- Evaluación: Solapamiento moderado. Configuración equilibrada.\n"
                else:
                    result += "- Evaluación: Solapamiento alto. Hay muchas marchas redundantes.\n"
            else:
                result += f"- No hay solapamiento entre marchas utilizables.\n"
                
            result += "\n"
        
        # Análisis general del rango
        if crosses:
            # Obtener relaciones sin cruces de cadena
            all_filtered_ratios = []
            for i, ratios in enumerate(all_ratios):
                filtered = [ratios[j] for j in range(len(ratios)) if not crosses[i][j]]
                if filtered:
                    all_filtered_ratios.extend(filtered)
            
            if all_filtered_ratios:
                min_ratio = min(all_filtered_ratios)
                max_ratio = max(all_filtered_ratios)
                range_ratio = max_ratio / min_ratio
                
                result += f"Rango total de marchas (sin cruces de cadena): {range_ratio:.2f}x\n"
            else:
                result += "No se puede calcular el rango sin cruces de cadena.\n"
        
        # También calculamos el rango total incluyendo cruces
        all_ratios_flat = [ratio for sublist in all_ratios for ratio in sublist]
        min_ratio = min(all_ratios_flat)
        max_ratio = max(all_ratios_flat)
        range_ratio = max_ratio / min_ratio
        
        result += f"Rango total de marchas (incluyendo cruces de cadena): {range_ratio:.2f}x\n"
        
        if range_ratio < 3:
            result += "Evaluación: Rango limitado. Adecuado para terreno uniforme o uso específico."
        elif range_ratio < 5:
            result += "Evaluación: Rango moderado. Bueno para uso general."
        else:
            result += "Evaluación: Rango amplio. Excelente versatilidad para diferentes terrenos."
        
        return result

    @handle_errors
    def update_tech_tab(self):
        """Actualiza la pestaña técnica si hay cambios en la configuración"""
        if self.validate_gear_configuration():
            for widget in self.tech_tab.winfo_children():
                widget.destroy()
            self.setup_scrollable_frame(self.tech_tab, self.setup_tech_tab)

    def show_basic_concepts(self):
        """Muestra una ventana con conceptos básicos de ciclismo"""
        concepts_window = tk.Toplevel(self.root)
        concepts_window.title("Conceptos básicos de ciclismo")
        concepts_window.geometry("600x500")
        
        # Contenido
        ttk.Label(concepts_window, text="Conceptos básicos de ciclismo", 
                 font=("Arial", 14, "bold")).pack(pady=PADDING)
        
        # Texto con scroll
        content = scrolledtext.ScrolledText(concepts_window, wrap=tk.WORD)
        content.pack(fill="both", expand=True, padx=LARGE_PADDING, pady=PADDING)
        
        concepts_text = """
        TRANSMISIÓN Y MARCHAS
        
        Platos (o coronas): Son los discos dentados unidos a los pedales. Determinan cuánta fuerza se transmite a la cadena.
        - Platos grandes (más dientes): Mayor velocidad, requieren más fuerza
        - Platos pequeños (menos dientes): Menor velocidad, pedaleo más fácil
        
        Piñones (o casete): Conjunto de discos dentados en la rueda trasera.
        - Piñones pequeños (menos dientes): Mayor velocidad, requieren más fuerza
        - Piñones grandes (más dientes): Menor velocidad, pedaleo más fácil
        
        Relación de marchas: Número de dientes del plato dividido por el número de dientes del piñón. Indica cuántas vueltas da la rueda por cada vuelta completa de los pedales.
        
        Desarrollo: Distancia recorrida por cada pedalada completa. Se calcula multiplicando la relación de marchas por la circunferencia de la rueda.
        
        CONCEPTOS DE PEDALEO
        
        Cadencia: Velocidad a la que se pedalea, medida en revoluciones por minuto (RPM).
        - Cadencia baja (<70 RPM): Mayor esfuerzo en cada pedalada, mayor tensión en articulaciones
        - Cadencia media (70-90 RPM): Equilibrio óptimo para la mayoría de ciclistas
        - Cadencia alta (>90 RPM): Menor esfuerzo por pedalada, mayor frecuencia cardíaca
        
        CRUCE DE CADENA
        
        El cruce de cadena ocurre cuando se utilizan combinaciones extremas:
        - Plato grande (delantero) con piñón grande (trasero)
        - Plato pequeño (delantero) con piñón pequeño (trasero)
        
        Estas combinaciones provocan que la cadena trabaje en un ángulo diagonal pronunciado, causando:
        - Mayor desgaste de la cadena, platos, piñones y desviador
        - Pérdida de eficiencia (desperdicias energía al pedalear)
        - Mayor ruido durante el pedaleo
        - Riesgo de que la cadena se salga o se dañe
        
        Por eso, en esta aplicación, estas combinaciones están marcadas o filtradas.
        La regla de oro es: usa combinaciones donde la cadena trabaje lo más recta posible.
        
        USO CORRECTO DE LAS MARCHAS
        
        Principios básicos:
        1. Mantén una cadencia constante y cómoda ajustando las marchas
        2. Anticipa cambios de terreno y cambia antes de necesitarlo
        3. Evita combinaciones extremas (cruce de cadena)
        4. Cambia secuencialmente, no saltes muchas marchas de golpe
        
        Situaciones específicas:
        - Subidas: Usa platos pequeños y piñones grandes para pedalear con menos esfuerzo
        - Bajadas: Usa platos grandes y piñones pequeños o deja de pedalear si la velocidad es alta
        - Llano: Busca una combinación que te permita mantener tu cadencia ideal
        """
        
        content.insert(tk.END, concepts_text)
        content.config(state="disabled")
        
        # Botón para cerrar
        ttk.Button(concepts_window, text="Cerrar", 
                  command=concepts_window.destroy).pack(pady=PADDING)

    def show_app_help(self):
        """Muestra una ventana con ayuda sobre el uso de la aplicación"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Cómo usar la aplicación")
        help_window.geometry("600x500")
        
        # Contenido
        ttk.Label(help_window, text="Cómo usar esta aplicación", 
                 font=("Arial", 14, "bold")).pack(pady=PADDING)
        
        # Texto con scroll
        content = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        content.pack(fill="both", expand=True, padx=LARGE_PADDING, pady=PADDING)
        
        help_text = """
        GUÍA DE USO RÁPIDA
        
        1. CONFIGURACIÓN DE TU BICICLETA (Pestaña "Mi Bicicleta")
           - Selecciona el tipo de bicicleta más parecido a la tuya
           - Ajusta el tamaño de rueda según corresponda
           - Establece tu cadencia habitual (si no estás seguro, deja el valor predeterminado)
           - Si conoces exactamente la configuración de tu bicicleta, usa "Configurar manualmente"
           - Pulsa "Visualizar mi bicicleta" para continuar
        
        2. VISUALIZACIÓN (Pestaña "Visualización")
           - Explora la "Tabla de marchas" para ver qué velocidad alcanzarás con cada combinación
           - Revisa el "Gráfico de velocidades" para entender cómo afecta cada piñón a tu velocidad
           - Observa el "Desarrollo" para comprender la distancia recorrida por pedalada
        
        3. RECOMENDACIONES (Pestaña "¿Qué marcha usar?")
           - Establece tu velocidad deseada y la pendiente del terreno
           - Obtén una recomendación personalizada de qué marcha usar
           - Lee los consejos específicos para tu situación
        
        4. ANÁLISIS TÉCNICO (Solo en modo técnico)
           - Explora análisis avanzados como relación de marchas, potencia y solapamiento
           - Útil para ciclistas experimentados que deseen optimizar su técnica
        
        CAMBIO DE MODO
        
        - Modo Principiante: Interfaz simplificada con conceptos básicos
        - Modo Deportivo/Técnico: Acceso a análisis avanzados y términos técnicos
        
        CONSEJOS GENERALES
        
        - Experimenta con diferentes configuraciones para entender mejor cómo funcionan las marchas
        - Usa la pestaña de recomendaciones antes de salir a rodar para planificar qué marchas usar
        - Consulta la ayuda o los conceptos básicos si algún término no te resulta familiar
        """
        
        content.insert(tk.END, help_text)
        content.config(state="disabled")
        
        # Botón para cerrar
        ttk.Button(help_window, text="Cerrar", 
                  command=help_window.destroy).pack(pady=PADDING)

    def show_about(self):
        """Muestra información sobre la aplicación"""
        about_window = tk.Toplevel(self.root)
        about_window.title("Acerca de")
        about_window.geometry("400x300")
        
        # Contenido
        ttk.Label(about_window, text="Ñu-sui", 
                 font=("Arial", 14, "bold")).pack(pady=PADDING)
        
        ttk.Label(about_window, text="Versión 1.0", 
                 font=("Arial", 10, "italic")).pack()
        
        ttk.Label(about_window, text="""
        "Ñu-sui" es un término en zapoteco que significa "ciclista".
        Una herramienta educativa para ciclistas de todos los niveles.
        
        Esta aplicación te ayuda a entender y optimizar el uso de las marchas
        de tu bicicleta para mejorar tu experiencia al pedalear.
        
        Desarrollada con Python y Tkinter por Gustavo Mondragón.
        Para más ideas o sugerencias, envíame un correo electrónico a gustavms93@gmail.com.
        """, wraplength=350, justify="center").pack(pady=LARGE_PADDING)
        
        # Botón para cerrar
        ttk.Button(about_window, text="Cerrar", 
                  command=about_window.destroy).pack(pady=PADDING)

# Función para iniciar la aplicación
def iniciar_app():
    root = tk.Tk()
    app = NuSui(root)
    root.mainloop()

if __name__ == "__main__":
    iniciar_app()