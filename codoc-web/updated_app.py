import ast
import os
import re
import textwrap
import logging
import concurrent.futures
import traceback
from dotenv import load_dotenv
import google.generativeai as genai
import javalang
import esprima
import pycparser
from functools import lru_cache

# Try to import radon, but provide fallbacks if it fails
try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit
    from radon.raw import analyze as raw_metrics
    RADON_AVAILABLE = True
except ImportError:
    logging.warning("Radon library not available. Using simplified Python analysis.")
    RADON_AVAILABLE = False

# --- Logging and Environment Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv(dotenv_path=os.getenv('GOOGLE_API_KEY_ENV', '.env'))

API_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('GENAI_API_KEY')
if API_KEY:
    genai.configure(api_key=API_KEY)
    logging.info("AI API key loaded successfully.")
else:
    logging.warning("No AI API key found. Skipping AI-powered analysis.")

# --- Language Detection Keywords ---
_LANGUAGE_KEYWORDS = {
    'python': ['def ', 'import ', 'print(', 'class ', 'if ', 'for ', 'while '],
    'javascript': ['function ', 'const ', 'let ', 'var ', '=>', 'console.log'],
    'java': ['public ', 'class ', 'static ', 'void ', 'private ', 'protected '],
    'c': ['#include', 'printf(', 'scanf(', 'int ', 'void ', 'return '],
}

# --- Analyzer Registry ---
ANALYZERS = {}

def register(lang):
    def wrapper(func):
        ANALYZERS[lang] = func
        return func
    return wrapper

# --- Language Detection ---
def detect_language(code: str) -> str:
    """Detect the programming language of the given code."""
    scores = {
        lang: sum(code.count(kw) for kw in keywords)
        for lang, keywords in _LANGUAGE_KEYWORDS.items()
    }
    top_lang, top_score = max(scores.items(), key=lambda x: x[1], default=('unknown', 0))
    if top_score == 0 or list(scores.values()).count(top_score) > 1:
        return 'unknown'
    return top_lang

# --- Standard Metrics ---
def standard_metrics(code: str, funcs: int, loc: int, time_c: int = None) -> dict:
    """Calculate standard code metrics."""
    if time_c is None:
        time_c = funcs * 2
    return {
        'functions': funcs,
        'loc': loc,
        'lloc': loc,
        'sloc': loc,
        'time_complexity': time_c,
        'space_complexity': loc * 2
    }

# --- Complexity Classification ---
def classify_complexity(value: int) -> str:
    """Classify complexity as low, medium, or high."""
    if value < 10:
        return "low"
    elif value < 20:
        return "medium"
    else:
        return "high"

# --- Fallback Python Analysis ---
def fallback_python_analysis(code: str) -> dict:
    """Fallback analysis when radon fails."""
    try:
        # Count lines
        loc = code.count('\n') + 1
        
        # Try to count functions using regex
        function_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        functions = re.findall(function_pattern, code)
        funcs = len(functions)
        
        # Create basic function data
        functions_data = []
        for func_name in functions:
            functions_data.append({
                'name': func_name,
                'complexity': 1,  # Default complexity
                'complexity_level': 'low',
                'loc': 5,  # Default LOC
                'nesting': 1  # Default nesting
            })
        
        return {
            'language': 'python',
            **standard_metrics(code, funcs, loc),
            'functions': functions_data
        }
    except Exception as e:
        logging.error(f"Fallback Python analysis error: {str(e)}")
        # Return minimal data
        return {
            'language': 'python',
            'functions': 0,
            'loc': code.count('\n') + 1,
            'lloc': code.count('\n') + 1,
            'sloc': code.count('\n') + 1,
            'time_complexity': 1,
            'space_complexity': 2,
            'functions': []
        }

