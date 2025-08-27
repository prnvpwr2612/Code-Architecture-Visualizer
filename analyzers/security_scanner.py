# analyzers/security_scanner.py

import re
import os
from pathlib import Path

class SecurityScanner:
    def __init__(self):
        print("🔒 SecurityScanner initialization complete.")
        self.vulnerability_patterns = {
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']'
            ],
            'sql_injection': [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'query\s*\(\s*["\'].*\+.*["\']',
                r'cursor\.execute\s*\(\s*["\'].*%.*["\']'
            ],
            'command_injection': [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
                r'exec\s*\(',
                r'eval\s*\('
            ],
            'unsafe_imports': [
                r'import\s+pickle',
                r'from\s+pickle\s+import',
                r'import\s+marshal',
                r'from\s+marshal\s+import'
            ],
            'weak_crypto': [
                r'hashlib\.md5\s*\(',
                r'hashlib\.sha1\s*\(',
                r'random\.random\s*\(',
                r'random\.choice\s*\('
            ]
        }

    def comprehensive_security_scan(self, parsing_results):
        print("🛡️ Starting comprehensive security analysis...")
        try:
            vulnerabilities = []
            risk_summary = {'high': 0, 'medium': 0, 'low': 0}
            
            parsed_files = parsing_results.get('parsed_files', {})
            
            for file_path, parse_data in parsed_files.items():
                if not parse_data.get('parsing_successful', False):
                    continue
                
                source_code = parse_data.get('source_code', '')
                if not source_code:
                    continue
                
                file_vulnerabilities = self._scan_file_content(file_path, source_code)
                vulnerabilities.extend(file_vulnerabilities)
                
                for vuln in file_vulnerabilities:
                    risk_summary[vuln['severity']] += 1
            
            scan_results = {
                'vulnerabilities': vulnerabilities,
                'risk_summary': risk_summary,
                'total_files_scanned': len([f for f in parsed_files if parsed_files[f].get('parsing_successful', False)]),
                'total_vulnerabilities': len(vulnerabilities)
            }
            
            print(f"✅ Security scan completed:")
            print(f"  📄 Files scanned: {scan_results['total_files_scanned']}")
            print(f"  🚨 Total vulnerabilities: {scan_results['total_vulnerabilities']}")
            print(f"  🔴 High risk: {risk_summary['high']}")
            print(f"  🟡 Medium risk: {risk_summary['medium']}")
            print(f"  🟢 Low risk: {risk_summary['low']}")
            
            return scan_results, "✅ Security scan completed successfully"
            
        except Exception as e:
            error_msg = f"❌ Security scan failed: {str(e)}"
            print(error_msg)
            print("⭐ Resolution Strategies:")
            print("  1. Check source code encoding and format")
            print("  2. Verify regex pattern compatibility")
            print("  3. Reduce file size for memory constraints")
            print("  4. Test with individual files first")
            print("  5. Update vulnerability pattern database")
            return None, error_msg

    def _scan_file_content(self, file_path, source_code):
        vulnerabilities = []
        lines = source_code.split('\n')
        
        for category, patterns in self.vulnerability_patterns.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        severity = self._determine_severity(category)
                        vulnerabilities.append({
                            'file_path': file_path,
                            'line_number': line_num,
                            'category': category,
                            'severity': severity,
                            'pattern_matched': pattern,
                            'code_snippet': line.strip(),
                            'description': self._get_vulnerability_description(category)
                        })
        
        return vulnerabilities

    def _determine_severity(self, category):
        severity_map = {
            'hardcoded_secrets': 'high',
            'sql_injection': 'high',
            'command_injection': 'high',
            'unsafe_imports': 'medium',
            'weak_crypto': 'medium'
        }
        return severity_map.get(category, 'low')

    def _get_vulnerability_description(self, category):
        descriptions = {
            'hardcoded_secrets': 'Hardcoded credentials detected. Store secrets in environment variables or secure vaults.',
            'sql_injection': 'Potential SQL injection vulnerability. Use parameterized queries or ORM methods.',
            'command_injection': 'Command injection risk detected. Validate and sanitize all user inputs.',
            'unsafe_imports': 'Unsafe serialization module imported. Consider safer alternatives like json.',
            'weak_crypto': 'Weak cryptographic function detected. Use stronger algorithms like SHA-256 or bcrypt.'
        }
        return descriptions.get(category, 'Security issue detected. Review code for potential vulnerabilities.')

    def generate_security_report(self, scan_results, output_dir="./artifacts", session_id="default"):
        print("📋 Generating security vulnerability report...")
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            vulnerabilities = scan_results.get('vulnerabilities', [])
            risk_summary = scan_results.get('risk_summary', {})
            
            report_content = f"""# Security Vulnerability Report

## Summary
- **Total Files Scanned:** {scan_results.get('total_files_scanned', 0)}
- **Total Vulnerabilities:** {len(vulnerabilities)}
- **High Risk:** {risk_summary.get('high', 0)}
- **Medium Risk:** {risk_summary.get('medium', 0)}
- **Low Risk:** {risk_summary.get('low', 0)}

## Detailed Findings

"""
            
            for i, vuln in enumerate(vulnerabilities, 1):
                severity_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(vuln['severity'], '⚪')
                report_content += f"""### {i}. {severity_emoji} {vuln['category'].replace('_', ' ').title()}

**File:** `{Path(vuln['file_path']).name}`  
**Line:** {vuln['line_number']}  
**Severity:** {vuln['severity'].upper()}

**Code:**
{vuln['code_snippet']}


**Description:** {vuln['description']}

---

"""
            
            report_path = os.path.join(output_dir, f"security_report_{session_id}.md")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"✅ Security report generated: {report_path}")
            return report_path, "✅ Security report generated successfully"
            
        except Exception as e:
            error_msg = f"❌ Report generation failed: {str(e)}"
            print(error_msg)
            print("⭐ Resolution Strategies:")
            print("  1. Check write permissions for output directory")
            print("  2. Ensure sufficient disk space")
            print("  3. Verify scan results data structure")
            print("  4. Try generating smaller reports")
            print("  5. Check file encoding compatibility")
            return None, error_msg

print("🎯 analyzers/security_scanner.py module export ready.")
