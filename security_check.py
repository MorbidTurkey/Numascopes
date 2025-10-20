#!/usr/bin/env python3
"""
Security verification script for GitHub deployment.
Checks for potential security issues before committing to version control.
"""

import os
import re
import glob
import sys

class SecurityChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        
    def check_env_files(self):
        """Check for .env files that shouldn't be committed."""
        print("🔍 Checking for .env files...")
        
        env_files = glob.glob('.env*')
        env_files = [f for f in env_files if not f.endswith('.example')]
        
        if env_files:
            for env_file in env_files:
                if os.path.exists(env_file):
                    self.issues.append(f"❌ Found {env_file} - this contains secrets and should not be committed!")
        else:
            print("✅ No .env files found in root directory")
    
    def check_database_files(self):
        """Check for database files that contain user data."""
        print("🔍 Checking for database files...")
        
        db_patterns = ['*.db', '*.sqlite', '*.sqlite3']
        db_files = []
        
        for pattern in db_patterns:
            db_files.extend(glob.glob(pattern))
            db_files.extend(glob.glob(f'**/{pattern}', recursive=True))
        
        if db_files:
            for db_file in db_files:
                self.issues.append(f"❌ Found {db_file} - database files contain user data and should not be committed!")
        else:
            print("✅ No database files found")
    
    def check_hardcoded_secrets(self):
        """Check for hardcoded API keys or secrets in Python files."""
        print("🔍 Checking for hardcoded secrets...")
        
        secret_patterns = [
            r'sk-[a-zA-Z0-9]{48,}',  # OpenAI API keys
            r'api_key\s*=\s*["\'][^"\']+["\']',  # API key assignments
            r'secret_key\s*=\s*["\'][^"\']+["\']',  # Secret key assignments (not env vars)
            r'password\s*=\s*["\'][^"\']+["\']',  # Password assignments
        ]
        
        python_files = glob.glob('**/*.py', recursive=True)
        
        for file_path in python_files:
            if file_path.startswith('.'):  # Skip hidden directories
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for pattern in secret_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            # Skip if it's using os.environ
                            if 'os.environ' in content or 'os.getenv' in content:
                                continue
                            self.issues.append(f"❌ Potential hardcoded secret in {file_path}: {matches[0][:20]}...")
                            
            except Exception as e:
                self.warnings.append(f"⚠️  Could not read {file_path}: {e}")
        
        print("✅ Hardcoded secrets check completed")
    
    def check_gitignore(self):
        """Check if .gitignore exists and contains essential entries."""
        print("🔍 Checking .gitignore file...")
        
        if not os.path.exists('.gitignore'):
            self.issues.append("❌ No .gitignore file found!")
            return
        
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        
        essential_entries = ['.env', '*.db', '__pycache__', '.venv']
        
        for entry in essential_entries:
            if entry not in gitignore_content:
                self.issues.append(f"❌ .gitignore missing essential entry: {entry}")
        
        print("✅ .gitignore check completed")
    
    def check_demo_credentials(self):
        """Check for demo credentials that should be changed in production."""
        print("🔍 Checking for demo credentials...")
        
        files_to_check = ['init_db.py', 'test_setup.py']
        demo_indicators = ['demopassword', 'demo@example.com', 'test-key', 'dev-secret-key']
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        for indicator in demo_indicators:
                            if indicator in content:
                                self.warnings.append(f"⚠️  Demo credential found in {file_path}: {indicator}")
                except UnicodeDecodeError:
                    # Try with different encoding
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                            
                            for indicator in demo_indicators:
                                if indicator in content:
                                    self.warnings.append(f"⚠️  Demo credential found in {file_path}: {indicator}")
                    except Exception:
                        self.warnings.append(f"⚠️  Could not read {file_path} for credential check")
        
        print("✅ Demo credentials check completed")
    
    def run_all_checks(self):
        """Run all security checks."""
        print("🔒 SECURITY VERIFICATION FOR GITHUB DEPLOYMENT")
        print("=" * 55)
        print()
        
        self.check_env_files()
        self.check_database_files()
        self.check_hardcoded_secrets()
        self.check_gitignore()
        self.check_demo_credentials()
        
        print()
        print("📋 SECURITY REPORT")
        print("=" * 20)
        
        if self.issues:
            print("🚨 CRITICAL ISSUES (must fix before commit):")
            for issue in self.issues:
                print(f"  {issue}")
            print()
        
        if self.warnings:
            print("⚠️  WARNINGS (review before production):")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        if not self.issues and not self.warnings:
            print("✅ No security issues found! Safe to commit to GitHub.")
        elif not self.issues:
            print("✅ No critical issues found. Review warnings before production.")
        else:
            print("❌ Critical security issues found. DO NOT commit to GitHub until resolved!")
            return False
        
        print()
        print("📚 Next steps:")
        print("1. Review SECURITY_GUIDE.md for deployment instructions")
        print("2. Set environment variables on your hosting platform")
        print("3. Use init_production_db.py for production database setup")
        print("4. Generate secure SECRET_KEY with generate_secret_key.py")
        
        return len(self.issues) == 0

def main():
    checker = SecurityChecker()
    is_safe = checker.run_all_checks()
    
    if not is_safe:
        sys.exit(1)  # Exit with error code if issues found
    
    sys.exit(0)  # Exit successfully

if __name__ == '__main__':
    main()