# --- Language-specific Analyzers ---
@register('python')
def analyze_python(code: str) -> dict:
    """Analyze Python code and return metrics."""
    # First try with ast to check for syntax errors
    try:
        ast.parse(code)
    except SyntaxError as e:
        logging.error(f"Python syntax error: {str(e)}")
        raise ValueError(f"Python syntax error: {str(e)}") from e
    except Exception as e:
        logging.error(f"AST parsing error: {str(e)}")
        return fallback_python_analysis(code)
    
    # If radon is not available, use fallback
    if not RADON_AVAILABLE:
        return fallback_python_analysis(code)
    
    try:
        raw = raw_metrics(code)
        cc = cc_visit(code)
        tree = ast.parse(code)
        funcs = sum(isinstance(n, ast.FunctionDef) for n in ast.walk(tree))

        # Create structured function data
        functions = []
        time_c = 0
        
        for r in cc:
            depth = getattr(r, 'nested_blocks', 0)
            loc = r.endline - r.lineno + 1
            complexity = r.complexity
            time_c += complexity
            
            functions.append({
                'name': r.name,
                'complexity': complexity,
                'complexity_level': classify_complexity(complexity),
                'loc': loc,
                'nesting': depth
            })

        return {
            'language': 'python',
            **standard_metrics(code, funcs, raw.loc, time_c),
            'mi': mi_visit(code, True),
            'functions': functions
        }
    except Exception as e:
        logging.error(f"Python analysis error: {str(e)}")
        logging.error(traceback.format_exc())
        return fallback_python_analysis(code)

@register('javascript')
def analyze_js(code: str) -> dict:
    """Analyze JavaScript code and return metrics."""
    try:
        tree = esprima.parseScript(code)
        
        # Count functions and extract their details
        functions = []
        for node in tree.body:
            if isinstance(node, esprima.nodes.FunctionDeclaration):
                # Estimate complexity based on the number of statements
                complexity = estimate_js_complexity(node)
                functions.append({
                    'name': node.id.name,
                    'complexity': complexity,
                    'complexity_level': classify_complexity(complexity),
                    'loc': count_node_lines(node, code),
                    'nesting': estimate_nesting_depth(node)
                })
        
        funcs = len(functions)
        loc = code.count('\n') + 1
        time_c = sum(func['complexity'] for func in functions) if functions else funcs * 2
        
        return {
            'language': 'javascript',
            **standard_metrics(code, funcs, loc, time_c),
            'functions': functions
        }
    except Exception as e:
        logging.error(f"JavaScript analysis error: {str(e)}")
        # Return minimal data
        return {
            'language': 'javascript',
            'functions': 0,
            'loc': code.count('\n') + 1,
            'lloc': code.count('\n') + 1,
            'sloc': code.count('\n') + 1,
            'time_complexity': 1,
            'space_complexity': 2,
            'functions': []
        }

def estimate_js_complexity(node):
    """Estimate cyclomatic complexity for JavaScript functions."""
    complexity = 1  # Base complexity
    
    # Count decision points
    def count_decisions(node):
        nonlocal complexity
        if hasattr(node, 'type'):
            if node.type in ['IfStatement', 'ConditionalExpression']:
                complexity += 1
            elif node.type in ['ForStatement', 'WhileStatement', 'DoWhileStatement', 'ForInStatement', 'ForOfStatement']:
                complexity += 1
            elif node.type == 'SwitchCase':
                complexity += 1
        
        # Recursively process children
        for key in dir(node):
            if key.startswith('_') or key == 'type':
                continue
            value = getattr(node, key)
            if isinstance(value, list):
                for item in value:
                    if hasattr(item, 'type'):
                        count_decisions(item)
            elif hasattr(value, 'type'):
                count_decisions(value)
    
    count_decisions(node)
    return complexity

def count_node_lines(node, code):
    """Count the lines of code in a node."""
    if hasattr(node, 'range'):
        start, end = node.range
        return code.count('\n', start, end) + 1
    return 1

def estimate_nesting_depth(node):
    """Estimate the maximum nesting depth in a function."""
    max_depth = 0
    current_depth = 0
    
    def traverse(node):
        nonlocal max_depth, current_depth
        
        if hasattr(node, 'type'):
            if node.type in ['BlockStatement', 'IfStatement', 'ForStatement', 'WhileStatement', 
                            'DoWhileStatement', 'ForInStatement', 'ForOfStatement', 'SwitchStatement']:
                current_depth += 1
                max_depth = max(max_depth, current_depth)
        
        # Recursively process children
        for key in dir(node):
            if key.startswith('_') or key == 'type':
                continue
            value = getattr(node, key)
            if isinstance(value, list):
                for item in value:
                    if hasattr(item, 'type'):
                        traverse(item)
            elif hasattr(value, 'type'):
                traverse(value)
        
        if hasattr(node, 'type'):
            if node.type in ['BlockStatement', 'IfStatement', 'ForStatement', 'WhileStatement', 
                            'DoWhileStatement', 'ForInStatement', 'ForOfStatement', 'SwitchStatement']:
                current_depth -= 1
    
    traverse(node)
    return max_depth

