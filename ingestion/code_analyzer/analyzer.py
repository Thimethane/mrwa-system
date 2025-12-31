import ast
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyze source code and extract structure"""
    
    def __init__(self):
        self.supported_languages = {
            'python': self._analyze_python,
            'javascript': self._analyze_generic,
            'typescript': self._analyze_generic,
            'java': self._analyze_generic,
            'cpp': self._analyze_generic,
        }
    
    def analyze(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """Analyze source code"""
        try:
            analyzer_func = self.supported_languages.get(
                language.lower(),
                self._analyze_generic
            )
            
            result = analyzer_func(code)
            result["success"] = True
            result["language"] = language
            
            logger.info(f"Successfully analyzed {language} code ({len(code)} chars)")
            return result
            
        except Exception as e:
            logger.error(f"Code analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _analyze_python(self, code: str) -> Dict[str, Any]:
        """Analyze Python code using AST"""
        try:
            tree = ast.parse(code)
            
            analysis = {
                "functions": [],
                "classes": [],
                "imports": [],
                "lines_of_code": len(code.split('\n')),
                "docstrings": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append({
                        "name": node.name,
                        "line_number": node.lineno,
                        "arguments": [arg.arg for arg in node.args.args],
                    })
                
                elif isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    analysis["classes"].append({
                        "name": node.name,
                        "line_number": node.lineno,
                        "methods": methods,
                    })
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append({
                            "module": alias.name,
                            "alias": alias.asname
                        })
            
            analysis["complexity"] = {
                "num_functions": len(analysis["functions"]),
                "num_classes": len(analysis["classes"]),
                "num_imports": len(analysis["imports"]),
            }
            
            return analysis
            
        except SyntaxError as e:
            logger.warning(f"Python syntax error: {e}")
            return self._analyze_generic(code)
    
    def _analyze_generic(self, code: str) -> Dict[str, Any]:
        """Generic code analysis"""
        lines = code.split('\n')
        
        analysis = {
            "lines_of_code": len(lines),
            "non_empty_lines": len([l for l in lines if l.strip()]),
            "comment_lines": 0,
            "estimated_functions": 0,
            "estimated_classes": 0
        }
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('#'):
                analysis["comment_lines"] += 1
            if 'function ' in stripped or 'def ' in stripped:
                analysis["estimated_functions"] += 1
            if 'class ' in stripped:
                analysis["estimated_classes"] += 1
        
        return analysis
