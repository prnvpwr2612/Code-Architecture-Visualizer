# utils/helpers.py

import os
import zipfile
import tempfile
import shutil
import git
from datetime import datetime
from pathlib import Path

class ProjectHelpers:
    def __init__(self):
        print("🛠️ ProjectHelpers initialization complete.")
        self.temp_directories = []

    def extract_codebase(self, file_upload):
        print("📂 Extracting uploaded codebase...")
        try:
            if not file_upload:
                raise ValueError("No file uploaded")
            
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = tempfile.mkdtemp(prefix=f"codebase_{session_id}_")
            self.temp_directories.append(temp_dir)
            
            file_path = file_upload.name if hasattr(file_upload, 'name') else file_upload
            
            if file_path.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                print(f"✅ ZIP file extracted to: {temp_dir}")
            elif file_path.endswith(('.tar.gz', '.tgz')):
                import tarfile
                with tarfile.open(file_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(temp_dir)
                print(f"✅ TAR.GZ file extracted to: {temp_dir}")
            else:
                raise ValueError(f"Unsupported file format: {Path(file_path).suffix}")
            
            extracted_files = list(Path(temp_dir).rglob('*'))
            print(f"📊 Extraction summary:")
            print(f"  📁 Total items: {len(extracted_files)}")
            print(f"  📄 Files: {len([f for f in extracted_files if f.is_file()])}")
            print(f"  📂 Directories: {len([f for f in extracted_files if f.is_dir()])}")
            
            return temp_dir
            
        except Exception as e:
            error_msg = f"❌ Codebase extraction failed: {str(e)}"
            print(error_msg)
            print("⭐ Resolution Strategies:")
            print("  1. Ensure file is a valid ZIP or TAR.GZ archive")
            print("  2. Check file is not corrupted or password-protected")
            print("  3. Verify sufficient disk space for extraction")
            print("  4. Try with smaller archive files")
            print("  5. Check file upload completed successfully")
            return None

    def clone_repository(self, github_url, github_token=None):
        print(f"🔗 Cloning repository: {github_url}")
        try:
            if not github_url or not github_url.startswith(('https://github.com', 'git@github.com')):
                raise ValueError("Invalid GitHub URL format")
            
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = tempfile.mkdtemp(prefix=f"repo_{session_id}_")
            self.temp_directories.append(temp_dir)
            
            if github_token:
                auth_url = github_url.replace('https://github.com/', f'https://{github_token}@github.com/')
                git.Repo.clone_from(auth_url, temp_dir)
                print("🔐 Repository cloned with authentication")
            else:
                git.Repo.clone_from(github_url, temp_dir)
                print("🌐 Repository cloned publicly")
            
            cloned_files = list(Path(temp_dir).rglob('*'))
            python_files = [f for f in cloned_files if f.suffix == '.py' and f.is_file()]
            
            print(f"📊 Clone summary:")
            print(f"  📁 Total items: {len(cloned_files)}")
            print(f"  🐍 Python files: {len(python_files)}")
            print(f"  📂 Location: {temp_dir}")
            
            return temp_dir
            
        except Exception as e:
            error_msg = f"❌ Repository cloning failed: {str(e)}"
            print(error_msg)
            print("⭐ Resolution Strategies:")
            print("  1. Verify GitHub URL is correct and accessible")
            print("  2. Check internet connectivity")
            print("  3. For private repos, provide valid GitHub token")
            print("  4. Ensure repository exists and is not archived")
            print("  5. Try with smaller repositories first")
            return None

    def create_session_artifacts(self, session_id):
        print(f"📁 Creating artifacts directory for session: {session_id}")
        try:
            artifacts_dir = f"./artifacts/{session_id}"
            os.makedirs(artifacts_dir, exist_ok=True)
            
            subdirs = ['diagrams', 'docs', 'exports', 'security', 'dependencies']
            for subdir in subdirs:
                os.makedirs(os.path.join(artifacts_dir, subdir), exist_ok=True)
            
            print(f"✅ Artifacts structure created:")
            for subdir in subdirs:
                print(f"  📂 {artifacts_dir}/{subdir}")
            
            return artifacts_dir
            
        except Exception as e:
            error_msg = f"❌ Artifacts creation failed: {str(e)}"
            print(error_msg)
            print("⭐ Resolution Strategies:")
            print("  1. Check write permissions in current directory")
            print("  2. Ensure sufficient disk space")
            print("  3. Verify session_id is valid filename")
            print("  4. Try creating in different location")
            print("  5. Check directory path length limits")
            return None

    def cleanup_session(self, session_id=None):
        print("🧹 Cleaning up temporary session files...")
        try:
            cleaned_count = 0
            for temp_dir in self.temp_directories[:]:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    self.temp_directories.remove(temp_dir)
                    cleaned_count += 1
            
            print(f"✅ Cleanup complete: {cleaned_count} directories removed")
            return True
            
        except Exception as e:
            error_msg = f"⚠️ Cleanup warning: {str(e)}"
            print(error_msg)
            print("⭐ Resolution Strategies:")
            print("  1. Some files may still be in use")
            print("  2. Check file permissions")
            print("  3. Restart session for full cleanup")
            print("  4. Manual cleanup may be needed")
            return False

    def validate_project_structure(self, project_path):
        print("🔍 Validating project structure...")
        try:
            project_path = Path(project_path)
            if not project_path.exists():
                raise ValueError("Project path does not exist")
            
            python_files = list(project_path.rglob('*.py'))
            js_files = list(project_path.rglob('*.js'))
            config_files = list(project_path.glob('*requirements*.txt')) + list(project_path.glob('setup.py')) + list(project_path.glob('pyproject.toml'))
            
            entry_points = []
            for py_file in python_files:
                if py_file.name in ['main.py', 'app.py', 'run.py', '__main__.py']:
                    entry_points.append(py_file)
            
            validation_result = {
                'valid': len(python_files) > 0 or len(js_files) > 0,
                'python_files': len(python_files),
                'js_files': len(js_files),
                'config_files': len(config_files),
                'entry_points': len(entry_points),
                'primary_language': 'python' if len(python_files) >= len(js_files) else 'javascript',
                'structure_score': min(100, (len(python_files) * 10) + (len(config_files) * 5) + (len(entry_points) * 15))
            }
            
            print(f"📊 Project validation results:")
            print(f"  ✅ Valid project: {validation_result['valid']}")
            print(f"  🐍 Python files: {validation_result['python_files']}")
            print(f"  📄 JavaScript files: {validation_result['js_files']}")
            print(f"  ⚙️ Config files: {validation_result['config_files']}")
            print(f"  🎯 Entry points: {validation_result['entry_points']}")
            print(f"  🏆 Structure score: {validation_result['structure_score']}/100")
            
            return validation_result, "✅ Project validation complete"
            
        except Exception as e:
            error_msg = f"❌ Project validation failed: {str(e)}"
            print(error_msg)
            print("⭐ Resolution Strategies:")
            print("  1. Check if path exists and is accessible")
            print("  2. Ensure project contains source code files")
            print("  3. Verify file permissions")
            print("  4. Try with different project structure")
            print("  5. Check for hidden or system files")
            return None, error_msg

print("🎯 utils/helpers.py module export ready.")