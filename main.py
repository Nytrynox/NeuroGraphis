import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog, scrolledtext
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree
from networkx.algorithms import isomorphism
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import webbrowser
import tempfile
import os
import json
from matplotlib.cm import get_cmap
import random
import colorsys

class NeuroGraphisApp:
    def __init__(self, root):
        # Initialize main graph
        self.G = nx.Graph()
        self.root = root
        self.root.title("NeuroGraphis - Advanced Graph Theory Visualization")
        self.root.geometry("1200x700")
        self.root.configure(bg='#1e1e1e')  # VS Code-like dark theme
        self.setup_styles()
        
        # Initialize algorithm settings
        self.start_node = tk.StringVar(value="0")
        self.algorithm_output = ""
        self.pos = None
        self.current_theme = "dark"
        self.node_color = "#36c6f4"  # Default cyan-blue
        self.edge_color = "#cccccc"  # Default light gray
        
        # Create main frames
        self.create_menu()
        self.create_sidebar()
        self.create_main_area()
        self.create_status_bar()
        
        # Add some sample data for demo
        self.load_sample_graph()
        
    def setup_styles(self):
        # Configure ttk styles for VS Code-like appearance
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define colors
        bg_color = '#1e1e1e'  # VS Code dark background
        fg_color = '#cccccc'  # Light gray text
        select_bg = '#264f78'  # Selection blue
        button_bg = '#333333'  # Button background
        entry_bg = '#3c3c3c'  # Input background
        
        # Configure styles
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TButton', background=button_bg, foreground=fg_color, borderwidth=1)
        style.configure('TEntry', fieldbackground=entry_bg, foreground=fg_color)
        style.configure('Treeview', background=bg_color, fieldbackground=bg_color, foreground=fg_color)
        style.map('Treeview', background=[('selected', select_bg)])
        style.configure('TNotebook', background=bg_color)
        style.configure('TNotebook.Tab', background=button_bg, foreground=fg_color, padding=[10, 2])
        style.map('TNotebook.Tab', background=[('selected', bg_color)], foreground=[('selected', '#ffffff')])
        
        # Configure statusbar style
        style.configure('Status.TLabel', background='#007acc', foreground='white', padding=2)
    
    def create_menu(self):
        menubar = tk.Menu(self.root, bg='#333333', fg='white', activebackground='#3c3c3c', activeforeground='white', borderwidth=0)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#333333', fg='white', activebackground='#3c3c3c', activeforeground='white')
        file_menu.add_command(label="New Graph", command=self.new_graph)
        file_menu.add_command(label="Open Graph...", command=self.open_graph)
        file_menu.add_command(label="Save Graph...", command=self.save_graph)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg='#333333', fg='white', activebackground='#3c3c3c', activeforeground='white')
        edit_menu.add_command(label="Clear All Edges", command=self.clear_graph)
        edit_menu.add_command(label="Remove Selected Edge", command=self.remove_edge)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg='#333333', fg='white', activebackground='#3c3c3c', activeforeground='white')
        view_menu.add_command(label="2D Visualization", command=self.show_graph)
        view_menu.add_command(label="3D Visualization", command=self.show_3d)
        
        # 3D effects submenu
        effects_menu = tk.Menu(view_menu, tearoff=0, bg='#333333', fg='white', activebackground='#3c3c3c', activeforeground='white')
        effects_menu.add_command(label="Sphere Layout", command=lambda: self.show_3d(layout="sphere"))
        effects_menu.add_command(label="Force-Directed", command=lambda: self.show_3d(layout="force"))
        effects_menu.add_command(label="Spiral Layout", command=lambda: self.show_3d(layout="spiral"))
        effects_menu.add_command(label="Grid Layout", command=lambda: self.show_3d(layout="grid"))
        view_menu.add_cascade(label="3D Effects", menu=effects_menu)
        
        view_menu.add_separator()
        theme_menu = tk.Menu(view_menu, tearoff=0, bg='#333333', fg='white', activebackground='#3c3c3c', activeforeground='white')
        theme_menu.add_command(label="Dark Theme", command=lambda: self.set_theme("dark"))
        theme_menu.add_command(label="Light Theme", command=lambda: self.set_theme("light"))
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Algorithms menu
        alg_menu = tk.Menu(menubar, tearoff=0, bg='#333333', fg='white', activebackground='#3c3c3c', activeforeground='white')
        alg_menu.add_command(label="Run All Algorithms", command=self.show_algorithms)
        alg_menu.add_separator()
        alg_menu.add_command(label="Dijkstra's Shortest Path", command=lambda: self.run_single_algorithm("dijkstra"))
        alg_menu.add_command(label="Kruskal's MST", command=lambda: self.run_single_algorithm("kruskal"))
        alg_menu.add_command(label="Prim's MST", command=lambda: self.run_single_algorithm("prim"))
        alg_menu.add_command(label="Eulerian Path", command=lambda: self.run_single_algorithm("eulerian"))
        alg_menu.add_command(label="Hamiltonian Path", command=lambda: self.run_single_algorithm("hamiltonian"))
        alg_menu.add_command(label="Generate Matrices", command=lambda: self.run_single_algorithm("matrices"))
        menubar.add_cascade(label="Algorithms", menu=alg_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg='#333333', fg='white', activebackground='#3c3c3c', activeforeground='white')
        help_menu.add_command(label="About NeuroGraphis", command=self.show_about)
        help_menu.add_command(label="Graph Theory Concepts", command=self.show_concepts)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_sidebar(self):
        # Create sidebar frame
        self.sidebar = ttk.Frame(self.root, style='TFrame', width=300)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.sidebar.pack_propagate(False)
        
        # Edge input section
        ttk.Label(self.sidebar, text="Add Edge", font=('Arial', 12, 'bold'), style='TLabel').pack(pady=(10, 5))
        
        input_frame = ttk.Frame(self.sidebar, style='TFrame')
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="Node U:", style='TLabel').grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_u = ttk.Entry(input_frame, width=10)
        self.entry_u.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(input_frame, text="Node V:", style='TLabel').grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_v = ttk.Entry(input_frame, width=10)
        self.entry_v.grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(input_frame, text="Weight:", style='TLabel').grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_weight = ttk.Entry(input_frame, width=10)
        self.entry_weight.grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Buttons for edge operations
        btn_frame = ttk.Frame(self.sidebar, style='TFrame')
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Add Edge", command=self.add_edge).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(btn_frame, text="Remove Edge", command=self.remove_edge).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Edge list section
        ttk.Label(self.sidebar, text="Edge List", font=('Arial', 12, 'bold'), style='TLabel').pack(pady=(15, 5))
        
        # Create Treeview for edge list
        self.edge_tree = ttk.Treeview(self.sidebar, columns=("u", "v", "weight"), show="headings", height=10)
        self.edge_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Define headings
        self.edge_tree.heading("u", text="Node U")
        self.edge_tree.heading("v", text="Node V")
        self.edge_tree.heading("weight", text="Weight")
        
        # Define columns
        self.edge_tree.column("u", width=50, anchor=tk.CENTER)
        self.edge_tree.column("v", width=50, anchor=tk.CENTER)
        self.edge_tree.column("weight", width=80, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.sidebar, orient=tk.VERTICAL, command=self.edge_tree.yview)
        self.edge_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(relx=1.0, rely=0.5, relheight=0.4, anchor='e')
        
        # Algorithm controls section
        ttk.Label(self.sidebar, text="Algorithm Settings", font=('Arial', 12, 'bold'), style='TLabel').pack(pady=(15, 5))
        
        alg_frame = ttk.Frame(self.sidebar, style='TFrame')
        alg_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(alg_frame, text="Start Node:", style='TLabel').grid(row=0, column=0, sticky=tk.W, pady=2)
        self.start_node_entry = ttk.Entry(alg_frame, width=10, textvariable=self.start_node)
        self.start_node_entry.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Visualization controls
        ttk.Label(self.sidebar, text="Visualization", font=('Arial', 12, 'bold'), style='TLabel').pack(pady=(15, 5))
        
        vis_frame = ttk.Frame(self.sidebar, style='TFrame')
        vis_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(vis_frame, text="Show 2D Graph", command=self.show_graph).pack(fill=tk.X, pady=2)
        ttk.Button(vis_frame, text="Show 3D Graph", command=self.show_3d).pack(fill=tk.X, pady=2)
        ttk.Button(vis_frame, text="Run Algorithms", command=self.show_algorithms).pack(fill=tk.X, pady=2)
    
    def create_main_area(self):
        # Create main area with notebook
        self.main_area = ttk.Frame(self.root, style='TFrame')
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook with tabs
        self.notebook = ttk.Notebook(self.main_area)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Graph visualization tab
        self.graph_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.graph_frame, text="Graph Visualization")
        
        # Create a frame for the graph canvas
        self.canvas_frame = ttk.Frame(self.graph_frame, style='TFrame')
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Algorithm results tab
        self.results_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.results_frame, text="Algorithm Results")
        
        # Create text area for algorithm results
        self.results_text = scrolledtext.ScrolledText(self.results_frame, bg='#1e1e1e', fg='#cccccc', font=('Consolas', 10))
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Matrix view tab
        self.matrix_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.matrix_frame, text="Matrix View")
        
        # Create text area for matrix display
        self.matrix_text = scrolledtext.ScrolledText(self.matrix_frame, bg='#1e1e1e', fg='#cccccc', font=('Consolas', 10))
        self.matrix_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_status_bar(self):
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, style='Status.TLabel', anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_edge_list(self):
        # Clear existing items
        for item in self.edge_tree.get_children():
            self.edge_tree.delete(item)
        
        # Add edges to the treeview
        for u, v, data in self.G.edges(data=True):
            self.edge_tree.insert("", tk.END, values=(u, v, data['weight']))
    
    def add_edge(self):
        try:
            u = int(self.entry_u.get())
            v = int(self.entry_v.get())
            w = float(self.entry_weight.get())
            
            # Check if edge already exists
            if self.G.has_edge(u, v):
                overwrite = messagebox.askyesno("Edge Exists", 
                    f"Edge ({u}, {v}) already exists with weight {self.G[u][v]['weight']}. Overwrite?")
                if not overwrite:
                    return
            
            self.G.add_edge(u, v, weight=w)
            self.entry_u.delete(0, tk.END)
            self.entry_v.delete(0, tk.END)
            self.entry_weight.delete(0, tk.END)
            
            # Update edge list
            self.update_edge_list()
            self.status_var.set(f"Added edge ({u}, {v}) with weight {w}")
            
            # Update graph visualization if it exists
            if hasattr(self, 'canvas'):
                self.show_graph()
                
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integers for nodes and a float for weight")
    
    def remove_edge(self):
        selected = self.edge_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select an edge to remove")
            return
        
        # Get the selected edge
        item = self.edge_tree.item(selected[0])
        values = item['values']
        u, v = int(values[0]), int(values[1])
        
        # Remove the edge
        if self.G.has_edge(u, v):
            self.G.remove_edge(u, v)
            self.update_edge_list()
            self.status_var.set(f"Removed edge ({u}, {v})")
            
            # Update graph visualization if it exists
            if hasattr(self, 'canvas'):
                self.show_graph()
        else:
            messagebox.showerror("Error", f"Edge ({u}, {v}) not found in the graph")
    
    def clear_graph(self):
        if messagebox.askyesno("Clear Graph", "Are you sure you want to remove all edges?"):
            self.G.clear_edges()
            self.update_edge_list()
            self.status_var.set("All edges removed")
            
            # Update graph visualization if it exists
            if hasattr(self, 'canvas'):
                self.show_graph()
    
    def new_graph(self):
        if messagebox.askyesno("New Graph", "Create a new graph? This will clear the current graph."):
            self.G = nx.Graph()
            self.update_edge_list()
            self.status_var.set("New graph created")
            
            # Clear visualization
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            
            # Clear results
            self.results_text.delete(1.0, tk.END)
            self.matrix_text.delete(1.0, tk.END)
    
    def save_graph(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Graph"
        )
        
        if not filename:
            return
        
        try:
            # Convert graph to dictionary
            data = nx.node_link_data(self.G)
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.status_var.set(f"Graph saved to {filename}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
    
    def open_graph(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Open Graph"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.G = nx.node_link_graph(data)
            self.update_edge_list()
            self.status_var.set(f"Graph loaded from {filename}")
            
            # Update visualization
            self.show_graph()
        except Exception as e:
            messagebox.showerror("Open Error", str(e))
    
    def show_graph(self):
        # Clear previous canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        if not self.G.edges():
            messagebox.showinfo("Empty Graph", "The graph has no edges to display")
            return
        
        # Create figure and plot
        fig = plt.figure(figsize=(8, 6))
        plt.clf()
        
        # Set background color based on theme
        if self.current_theme == "dark":
            fig.patch.set_facecolor('#1e1e1e')
            plt.rcParams.update({'text.color': '#cccccc', 'axes.labelcolor': '#cccccc', 
                               'xtick.color': '#cccccc', 'ytick.color': '#cccccc'})
        else:
            fig.patch.set_facecolor('#ffffff')
            plt.rcParams.update({'text.color': '#000000', 'axes.labelcolor': '#000000', 
                               'xtick.color': '#000000', 'ytick.color': '#000000'})
        
        # Create layout if not exists
        if self.pos is None:
            self.pos = nx.spring_layout(self.G)
        
        # Draw the graph
        nx.draw(self.G, self.pos, with_labels=True, node_size=700, node_color=self.node_color, 
                font_weight='bold', font_color='black', edge_color=self.edge_color, width=2)
        
        # Draw edge labels
        edge_labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=edge_labels, font_color='#ffffff' if self.current_theme == "dark" else '#000000')
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas = canvas
        
        self.status_var.set("Graph visualization updated")
    
    def show_3d(self, layout="force"):
        if not self.G.edges():
            messagebox.showinfo("Empty Graph", "The graph has no edges to display")
            return
        
        # Generate 3D positions based on selected layout
        if layout == "sphere":
            pos = self.generate_sphere_layout()
        elif layout == "spiral":
            pos = self.generate_spiral_layout()
        elif layout == "grid":
            pos = self.generate_grid_layout()
        else:  # force layout
            pos = nx.spring_layout(self.G, dim=3)
        
        # Create edge traces
        edge_traces = []
        for edge in self.G.edges():
            x0, y0, z0 = pos[edge[0]]
            x1, y1, z1 = pos[edge[1]]
            
            # Get edge weight for color and width
            weight = self.G[edge[0]][edge[1]]['weight']
            max_weight = max([d['weight'] for _, _, d in self.G.edges(data=True)])
            width = 2 + (weight / max_weight) * 8  # Scale width between 2 and 10
            
            # Use color gradient based on weight
            color = self.get_color_for_weight(weight, max_weight)
            
            edge_trace = go.Scatter3d(
                x=[x0, x1, None], y=[y0, y1, None], z=[z0, z1, None],
                mode='lines',
                line=dict(color=color, width=width),
                hoverinfo='text',
                text=f"Weight: {weight}",
                showlegend=False
            )
            edge_traces.append(edge_trace)
        
        # Create node trace
        node_x = [pos[node][0] for node in self.G.nodes()]
        node_y = [pos[node][1] for node in self.G.nodes()]
        node_z = [pos[node][2] for node in self.G.nodes()]
        
        # Color nodes based on degree
        node_degrees = dict(self.G.degree())
        node_colors = [self.get_color_for_degree(node_degrees[n], max(node_degrees.values())) for n in self.G.nodes()]
        
        node_trace = go.Scatter3d(
            x=node_x, y=node_y, z=node_z,
            mode='markers+text',
            marker=dict(
                size=15,
                color=node_colors,
                opacity=0.9,
                line=dict(width=2, color='#ffffff' if self.current_theme == "dark" else '#000000')
            ),
            text=[str(n) for n in self.G.nodes()],
            textposition="top center",
            hoverinfo='text',
            hovertext=[f"Node: {n}<br>Degree: {node_degrees[n]}" for n in self.G.nodes()],
            showlegend=False
        )
        
        # Create the figure
        fig = go.Figure(data=edge_traces + [node_trace])
        
        # Update layout
        fig.update_layout(
            title="NeuroGraphis 3D Graph Visualization",
            titlefont_size=16,
            showlegend=False,
            autosize=True,
            width=900,
            height=700,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            scene=dict(
                xaxis=dict(showbackground=False, showticklabels=False, title=''),
                yaxis=dict(showbackground=False, showticklabels=False, title=''),
                zaxis=dict(showbackground=False, showticklabels=False, title=''),
                bgcolor='#1e1e1e' if self.current_theme == "dark" else '#ffffff'
            ),
            updatemenus=[
                dict(
                    type='buttons',
                    showactive=False,
                    buttons=[
                        dict(
                            label='Play Animation',
                            method='animate',
                            args=[None, {'frame': {'duration': 50, 'redraw': True}, 'fromcurrent': True}]
                        )
                    ],
                    font=dict(color='#cccccc' if self.current_theme == "dark" else '#000000'),
                    bgcolor='#333333' if self.current_theme == "dark" else '#f0f0f0',
                    x=0.1,
                    y=0,
                    xanchor='right',
                    yanchor='top'
                )
            ]
        )
        
        # Add camera controls
        fig.update_layout(
            scene_camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        )
        
        # Add frames for animation
        frames = []
        for i in range(36):  # 36 frames for a full rotation
            camera_eye = dict(
                x=1.5 * np.cos(i * 10 * np.pi / 180),
                y=1.5 * np.sin(i * 10 * np.pi / 180),
                z=0.8
            )
            frames.append(go.Frame(layout=dict(scene_camera_eye=camera_eye)))
        
        fig.frames = frames
        
        # Generate HTML and open in browser
        temp_html = tempfile.mktemp(suffix='.html')
        fig.write_html(temp_html, include_plotlyjs='cdn', full_html=True)
        webbrowser.open('file://' + os.path.realpath(temp_html))
        
        self.status_var.set(f"3D visualization with {layout} layout opened in browser")
    
    def generate_sphere_layout(self):
        # Generate positions on a sphere
        pos = {}
        nodes = list(self.G.nodes())
        n = len(nodes)
        phi = np.pi * (3. - np.sqrt(5.))  # Golden angle
        
        for i, node in enumerate(nodes):
            y = 1 - (i / float(n - 1)) * 2 if n > 1 else 0  # y goes from 1 to -1
            radius = np.sqrt(1 - y * y)  # radius at y
            
            theta = phi * i  # Golden angle increment
            
            x = np.cos(theta) * radius
            z = np.sin(theta) * radius
            
            pos[node] = (x, y, z)
        
        return pos
    
    def generate_spiral_layout(self):
        # Generate positions on a spiral
        pos = {}
        nodes = list(self.G.nodes())
        n = len(nodes)
        
        for i, node in enumerate(nodes):
            t = i / float(n) * 2 * np.pi * 3  # 3 turns of spiral
            r = 0.5 + i / float(n) * 0.5  # Radius increases with node index
            
            x = r * np.cos(t)
            y = r * np.sin(t)
            z = i / float(n) * 2 - 1  # z from -1 to 1
            
            pos[node] = (x, y, z)
        
        return pos
    
    def generate_grid_layout(self):
        # Generate positions on a 3D grid
        pos = {}
        nodes = list(self.G.nodes())
        n = len(nodes)
        
        # Calculate grid dimensions
        dim = int(n ** (1/3)) + 1
        
        for i, node in enumerate(nodes):
            # Calculate 3D grid coordinates
            x = (i % dim) / float(dim) * 2 - 1
            y = ((i // dim) % dim) / float(dim) * 2 - 1
            z = (i // (dim * dim)) / float(dim) * 2 - 1
            
            pos[node] = (x, y, z)
        
        return pos
    
    def get_color_for_weight(self, weight, max_weight):
        # Create color gradient from blue to red based on weight
        ratio = weight / max_weight if max_weight > 0 else 0
        
        r = int(255 * ratio)
        g = int(100 * (1 - ratio))
        b = int(255 * (1 - ratio))
        
        # Convert to hex color code
        return f'rgb({r},{g},{b})'
    
    def get_color_for_degree(self, degree, max_degree):
        # Create color gradient for nodes based on degree centrality
        ratio = degree / max_degree if max_degree > 0 else 0
        
        hue = 0.6 * (1 - ratio)  # Blue (0.6) to Red (0.0)
        saturation = 0.8
        value = 0.9
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return f'rgb({int(r*255)},{int(g*255)},{int(b*255)})'
    
    def show_algorithms(self):
        if not self.G.nodes():
            messagebox.showinfo("Empty Graph", "The graph has no nodes")
            return
        
        output = "# NeuroGraphis Algorithm Results\n\n"
        
        # Dijkstra
        try:
            # Get start node from entry or use first node
            try:
                start = int(self.start_node.get())
                if start not in self.G.nodes():
                    start = list(self.G.nodes())[0]
                    output += f"⚠️ Start node {self.start_node.get()} not found, using {start} instead.\n\n"
            except:
                start = list(self.G.nodes())[0]
            
            # Calculate shortest paths
            length, path = nx.single_source_dijkstra(self.G, start)
            
            output += f"## Dijkstra's Shortest Path from node {start}\n\n"
            for node in sorted(path.keys()):
                if node != start:
                    # Calculate total path weight
                    total_weight = length[node]
                    path_str = " → ".join(str(n) for n in path[node])
                    output += f"To node {node}: [{path_str}] (Total weight: {total_weight})\n"
            output += "\n"
            
        except Exception as e:
            output += f"⚠️ Dijkstra Algorithm Error: {str(e)}\n\n"
        
        # MST Kruskal
        try:
            mst_k = nx.minimum_spanning_tree(self.G, algorithm="kruskal")
            
            total_weight = sum(mst_k[u][v]['weight'] for u, v in mst_k.edges())
            
            output += f"## Kruskal's Minimum Spanning Tree (Total weight: {total_weight})\n\n"
            for u, v, d in sorted(mst_k.edges(data=True)):
                output += f"Edge {u}-{v} (weight: {d['weight']})\n"
            output += "\n"
        except Exception as e:
            output += f"⚠️ Kruskal Algorithm Error: {str(e)}\n\n"
        
        # MST Prim
        try:
            mst_p = nx.minimum_spanning_tree(self.G, algorithm="prim")
            
            total_weight = sum(mst_p[u][v]['weight'] for u, v in mst_p.edges())
            
            output += f"## Prim's Minimum Spanning Tree (Total weight: {total_weight})\n\n"
            for u, v, d in sorted(mst_p.edges(data=True)):
                output += f"Edge {u}-{v} (weight: {d['weight']})\n"
            output += "\n"
        except Exception as e:
            output += f"⚠️ Prim Algorithm Error: {str(e)}\n\n"
        
        # Eulerian
        try:
            output += "## Eulerian Path Analysis\n\n"
            
            if nx.is_eulerian(self.G):
                eulerian_circuit = list(nx.eulerian_circuit(self.G))
                path_str = " → ".join(f"{u}-{v}" for u, v in eulerian_circuit)
                output += f"✅ Graph is Eulerian\nEulerian Circuit: {path_str}\n\n"
            elif nx.has_eulerian_path(self.G):
                output += "⚠️ Graph has an Eulerian path but not an Eulerian circuit\n\n"
            else:
                output += "❌ Graph is not Eulerian\n\n"
                # Add info about odd degree vertices
                odd_degree_vertices = [v for v, d in self.G.degree() if d % 2 == 1]
                output += f"Vertices with odd degree: {odd_degree_vertices}\n"
                output += f"To be Eulerian, a graph must have 0 or 2 vertices with odd degree.\n\n"
        except Exception as e:
            output += f"⚠️ Eulerian Analysis Error: {str(e)}\n\n"
        
        # Hamiltonian Path Approximation
        try:
            output += "## Hamiltonian Path Analysis\n\n"
            
            try:
                from networkx.algorithms.approximation import traveling_salesman_problem
                hamiltonian_path = traveling_salesman_problem(self.G)
                path_str = " → ".join(str(n) for n in hamiltonian_path)
                
                # Calculate total path weight
                total_weight = sum(self.G[hamiltonian_path[i]][hamiltonian_path[i+1]]['weight'] 
                                   for i in range(len(hamiltonian_path)-1))
                
                output += f"Approximated Hamiltonian Path: [{path_str}] (Total weight: {total_weight})\n"
                output += "Note: This is an approximation using a traveling salesman heuristic.\n\n"
            except ImportError:
                output += "⚠️ Hamiltonian Path approximation unavailable (missing networkx.algorithms.approximation)\n\n"
        except Exception as e:
            output += f"⚠️ Hamiltonian Analysis Error: {str(e)}\n\n"
        
        # Isomorphism Check with K-regular graph
        try:
            output += "## Graph Properties\n\n"
            
            # Check if graph is connected
            is_connected = nx.is_connected(self.G)
            output += f"Connected: {'✅ Yes' if is_connected else '❌ No'}\n"
            
            # Check if graph is bipartite
            is_bipartite = nx.is_bipartite(self.G)
            output += f"Bipartite: {'✅ Yes' if is_bipartite else '❌ No'}\n"
            
            # Check if graph is regular
            degrees = [d for _, d in self.G.degree()]
            is_regular = len(set(degrees)) <= 1
            if is_regular and degrees:
                output += f"Regular: ✅ Yes ({degrees[0]}-regular)\n"
            else:
                output += "Regular: ❌ No\n"
            
            # Check if graph is complete
            n = self.G.number_of_nodes()
            max_edges = n * (n - 1) // 2
            is_complete = self.G.number_of_edges() == max_edges
            output += f"Complete: {'✅ Yes' if is_complete else '❌ No'}\n\n"
        except Exception as e:
            output += f"⚠️ Graph Properties Error: {str(e)}\n\n"
        
        # Display the results in the text widget
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, output)
        
        # Generate matrices
        self.generate_matrices()
        
        # Select the results tab
        self.notebook.select(1)
        self.status_var.set("Algorithm analysis completed")
    
    def run_single_algorithm(self, algorithm):
        if not self.G.nodes():
            messagebox.showinfo("Empty Graph", "The graph has no nodes")
            return
            
        output = f"# NeuroGraphis {algorithm.title()} Analysis\n\n"
        
        if algorithm == "dijkstra":
            try:
                # Get start node from entry or use first node
                try:
                    start = int(self.start_node.get())
                    if start not in self.G.nodes():
                        start = list(self.G.nodes())[0]
                        output += f"⚠️ Start node {self.start_node.get()} not found, using {start} instead.\n\n"
                except:
                    start = list(self.G.nodes())[0]
                
                # Calculate shortest paths
                length, path = nx.single_source_dijkstra(self.G, start)
                
                output += f"## Dijkstra's Shortest Path from node {start}\n\n"
                for node in sorted(path.keys()):
                    if node != start:
                        # Calculate total path weight
                        total_weight = length[node]
                        path_str = " → ".join(str(n) for n in path[node])
                        output += f"To node {node}: [{path_str}] (Total weight: {total_weight})\n"
            except Exception as e:
                output += f"⚠️ Dijkstra Algorithm Error: {str(e)}"
                
        elif algorithm == "kruskal":
            try:
                mst_k = nx.minimum_spanning_tree(self.G, algorithm="kruskal")
                
                total_weight = sum(mst_k[u][v]['weight'] for u, v in mst_k.edges())
                
                output += f"## Kruskal's Minimum Spanning Tree (Total weight: {total_weight})\n\n"
                for u, v, d in sorted(mst_k.edges(data=True)):
                    output += f"Edge {u}-{v} (weight: {d['weight']})\n"
            except Exception as e:
                output += f"⚠️ Kruskal Algorithm Error: {str(e)}"
                
        elif algorithm == "prim":
            try:
                mst_p = nx.minimum_spanning_tree(self.G, algorithm="prim")
                
                total_weight = sum(mst_p[u][v]['weight'] for u, v in mst_p.edges())
                
                output += f"## Prim's Minimum Spanning Tree (Total weight: {total_weight})\n\n"
                for u, v, d in sorted(mst_p.edges(data=True)):
                    output += f"Edge {u}-{v} (weight: {d['weight']})\n"
            except Exception as e:
                output += f"⚠️ Prim Algorithm Error: {str(e)}"
                
        elif algorithm == "eulerian":
            try:
                output += "## Eulerian Path Analysis\n\n"
                
                if nx.is_eulerian(self.G):
                    eulerian_circuit = list(nx.eulerian_circuit(self.G))
                    path_str = " → ".join(f"{u}-{v}" for u, v in eulerian_circuit)
                    output += f"✅ Graph is Eulerian\nEulerian Circuit: {path_str}\n"
                elif nx.has_eulerian_path(self.G):
                    output += "⚠️ Graph has an Eulerian path but not an Eulerian circuit\n"
                else:
                    output += "❌ Graph is not Eulerian\n"
                    # Add info about odd degree vertices
                    odd_degree_vertices = [v for v, d in self.G.degree() if d % 2 == 1]
                    output += f"Vertices with odd degree: {odd_degree_vertices}\n"
                    output += f"To be Eulerian, a graph must have 0 or 2 vertices with odd degree.\n"
            except Exception as e:
                output += f"⚠️ Eulerian Analysis Error: {str(e)}"
                
        elif algorithm == "hamiltonian":
            try:
                output += "## Hamiltonian Path Analysis\n\n"
                
                try:
                    from networkx.algorithms.approximation import traveling_salesman_problem
                    hamiltonian_path = traveling_salesman_problem(self.G)
                    path_str = " → ".join(str(n) for n in hamiltonian_path)
                    
                    # Calculate total path weight
                    total_weight = sum(self.G[hamiltonian_path[i]][hamiltonian_path[i+1]]['weight'] 
                                      for i in range(len(hamiltonian_path)-1))
                    
                    output += f"Approximated Hamiltonian Path: [{path_str}] (Total weight: {total_weight})\n"
                    output += "Note: This is an approximation using a traveling salesman heuristic.\n"
                except ImportError:
                    output += "⚠️ Hamiltonian Path approximation unavailable (missing networkx.algorithms.approximation)\n"
            except Exception as e:
                output += f"⚠️ Hamiltonian Analysis Error: {str(e)}"
                
        elif algorithm == "matrices":
            try:
                self.generate_matrices()
                self.notebook.select(2)  # Switch to Matrix tab
                self.status_var.set("Matrix generation completed")
                return
            except Exception as e:
                output += f"⚠️ Matrix Generation Error: {str(e)}"
        
        # Display the results in the text widget
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, output)
        
        # Select the results tab
        self.notebook.select(1)
        self.status_var.set(f"{algorithm.title()} analysis completed")
    
    def generate_matrices(self):
        if not self.G.nodes():
            self.matrix_text.delete(1.0, tk.END)
            self.matrix_text.insert(tk.END, "No nodes in graph. Cannot generate matrices.")
            return
        
        output = "# Graph Matrix Representations\n\n"
        
        # Adjacency Matrix
        try:
            output += "## Adjacency Matrix\n\n"
            output += "The adjacency matrix represents connections between nodes:\n"
            output += "* A[i,j] = weight if there is an edge from node i to node j\n"
            output += "* A[i,j] = 0 if there is no edge\n\n"
            
            # Get adjacency matrix as numpy array with sorted nodes
            nodes = sorted(self.G.nodes())
            A = nx.to_numpy_array(self.G, nodelist=nodes)
            
            # Format matrix for display
            output += "Nodes: " + " ".join(str(n) for n in nodes) + "\n\n"
            output += "```\n"
            for i, row in enumerate(A):
                output += f"{nodes[i]:2d} | " + " ".join(f"{x:5.1f}" for x in row) + "\n"
            output += "```\n\n"
            
        except Exception as e:
            output += f"⚠️ Adjacency Matrix Error: {str(e)}\n\n"
        
        # Incidence Matrix
        try:
            output += "## Incidence Matrix\n\n"
            output += "The incidence matrix represents node-edge relationships:\n"
            output += "* I[i,j] = 1 if node i is connected to edge j\n"
            output += "* I[i,j] = 0 otherwise\n\n"
            
            # Create incidence matrix
            I = nx.incidence_matrix(self.G, oriented=True).toarray()
            
            # Format edges for display
            edges = list(self.G.edges())
            edge_labels = [f"({u},{v})" for u, v in edges]
            
            # Format matrix for display
            output += "Nodes: " + " ".join(str(n) for n in sorted(self.G.nodes())) + "\n"
            output += "Edges: " + " ".join(edge_labels) + "\n\n"
            
            output += "```\n"
            for i, node in enumerate(sorted(self.G.nodes())):
                output += f"{node:2d} | " + " ".join(f"{x:5.1f}" for x in I[i]) + "\n"
            output += "```\n\n"
            
        except Exception as e:
            output += f"⚠️ Incidence Matrix Error: {str(e)}\n\n"
        
        # Laplacian Matrix
        try:
            output += "## Laplacian Matrix\n\n"
            output += "The Laplacian matrix L = D - A where:\n"
            output += "* D is the degree matrix (diagonal matrix where D[i,i] = degree of node i)\n"
            output += "* A is the adjacency matrix\n\n"
            
            # Get Laplacian matrix
            L = nx.laplacian_matrix(self.G, nodelist=sorted(self.G.nodes())).toarray()
            
            # Format matrix for display
            output += "```\n"
            for i, node in enumerate(sorted(self.G.nodes())):
                output += f"{node:2d} | " + " ".join(f"{x:5.1f}" for x in L[i]) + "\n"
            output += "```\n\n"
            
            # Eigenvalues of Laplacian
            eigenvalues = np.linalg.eigvals(L)
            eigenvalues = sorted(eigenvalues)
            
            output += "### Eigenvalues of Laplacian\n\n"
            output += ", ".join(f"{e:.4f}" for e in eigenvalues) + "\n\n"
            output += f"Algebraic connectivity: {eigenvalues[1] if len(eigenvalues) > 1 else 'N/A'}\n"
            
        except Exception as e:
            output += f"⚠️ Laplacian Matrix Error: {str(e)}\n\n"
        
        # Display matrices
        self.matrix_text.delete(1.0, tk.END)
        self.matrix_text.insert(tk.END, output)
    
    def set_theme(self, theme):
        if theme == self.current_theme:
            return
            
        self.current_theme = theme
        
        if theme == "dark":
            self.root.configure(bg='#1e1e1e')
            self.results_text.configure(bg='#1e1e1e', fg='#cccccc')
            self.matrix_text.configure(bg='#1e1e1e', fg='#cccccc')
            self.node_color = "#36c6f4"  # Cyan-blue
            self.edge_color = "#cccccc"  # Light gray
        else:
            self.root.configure(bg='#f0f0f0')
            self.results_text.configure(bg='#ffffff', fg='#000000')
            self.matrix_text.configure(bg='#ffffff', fg='#000000')
            self.node_color = "#1f77b4"  # Matplotlib default blue
            self.edge_color = "#333333"  # Dark gray
        
        # Redraw the graph if it exists
        if hasattr(self, 'canvas'):
            self.show_graph()
            
        self.status_var.set(f"Theme changed to {theme}")
    
    def show_about(self):
        about_text = """
        NeuroGraphis - Advanced Graph Theory Visualization
        
        Version 2.0
        
        NeuroGraphis is an advanced graph theory project that combines a 
        user-friendly GUI with powerful algorithms for exploring key 
        graph theory concepts.
        
        Features:
        • Dijkstra's shortest path algorithm
        • Kruskal and Prim's minimum spanning tree algorithms
        • Eulerian and Hamiltonian path detection
        • Graph isomorphism testing
        • Matrix representations (adjacency, incidence, Laplacian)
        • 2D and interactive 3D visualizations
        
        Made with NetworkX, Matplotlib, and Plotly
        """
        
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About NeuroGraphis")
        about_dialog.geometry("500x400")
        about_dialog.configure(bg='#1e1e1e' if self.current_theme == "dark" else '#f0f0f0')
        
        text = scrolledtext.ScrolledText(
            about_dialog,
            bg='#1e1e1e' if self.current_theme == "dark" else '#ffffff',
            fg='#cccccc' if self.current_theme == "dark" else '#000000',
            font=('Arial', 11)
        )
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, about_text)
        text.configure(state='disabled')
    
    def show_concepts(self):
        concepts_text = """
        # Graph Theory Key Concepts
        
        ## Shortest Path (Dijkstra's Algorithm)
        Finds the shortest path between nodes in a weighted graph.
        
        ## Minimum Spanning Tree (MST)
        A subset of edges that connects all nodes with minimum total edge weight.
        • Kruskal's Algorithm: Adds edges in order of increasing weight.
        • Prim's Algorithm: Grows from a starting node by adding the nearest vertex.
        
        ## Eulerian Path
        A path that visits every edge exactly once.
        • A graph has an Eulerian circuit if all vertices have even degree.
        • A graph has an Eulerian path if exactly 0 or 2 vertices have odd degree.
        
        ## Hamiltonian Path
        A path that visits every vertex exactly once.
        • Finding a Hamiltonian path is NP-complete.
        • The traveling salesman problem is a special case.
        
        ## Graph Isomorphism
        Two graphs are isomorphic if they have the same structure.
        
        ## Matrix Representations
        • Adjacency Matrix: Shows connections between vertices.
        • Incidence Matrix: Shows vertex-edge relationships.
        • Laplacian Matrix: L = D - A, where D is degree matrix and A is adjacency matrix.
        """
        
        concepts_dialog = tk.Toplevel(self.root)
        concepts_dialog.title("Graph Theory Concepts")
        concepts_dialog.geometry("600x500")
        concepts_dialog.configure(bg='#1e1e1e' if self.current_theme == "dark" else '#f0f0f0')
        
        text = scrolledtext.ScrolledText(
            concepts_dialog,
            bg='#1e1e1e' if self.current_theme == "dark" else '#ffffff',
            fg='#cccccc' if self.current_theme == "dark" else '#000000',
            font=('Arial', 11)
        )
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, concepts_text)
        text.configure(state='disabled')
    
    def load_sample_graph(self):
        # Add a small sample graph for demonstration
        self.G.add_edge(0, 1, weight=7.0)
        self.G.add_edge(0, 2, weight=9.0)
        self.G.add_edge(1, 2, weight=10.0)
        self.G.add_edge(1, 3, weight=15.0)
        self.G.add_edge(2, 3, weight=11.0)
        self.G.add_edge(2, 5, weight=2.0)
        self.G.add_edge(3, 4, weight=6.0)
        self.G.add_edge(4, 5, weight=9.0)
        
        # Update edge list
        self.update_edge_list()
        
        # Generate initial layout
        self.pos = nx.spring_layout(self.G)

# Main application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = NeuroGraphisApp(root)
    root.mainloop()