# analyzers/dependency_analyzer.py

import os
import json
import networkx as nx
import time
from pathlib import Path
from collections import defaultdict, Counter

try:
    import pygraphviz as pgv
    PYGRAPHVIZ_AVAILABLE = True
except ImportError:
    PYGRAPHVIZ_AVAILABLE = False

class DependencyAnalyzer:
    def __init__(self):
        print("🔗 DependencyAnalyzer initialization complete.")
        self.dependency_graph = nx.DiGraph()
        self.module_info = {}
        self.external_dependencies = set()
        self.circular_dependencies = []
        self.orphaned_modules = []

    def analyze_import_relationships(self, parsing_results):
        print("🔍 Analyzing import relationships across all modules...")
        try:
            start_time = time.time()
            module_mapping = {}
            file_to_module = {}
            
            for file_path, parse_data in parsing_results.get('parsed_files', {}).items():
                if not parse_data.get('parsing_successful', False):
                    continue
                
                module_name = Path(file_path).stem
                module_mapping[module_name] = file_path
                file_to_module[file_path] = module_name
                
                self.dependency_graph.add_node(module_name, 
                    file_path=file_path,
                    functions=len(parse_data.get('functions', [])),
                    classes=len(parse_data.get('classes', [])),
                    source_lines=parse_data.get('source_lines', 0)
                )
                
                self.module_info[module_name] = {
                    'file_path': file_path,
                    'functions': parse_data.get('functions', []),
                    'classes': parse_data.get('classes', []),
                    'imports': parse_data.get('imports', {}),
                    'metrics': {
                        'function_count': len(parse_data.get('functions', [])),
                        'class_count': len(parse_data.get('classes', [])),
                        'source_lines': parse_data.get('source_lines', 0)
                    }
                }
            
            dependency_count = 0
            
            for file_path, parse_data in parsing_results.get('parsed_files', {}).items():
                if not parse_data.get('parsing_successful', False):
                    continue
                
                source_module = file_to_module[file_path]
                imports_data = parse_data.get('imports', {})
                
                for import_info in imports_data.get('standard_imports', []):
                    target_module = import_info.get('module', '')
                    
                    if target_module in module_mapping:
                        self.dependency_graph.add_edge(
                            source_module, 
                            target_module,
                            import_type='standard',
                            line_number=import_info.get('line', 0),
                            alias=import_info.get('alias')
                        )
                        dependency_count += 1
                    else:
                        self.external_dependencies.add(target_module)
                
                for import_info in imports_data.get('from_imports', []):
                    source_module_name = import_info.get('module', '')
                    imported_name = import_info.get('name', '')
                    
                    if source_module_name in module_mapping:
                        self.dependency_graph.add_edge(
                            source_module,
                            source_module_name,
                            import_type='from_import',
                            imported_name=imported_name,
                            line_number=import_info.get('line', 0),
                            alias=import_info.get('alias')
                        )
                        dependency_count += 1
                    else:
                        self.external_dependencies.add(source_module_name)
            
            self._detect_circular_dependencies()
            self._identify_orphaned_modules()
            
            analysis_time = time.time() - start_time
            
            print(f"✅ Dependency analysis completed:")
            print(f"  📦 Modules analyzed: {self.dependency_graph.number_of_nodes()}")
            print(f"  🔗 Dependencies found: {dependency_count}")
            print(f"  🌐 External dependencies: {len(self.external_dependencies)}")
            print(f"  🔄 Circular dependencies: {len(self.circular_dependencies)}")
            print(f"  👤 Orphaned modules: {len(self.orphaned_modules)}")
            print(f"  ⏱️ Analysis time: {analysis_time:.2f}s")
            
            return {
                'graph': self.dependency_graph,
                'module_info': self.module_info,
                'external_dependencies': list(self.external_dependencies),
                'circular_dependencies': self.circular_dependencies,
                'orphaned_modules': self.orphaned_modules,
                'analysis_time': analysis_time,
                'summary': {
                    'total_modules': self.dependency_graph.number_of_nodes(),
                    'total_dependencies': dependency_count,
                    'external_count': len(self.external_dependencies),
                    'circular_count': len(self.circular_dependencies),
                    'orphaned_count': len(self.orphaned_modules)
                }
            }, "✅ Dependency graph analysis completed"
            
        except Exception as e:
            error_msg = f"❌ Dependency analysis failed: {str(e)}"
            print(error_msg)
            print("⭐ Resolution Strategies:")
            print("  1. Check parsing results structure and data integrity")
            print("  2. Verify NetworkX installation and compatibility")
            print("  3. Ensure sufficient memory for large projects")
            print("  4. Try analyzing smaller module subsets")
            print("  5. Check for circular import issues in source code")
            return None, error_msg

    def _detect_circular_dependencies(self):
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            self.circular_dependencies = cycles
            
            if cycles:
                print(f"⚠️ Found {len(cycles)} circular dependency chains")
                for i, cycle in enumerate(cycles[:3], 1):
                    print(f"  {i}. {' → '.join(cycle)} → {cycle[0]}")
        except Exception as e:
            print(f"⚠️ Circular dependency detection failed: {str(e)}")

    def _identify_orphaned_modules(self):
        try:
            self.orphaned_modules = [
                node for node in self.dependency_graph.nodes()
                if self.dependency_graph.in_degree(node) == 0 and 
                self.dependency_graph.out_degree(node) == 0
            ]
        except Exception as e:
            print(f"⚠️ Orphaned module detection failed: {str(e)}")

    def export_to_formats(self, output_dir="./artifacts", session_id="default"):
        print("📁 Exporting dependency data to multiple formats...")
        try:
            os.makedirs(output_dir, exist_ok=True)
            exported_files = {}
            
            base_name = f"dependencies_{session_id}"
            
            json_data = {
                'nodes': [
                    {
                        'id': node,
                        'file_path': data.get('file_path', ''),
                        'functions': data.get('functions', 0),
                        'classes': data.get('classes', 0),
                        'source_lines': data.get('source_lines', 0)
                    }
                    for node, data in self.dependency_graph.nodes(data=True)
                ],
                'edges': [
                    {
                        'source': u,
                        'target': v,
                        'import_type': data.get('import_type', 'unknown'),
                        'line_number': data.get('line_number', 0),
                        'imported_name': data.get('imported_name', ''),
                        'alias': data.get('alias', '')
                    }
                    for u, v, data in self.dependency_graph.edges(data=True)
                ],
                'external_dependencies': list(self.external_dependencies),
                'circular_dependencies': self.circular_dependencies,
                'orphaned_modules': self.orphaned_modules
            }
            
            json_path = os.path.join(output_dir, f"{base_name}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
            exported_files['json'] = json_path
            
            try:
                nx.nx_pydot.write_dot(self.dependency_graph, os.path.join(output_dir, f"{base_name}.dot"))
                exported_files['dot'] = os.path.join(output_dir, f"{base_name}.dot")
            except:
                print("⚠️ DOT export skipped (pydot not available)")
            
            adjacency_path = os.path.join(output_dir, f"{base_name}_adjacency.json")
            adjacency_data = nx.adjacency_data(self.dependency_graph)
            with open(adjacency_path, 'w', encoding='utf-8') as f:
                json.dump(adjacency_data, f, indent=2)
            exported_files['adjacency'] = adjacency_path
            
            print(f"✅ Exported dependency data to {len(exported_files)} formats")
            return exported_files, "✅ Export completed successfully"
            
        except Exception as e:
            error_msg = f"❌ Export failed: {str(e)}"
            print(error_msg)
            print("⭐ Resolution Strategies:")
            print("  1. Check output directory permissions")
            print("  2. Ensure sufficient disk space")
            print("  3. Verify NetworkX pydot integration")
            print("  4. Try exporting smaller datasets")
            return None, error_msg

print("🎯 analyzers/dependency_analyzer.py module export ready.")