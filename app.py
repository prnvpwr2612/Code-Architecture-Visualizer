# app.py - Complete Code Architecture Visualizer

import gradio as gr
import os
import torch
import json
from datetime import datetime
from pathlib import Path

# Import your modules
from models.glm_handler import GLMHandler
from analyzers.code_parser import CodeParser
from analyzers.dependency_analyzer import DependencyAnalyzer
from analyzers.security_scanner import SecurityScanner
from visualizers.diagram_generator import DiagramGenerator
from visualizers.chart_creator import ChartCreator
from utils.helpers import ProjectHelpers

# Initialize global components
print("🚀 Initializing Code Architecture Visualizer...")
MODEL_NAME = "THUDM/glm-4-9b-chat"
glm_handler = GLMHandler(MODEL_NAME)
code_parser = CodeParser()
dependency_analyzer = DependencyAnalyzer()
security_scanner = SecurityScanner()
diagram_generator = DiagramGenerator()
chart_creator = ChartCreator()
helpers = ProjectHelpers()
print("✅ All modules initialized successfully!")

def analyze_codebase(file_upload, github_url, features_selected, progress=gr.Progress()):
    """Main analysis function combining all notebook functionality"""
    try:
        progress(0, desc="🚀 Starting analysis...")
        
        # Step 1: Get codebase
        if file_upload:
            codebase_path = helpers.extract_codebase(file_upload)
            source_type = "upload"
        elif github_url:
            codebase_path = helpers.clone_repository(github_url)
            source_type = "github"
        else:
            return "❌ Please provide either a file upload or GitHub URL", None, None
        
        if not codebase_path:
            return "❌ Failed to prepare codebase for analysis", None, None
        
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifacts_dir = helpers.create_session_artifacts(session_id)
        
        results = {"session_id": session_id, "source": source_type, "features": []}
        
        # Step 2: Parse codebase
        progress(0.2, desc="🔍 Parsing source code...")
        parsing_results, parse_msg = code_parser.parse_project(codebase_path)
        results["parsing"] = {"results": parsing_results, "message": parse_msg}
        
        diagrams_html = ""
        charts_html = ""
        download_files = []
        
        # Step 3: Run selected features
        if "Architecture Diagram" in features_selected:
            progress(0.4, desc="🎨 Generating architecture diagrams...")
            diagram_result, diagram_msg = diagram_generator.create_diagrams(
                parsing_results, artifacts_dir, session_id
            )
            results["features"].append({
                "name": "Architecture Diagram",
                "result": diagram_result,
                "message": diagram_msg
            })
            
            if diagram_result:
                for diagram_type, diagram_data in diagram_result.items():
                    if 'html_content' in diagram_data:
                        diagrams_html += f"<h3>{diagram_type.title()}</h3>" + diagram_data['html_content']
                    if 'file_path' in diagram_data:
                        download_files.append(diagram_data['file_path'])
        
        if "Dependency Analysis" in features_selected:
            progress(0.6, desc="🔗 Analyzing dependencies...")
            dep_result, dep_msg = dependency_analyzer.analyze_import_relationships(parsing_results)
            results["features"].append({
                "name": "Dependency Analysis", 
                "result": dep_result,
                "message": dep_msg
            })
        
        if "Security Scan" in features_selected:
            progress(0.8, desc="🔒 Scanning for vulnerabilities...")
            security_result, security_msg = security_scanner.comprehensive_security_scan(parsing_results)
            results["features"].append({
                "name": "Security Scan",
                "result": security_result,
                "message": security_msg
            })
        
        if "AI Documentation" in features_selected:
            progress(0.9, desc="📚 Generating AI documentation...")
            doc_result, doc_msg = glm_handler.generate_documentation(parsing_results)
            results["features"].append({
                "name": "AI Documentation",
                "result": doc_result,
                "message": doc_msg
            })
        
        if "Metrics Charts" in features_selected:
            progress(0.95, desc="📊 Creating metrics charts...")
            chart_result, chart_msg = chart_creator.create_metrics_dashboard(
                parsing_results, artifacts_dir, session_id
            )
            if chart_result:
                for chart_type, chart_data in chart_result.items():
                    if 'html_content' in chart_data:
                        charts_html += f"<h3>{chart_type.title()}</h3>" + chart_data['html_content']
                    if 'file_path' in chart_data:
                        download_files.append(chart_data['file_path'])
        
        progress(1.0, desc="✅ Analysis complete!")
        
        # Format results for display
        summary = format_results_display(results)
        combined_visuals = diagrams_html + charts_html if (diagrams_html or charts_html) else "<p>No visualizations generated</p>"
        
        return summary, combined_visuals, download_files
        
    except Exception as e:
        error_msg = f"❌ Analysis failed: {str(e)}"
        print(error_msg)
        return error_msg, None, None

