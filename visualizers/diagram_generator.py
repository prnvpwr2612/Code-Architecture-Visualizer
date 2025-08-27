# visualizers/diagram_generator.py

import os
import time
import base64
import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
from pathlib import Path

try:
    import pygraphviz as pgv
    PYGRAPHVIZ_AVAILABLE = True
except ImportError:
    PYGRAPHVIZ_AVAILABLE = False

class DiagramGenerator:
    def __init__(self):
        print("🎨 DiagramGenerator initialization complete.")
        self.color_scheme = {
            'node_colors': {
                'module': '#4CAF50',
                'class': '#2196F3', 
                'function': '#FF9800',
                'entry_point': '#F44336',
                'utility': '#9C27B0'
            },
            'edge_colors': {
                'imports': '#666666',
                'calls': '#1976D2',
                'inheritance': '#E91E63'
            }
        }

    def create_diagrams(self, parsing_results, output_dir="./artifacts", session_id="default"):
        print("🖼️ Creating architecture diagrams from parsed codebase...")
        try:
            os.makedirs(output_dir, exist_ok=True)
            generated_diagrams = {}
            
            module_diagram = self._create_module_overview(parsing_results, output_dir, session_id)
            if module_diagram:
                generated_diagrams['module_overview'] = module_diagram
            
            class_diagram = self._create_class_hierarchy(parsing_results, output_dir, session_id)
            if class_diagram:
                generated_diagrams['class_hierarchy'] = class_diagram
            
            function_diagram = self._create_function_map(parsing_results, output_dir, session_id)
            if function_diagram:
                generated_diagrams['function_map'] = function_diagram
            
            print(f"✅ Generated {len(generated_diagrams)} diagram types")
            return generated_diagrams, "✅ Architecture diagrams created successfully"
            
        except Exception as e:
            error_msg = f"❌ Diagram generation failed: {str(e)}"
            print(error_msg)
            print("⭐ Resolution Strategies:")
            print("  1. Install Graphviz system package and PyGraphviz")
            print("  2. Try matplotlib fallback for basic visualization")
            print("  3. Reduce graph complexity with filtering")
            print("  4. Check output directory permissions")
            print("  5. Restart kernel if memory issues persist")
            return None, error_msg

    def _create_module_overview(self, parsing_results, output_dir, session_id):
        print("📊 Creating module overview diagram...")
        try:
            if PYGRAPHVIZ_AVAILABLE:
                return self._create_pygraphviz_module_diagram(parsing_results, output_dir, session_id)
            else:
                return self._create_matplotlib_module_diagram(parsing_results, output_dir, session_id)
        except Exception as e:
            print(f"⚠️ Module diagram creation failed: {str(e)}")
            return None

    def _create_pygraphviz_module_diagram(self, parsing_results, output_dir, session_id):
        A = pgv.AGraph(strict=False, directed=True)
        A.graph_attr.update(
            rankdir='TB',
            fontsize='12',
            fontname='Arial',
            bgcolor='white',
            size='10,8'
        )
        A.node_attr.update(
            shape='box',
            style='rounded,filled',
            fontname='Arial',
            fontsize='10'
        )
        
        parsed_files = parsing_results.get('parsed_files', {})
        
        for file_path, parse_data in parsed_files.items():
            if not parse_data.get('parsing_successful', False):
                continue
            
            module_name = Path(file_path).stem
            functions = len(parse_data.get('functions', []))
            classes = len(parse_data.get('classes', []))
            
            node_color = self.color_scheme['node_colors']['module']
            if 'main' in module_name.lower() or 'app' in module_name.lower():
                node_color = self.color_scheme['node_colors']['entry_point']
            
            label = f"{module_name}\\n{functions}f, {classes}c"
            A.add_node(module_name, label=label, fillcolor=node_color)
        
        A.layout(prog='dot')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        svg_path = os.path.join(output_dir, f"module_overview_{timestamp}.svg")
        png_path = os.path.join(output_dir, f"module_overview_{timestamp}.png")
        
        A.draw(svg_path, format='svg')
        A.draw(png_path, format='png')
        
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        print(f"✅ PyGraphviz module diagram created: {svg_path}")
        return {'svg_content': svg_content, 'svg_path': svg_path, 'png_path': png_path, 'method': 'pygraphviz'}

    def _create_matplotlib_module_diagram(self, parsing_results, output_dir, session_id):
        plt.figure(figsize=(12, 8))
        
        G = nx.Graph()
        parsed_files = parsing_results.get('parsed_files', {})
        
        for file_path, parse_data in parsed_files.items():
            if not parse_data.get('parsing_successful', False):
                continue
            
            module_name = Path(file_path).stem
            functions = len(parse_data.get('functions', []))
            classes = len(parse_data.get('classes', []))
            
            G.add_node(module_name, functions=functions, classes=classes)
        
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        node_colors = [
            self.color_scheme['node_colors']['entry_point'] 
            if 'main' in node.lower() or 'app' in node.lower() 
            else self.color_scheme['node_colors']['module']
            for node in G.nodes()
        ]
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000, alpha=0.8)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        plt.title("Module Overview", fontsize=16, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        png_path = os.path.join(output_dir, f"module_overview_matplotlib_{timestamp}.png")
        plt.savefig(png_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        with open(png_path, 'rb') as f:
            png_b64 = base64.b64encode(f.read()).decode('utf-8')
        
        html_content = f'<img src="data:image/png;base64,{png_b64}" style="max-width:100%; height:auto;">'
        
        print(f"✅ Matplotlib module diagram created: {png_path}")
        return {'html_content': html_content, 'png_path': png_path, 'method': 'matplotlib'}

    def _create_class_hierarchy(self, parsing_results, output_dir, session_id):
        print("🏗️ Creating class hierarchy diagram...")
        try:
            plt.figure(figsize=(14, 10))
            
            G = nx.DiGraph()
            parsed_files = parsing_results.get('parsed_files', {})
            
            for file_path, parse_data in parsed_files.items():
                if not parse_data.get('parsing_successful', False):
                    continue
                
                classes = parse_data.get('classes', [])
                module_name = Path(file_path).stem
                
                for class_info in classes:
                    class_name = class_info.get('name', 'Unknown')
                    full_class_name = f"{module_name}.{class_name}"
                    G.add_node(full_class_name, type='class', module=module_name)
            
            if len(G.nodes()) == 0:
                print("⚠️ No classes found for hierarchy diagram")
                return None
            
            pos = nx.spring_layout(G, k=3, iterations=50)
            
            nx.draw_networkx_nodes(G, pos, 
                node_color=self.color_scheme['node_colors']['class'],
                node_size=1500, alpha=0.8)
            nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
            
            plt.title("Class Hierarchy", fontsize=16, fontweight='bold', pad=20)
            plt.axis('off')
            plt.tight_layout()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            png_path = os.path.join(output_dir, f"class_hierarchy_{timestamp}.png")
            plt.savefig(png_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            with open(png_path, 'rb') as f:
                png_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            html_content = f'<img src="data:image/png;base64,{png_b64}" style="max-width:100%; height:auto;">'
            
            print(f"✅ Class hierarchy diagram created: {png_path}")
            return {'html_content': html_content, 'png_path': png_path, 'method': 'matplotlib'}
            
        except Exception as e:
            print(f"⚠️ Class hierarchy diagram failed: {str(e)}")
            return None

    def _create_function_map(self, parsing_results, output_dir, session_id):
        print("🔧 Creating function map diagram...")
        try:
            plt.figure(figsize=(16, 12))
            
            G = nx.Graph()
            parsed_files = parsing_results.get('parsed_files', {})
            
            for file_path, parse_data in parsed_files.items():
                if not parse_data.get('parsing_successful', False):
                    continue
                
                functions = parse_data.get('functions', [])
                module_name = Path(file_path).stem
                
                for func_info in functions:
                    func_name = func_info.get('name', 'Unknown')
                    full_func_name = f"{module_name}.{func_name}"
                    G.add_node(full_func_name, type='function', module=module_name)
            
            if len(G.nodes()) == 0:
                print("⚠️ No functions found for function map")
                return None
            
            pos = nx.spring_layout(G, k=2, iterations=50)
            
            nx.draw_networkx_nodes(G, pos, 
                node_color=self.color_scheme['node_colors']['function'],
                node_size=800, alpha=0.7)
            nx.draw_networkx_labels(G, pos, font_size=6, font_weight='bold')
            
            plt.title("Function Map", fontsize=16, fontweight='bold', pad=20)
            plt.axis('off')
            plt.tight_layout()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            png_path = os.path.join(output_dir, f"function_map_{timestamp}.png")
            plt.savefig(png_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            with open(png_path, 'rb') as f:
                png_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            html_content = f'<img src="data:image/png;base64,{png_b64}" style="max-width:100%; height:auto;">'
            
            print(f"✅ Function map diagram created: {png_path}")
            return {'html_content': html_content, 'png_path': png_path, 'method': 'matplotlib'}
            
        except Exception as e:
            print(f"⚠️ Function map diagram failed: {str(e)}")
            return None

print("🎯 visualizers/diagram_generator.py module export ready.")