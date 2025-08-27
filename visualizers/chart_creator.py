# visualizers/chart_creator.py

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import os
import base64
from pathlib import Path

class ChartCreator:
    def __init__(self):
        print("📊 ChartCreator initialization complete.")
        self.chart_style = {
            'figure_size': (12, 8),
            'color_palette': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],
            'background_color': '#ffffff',
            'grid_alpha': 0.3,
            'title_size': 16,
            'label_size': 12
        }

    def create_metrics_dashboard(self, parsing_results, output_dir="./artifacts", session_id="default"):
        print("📈 Creating comprehensive metrics dashboard...")
        try:
            os.makedirs(output_dir, exist_ok=True)
            parsed_files = parsing_results.get('parsed_files', {})
            
            if not parsed_files:
                print("⚠️ No parsed files found for metrics")
                return None
            
            metrics_data = self._extract_metrics_data(parsed_files)
            charts_created = {}
            
            file_metrics_chart = self._create_file_metrics_chart(metrics_data, output_dir, session_id)
            if file_metrics_chart:
                charts_created['file_metrics'] = file_metrics_chart
            
            complexity_chart = self._create_complexity_distribution_chart(metrics_data, output_dir, session_id)
            if complexity_chart:
                charts_created['complexity'] = complexity_chart
            
            language_chart = self._create_language_breakdown_chart(metrics_data, output_dir, session_id)
            if language_chart:
                charts_created['language_breakdown'] = language_chart
            
            trend_chart = self._create_project_health_chart(metrics_data, output_dir, session_id)
            if trend_chart:
                charts_created['project_health'] = trend_chart
            
            print(f"✅ Created {len(charts_created)} metric charts")
            return charts_created, "✅ Metrics dashboard created successfully"
            
        except Exception as e:
            error_msg = f"❌ Metrics dashboard creation failed: {str(e)}"
            print(error_msg)
            print("⭐ Resolution Strategies:")
            print("  1. Verify parsing results contain valid data")
            print("  2. Check matplotlib installation and compatibility")
            print("  3. Ensure output directory has write permissions")
            print("  4. Try with reduced dataset size")
            print("  5. Check memory availability for chart generation")
            return None, error_msg

    def _extract_metrics_data(self, parsed_files):
        metrics = {
            'file_names': [],
            'function_counts': [],
            'class_counts': [],
            'line_counts': [],
            'import_counts': [],
            'complexity_scores': []
        }
        
        for file_path, parse_data in parsed_files.items():
            if not parse_data.get('parsing_successful', False):
                continue
            
            file_name = Path(file_path).name
            functions = len(parse_data.get('functions', []))
            classes = len(parse_data.get('classes', []))
            lines = parse_data.get('source_lines', 0)
            imports = len(parse_data.get('imports', {}).get('standard_imports', [])) + len(parse_data.get('imports', {}).get('from_imports', []))
            
            complexity = functions * 2 + classes * 3 + (imports * 0.5)
            
            metrics['file_names'].append(file_name)
            metrics['function_counts'].append(functions)
            metrics['class_counts'].append(classes)
            metrics['line_counts'].append(lines)
            metrics['import_counts'].append(imports)
            metrics['complexity_scores'].append(complexity)
        
        return metrics

    def _create_file_metrics_chart(self, metrics_data, output_dir, session_id):
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Project File Metrics Overview', fontsize=self.chart_style['title_size'], fontweight='bold')
            
            ax1.bar(range(len(metrics_data['function_counts'])), metrics_data['function_counts'], 
                   color=self.chart_style['color_palette'][0], alpha=0.7)
            ax1.set_title('Functions per File')
            ax1.set_xlabel('Files')
            ax1.set_ylabel('Function Count')
            ax1.grid(True, alpha=self.chart_style['grid_alpha'])
            
            ax2.bar(range(len(metrics_data['class_counts'])), metrics_data['class_counts'], 
                   color=self.chart_style['color_palette'][1], alpha=0.7)
            ax2.set_title('Classes per File')
            ax2.set_xlabel('Files')
            ax2.set_ylabel('Class Count')
            ax2.grid(True, alpha=self.chart_style['grid_alpha'])
            
            ax3.plot(metrics_data['line_counts'], color=self.chart_style['color_palette'][2], 
                    marker='o', linewidth=2, markersize=4)
            ax3.set_title('Lines of Code per File')
            ax3.set_xlabel('Files')
            ax3.set_ylabel('Lines of Code')
            ax3.grid(True, alpha=self.chart_style['grid_alpha'])
            
            ax4.scatter(metrics_data['function_counts'], metrics_data['complexity_scores'], 
                       color=self.chart_style['color_palette'][3], alpha=0.6, s=50)
            ax4.set_title('Complexity vs Functions')
            ax4.set_xlabel('Function Count')
            ax4.set_ylabel('Complexity Score')
            ax4.grid(True, alpha=self.chart_style['grid_alpha'])
            
            plt.tight_layout()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_path = os.path.join(output_dir, f"file_metrics_{timestamp}.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            with open(chart_path, 'rb') as f:
                chart_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            html_content = f'<img src="data:image/png;base64,{chart_b64}" style="max-width:100%; height:auto;">'
            
            print(f"✅ File metrics chart created: {chart_path}")
            return {'html_content': html_content, 'file_path': chart_path, 'chart_type': 'file_metrics'}
            
        except Exception as e:
            print(f"⚠️ File metrics chart creation failed: {str(e)}")
            return None

    def _create_complexity_distribution_chart(self, metrics_data, output_dir, session_id):
        try:
            plt.figure(figsize=self.chart_style['figure_size'])
            
            complexity_scores = metrics_data['complexity_scores']
            if not complexity_scores:
                print("⚠️ No complexity data available")
                return None
            
            plt.hist(complexity_scores, bins=min(20, len(complexity_scores)), 
                    color=self.chart_style['color_palette'][4], alpha=0.7, edgecolor='black')
            plt.title('Code Complexity Distribution', fontsize=self.chart_style['title_size'], fontweight='bold')
            plt.xlabel('Complexity Score', fontsize=self.chart_style['label_size'])
            plt.ylabel('Number of Files', fontsize=self.chart_style['label_size'])
            plt.grid(True, alpha=self.chart_style['grid_alpha'])
            
            mean_complexity = np.mean(complexity_scores)
            plt.axvline(mean_complexity, color='red', linestyle='--', linewidth=2, 
                       label=f'Mean: {mean_complexity:.1f}')
            plt.legend()
            
            plt.tight_layout()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_path = os.path.join(output_dir, f"complexity_dist_{timestamp}.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            with open(chart_path, 'rb') as f:
                chart_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            html_content = f'<img src="data:image/png;base64,{chart_b64}" style="max-width:100%; height:auto;">'
            
            print(f"✅ Complexity distribution chart created: {chart_path}")
            return {'html_content': html_content, 'file_path': chart_path, 'chart_type': 'complexity_distribution'}
            
        except Exception as e:
            print(f"⚠️ Complexity distribution chart creation failed: {str(e)}")
            return None

    def _create_language_breakdown_chart(self, metrics_data, output_dir, session_id):
        try:
            file_extensions = {}
            for file_name in metrics_data['file_names']:
                ext = Path(file_name).suffix or '.unknown'
                file_extensions[ext] = file_extensions.get(ext, 0) + 1
            
            if not file_extensions:
                print("⚠️ No file extension data available")
                return None
            
            plt.figure(figsize=(10, 8))
            
            extensions = list(file_extensions.keys())
            counts = list(file_extensions.values())
            colors = self.chart_style['color_palette'][:len(extensions)]
            
            plt.pie(counts, labels=extensions, autopct='%1.1f%%', startangle=90, 
                   colors=colors, explode=[0.05] * len(extensions))
            plt.title('Project Language Breakdown', fontsize=self.chart_style['title_size'], fontweight='bold')
            plt.axis('equal')
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_path = os.path.join(output_dir, f"language_breakdown_{timestamp}.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            with open(chart_path, 'rb') as f:
                chart_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            html_content = f'<img src="data:image/png;base64,{chart_b64}" style="max-width:100%; height:auto;">'
            
            print(f"✅ Language breakdown chart created: {chart_path}")
            return {'html_content': html_content, 'file_path': chart_path, 'chart_type': 'language_breakdown'}
            
        except Exception as e:
            print(f"⚠️ Language breakdown chart creation failed: {str(e)}")
            return None

    def _create_project_health_chart(self, metrics_data, output_dir, session_id):
        try:
            plt.figure(figsize=(14, 8))
            
            total_functions = sum(metrics_data['function_counts'])
            total_classes = sum(metrics_data['class_counts'])
            total_lines = sum(metrics_data['line_counts'])
            avg_complexity = np.mean(metrics_data['complexity_scores']) if metrics_data['complexity_scores'] else 0
            
            health_metrics = ['Functions', 'Classes', 'Lines (÷100)', 'Avg Complexity']
            health_values = [total_functions, total_classes, total_lines / 100, avg_complexity]
            
            bars = plt.bar(health_metrics, health_values, 
                          color=self.chart_style['color_palette'][:4], alpha=0.8)
            
            plt.title('Project Health Overview', fontsize=self.chart_style['title_size'], fontweight='bold')
            plt.ylabel('Count / Score', fontsize=self.chart_style['label_size'])
            plt.grid(True, alpha=self.chart_style['grid_alpha'])
            
            for bar, value in zip(bars, health_values):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(health_values) * 0.01,
                        f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_path = os.path.join(output_dir, f"project_health_{timestamp}.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            with open(chart_path, 'rb') as f:
                chart_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            html_content = f'<img src="data:image/png;base64,{chart_b64}" style="max-width:100%; height:auto;">'
            
            print(f"✅ Project health chart created: {chart_path}")
            return {'html_content': html_content, 'file_path': chart_path, 'chart_type': 'project_health'}
            
        except Exception as e:
            print(f"⚠️ Project health chart creation failed: {str(e)}")
            return None

print("🎯 visualizers/chart_creator.py module export ready.")