@register('java')
def analyze_java(code: str) -> dict:
    """Analyze Java code and return metrics."""
    try:
        tree = javalang.parse.parse(code)
        
        # Extract methods and their details
        functions = []
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            # Estimate complexity based on the method body
            complexity = estimate_java_complexity(node)
            
            functions.append({
                'name': node.name,
                'complexity': complexity,
                'complexity_level': classify_complexity(complexity),
                'loc': estimate_method_loc(node, code),
                'nesting': estimate_java_nesting(node)
            })
        
        funcs = len(functions)
        loc = code.count('\n') + 1
        time_c = sum(func['complexity'] for func in functions) if functions else funcs * 2
        
        return {
            'language': 'java',
            **standard_metrics(code, funcs, loc, time_c),
            'functions': functions
        }
    except Exception as e:
        logging.error(f"Java analysis error: {str(e)}")
        # Return minimal data
        return {
            'language': 'java',
            'functions': 0,
            'loc': code.count('\n') + 1,
            'lloc': code.count('\n') + 1,
            'sloc': code.count('\n') + 1,
            'time_complexity': 1,
            'space_complexity': 2,
            'functions': []
        }

def estimate_java_complexity(method):
    """Estimate cyclomatic complexity for Java methods."""
    complexity = 1  # Base complexity
    
    # Count decision points in the method body
    if method.body:
        for statement in method.body:
            if isinstance(statement, javalang.tree.IfStatement):
                complexity += 1
            elif isinstance(statement, (javalang.tree.WhileStatement, javalang.tree.ForStatement, javalang.tree.DoStatement)):
                complexity += 1
            elif isinstance(statement, javalang.tree.SwitchStatement):
                complexity += len(statement.cases)
    
    return complexity

def estimate_method_loc(method, code):
    """Estimate lines of code in a Java method."""
    # This is a rough estimate since javalang doesn't provide line numbers
    return 10  # Default estimate

def estimate_java_nesting(method):
    """Estimate the maximum nesting depth in a Java method."""
    max_depth = 0
    current_depth = 0
    
    def traverse(node):
        nonlocal max_depth, current_depth
        
        if isinstance(node, (javalang.tree.BlockStatement, javalang.tree.IfStatement, 
                            javalang.tree.ForStatement, javalang.tree.WhileStatement,
                            javalang.tree.DoStatement, javalang.tree.SwitchStatement)):
            current_depth += 1
            max_depth = max(max_depth, current_depth)
        
        # Process children
        for attr_name in dir(node):
            if attr_name.startswith('_'):
                continue
            attr = getattr(node, attr_name)
            if isinstance(attr, list):
                for item in attr:
                    if isinstance(item, javalang.ast.Node):
                        traverse(item)
            elif isinstance(attr, javalang.ast.Node):
                traverse(attr)
        
        if isinstance(node, (javalang.tree.BlockStatement, javalang.tree.IfStatement, 
                            javalang.tree.ForStatement, javalang.tree.WhileStatement,
                            javalang.tree.DoStatement, javalang.tree.SwitchStatement)):
            current_depth -= 1
    
    if method.body:
        for statement in method.body:
            traverse(statement)
    
    return max_depth

@register('c')
def analyze_c(code: str) -> dict:
    """Analyze C code and return metrics."""
    parser = pycparser.CParser()
    try:
        astree = parser.parse(code)
        
        # Extract functions and their details
        functions = []
        for node in astree.ext:
            if isinstance(node, pycparser.c_ast.FuncDef):
                # Estimate complexity based on the function body
                complexity = estimate_c_complexity(node)
                
                functions.append({
                    'name': node.decl.name,
                    'complexity': complexity,
                    'complexity_level': classify_complexity(complexity),
                    'loc': estimate_c_loc(node, code),
                    'nesting': estimate_c_nesting(node)
                })
        
        funcs = len(functions)
        loc = code.count('\n') + 1
        time_c = sum(func['complexity'] for func in functions) if functions else funcs * 2
        
        return {
            'language': 'c',
            **standard_metrics(code, funcs, loc, time_c),
            'functions': functions
        }
    except Exception as e:
        logging.error(f"C analysis error: {str(e)}")
        # Return minimal data
        return {
            'language': 'c',
            'functions': 0,
            'loc': code.count('\n') + 1,
            'lloc': code.count('\n') + 1,
            'sloc': code.count('\n') + 1,
            'time_complexity': 1,
            'space_complexity': 2,
            'functions': []
        }

