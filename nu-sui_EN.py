from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

# Application Constants
APP_TITLE = "Ñu-sui: learn how to use your bike gears"
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

# General configuration for charts
matplotlib.rcParams.update({'font.size': DEFAULT_FONT_SIZE})

# Dictionary to store wheel sizes and their corresponding circumference in meters
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
                f"Error in {func.__name__}: {str(e)}"
            )
            return None
    return wrapper

@dataclass
class BikeType:
    """Data class for bike type configuration"""
    name: str
    value: str
    chainrings: List[int]
    sprockets: List[int]

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
        self.technical_mode = tk.BooleanVar(value=False)
        self.debug_var = tk.BooleanVar(value=False)
        
    def setup_scrollable_frame(self, parent, setup_function):
        """
        Creates a scrollable frame inside the parent and executes the setup_function
        within the scrollable frame.
        
        Args:
            parent: Container frame
            setup_function: Function that configures content
        """
        # Create a canvas to contain the scrollable frame
        canvas = tk.Canvas(parent)
        canvas.pack(side="left", fill="both", expand=True)
        
        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        # Configure canvas to use scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create inner frame for content
        inner_frame = ttk.Frame(canvas)
        
        # Create window in canvas to display the frame
        canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        # Function to adjust the canvas size when the frame size changes
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Function to adjust the window width when the size changes
        def configure_canvas_window(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        # Bind events
        inner_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_canvas_window)
        
        # Allow scrolling with the mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Execute the provided setup function in the scrollable frame
        if setup_function:
            setup_function(inner_frame)
        
        return inner_frame
        
    def create_ui(self):
        # Add mode switch button at the top
        mode_frame = ttk.Frame(self.root)
        mode_frame.pack(fill="x", padx=PADDING, pady=PADDING)
        
        ttk.Label(mode_frame, text="Mode:").pack(side="left", padx=PADDING)
        
        ttk.Radiobutton(mode_frame, text="Beginner", 
                       variable=self.technical_mode, value=False,
                       command=self.change_mode).pack(side="left", padx=PADDING)
        
        ttk.Radiobutton(mode_frame, text="Technical/Sport", 
                       variable=self.technical_mode, value=True,
                       command=self.change_mode).pack(side="left", padx=PADDING)
        
        # Button to show debug
        self.debug_var = tk.BooleanVar(value=False)
        self.debug_check = ttk.Checkbutton(mode_frame, text="Show debug",
                                      variable=self.debug_var)
        self.debug_check.pack(side="right", padx=PADDING)
        
        # Create menu bar with help
        self.create_menu()
        
        # Create main tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Welcome tab and basic concepts - WITH SCROLL
        self.welcome_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.welcome_tab, text="Introduction")
        # Add canvas with scrollbar for welcome tab
        self.setup_scrollable_frame(self.welcome_tab, self.setup_welcome_tab)
        
        # Configuration tab - WITH SCROLL
        self.config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.config_tab, text="My Bicycle")
        self.setup_scrollable_frame(self.config_tab, self.setup_config_tab)
        
        # Visualization tab - WITH SCROLL
        self.visual_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.visual_tab, text="Visualization")
        # Content will be added later with visualize_bike()
        
        # Recommendations tab - WITH SCROLL
        self.recom_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.recom_tab, text="Which Gear to Use?")
        self.setup_scrollable_frame(self.recom_tab, self.setup_recom_tab)
        
        # Technical analysis tab - WITH SCROLL
        self.tech_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tech_tab, text="Technical Analysis")
        self.setup_scrollable_frame(self.tech_tab, self.setup_tech_tab)
        
        # Initially hide technical tab in beginner mode
        self.change_mode()
    
    def change_mode(self):
        """Switches between beginner and sport/technical mode"""
        if self.technical_mode.get():
            # Change to technical mode
            self.notebook.tab(4, state="normal")  # Show technical tab
            # Update visualizations and recommendations if data already exists
            if self.crankset_teeth and self.cassette_teeth:
                self.visualize_bike()
                # Update technical tab
                self.update_tech_tab()
        else:
            # Change to beginner mode
            self.notebook.tab(4, state="hidden")  # Hide technical tab
    
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Basic Concepts", command=self.show_basic_concepts)
        help_menu.add_command(label="How to Use the App", command=self.show_app_help)
        help_menu.add_command(label="About", command=self.show_about)
        
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)
    
    def setup_welcome_tab(self, parent):
        # Title
        ttk.Label(parent, text="Ñu-sui: Learn how to use your bike gears!", 
                 font=("Arial", 16, "bold")).pack(pady=LARGE_PADDING)
        
        # Simple explanation
        intro_text = """
        PLEASE! If you like this application, any donation is welcome.
        This is part of a personal project, non-profit.
        You can donate via PayPal: https://paypal.me/gimondragon?country.x=MX&locale.x=es_XC
        Code originally made by: Gustavo Mondragón. You can follow me on social media:
        - Twitter/X: @GustavMondragon
        - Instagram: @gmondragons
        
        Hello! This app will help you understand how to use your bicycle gears.
        
        Learning to use gears properly will allow you to:
        • Pedal with less effort
        • Maintain a comfortable speed
        • Climb hills more easily
        • Prevent premature wear on your bicycle
        
        It's like choosing the right gear in a car, but for your bicycle.
        """
        
        intro_label = scrolledtext.ScrolledText(parent, wrap=tk.WORD, width=70, height=10)
        intro_label.pack(pady=PADDING, padx=LARGE_PADDING)
        intro_label.insert(tk.END, intro_text)
        intro_label.config(state="disabled")
        
        # Explanatory images (real images should be added)
        concepts_frame = ttk.LabelFrame(parent, text="Basic Concepts")
        concepts_frame.pack(fill="both", expand=True, padx=LARGE_PADDING, pady=PADDING)
        
        # Here we would add images with explanations
        # For now, we'll use only text as an example
        
        basic_concepts = [
            {
                "title": "What are gears?",
                "text": "Gears are combinations of 'chainrings' (front) and 'sprockets' (rear) that determine how far your bicycle moves with each pedal stroke."
            },
            {
                "title": "Chainrings (front)",
                "text": "These are the toothed discs attached to the pedals. The larger ones are for speed on flat terrain, the smaller ones for climbing hills."
            },
            {
                "title": "Sprockets (rear)",
                "text": "These are the toothed discs on the rear wheel. The smaller ones are for speed, the larger ones for easier pedaling uphill."
            },
            {
                "title": "Cadence",
                "text": "This is the speed at which you pedal (revolutions per minute). Ideally, maintain between 70-90 RPM for most cyclists."
            }
        ]
        
        for i, concept in enumerate(basic_concepts):
            frame = ttk.Frame(concepts_frame)
            frame.grid(row=i//2, column=i%2, padx=LARGE_PADDING, pady=PADDING, sticky="nsew")
            
            ttk.Label(frame, text=concept["title"], font=("Arial", 12, "bold")).pack(anchor="w")
            ttk.Label(frame, text=concept["text"], wraplength=400).pack(anchor="w", pady=PADDING)
        
        # Button to start
        ttk.Button(parent, text="Let's configure my bicycle!", 
                  command=lambda: self.notebook.select(1)).pack(pady=LARGE_PADDING)
    
    def setup_config_tab(self, parent):
        # Title
        ttk.Label(parent, text="Configure your bicycle", 
                 font=("Arial", 14, "bold")).pack(pady=PADDING)
        
        # Explanation
        ttk.Label(parent, text="Let's configure your bicycle step by step. If you don't know some data, you can use the default values.",
                 wraplength=800).pack(pady=PADDING)
        
        # Main panel
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=LARGE_PADDING, pady=PADDING)
        
        # Left panel - Bicycle type selection
        left_frame = ttk.LabelFrame(main_frame, text="Bicycle type")
        left_frame.pack(side="left", fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        ttk.Label(left_frame, text="Select the type of bicycle you have:").pack(pady=PADDING)
        
        # Variables for bicycle type
        self.bike_type_var = tk.StringVar(value="mtb")
        
        # Type options with images and predefined configurations
        bike_types = [
            {"name": "MTB (Mountain)", "value": "mtb", "chainrings": [24, 34, 42], "sprockets": [14, 16, 18, 20, 22, 24, 34]},
            {"name": "Road", "value": "road", "chainrings": [34, 50], "sprockets": [14, 16, 18, 20, 22, 24, 28]},
            {"name": "Urban/Commuter", "value": "urban", "chainrings": [24, 34, 42], "sprockets": [14, 16, 18, 20, 22, 24, 28]},
            {"name": "Custom", "value": "custom", "chainrings": [], "sprockets": []}
        ]
        
        for bike in bike_types:
            ttk.Radiobutton(left_frame, text=bike["name"], value=bike["value"], 
                          variable=self.bike_type_var,
                          command=lambda b=bike: self.select_bike_type(b)).pack(anchor="w", pady=PADDING, padx=LARGE_PADDING)
        
        # Right panel - Detailed configuration
        self.right_frame = ttk.LabelFrame(main_frame, text="Detailed configuration")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Wheel size selection
        ttk.Label(self.right_frame, text="Wheel size:").pack(anchor="w", pady=PADDING)
        self.wheel_size_var = tk.StringVar(value="26x2.1")  # Default value
        
        # Group wheel sizes by categories for easier selection
        wheel_categories = {
            "MTB": ["26x1.95", "26x2.1", "26x2.35", "27.5x2.10", "27.5x2.25", "29x2.1", "29x2.25"],
            "Road": ["700x23C", "700x25C", "700x28C", "700C"],
            "Urban": ["700x35C", "700x38C", "700x40C", "26x1.75"],
            "Custom": list(wheel_sizes.keys())  # Use all available wheel sizes from the dictionary
        }
        
        self.wheel_combo = ttk.Combobox(self.right_frame, textvariable=self.wheel_size_var, width=30)
        self.wheel_combo.pack(anchor="w", pady=PADDING, padx=LARGE_PADDING)
        
        # Update wheel options based on selected bicycle type
        self.wheel_combo['values'] = wheel_categories["MTB"]  # Default value
        
        # Default cadence
        ttk.Label(self.right_frame, text="Usual cadence (pedal strokes per minute):").pack(anchor="w", pady=PADDING)
        self.cadencia_var = tk.StringVar(value=str(DEFAULT_CADENCE))  # Default value for beginners
        
        cadencia_frame = ttk.Frame(self.right_frame)
        cadencia_frame.pack(anchor="w", fill="x", pady=PADDING, padx=LARGE_PADDING)
        
        ttk.Scale(cadencia_frame, from_=MIN_CADENCE, to=MAX_CADENCE, orient="horizontal", 
                variable=self.cadencia_var, length=200,
                command=lambda s: self.cadencia_var.set(str(int(float(s))))).pack(side="left")
        
        ttk.Label(cadencia_frame, textvariable=self.cadencia_var).pack(side="left", padx=PADDING)
        ttk.Label(cadencia_frame, text="RPM").pack(side="left")
        
        # Cadence explanation
        cadencia_info = ttk.Label(self.right_frame, text="A cadence of 70-90 RPM is suitable for most cyclists.", 
                               font=("Arial", 9, "italic"))
        cadencia_info.pack(anchor="w", padx=LARGE_PADDING)
        
        # Button for manual configuration
        self.manual_config_button = ttk.Button(self.right_frame, text="Configure manually",
                                            command=self.setup_custom_gears)
        self.manual_config_button.pack(anchor="w", pady=LARGE_PADDING, padx=LARGE_PADDING)
        
        # Button to visualize
        self.visualize_button = ttk.Button(parent, text="Visualize my bicycle", 
                                        command=self.visualize_bike)
        self.visualize_button.pack(pady=LARGE_PADDING)
        
        # Select MTB type by default
        self.select_bike_type(bike_types[0])

    @handle_errors
    def setup_custom_gears(self):
        """Opens a popup window to manually configure chainrings and sprockets"""
        custom_window = tk.Toplevel(self.root)
        custom_window.title("Manual gear configuration")
        custom_window.geometry("500x400")
        custom_window.grab_set()  # Modal window
        
        ttk.Label(custom_window, text="Configure the teeth of chainrings and sprockets", 
                 font=("Arial", 12, "bold")).pack(pady=PADDING)
        
        # Main frame with two columns
        main_frame = ttk.Frame(custom_window)
        main_frame.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Left column - Chainrings
        left_frame = ttk.LabelFrame(main_frame, text="Chainrings (front)")
        left_frame.pack(side="left", fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        ttk.Label(left_frame, text="Enter the number of teeth separated by commas:").pack(pady=PADDING)
        
        # Default values if configuration already exists
        platos_default = ",".join(map(str, self.crankset_teeth)) if self.crankset_teeth else ""
        self.platos_entry = ttk.Entry(left_frame)
        self.platos_entry.pack(padx=PADDING, pady=PADDING, fill="x")
        self.platos_entry.insert(0, platos_default)
        
        ttk.Label(left_frame, text="Example: 24,34,42 for triple chainring\nor 34,50 for double chainring", 
                 font=("Arial", 9, "italic")).pack(pady=PADDING)
        
        # Right column - Sprockets
        right_frame = ttk.LabelFrame(main_frame, text="Sprockets (rear)")
        right_frame.pack(side="right", fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        ttk.Label(right_frame, text="Enter the number of teeth separated by commas:").pack(pady=PADDING)
        
        # Default values if configuration already exists
        piñones_default = ",".join(map(str, self.cassette_teeth)) if self.cassette_teeth else ""
        self.piñones_entry = ttk.Entry(right_frame)
        self.piñones_entry.pack(padx=PADDING, pady=PADDING, fill="x")
        self.piñones_entry.insert(0, piñones_default)
        
        ttk.Label(right_frame, text="Example: 11,12,14,16,18,21,24,28,32,36\nfor a 10-speed cassette", 
                 font=("Arial", 9, "italic")).pack(pady=PADDING)
        
        # Action buttons
        button_frame = ttk.Frame(custom_window)
        button_frame.pack(fill="x", padx=PADDING, pady=PADDING)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=custom_window.destroy).pack(side="left", padx=PADDING)
        
        ttk.Button(button_frame, text="Save configuration", 
                  command=lambda: self.save_custom_gears(custom_window)).pack(side="right", padx=PADDING)

    @handle_errors
    def save_custom_gears(self, window):
        """Saves the manual gear configuration and closes the window"""
        try:
            # Process chainrings
            platos_text = self.platos_entry.get().strip()
            if platos_text:
                self.crankset_teeth = [int(x.strip()) for x in platos_text.split(',')]
            else:
                self.crankset_teeth = []
                
            # Process sprockets
            piñones_text = self.piñones_entry.get().strip()
            if piñones_text:
                self.cassette_teeth = [int(x.strip()) for x in piñones_text.split(',')]
            else:
                self.cassette_teeth = []
                
            # Validate configuration
            if not self.crankset_teeth or not self.cassette_teeth:
                raise ValueError("You must configure at least one chainring and one sprocket")
                
            # Sort teeth from smallest to largest (sprockets) and largest to smallest (chainrings)
            self.cassette_teeth.sort()  # Smallest to largest for sprockets
            self.crankset_teeth.sort(reverse=True)  # Largest to smallest for chainrings
            
            # Close window
            window.destroy()
            messagebox.showinfo("Configuration saved", "Gear configuration saved successfully")
            
        except ValueError as e:
            messagebox.showwarning("Configuration error", str(e))
    
    @handle_errors
    def select_bike_type(self, bike_type: Dict[str, Union[str, List[int]]]) -> None:
        """
        Update bike configuration based on selected type
        
        Args:
            bike_type: Dictionary containing bike configuration
        """
        # Validate input
        required_keys = ["value", "chainrings", "sprockets"]
        if not all(key in bike_type for key in required_keys):
            raise ValueError("Invalid bike type configuration")
            
        # Update values
        self.crankset_teeth = bike_type["chainrings"].copy()
        self.cassette_teeth = bike_type["sprockets"].copy()
        
        # Sort teeth from smallest to largest (sprockets) and largest to smallest (chainrings)
        self.cassette_teeth.sort()  # Smallest to largest for sprockets
        self.crankset_teeth.sort(reverse=True)  # Largest to smallest for chainrings
        
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
                "Insufficient data",
                "Please select a bicycle type or configure manually."
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
                "Invalid configuration",
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
        Determines if a chainring and sprocket combination causes chain crossing
        
        Args:
            chainring_idx: Index of the chainring (0 for the largest)
            sprocket_idx: Index of the sprocket (0 for the smallest)
            
        Returns:
            bool: True if the combination causes chain crossing, False otherwise
            str: Message describing the problem, or None if no crossing
        """
        num_chainrings = len(self.crankset_teeth)
        num_sprockets = len(self.cassette_teeth)
        
        # If there is only one chainring, no crossing is possible
        if num_chainrings <= 1:
            return False, None
            
        # Debug info
        if hasattr(self, 'debug_var') and self.debug_var.get():
            print(f"Checking chain crossing for chainring idx={chainring_idx} with sprocket idx={sprocket_idx}")
            print(f"Chainrings={self.crankset_teeth}, Sprockets={self.cassette_teeth}")
        
        # Adjust chain crossing logic according to the number of chainrings and sprockets
        if num_chainrings == 2:  # Double chainring
            # For double chainring, consider 35% of sprockets as extremes
            extreme_count = max(2, round(num_sprockets * 0.35))
            
            # Debug info
            if hasattr(self, 'debug_var') and self.debug_var.get():
                print(f"Double chainring: extreme_count={extreme_count}")
            
            # Large chainring with large sprockets
            if chainring_idx == 0 and sprocket_idx >= num_sprockets - extreme_count:
                return True, "Large chainring with large sprocket: increases wear and reduces efficiency"
            
            # Small chainring with small sprockets
            if chainring_idx == num_chainrings - 1 and sprocket_idx < extreme_count:
                return True, "Small chainring with small sprocket: increases wear and reduces efficiency"
                
        elif num_chainrings == 3:  # Triple chainring
            # More restrictive with triples: 40% of sprockets are extremes
            extreme_count_large = max(2, round(num_sprockets * 0.4))
            extreme_count_small = max(2, round(num_sprockets * 0.4))
            
            medium_extreme_large = max(1, round(num_sprockets * 0.15))
            medium_extreme_small = max(1, round(num_sprockets * 0.15))
            
            # Debug info
            if hasattr(self, 'debug_var') and self.debug_var.get():
                print(f"Triple chainring: extreme_count_large={extreme_count_large}, "
                     f"extreme_count_small={extreme_count_small}, "
                     f"medium_extreme_large={medium_extreme_large}, "
                     f"medium_extreme_small={medium_extreme_small}")
            
            # Large chainring with large sprockets
            if chainring_idx == 0 and sprocket_idx >= num_sprockets - extreme_count_large:
                return True, "Large chainring with large sprocket: increases wear and reduces efficiency"
            
            # Small chainring with small sprockets
            if chainring_idx == num_chainrings - 1 and sprocket_idx < extreme_count_small:
                return True, "Small chainring with small sprocket: increases wear and reduces efficiency"
            
            # For the middle chainring, there are also restrictions but less severe
            if chainring_idx == 1 and (sprocket_idx >= num_sprockets - medium_extreme_large or 
                                    sprocket_idx < medium_extreme_small):
                return True, "Middle chainring with extreme sprocket: may cause wear"
        
        # For other cases (unusual number of chainrings), use a general rule
        else:
            # General rule: 30% of sprockets at each end
            extreme_count = max(1, round(num_sprockets * 0.3))
            
            # Large chainring with large sprockets
            if chainring_idx == 0 and sprocket_idx >= num_sprockets - extreme_count:
                return True, "Large chainring with large sprocket: increases wear and reduces efficiency"
            
            # Small chainring with small sprockets
            if chainring_idx == num_chainrings - 1 and sprocket_idx < extreme_count:
                return True, "Small chainring with small sprocket: increases wear and reduces efficiency"
            
            # For intermediate chainrings in configurations with more than 2 chainrings
            if len(self.crankset_teeth) > 2 and 0 < chainring_idx < len(self.crankset_teeth) - 1:
                # Only the extremes for intermediate chainrings
                if sprocket_idx == 0 or sprocket_idx >= num_sprockets - 1:
                    return True, "Intermediate chainring with extreme sprocket: may cause wear"
        
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
        """Visualizes the bicycle configuration and creates charts"""
        # Validate configuration
        if not self.validate_gear_configuration():
            return
            
        # If debug mode is active, show a chain crossing table
        if self.debug_var.get():
            self.show_chain_crossing_debug()
        
        # Clear visualization tab
        for widget in self.visual_tab.winfo_children():
            widget.destroy()
        
        # Create a scrollable frame for the visualization tab
        scrollable_frame = self.setup_scrollable_frame(self.visual_tab, None)
        
        # Get parameters
        cadence = int(self.cadencia_var.get())
        wheel_size = self.wheel_size_var.get()
        
        # Create tab structure for visualizations
        visual_notebook = ttk.Notebook(scrollable_frame)
        visual_notebook.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Gear table tab
        table_tab = ttk.Frame(visual_notebook)
        visual_notebook.add(table_tab, text="Gear table")
        self.create_gear_table(table_tab, cadence)
        
        # Speed chart tab
        chart_tab = ttk.Frame(visual_notebook)
        visual_notebook.add(chart_tab, text="Speed chart")
        self.create_speed_chart(chart_tab, cadence)
        
        # Development tab
        dev_tab = ttk.Frame(visual_notebook)
        visual_notebook.add(dev_tab, text="Development")
        self.create_development_chart(dev_tab)
        
        # Update recommendations tab - recreate with scroll
        for widget in self.recom_tab.winfo_children():
            widget.destroy()
        self.setup_scrollable_frame(self.recom_tab, self.setup_recom_tab)
        
        # Update technical tab if we're in technical mode
        if self.technical_mode.get():
            for widget in self.tech_tab.winfo_children():
                widget.destroy()
            self.setup_scrollable_frame(self.tech_tab, self.setup_tech_tab)
        
        # Switch to visualization tab
        self.notebook.select(2)  # Index 2 = visualization tab
        
    def show_chain_crossing_debug(self):
        """Shows a debug window with the chain crossing matrix"""
        debug_window = tk.Toplevel(self.root)
        debug_window.title("Debug: Chain Crossing Matrix")
        debug_window.geometry("700x500")
        
        # Frame with scroll to accommodate larger matrices
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
        
        # Title
        ttk.Label(frame, text="Chain Crossing Matrix (X = crossing, O = safe)", 
                 font=("Arial", 12, "bold")).pack(pady=PADDING)
        
        # Information panel
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill="x", pady=PADDING)
        
        ttk.Label(info_frame, text=f"Chainrings: {self.crankset_teeth}", 
                font=("Arial", 10)).pack(anchor="w", pady=2)
        ttk.Label(info_frame, text=f"Sprockets: {self.cassette_teeth}", 
                font=("Arial", 10)).pack(anchor="w", pady=2)
        
        # Show parameters used for calculation according to bicycle type
        if len(self.crankset_teeth) == 3:
            num_sprockets = len(self.cassette_teeth)
            extreme_count_large = max(2, round(num_sprockets * 0.4))
            extreme_count_small = max(2, round(num_sprockets * 0.4))
            medium_extreme_large = max(1, round(num_sprockets * 0.15))
            medium_extreme_small = max(1, round(num_sprockets * 0.15))
            
            ttk.Label(info_frame, text=f"Triple chainring: Crossings on large chainring: {extreme_count_large} large sprockets", 
                    font=("Arial", 9, "italic")).pack(anchor="w", pady=1)
            ttk.Label(info_frame, text=f"Triple chainring: Crossings on small chainring: {extreme_count_small} small sprockets", 
                    font=("Arial", 9, "italic")).pack(anchor="w", pady=1)
            ttk.Label(info_frame, text=f"Triple chainring: Crossings on middle chainring: {medium_extreme_small} small sprockets and {medium_extreme_large} large sprockets", 
                    font=("Arial", 9, "italic")).pack(anchor="w", pady=1)
        elif len(self.crankset_teeth) == 2:
            num_sprockets = len(self.cassette_teeth)
            extreme_count = max(2, round(num_sprockets * 0.35))
            
            ttk.Label(info_frame, text=f"Double chainring: Crossings on large chainring: {extreme_count} large sprockets", 
                    font=("Arial", 9, "italic")).pack(anchor="w", pady=1)
            ttk.Label(info_frame, text=f"Double chainring: Crossings on small chainring: {extreme_count} small sprockets", 
                    font=("Arial", 9, "italic")).pack(anchor="w", pady=1)
        
        # Create table
        tabla_frame = ttk.Frame(frame)
        tabla_frame.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Column headers (sprockets)
        ttk.Label(tabla_frame, text="Chainring\\Sprocket", width=10, 
                 font=("Arial", 10, "bold")).grid(row=0, column=0, padx=2, pady=2)
        
        for j, sprocket in enumerate(self.cassette_teeth):
            ttk.Label(tabla_frame, text=f"{sprocket}T", width=6, 
                     font=("Arial", 10, "bold")).grid(row=0, column=j+1, padx=2, pady=2)
        
        # Rows (chainrings)
        for i, chainring in enumerate(self.crankset_teeth):
            ttk.Label(tabla_frame, text=f"{chainring}T", width=10, 
                     font=("Arial", 10, "bold")).grid(row=i+1, column=0, padx=2, pady=2)
            
            for j in range(len(self.cassette_teeth)):
                # Calculate crossing directly
                crossing, _ = self.is_chain_crossing(i, j)
                
                text = "X" if crossing else "O"
                
                # Use colored Frame with Label inside
                cell_frame = ttk.Frame(tabla_frame, width=50, height=30)
                cell_frame.grid(row=i+1, column=j+1, padx=2, pady=2)
                cell_frame.grid_propagate(False)  # Maintain size
                
                if crossing:
                    label = ttk.Label(cell_frame, text=text, font=("Arial", 10, "bold"), foreground="red")
                else:
                    label = ttk.Label(cell_frame, text=text, font=("Arial", 10, "bold"), foreground="green")
                    
                label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Explanation panel
        explanation = """
        This matrix shows which chainring and sprocket combinations cause 'chain crossing'.
        
        Combinations marked with X should be avoided for prolonged periods because:
        - They increase wear on the chain, chainrings, sprockets, and derailleur
        - They reduce pedaling efficiency
        - They increase the risk of the chain coming off or getting damaged
        
        General rules:
        - For large chainring: avoid large sprockets
        - For small chainring: avoid small sprockets
        - For middle chainring: avoid extreme sprockets
        """
        
        explanation_frame = ttk.LabelFrame(frame, text="Explanation")
        explanation_frame.pack(fill="x", padx=PADDING, pady=PADDING)
        
        ttk.Label(explanation_frame, text=explanation, justify="left", wraplength=650).pack(padx=PADDING, pady=PADDING)
        
        # Button to close
        ttk.Button(frame, text="Close", 
                  command=debug_window.destroy).pack(pady=PADDING)

    @handle_errors
    def create_gear_table(self, parent, cadence):
        """Creates a table with all gears and their speeds, hiding chain crossings"""
        # Container frame with scroll
        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Create an explanatory title
        ttk.Label(container, text=f"Estimated speeds (km/h) at {cadence} RPM", 
                 font=("Arial", 12, "bold")).pack(pady=PADDING)
        
        # Create table with treeview
        columns = ["Chainring"] + [f"{teeth}" for teeth in self.cassette_teeth]
        
        tree = ttk.Treeview(container, columns=columns, show="headings", height=len(self.crankset_teeth))
        tree.pack(fill="both", expand=True)
        
        # Configure columns
        tree.heading("Chainring", text="Chainring")
        for teeth in self.cassette_teeth:
            tree.heading(f"{teeth}", text=f"{teeth}")
            tree.column(f"{teeth}", width=60, anchor="center")
        
        # Counter for combinations with chain crossing
        crossing_count = 0
        total_combinations = len(self.crankset_teeth) * len(self.cassette_teeth)
        
        # Fill table with speeds
        for i, chainring in enumerate(self.crankset_teeth):
            row_values = [f"{chainring}T"]
            for j, sprocket in enumerate(self.cassette_teeth):
                gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
                speed = self.calculate_speed(gear_ratio, cadence)
                
                # Check if this combination crosses the chain
                crossing, _ = self.is_chain_crossing(i, j)
                
                if crossing:
                    # Mark cells with chain crossing
                    row_values.append("---")
                    crossing_count += 1
                else:
                    row_values.append(f"{speed:.1f}")
            
            tree.insert("", "end", values=row_values)
        
        # Add legend
        ttk.Label(container, text="Speeds are calculated with wheel size: " + 
                 f"{self.wheel_size_var.get()} ({self.wheel_sizes[self.wheel_size_var.get()]}m circumference)",
                 font=("Arial", 9, "italic")).pack(pady=(PADDING, 0))
        
        # Add warning about chain crossing
        warning_frame = ttk.Frame(container)
        warning_frame.pack(fill="x", pady=PADDING)
        
        warning_icon = ttk.Label(warning_frame, text="⚠️", font=("Arial", 12))
        warning_icon.pack(side="left", padx=(0, PADDING))
        
        warning_text = f"Speeds for {crossing_count} of {total_combinations} combinations are not shown because they cause 'chain crossing', "
        warning_text += "which increases component wear and reduces efficiency. "
        warning_text += "These combinations are marked with '---'."
        
        warning_label = ttk.Label(warning_frame, text=warning_text, 
                                wraplength=600, justify="left")
        warning_label.pack(side="left", fill="x", expand=True)

    @handle_errors
    def create_speed_chart(self, parent, cadence):
        """Creates a line chart with speeds for each gear, indicating chain crossings"""
        # Create figure
        fig, ax = plt.subplots(figsize=CHART_SIZE)
        
        # Prepare data
        for i, chainring in enumerate(self.crankset_teeth):
            speeds = []
            crosses = []  # To mark points that cross the chain
            
            for j, sprocket in enumerate(self.cassette_teeth):
                gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
                speed = self.calculate_speed(gear_ratio, cadence)
                speeds.append(speed)
                
                # Verify if this combination crosses the chain
                crossing, _ = self.is_chain_crossing(i, j)
                crosses.append(crossing)
            
            # Plot main line (all points)
            line, = ax.plot(self.cassette_teeth, speeds, '-', color=f'C{i}', label=f"Chainring {chainring}T")
            
            # Add "safe" points (without crossing) in solid color
            safe_x = [self.cassette_teeth[j] for j in range(len(self.cassette_teeth)) if not crosses[j]]
            safe_y = [speeds[j] for j in range(len(speeds)) if not crosses[j]]
            ax.plot(safe_x, safe_y, 'o', color=f'C{i}')
            
            # Add "dangerous" points (with crossing) in another style
            cross_x = [self.cassette_teeth[j] for j in range(len(self.cassette_teeth)) if crosses[j]]
            cross_y = [speeds[j] for j in range(len(speeds)) if crosses[j]]
            if cross_x:  # Only if there are dangerous points
                ax.plot(cross_x, cross_y, 'x', color=f'C{i}', markersize=8, alpha=0.7)
        
        # Configure chart
        ax.set_xlabel('Sprocket teeth')
        ax.set_ylabel('Speed (km/h)')
        ax.set_title(f'Speeds at {cadence} RPM')
        ax.grid(True)
        ax.legend()
        
        # If we're in beginner mode, simplify the chart
        if not self.technical_mode.get():
            ax.set_xlabel('Sprockets (from fastest to easiest)')
            # Simplify X-axis labels
            ax.set_xticks(range(len(self.cassette_teeth)))
            ax.set_xticklabels([f"{i+1}" for i in range(len(self.cassette_teeth))])
        
        # Create canvas to display the chart
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add legend for chain crossings
        legend_frame = ttk.Frame(parent)
        legend_frame.pack(fill="x", pady=PADDING)
        
        ttk.Label(legend_frame, text="○ = Safe combinations", font=("Arial", 9)).pack(side="left", padx=PADDING)
        ttk.Label(legend_frame, text="✕ = Chain crossing combinations (avoid)", font=("Arial", 9)).pack(side="left", padx=PADDING)

    @handle_errors
    def create_development_chart(self, parent):
        """Creates a bar chart with the development of each gear, marking chain crossings"""
        # Frame with explanation
        ttk.Label(parent, text="Gear Development", 
                 font=("Arial", 12, "bold")).pack(pady=PADDING)
        
        ttk.Label(parent, text="Development indicates the distance traveled in meters for each complete pedal stroke.",
                 wraplength=800).pack(pady=PADDING)
        
        # Create figure
        fig, ax = plt.subplots(figsize=CHART_SIZE)
        
        # Define colors for each chainring
        color_map = {
            0: 'red',      # First chainring (largest)
            1: 'blue',     # Second chainring
            2: 'green'     # Third chainring (if it exists)
        }
        
        # For storing development data by chainring
        width = 0.8 / len(self.crankset_teeth)  # Bar width adjusted according to number of chainrings
        
        # For each chainring, create a set of bars
        for i, chainring in enumerate(self.crankset_teeth):
            developments = []
            safe_markers = []  # To mark safe combinations and crossings
            
            for j, sprocket in enumerate(self.cassette_teeth):
                gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
                development = gear_ratio * self.wheel_sizes[self.wheel_size_var.get()]
                developments.append(development)
                
                # Verify chain crossing
                crossing, _ = self.is_chain_crossing(i, j)
                safe_markers.append(not crossing)  # True if safe, False if crossing
            
            # Position of bars for this chainring
            bar_positions = [j + width*i for j in range(len(self.cassette_teeth))]
            
            # Create bars for safe combinations (without crossing)
            safe_dev = [dev if safe else 0 for dev, safe in zip(developments, safe_markers)]
            ax.bar(bar_positions, safe_dev, width=width, color=color_map.get(i, 'gray'), 
                  label=f"Chainring {chainring}T")
            
            # Create bars for combinations with crossing (hatched pattern)
            cross_dev = [dev if not safe else 0 for dev, safe in zip(developments, safe_markers)]
            if any(cross_dev):  # Only if there is any bar with crossing
                ax.bar(bar_positions, cross_dev, width=width, color=color_map.get(i, 'gray'), 
                      alpha=0.5, hatch='xxx')
        
        # Configure X axis
        ax.set_xticks(range(len(self.cassette_teeth)))
        ax.set_xticklabels([f"{sprocket}T" for sprocket in self.cassette_teeth])
        
        # Configure labels and title
        ax.set_xlabel('Sprocket teeth')
        ax.set_ylabel('Development (meters/pedal stroke)')
        ax.set_title('Development by chainring')
        ax.legend()
        
        # Adjust layout
        fig.tight_layout()
        
        # Create canvas to display the chart
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add legend to interpret the chart
        note_frame = ttk.Frame(parent)
        note_frame.pack(fill="x", pady=PADDING)
        
        note_text = """
        • Solid bars represent safe combinations.
        • Bars with pattern (xxx) and semi-transparent represent combinations with chain crossing.
        • Higher development = greater distance traveled per pedal stroke (more "hard" to pedal).
        • Lower development = less distance traveled per pedal stroke (more "light" to pedal).
        """
        
        note_label = ttk.Label(note_frame, text=note_text, wraplength=800, justify="left")
        note_label.pack(fill="x", expand=True, padx=PADDING)
        
        # Add warning about chain crossing
        warning_frame = ttk.Frame(parent)
        warning_frame.pack(fill="x", pady=PADDING)
        
        warning_icon = ttk.Label(warning_frame, text="⚠️", font=("Arial", 12))
        warning_icon.pack(side="left", padx=(0, PADDING))
        
        warning_text = "Combinations marked with patterns (xxx) cause 'chain crossing', "
        warning_text += "which increases component wear and reduces efficiency. "
        warning_text += "It is recommended to avoid these combinations for prolonged periods."
        
        warning_label = ttk.Label(warning_frame, text=warning_text, 
                                wraplength=800, justify="left")
        warning_label.pack(side="left", fill="x", expand=True)

    @handle_errors
    def setup_recom_tab(self, parent):
        """Configures the recommendations tab"""
        # If there is no configuration, show message
        if not self.crankset_teeth or not self.cassette_teeth:
            ttk.Label(parent, text="Please configure your bicycle first in the 'My Bicycle' tab",
                     font=("Arial", 12)).pack(pady=LARGE_PADDING)
            return
        
        # Create title
        ttk.Label(parent, text="Which gear should I use?", 
                 font=("Arial", 14, "bold")).pack(pady=PADDING)
        
        # Main panel
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=LARGE_PADDING, pady=PADDING)
        
        # Left panel - Form
        form_frame = ttk.LabelFrame(main_frame, text="What is your route like?")
        form_frame.pack(side="left", fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Desired speed
        ttk.Label(form_frame, text="Desired speed (km/h):").pack(anchor="w", pady=PADDING)
        
        self.target_speed_var = tk.StringVar(value="20")
        speed_frame = ttk.Frame(form_frame)
        speed_frame.pack(fill="x", pady=PADDING, padx=LARGE_PADDING)
        
        ttk.Scale(speed_frame, from_=5, to=50, orient="horizontal", 
                 variable=self.target_speed_var, length=200,
                 command=lambda s: self.target_speed_var.set(str(int(float(s))))).pack(side="left")
        
        ttk.Label(speed_frame, textvariable=self.target_speed_var).pack(side="left", padx=PADDING)
        ttk.Label(speed_frame, text="km/h").pack(side="left")
        
        # Slope
        ttk.Label(form_frame, text="Slope (%):").pack(anchor="w", pady=PADDING)
        
        self.slope_var = tk.StringVar(value="0")
        slope_frame = ttk.Frame(form_frame)
        slope_frame.pack(fill="x", pady=PADDING, padx=LARGE_PADDING)
        
        ttk.Scale(slope_frame, from_=-10, to=20, orient="horizontal", 
                 variable=self.slope_var, length=200,
                 command=lambda s: self.slope_var.set(str(int(float(s))))).pack(side="left")
        
        ttk.Label(slope_frame, textvariable=self.slope_var).pack(side="left", padx=PADDING)
        ttk.Label(slope_frame, text="%").pack(side="left")
        
        # Slope description
        slope_desc = ttk.Label(form_frame, text="0% = flat terrain, positive values = uphill, negative values = downhill", 
                             font=("Arial", 9, "italic"))
        slope_desc.pack(anchor="w", padx=LARGE_PADDING)
        
        # Button to calculate
        ttk.Button(form_frame, text="Calculate recommended gear", 
                  command=self.calculate_recommended_gear).pack(pady=LARGE_PADDING)
        
        # Right panel - Results
        self.results_frame = ttk.LabelFrame(main_frame, text="Recommendation")
        self.results_frame.pack(side="right", fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Initial message
        ttk.Label(self.results_frame, text="Complete the form and press 'Calculate' to get\na gear recommendation.",
                 wraplength=400).pack(pady=LARGE_PADDING)

    @handle_errors
    def calculate_recommended_gear(self):
        """Calculates and displays the recommended gear according to parameters, avoiding chain crossings"""
        # Clear results panel
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Get parameters
        target_speed = float(self.target_speed_var.get())
        slope = float(self.slope_var.get())
        cadence = int(self.cadencia_var.get())
        
        # Calculate all gears and their speeds, avoiding chain crossings
        best_chainring = None
        best_sprocket = None
        min_diff = float('inf')
        
        for i, chainring in enumerate(self.crankset_teeth):
            for j, sprocket in enumerate(self.cassette_teeth):
                # Verify if this combination crosses the chain
                crossing, _ = self.is_chain_crossing(i, j)
                if crossing:
                    continue  # Skip this combination
                
                gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
                speed = self.calculate_speed(gear_ratio, cadence)
                
                # Adjust speed according to slope (simplification)
                adjusted_speed = speed * (1 - slope/100 * 0.1)
                
                # Find the gear closest to the desired speed
                diff = abs(adjusted_speed - target_speed)
                if diff < min_diff:
                    min_diff = diff
                    best_chainring = chainring
                    best_sprocket = sprocket
        
        # If we didn't find any valid gear (all cross the chain), find the smallest difference regardless of crossings
        if best_chainring is None:
            min_diff = float('inf')
            for i, chainring in enumerate(self.crankset_teeth):
                for j, sprocket in enumerate(self.cassette_teeth):
                    gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
                    speed = self.calculate_speed(gear_ratio, cadence)
                    
                    # Adjust speed according to slope
                    adjusted_speed = speed * (1 - slope/100 * 0.1)
                    
                    diff = abs(adjusted_speed - target_speed)
                    if diff < min_diff:
                        min_diff = diff
                        best_chainring = chainring
                        best_sprocket = sprocket
                        best_i = i
                        best_j = j
            
            # Verify if the best option crosses the chain
            crossing, crossing_message = self.is_chain_crossing(best_i, best_j)
        else:
            crossing = False
            crossing_message = None
        
        # Show recommendation
        if best_chainring and best_sprocket:
            gear_ratio = self.calculate_gear_ratio(best_chainring, best_sprocket)
            actual_speed = self.calculate_speed(gear_ratio, cadence)
            
            # Title with recommendation
            ttk.Label(self.results_frame, text=f"Recommended gear: {best_chainring}T / {best_sprocket}T", 
                     font=("Arial", 14, "bold")).pack(pady=PADDING)
            
            # Visual explanation (simple)
            chainring_idx = self.crankset_teeth.index(best_chainring) + 1
            sprocket_idx = self.cassette_teeth.index(best_sprocket) + 1
            
            if len(self.crankset_teeth) == 3:  # Triple chainring
                chainring_desc = "small" if chainring_idx == 3 else ("middle" if chainring_idx == 2 else "large")
            elif len(self.crankset_teeth) == 2:  # Double chainring
                chainring_desc = "small" if chainring_idx == 2 else "large"
            else:
                chainring_desc = f"#{chainring_idx}"
                
            ttk.Label(self.results_frame, text=f"Use the {chainring_desc} chainring (of {len(self.crankset_teeth)}) and sprocket #{sprocket_idx} (of {len(self.cassette_teeth)})",
                     wraplength=400).pack(pady=PADDING)
            
            # Technical details
            details_frame = ttk.Frame(self.results_frame)
            details_frame.pack(fill="x", pady=PADDING)
            
            ttk.Label(details_frame, text=f"Estimated speed:").grid(row=0, column=0, sticky="w", padx=PADDING)
            ttk.Label(details_frame, text=f"{actual_speed:.1f} km/h").grid(row=0, column=1, sticky="e")
            
            ttk.Label(details_frame, text=f"Gear ratio:").grid(row=1, column=0, sticky="w", padx=PADDING)
            ttk.Label(details_frame, text=f"{gear_ratio:.2f}").grid(row=1, column=1, sticky="e")
            
            ttk.Label(details_frame, text=f"Development:").grid(row=2, column=0, sticky="w", padx=PADDING)
            development = gear_ratio * self.wheel_sizes[self.wheel_size_var.get()]
            ttk.Label(details_frame, text=f"{development:.2f} meters/pedal stroke").grid(row=2, column=1, sticky="e")
            
            # Show warning if it crosses the chain
            if crossing:
                warning_frame = ttk.Frame(self.results_frame)
                warning_frame.pack(fill="x", pady=PADDING)
                
                warning_icon = ttk.Label(warning_frame, text="⚠️", font=("Arial", 12), foreground="red")
                warning_icon.pack(side="left", padx=(0, PADDING))
                
                warning_text = "WARNING: This combination crosses the chain. "
                warning_text += "No optimal combination was found that does not cross the chain for the specified speed and slope. "
                warning_text += "It is recommended to use this gear only briefly and adjust the target speed."
                
                warning_label = ttk.Label(warning_frame, text=warning_text, 
                                       wraplength=400, foreground="red", justify="left")
                warning_label.pack(side="left")
            
            # Tips according to slope
            if slope > 8:
                advice = "For steep slopes, maintain a high cadence and use lighter gears to avoid straining your knees."
            elif slope > 0:
                advice = "Maintain a constant cadence. If you feel you're exerting too much force, switch to a lighter gear."
            elif slope < -5:
                advice = "On descents, you can use harder gears or simply stop pedaling if the speed is high."
            else:
                advice = "On flat terrain, try to maintain a comfortable cadence (80-90 RPM) and adjust the gear according to the wind and your physical condition."
            
            ttk.Label(self.results_frame, text="Tip:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(PADDING, 0))
            ttk.Label(self.results_frame, text=advice, wraplength=400).pack(anchor="w", padx=PADDING)

    @handle_errors
    def setup_tech_tab(self, parent):
        """Configures the technical analysis tab"""
        # Title
        ttk.Label(parent, text="Technical Analysis", 
                 font=("Arial", 14, "bold")).pack(pady=PADDING)
        
        # Explanation
        ttk.Label(parent, text="This tab contains technical analyses for experienced cyclists.",
                 wraplength=800).pack(pady=PADDING)
        
        # If there is no configuration, show message
        if not self.crankset_teeth or not self.cassette_teeth:
            ttk.Label(parent, text="Please configure your bicycle first in the 'My Bicycle' tab",
                     font=("Arial", 12)).pack(pady=LARGE_PADDING)
            return
        
        # Create notebook for analysis techniques
        tech_notebook = ttk.Notebook(parent)
        tech_notebook.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Gear ratio tab
        ratio_tab = ttk.Frame(tech_notebook)
        tech_notebook.add(ratio_tab, text="Gear ratio")
        
        # Cadence vs power tab
        power_tab = ttk.Frame(tech_notebook)
        tech_notebook.add(power_tab, text="Cadence vs Power")
        
        # Overlap tab (gear overlap)
        overlap_tab = ttk.Frame(tech_notebook)
        tech_notebook.add(overlap_tab, text="Overlap")
        
        # Configure each technical tab
        self.setup_ratio_tab(ratio_tab)
        self.setup_power_tab(power_tab)
        self.setup_overlap_tab(overlap_tab)

    @handle_errors
    def setup_ratio_tab(self, parent):
        """Configures the technical tab for gear ratio"""
        # Create title
        ttk.Label(parent, text="Gear ratio analysis", 
                 font=("Arial", 12, "bold")).pack(pady=PADDING)
        
        # Create chart
        fig, ax = plt.subplots(figsize=CHART_SIZE)
        
        # Prepare data
        combinations = []
        ratios = []
        colors = []
        
        color_map = {
            0: 'red',      # First chainring (largest)
            1: 'blue',     # Second chainring
            2: 'green'     # Third chainring (if it exists)
        }
        
        for i, chainring in enumerate(self.crankset_teeth):
            for sprocket in self.cassette_teeth:
                combinations.append(f"{chainring}/{sprocket}")
                gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
                ratios.append(gear_ratio)
                colors.append(color_map.get(i, 'gray'))
        
        # Create bar chart
        bars = ax.bar(combinations, ratios, color=colors)
        
        # Reference lines for optimal range
        ax.axhline(y=2.5, color='gray', linestyle='--', alpha=0.5)
        ax.axhline(y=5.0, color='gray', linestyle='--', alpha=0.5)
        
        # Configure chart
        ax.set_xlabel('Combination (chainring/sprocket)')
        ax.set_ylabel('Gear ratio')
        ax.set_title('Gear ratio by combination')
        ax.tick_params(axis='x', rotation=90)
        
        # Legend for colors
        legend_elements = []
        for i, chainring in enumerate(self.crankset_teeth):
            legend_elements.append(plt.Line2D([0], [0], color=color_map.get(i, 'gray'), lw=4, label=f'Chainring {chainring}T'))
        legend_elements.append(plt.Line2D([0], [0], color='gray', linestyle='--', label='Optimal range (2.5-5.0)'))
        ax.legend(handles=legend_elements)
        
        # Adjust layout
        fig.tight_layout()
        
        # Create canvas to display the chart
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Technical explanation
        explanation = """
        The gear ratio is the number of teeth on the chainring divided by the number of teeth on the sprocket. 
        A higher value indicates a "harder" gear (for speed), while a lower value indicates a "lighter" gear (for climbing).
        
        In general:
        • Values > 5.0: Very hard gears for descents or speed
        • Values 2.5-5.0: Optimal range for normal use
        • Values < 2.5: Light gears for climbing
        
        The total range of ratios on your bicycle directly affects its versatility.
        """
        
        explanation_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=6)
        explanation_text.pack(fill="x", expand=False, padx=PADDING, pady=PADDING)
        explanation_text.insert(tk.END, explanation)
        explanation_text.config(state="disabled")

    @handle_errors
    def setup_power_tab(self, parent):
        """Configures the technical tab for cadence vs power"""
        # Create title
        ttk.Label(parent, text="Relationship between cadence, speed, and power", 
                 font=("Arial", 12, "bold")).pack(pady=PADDING)
        
        # Create panel for controls
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill="x", padx=PADDING, pady=PADDING)
        
        # Chainring/sprocket selector
        ttk.Label(control_frame, text="Chainring:").grid(row=0, column=0, padx=PADDING)
        self.power_plato_var = tk.StringVar(value=str(self.crankset_teeth[0]))
        plato_combo = ttk.Combobox(control_frame, textvariable=self.power_plato_var, 
                                   values=[str(t) for t in self.crankset_teeth], width=5)
        plato_combo.grid(row=0, column=1, padx=PADDING)
        
        ttk.Label(control_frame, text="Sprocket:").grid(row=0, column=2, padx=PADDING)
        self.power_piñon_var = tk.StringVar(value=str(self.cassette_teeth[len(self.cassette_teeth)//2]))
        piñon_combo = ttk.Combobox(control_frame, textvariable=self.power_piñon_var, 
                                   values=[str(t) for t in self.cassette_teeth], width=5)
        piñon_combo.grid(row=0, column=3, padx=PADDING)
        
        ttk.Button(control_frame, text="Update chart", 
                  command=lambda: self.update_power_chart(chart_frame)).grid(row=0, column=4, padx=LARGE_PADDING)
        
        # Frame for chart
        chart_frame = ttk.Frame(parent)
        chart_frame.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Create initial chart
        self.update_power_chart(chart_frame)
        
        # Technical explanation
        explanation = """
        This chart shows the relationship between cadence, speed, and estimated power for a specific chainring/sprocket combination.
        
        The power is an estimate based on a simplified model, considering the aerodynamic resistance that increases exponentially with speed.
        
        Key observations:
        • For the same gear, increasing cadence linearly increases speed
        • Power required increases exponentially with speed
        • The optimal cadence is usually between 80-90 RPM for most cyclists
        • At very low cadences (<60 RPM) you strain your joints more, while very high cadences (>100 RPM) are less energy efficient
        """
        
        explanation_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=8)
        explanation_text.pack(fill="x", expand=False, padx=PADDING, pady=PADDING)
        explanation_text.insert(tk.END, explanation)
        explanation_text.config(state="disabled")

    @handle_errors
    def update_power_chart(self, parent):
        """Updates the power vs cadence chart"""
        # Clear frame
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Get selected values
        try:
            chainring = int(self.power_plato_var.get())
            sprocket = int(self.power_piñon_var.get())
        except ValueError:
            messagebox.showwarning("Invalid value", "Please select valid numerical values")
            return
        
        # Create figure with two Y axes
        fig, ax1 = plt.subplots(figsize=CHART_SIZE)
        ax2 = ax1.twinx()
        
        # Range of cadences to evaluate
        cadences = np.arange(60, 110, 2)
        
        # Calculate speeds and powers for each cadence
        gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
        speeds = []
        powers = []
        
        for cadence in cadences:
            speed = self.calculate_speed(gear_ratio, cadence)
            speeds.append(speed)
            powers.append(self.calculate_power_estimate(speed))
        
        # Optimal cadence zone
        optimal_min_idx = np.abs(cadences - OPTIMAL_CADENCE_MIN).argmin()
        optimal_max_idx = np.abs(cadences - OPTIMAL_CADENCE_MAX).argmin()
        
        # Plot speed vs cadence
        line1, = ax1.plot(cadences, speeds, 'b-', label='Speed')
        ax1.fill_between(cadences[optimal_min_idx:optimal_max_idx+1], 
                        0, max(speeds)*1.1, 
                        color='gray', alpha=0.1, label='Optimal cadence range')
        
        # Plot power vs cadence
        line2, = ax2.plot(cadences, powers, 'r-', label='Estimated power')
        
        # Configure axes
        ax1.set_xlabel('Cadence (RPM)')
        ax1.set_ylabel('Speed (km/h)', color='b')
        ax1.tick_params(axis='y', labelcolor='b')
        
        ax2.set_ylabel('Estimated power (relative units)', color='r')
        ax2.tick_params(axis='y', labelcolor='r')
        
        # Title
        plt.title(f'Speed and power for combination {chainring}T / {sprocket}T')
        
        # Combined legend
        lines = [line1, line2]
        labels = [line.get_label() for line in lines]
        ax1.legend(lines, labels, loc='upper left')
        
        # Adjust layout
        fig.tight_layout()
        
        # Show chart
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    @handle_errors
    def setup_overlap_tab(self, parent):
        """Configures the technical tab for gear overlap"""
        # Create title
        ttk.Label(parent, text="Gear overlap analysis", 
                 font=("Arial", 12, "bold")).pack(pady=PADDING)
        
        # Create chart
        fig, ax = plt.subplots(figsize=CHART_SIZE)
        
        # Prepare data
        all_ratios = []
        colors = []
        labels = []
        
        color_map = {
            0: 'red',
            1: 'blue',
            2: 'green'
        }
        
        # Markers for chain crossings
        crosses = []
        
        # Calculate ratios for each chainring
        for i, chainring in enumerate(self.crankset_teeth):
            ratios = []
            cross_positions = []
            for j, sprocket in enumerate(self.cassette_teeth):
                gear_ratio = self.calculate_gear_ratio(chainring, sprocket)
                ratios.append(gear_ratio)
                
                # Verify chain crossing
                crossing, _ = self.is_chain_crossing(i, j)
                cross_positions.append(crossing)
            
            # Add to chart
            line, = ax.plot(range(len(self.cassette_teeth)), ratios, '-', 
                    color=color_map.get(i, 'gray'), label=f"Chainring {chainring}T")
            
            # Mark points without chain crossing
            safe_x = [j for j in range(len(self.cassette_teeth)) if not cross_positions[j]]
            safe_y = [ratios[j] for j in range(len(ratios)) if not cross_positions[j]]
            ax.plot(safe_x, safe_y, 'o', color=color_map.get(i, 'gray'))
            
            # Mark points with chain crossing
            cross_x = [j for j in range(len(self.cassette_teeth)) if cross_positions[j]]
            cross_y = [ratios[j] for j in range(len(ratios)) if cross_positions[j]]
            if cross_x:
                ax.plot(cross_x, cross_y, 'x', color=color_map.get(i, 'gray'), markersize=8, alpha=0.7)
            
            # Save for overlap analysis
            all_ratios.append(ratios)
            crosses.append(cross_positions)
        
        # Configure chart
        ax.set_xlabel('Sprocket position')
        ax.set_ylabel('Gear ratio')
        ax.set_title('Overlap between chainrings')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # X-axis labels
        ax.set_xticks(range(len(self.cassette_teeth)))
        ax.set_xticklabels([str(t) for t in self.cassette_teeth])
        
        # Legend
        legend_elements = []
        for i, chainring in enumerate(self.crankset_teeth):
            legend_elements.append(plt.Line2D([0], [0], color=color_map.get(i, 'gray'), lw=2, label=f'Chainring {chainring}T'))
        
        # Add legend for chain crossings
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='gray', linestyle='None', label='Safe combination'))
        legend_elements.append(plt.Line2D([0], [0], marker='x', color='gray', linestyle='None', label='Chain crossing'))
        
        ax.legend(handles=legend_elements)
        
        # Adjust layout
        fig.tight_layout()
        
        # Create canvas to display the chart
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Panel for overlap analysis
        overlap_frame = ttk.LabelFrame(parent, text="Overlap analysis")
        overlap_frame.pack(fill="x", padx=PADDING, pady=PADDING)
        
        # Calculate and show overlap
        overlap_text = self.calculate_overlap_analysis(all_ratios, crosses)
        
        overlap_info = scrolledtext.ScrolledText(overlap_frame, wrap=tk.WORD, height=8)
        overlap_info.pack(fill="x", expand=False, padx=PADDING, pady=PADDING)
        overlap_info.insert(tk.END, overlap_text)
        overlap_info.config(state="disabled")

    @handle_errors
    def calculate_overlap_analysis(self, all_ratios, crosses=None):
        """
        Calculates and prepares a gear overlap analysis
        
        Args:
            all_ratios: List of lists with the ratios of each chainring
            crosses: List of lists with the chain crossings (optional)
        """
        if len(all_ratios) <= 1:
            return "At least two chainrings are needed to analyze overlap."
        
        result = "Overlap analysis between chainrings:\n\n"
        
        # Analyze overlap between adjacent chainrings
        for i in range(len(all_ratios) - 1):
            chainring1 = self.crankset_teeth[i]
            chainring2 = self.crankset_teeth[i + 1]
            
            ratios1 = all_ratios[i]
            ratios2 = all_ratios[i + 1]
            
            # If we have crossing information, filter the ratios
            if crosses:
                # Filter ratios from chainring 1 that don't cross the chain
                filtered_ratios1 = [ratios1[j] for j in range(len(ratios1)) if not crosses[i][j]]
                # Filter ratios from chainring 2 that don't cross the chain
                filtered_ratios2 = [ratios2[j] for j in range(len(ratios2)) if not crosses[i+1][j]]
                
                # If there are no valid gears after filtering, use the originals
                if filtered_ratios1 and filtered_ratios2:
                    min_ratio1 = min(filtered_ratios1)
                    max_ratio1 = max(filtered_ratios1)
                    min_ratio2 = min(filtered_ratios2)
                    max_ratio2 = max(filtered_ratios2)
                    
                    result += f"Between chainring {chainring1}T and {chainring2}T (without chain crossings):\n"
                else:
                    min_ratio1 = min(ratios1)
                    max_ratio1 = max(ratios1)
                    min_ratio2 = min(ratios2)
                    max_ratio2 = max(ratios2)
                    
                    result += f"Between chainring {chainring1}T and {chainring2}T (including chain crossings):\n"
            else:
                min_ratio1 = min(ratios1)
                max_ratio1 = max(ratios1)
                min_ratio2 = min(ratios2)
                max_ratio2 = max(ratios2)
                
                result += f"Between chainring {chainring1}T and {chainring2}T:\n"
            
            # Calculate overlap
            overlap_start = max(min_ratio1, min_ratio2)
            overlap_end = min(max_ratio1, max_ratio2)
            
            if overlap_start <= overlap_end:
                overlap_pct = (overlap_end - overlap_start) / (max_ratio1 - min_ratio1) * 100
                result += f"- Overlap range: {overlap_start:.2f} to {overlap_end:.2f}\n"
                result += f"- Overlap percentage: {overlap_pct:.1f}%\n"
                
                if overlap_pct < 10:
                    result += "- Evaluation: Low overlap. There may be 'gaps' when changing chainrings.\n"
                elif overlap_pct < 30:
                    result += "- Evaluation: Moderate overlap. Balanced configuration.\n"
                else:
                    result += "- Evaluation: High overlap. There are many redundant gears.\n"
            else:
                result += f"- There is no overlap between usable gears.\n"
                
            result += "\n"
        
        # General range analysis
        if crosses:
            # Get ratios without chain crossings
            all_filtered_ratios = []
            for i, ratios in enumerate(all_ratios):
                filtered = [ratios[j] for j in range(len(ratios)) if not crosses[i][j]]
                if filtered:
                    all_filtered_ratios.extend(filtered)
            
            if all_filtered_ratios:
                min_ratio = min(all_filtered_ratios)
                max_ratio = max(all_filtered_ratios)
                range_ratio = max_ratio / min_ratio
                
                result += f"Total gear range (without chain crossings): {range_ratio:.2f}x\n"
            else:
                result += "Cannot calculate range without chain crossings.\n"
        
        # Also calculate total range including crossings
        all_ratios_flat = [ratio for sublist in all_ratios for ratio in sublist]
        min_ratio = min(all_ratios_flat)
        max_ratio = max(all_ratios_flat)
        range_ratio = max_ratio / min_ratio
        
        result += f"Total gear range (including chain crossings): {range_ratio:.2f}x\n"
        
        if range_ratio < 3:
            result += "Evaluation: Limited range. Suitable for uniform terrain or specific use."
        elif range_ratio < 5:
            result += "Evaluation: Moderate range. Good for general use."
        else:
            result += "Evaluation: Wide range. Excellent versatility for different terrains."
        
        return result

    @handle_errors
    def update_tech_tab(self):
        """Updates the technical tab if there are changes in the configuration"""
        if self.validate_gear_configuration():
            for widget in self.tech_tab.winfo_children():
                widget.destroy()
            self.setup_scrollable_frame(self.tech_tab, self.setup_tech_tab)

    def show_basic_concepts(self):
        """Shows a window with basic cycling concepts"""
        concepts_window = tk.Toplevel(self.root)
        concepts_window.title("Basic cycling concepts")
        concepts_window.geometry("600x500")
        
        # Content
        ttk.Label(concepts_window, text="Basic cycling concepts", 
                 font=("Arial", 14, "bold")).pack(pady=PADDING)
        
        # Text with scroll
        content = scrolledtext.ScrolledText(concepts_window, wrap=tk.WORD)
        content.pack(fill="both", expand=True, padx=LARGE_PADDING, pady=PADDING)
        
        concepts_text = """
        TRANSMISSION AND GEARS
        
        Chainrings (or crowns): These are the toothed discs attached to the pedals. They determine how much force is transmitted to the chain.
        - Large chainrings (more teeth): Higher speed, require more force
        - Small chainrings (fewer teeth): Lower speed, easier pedaling
        
        Sprockets (or cassette): Set of toothed discs on the rear wheel.
        - Small sprockets (fewer teeth): Higher speed, require more force
        - Large sprockets (more teeth): Lower speed, easier pedaling
        
        Gear ratio: Number of teeth on the chainring divided by the number of teeth on the sprocket. Indicates how many turns the wheel makes for each complete revolution of the pedals.
        
        Development: Distance traveled for each complete pedal stroke. It is calculated by multiplying the gear ratio by the wheel circumference.
        
        PEDALING CONCEPTS
        
        Cadence: The speed at which you pedal, measured in revolutions per minute (RPM).
        - Low cadence (<70 RPM): Greater effort on each pedal stroke, more tension on joints
        - Medium cadence (70-90 RPM): Optimal balance for most cyclists
        - High cadence (>90 RPM): Less effort per pedal stroke, higher heart rate
        
        CHAIN CROSSING
        
        Chain crossing occurs when using extreme combinations:
        - Large chainring (front) with large sprocket (rear)
        - Small chainring (front) with small sprocket (rear)
        
        These combinations cause the chain to work at a pronounced diagonal angle, causing:
        - Increased wear on the chain, chainrings, sprockets, and derailleur
        - Loss of efficiency (you waste energy when pedaling)
        - More noise during pedaling
        - Risk of the chain coming off or getting damaged
        
        That's why, in this application, these combinations are marked or filtered.
        The golden rule is: use combinations where the chain works as straight as possible.
        
        PROPER USE OF GEARS
        
        Basic principles:
        1. Maintain a constant and comfortable cadence by adjusting gears
        2. Anticipate terrain changes and shift before you need to
        3. Avoid extreme combinations (chain crossing)
        4. Shift sequentially, don't skip many gears at once
        
        Specific situations:
        - Climbs: Use small chainrings and large sprockets to pedal with less effort
        - Descents: Use large chainrings and small sprockets or stop pedaling if speed is high
        - Flat terrain: Find a combination that allows you to maintain your ideal cadence
        """
        
        content.insert(tk.END, concepts_text)
        content.config(state="disabled")
        
        # Button to close
        ttk.Button(concepts_window, text="Close", 
                  command=concepts_window.destroy).pack(pady=PADDING)

    def show_app_help(self):
        """Shows a window with help on using the application"""
        help_window = tk.Toplevel(self.root)
        help_window.title("How to use the application")
        help_window.geometry("600x500")
        
        # Content
        ttk.Label(help_window, text="How to use this application", 
                 font=("Arial", 14, "bold")).pack(pady=PADDING)
        
        # Text with scroll
        content = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        content.pack(fill="both", expand=True, padx=LARGE_PADDING, pady=PADDING)
        
        help_text = """
        QUICK USAGE GUIDE
        
        1. CONFIGURING YOUR BICYCLE (Tab "My Bicycle")
           - Select the bicycle type most similar to yours
           - Adjust the wheel size accordingly
           - Set your usual cadence (if you're not sure, leave the default value)
           - If you know exactly the configuration of your bicycle, use "Configure manually"
           - Press "Visualize my bicycle" to continue
        
        2. VISUALIZATION (Tab "Visualization")
           - Explore the "Gear table" to see what speed you'll reach with each combination
           - Review the "Speed chart" to understand how each sprocket affects your speed
           - Observe the "Development" to understand the distance traveled per pedal stroke
        
        3. RECOMMENDATIONS (Tab "Which Gear to Use?")
           - Set your desired speed and the slope of the terrain
           - Get a personalized recommendation of which gear to use
           - Read the specific tips for your situation
        
        4. TECHNICAL ANALYSIS (Only in technical mode)
           - Explore advanced analyses such as gear ratio, power, and overlap
           - Useful for experienced cyclists who want to optimize their technique
        
        MODE CHANGE
        
        - Beginner Mode: Simplified interface with basic concepts
        - Technical/Sport Mode: Access to advanced analyses and technical terms
        
        GENERAL TIPS
        
        - Experiment with different configurations to better understand how gears work
        - Use the recommendations tab before going for a ride to plan which gears to use
        - Consult the help or basic concepts if any term is unfamiliar to you
        """
        
        content.insert(tk.END, help_text)
        content.config(state="disabled")
        
        # Button to close
        ttk.Button(help_window, text="Close", 
                  command=help_window.destroy).pack(pady=PADDING)

    def show_about(self):
        """Shows information about the application"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("400x300")
        
        # Content
        ttk.Label(about_window, text="Bicycle Speed Calculator", 
                 font=("Arial", 14, "bold")).pack(pady=PADDING)
        
        ttk.Label(about_window, text="Version 1.0", 
                 font=("Arial", 10, "italic")).pack()
        
        ttk.Label(about_window, text="""
        The term "Ñu-sui" means "cyclist" in Zapoteco, a native language
        from Oaxaca, Mexico.
        An educational tool for cyclists of all levels.
        
        This application helps you understand and optimize the use of your
        bicycle gears to improve your pedaling experience.
        
        Developed with Python and Tkinter by Gustavo Mondragón.
        For questions and suggestions, email me! gustavms93@gmail.com.
        """, wraplength=350, justify="center").pack(pady=LARGE_PADDING)
        
        # Button to close
        ttk.Button(about_window, text="Close", 
                  command=about_window.destroy).pack(pady=PADDING)

# Function to start the application
def start_app():
    root = tk.Tk()
    app = NuSui(root)
    root.mainloop()

if __name__ == "__main__":
    start_app()