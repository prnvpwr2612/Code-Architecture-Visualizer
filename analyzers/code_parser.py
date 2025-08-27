# analyzers/code_parser.py

import os
import ast

class CodeParser:
    def __init__(self):
        print("🧩 CodeParser initialization complete.")
        self.supported_ext = [".py"]

    def parse_project(self, root_dir):
        print(f"🔍 Parsing project in: {root_dir}")
        results = {"parsed_files": {}, "unsupported_files": []}
        try:
            for dirpath, _, files in os.walk(root_dir):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    fpath = os.path.join(dirpath, file)
                    if ext in self.supported_ext:
                        parse_data = self._parse_python_file(fpath)
                        results["parsed_files"][fpath] = parse_data
                    else:
                        results["unsupported_files"].append(fpath)
            print(f"✅ Parsing complete. Files: {len(results['parsed_files'])}")
            return results, "✅ All supported files parsed"
        except Exception as e:
            print(f"❌ Project parse error: {str(e)}")
            print("Resolution strategies:\n- Verify directory path\n- Permission check\n- Reduce input size\n- Inspect failing files\n- Debug with minimal example")
            return {}, "❌ Parse error"

    def _parse_python_file(self, fpath):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                code = f.read()
            node = ast.parse(code)
            functions, classes, imports = [], [], {"standard_imports": [], "from_imports": []}
            for n in ast.walk(node):
                if isinstance(n, ast.FunctionDef):
                    functions.append({"name": n.name, "lineno": n.lineno, "end_lineno": getattr(n, "end_lineno", None)})
                elif isinstance(n, ast.ClassDef):
                    classes.append({"name": n.name, "lineno": n.lineno, "end_lineno": getattr(n, "end_lineno", None)})
                elif isinstance(n, ast.Import):
                    for alias in n.names:
                        imports["standard_imports"].append({"module": alias.name, "alias": alias.asname, "line": n.lineno})
                elif isinstance(n, ast.ImportFrom):
                    for alias in n.names:
                        imports["from_imports"].append({
                            "module": n.module, "name": alias.name, "alias": alias.asname, "line": n.lineno
                        })
            print(f"📄 {os.path.basename(fpath)}: Parsed ({len(functions)} funcs, {len(classes)} classes, {len(imports['standard_imports'])+len(imports['from_imports'])} imports)")
            return {
                "parsing_successful": True,
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "source_lines": len(code.splitlines()),
                "source_code": code
            }
        except Exception as e:
            print(f"❌ Failed to parse {fpath}: {str(e)}")
            print("Resolution strategies:\n- Check syntax validity\n- Remove non-UTF8 chars\n- Check unsupported Python versions\n- Reduce file size\n- Test with simpler file")
            return {"parsing_successful": False, "error": str(e)}

# Test print for CodeParser cell
print("🎯 analyzers/code_parser.py module export ready.")