def estimate_c_complexity(func):
    """Estimate cyclomatic complexity for C functions."""
    complexity = 1  # Base complexity
    
    class ComplexityVisitor(pycparser.c_ast.NodeVisitor):
        def __init__(self):
            self.complexity = 1
        
        def visit_If(self, node):
            self.complexity += 1
            self.generic_visit(node)
        
        def visit_For(self, node):
            self.complexity += 1
            self.generic_visit(node)
        
        def visit_While(self, node):
            self.complexity += 1
            self.generic_visit(node)
        
        def visit_DoWhile(self, node):
            self.complexity += 1
            self.generic_visit(node)
        
        def visit_Switch(self, node):
            if node.cond is not None:
                self.complexity += len(node.stmt.block_items) if node.stmt.block_items else 1
            self.generic_visit(node)
        
        def visit_BinaryOp(self, node):
            if node.op in ['&&', '||']:
                self.complexity += 1
            self.generic_visit(node)
    
    visitor = ComplexityVisitor()
    visitor.visit(func)
    return visitor.complexity

def estimate_c_loc(func, code):
    """Estimate lines of code in a C function."""
    # This is a rough estimate since pycparser doesn't provide line numbers
    return 10  # Default estimate

def estimate_c_nesting(func):
    """Estimate the maximum nesting depth in a C function."""
    max_depth = 0
    current_depth = 0
    
    class NestingVisitor(pycparser.c_ast.NodeVisitor):
        def __init__(self):
            self.max_depth = 0
            self.current_depth = 0
        
        def visit_Compound(self, node):
            self.current_depth += 1
            self.max_depth = max(self.max_depth, self.current_depth)
            self.generic_visit(node)
            self.current_depth -= 1
        
        def visit_If(self, node):
            self.current_depth += 1
            self.max_depth = max(self.max_depth, self.current_depth)
            self.generic_visit(node)
            self.current_depth -= 1
        
        def visit_For(self, node):
            self.current_depth += 1
            self.max_depth = max(self.max_depth, self.current_depth)
            self.generic_visit(node)
            self.current_depth -= 1
        
        def visit_While(self, node):
            self.current_depth += 1
            self.max_depth = max(self.max_depth, self.current_depth)
            self.generic_visit(node)
            self.current_depth -= 1
        
        def visit_DoWhile(self, node):
            self.current_depth += 1
            self.max_depth = max(self.max_depth, self.current_depth)
            self.generic_visit(node)
            self.current_depth -= 1
        
        def visit_Switch(self, node):
            self.current_depth += 1
            self.max_depth = max(self.max_depth, self.current_depth)
            self.generic_visit(node)
            self.current_depth -= 1
    
    visitor = NestingVisitor()
    visitor.visit(func)
    return visitor.max_depth

# --- AI Summary Generator ---
@lru_cache(maxsize=32)
def ai_analysis(code: str, lang: str) -> str:
    """Generate AI-powered analysis of the code."""
    if not API_KEY:
        return 'Skipped AI analysis.'
    
    prompt = textwrap.dedent(f"""
        Analyze this {lang} code briefly: summary, time/space complexity, and refactoring areas.
        Don't give out long explanations, just a clear and brief summary.

        {code}
    """)
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        return model.generate_content(prompt).text.strip()
    except Exception as e:
        logging.error(f"AI analysis error: {str(e)}")
        return f"AI error: {e}"

# --- Entry Point for GUI ---
def run_analysis(code: str) -> dict:
    """Run code analysis and return results."""
    lang = detect_language(code)
    if lang == 'unknown':
        raise ValueError("Ambiguous or mixed languages detected. Submit code in one language only.")

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            native_future = executor.submit(ANALYZERS[lang], code)
            ai_future = executor.submit(ai_analysis, code, lang)
            
            try:
                res = native_future.result()
            except Exception as e:
                logging.error(f"Native analysis failed: {str(e)}")
                # Provide fallback analysis
                res = {
                    'language': lang,
                    'functions': 0,
                    'loc': code.count('\n') + 1,
                    'lloc': code.count('\n') + 1,
                    'sloc': code.count('\n') + 1,
                    'time_complexity': 1,
                    'space_complexity': 2,
                    'functions': []
                }
            
            try:
                ai_insights = ai_future.result()
            except Exception as e:
                logging.error(f"AI analysis failed: {str(e)}")
                ai_insights = "AI analysis failed. Please try again later."
            
            return {
                'native_analysis': res,
                'ai_insights': ai_insights
            }
    except Exception as e:
        logging.error(f"Analysis error: {str(e)}")
        logging.error(traceback.format_exc())
        raise RuntimeError(f"Analysis error: {str(e)}")