def format_results_display(results):
    """Format analysis results for Gradio display"""
    output = f"# 🎯 Analysis Results - {results['session_id']}\n\n"
    
    parsing_info = results.get("parsing", {})
    if parsing_info:
        output += f"**📊 Parsing Status:** {parsing_info.get('message', 'Unknown')}\n\n"
    
    for feature in results["features"]:
        output += f"## {feature['name']}\n\n"
        output += f"**Status:** {feature['message']}\n\n"
        
        if feature['name'] == "Architecture Diagram":
            if feature['result']:
                output += f"**Diagrams Generated:** ✅ ({len(feature['result'])} types)\n\n"
            else:
                output += f"**Diagrams Generated:** ❌\n\n"
                
        elif feature['name'] == "Dependency Analysis":
            if feature['result']:
                summary = feature['result'].get('summary', {})
                output += f"**Modules:** {summary.get('total_modules', 0)}\n"
                output += f"**Dependencies:** {summary.get('total_dependencies', 0)}\n"
                output += f"**Circular Dependencies:** {summary.get('circular_count', 0)}\n\n"
                
        elif feature['name'] == "Security Scan":
            if feature['result']:
                vulnerabilities = feature['result'].get('vulnerabilities', [])
                output += f"**Vulnerabilities Found:** {len(vulnerabilities)}\n\n"
                
        elif feature['name'] == "AI Documentation":
            if feature['result']:
                output += f"**Documentation Generated:** ✅\n\n"
    
    return output

def create_gradio_app():
    """Create the main Gradio interface"""
    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate"
    )
    
    with gr.Blocks(
        title="Code Architecture Visualizer",
        theme=theme,
        css="""
        .gradio-container { max-width: 1400px !important; margin: auto !important; }
        .card { background: #f8f9fa; padding: 14px; border-radius: 10px; border-left: 4px solid #1976d2; }
        """
    ) as app:
        
        gr.HTML("""
        <div class="card" style="text-align: center; margin-bottom: 20px;">
            <h1>🏗️ Code Architecture Visualizer</h1>
            <p>Transform your codebase into visual intelligence with AI-powered analysis</p>
            <p><strong>🤖 Powered by GLM-4</strong> | <strong>⚡ Real-time Analysis</strong> | <strong>🎨 Interactive Visualizations</strong></p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("<h3>📥 Input Source</h3>")
                
                file_upload = gr.File(
                    label="Upload Codebase (.zip)",
                    file_types=[".zip", ".tar.gz"],
                    type="filepath"
                )
                
                github_url = gr.Textbox(
                    label="GitHub Repository URL",
                    placeholder="https://github.com/user/repo",
                    info="Alternative to file upload"
                )
                
                features_selected = gr.CheckboxGroup(
                    choices=[
                        "Architecture Diagram",
                        "Dependency Analysis", 
                        "Security Scan",
                        "AI Documentation",
                        "Metrics Charts"
                    ],
                    value=["Architecture Diagram", "Dependency Analysis", "Metrics Charts"],
                    label="Analysis Features"
                )
                
                analyze_btn = gr.Button(
                    "🚀 Start Analysis",
                    variant="primary",
                    size="lg"
                )
            
            with gr.Column(scale=2):
                gr.HTML("<h3>📊 Results</h3>")
                
                with gr.Tabs():
                    with gr.TabItem("📋 Summary"):
                        results_display = gr.Markdown(
                            value="Upload a codebase or provide GitHub URL to start analysis.",
                            height=500
                        )
                    
                    with gr.TabItem("🎨 Visualizations"):
                        diagram_display = gr.HTML(
                            value="<p>Architecture diagrams and charts will appear here after analysis.</p>",
                            height=600
                        )
                    
                    with gr.TabItem("📁 Downloads"):
                        download_files = gr.File(
                            label="Generated Files",
                            file_count="multiple",
                            visible=True
                        )
        
        # Event handlers
        analyze_btn.click(
            fn=analyze_codebase,
            inputs=[file_upload, github_url, features_selected],
            outputs=[results_display, diagram_display, download_files],
            show_progress=True
        )
        
        gr.HTML("""
        <div style="margin-top: 30px; text-align: center; color: #666;">
            <p>Built with ❤️ using GLM-4 • Open Source • Made for Developers</p>
            <p><small>Powered by Gradio, PyTorch, and HuggingFace Transformers</small></p>
        </div>
        """)
    
    return app

if __name__ == "__main__":
    print("🌟 Launching Code Architecture Visualizer...")
    app = create_gradio_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )