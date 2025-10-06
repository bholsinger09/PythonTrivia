"""
Technical Debt Analysis and Cleanup Plan
Identifies and addresses technical debt across the Python Trivia codebase
"""

# 🚨 TECHNICAL DEBT ANALYSIS
# ========================

## HIGH PRIORITY ISSUES (Fix Immediately):

### 1. Empty Core Files
- models.py (EMPTY) - Critical database models missing
- db_service.py (EMPTY) - Database service layer missing
- These are imported by app.py but contain no code

### 2. Import Resolution Issues
- psycopg2 imports in database files (missing from requirements?)
- orjson optional dependency handling

### 3. HTML Template Issues
- JavaScript errors in admin templates (Jinja2 template syntax in onclick)
- Multiple duplicate/similar template files

## MEDIUM PRIORITY ISSUES:

### 4. Code Duplication
- Multiple user management files (manage_users.py, manage_users_original.py)
- Multiple persistence files (user_persistence.py, user_persistence_original.py)
- Backup versions of app.py files

### 5. Database Access Patterns
- Multiple database access utilities doing similar things
- Direct database access scripts mixed with application logic

### 6. Test Organization
- 30+ test files with overlapping coverage
- Tests scattered across different patterns

## LOW PRIORITY ISSUES:

### 7. File Organization
- Too many utility scripts in root directory
- Optional features should be properly organized
- Debug/development scripts mixed with production code

### 8. Configuration Management
- Multiple configuration approaches
- Environment-specific logic scattered

## 🔧 CLEANUP PLAN
# ===============

Priority 1: Fix Critical Missing Files
Priority 2: Consolidate Duplicated Code
Priority 3: Organize File Structure
Priority 4: Clean Up Import Issues
Priority 5: Optimize Test Suite
"""

import os
import sys
from typing import List, Dict, Tuple

class TechnicalDebtAnalyzer:
    """Analyzes and helps clean up technical debt"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.issues = []
        self.duplicates = []
        self.empty_files = []
        
    def analyze_empty_files(self) -> List[str]:
        """Find empty or nearly empty important files"""
        critical_files = [
            'models.py',
            'db_service.py', 
            'wsgi.py'
        ]
        
        empty_files = []
        for file in critical_files:
            file_path = os.path.join(self.project_root, file)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read().strip()
                    if len(content) < 50:  # Essentially empty
                        empty_files.append(file)
        
        return empty_files
    
    def find_duplicate_files(self) -> List[Tuple[str, List[str]]]:
        """Find files that appear to be duplicates or versions"""
        duplicates = []
        
        # Known duplicate patterns
        patterns = [
            ('manage_users', ['manage_users.py', 'manage_users_original.py']),
            ('user_persistence', ['user_persistence.py', 'user_persistence_original.py']),
            ('app', ['app.py', 'app.py.backup', 'app.py.bak', 'app.py.new']),
            ('init_db', ['init_db.py', 'init_db_fixed.py']),
        ]
        
        for pattern_name, files in patterns:
            existing_files = []
            for file in files:
                if os.path.exists(os.path.join(self.project_root, file)):
                    existing_files.append(file)
            
            if len(existing_files) > 1:
                duplicates.append((pattern_name, existing_files))
        
        return duplicates
    
    def analyze_import_issues(self) -> Dict[str, List[str]]:
        """Analyze import resolution issues"""
        issues = {
            'missing_optional': [],
            'missing_required': [],
            'circular_imports': []
        }
        
        # Known optional dependencies
        optional_deps = ['orjson', 'redis']
        
        # Known required dependencies that might be missing
        required_deps = ['psycopg2', 'flask-login']
        
        # This is a simplified analysis - in practice you'd parse AST
        return issues
    
    def count_test_files(self) -> Dict[str, int]:
        """Count and categorize test files"""
        test_dir = os.path.join(self.project_root, 'tests')
        if not os.path.exists(test_dir):
            return {'total': 0}
        
        test_files = [f for f in os.listdir(test_dir) if f.startswith('test_') and f.endswith('.py')]
        
        return {
            'total': len(test_files),
            'auth_tests': len([f for f in test_files if 'auth' in f]),
            'coverage_tests': len([f for f in test_files if 'coverage' in f]),
            'database_tests': len([f for f in test_files if 'database' in f or 'db' in f]),
        }
    
    def generate_cleanup_recommendations(self) -> List[str]:
        """Generate specific cleanup recommendations"""
        recommendations = []
        
        # Check for empty critical files
        empty_files = self.analyze_empty_files()
        if empty_files:
            recommendations.append(f"🚨 CRITICAL: Restore missing core files: {', '.join(empty_files)}")
        
        # Check for duplicates
        duplicates = self.find_duplicate_files()
        if duplicates:
            for pattern, files in duplicates:
                recommendations.append(f"📁 DUPLICATE: Consolidate {pattern} files: {', '.join(files)}")
        
        # Check test organization
        test_stats = self.count_test_files()
        if test_stats['total'] > 20:
            recommendations.append(f"🧪 TEST CLEANUP: {test_stats['total']} test files - consider consolidation")
        
        # File organization
        recommendations.append("📂 ORGANIZE: Move debug/utility scripts to scripts/ directory")
        recommendations.append("🧹 CLEANUP: Remove backup files and consolidate similar functionality")
        
        return recommendations

def main():
    """Analyze technical debt and generate cleanup plan"""
    project_root = '/Users/benh/Documents/PythonTrivia'
    analyzer = TechnicalDebtAnalyzer(project_root)
    
    print("🔍 TECHNICAL DEBT ANALYSIS")
    print("=" * 40)
    
    recommendations = analyzer.generate_cleanup_recommendations()
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    print(f"\n📊 STATISTICS:")
    test_stats = analyzer.count_test_files()
    print(f"   - Test files: {test_stats['total']}")
    print(f"   - Auth tests: {test_stats.get('auth_tests', 0)}")
    print(f"   - Coverage tests: {test_stats.get('coverage_tests', 0)}")
    print(f"   - Database tests: {test_stats.get('database_tests', 0)}")
    
    empty_files = analyzer.analyze_empty_files()
    if empty_files:
        print(f"   - Empty critical files: {len(empty_files)}")
    
    duplicates = analyzer.find_duplicate_files()
    if duplicates:
        print(f"   - Duplicate file groups: {len(duplicates)}")

if __name__ == '__main__':
    main()