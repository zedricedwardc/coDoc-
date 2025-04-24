import ast
import os
import re
import textwrap
import logging
import concurrent.futures
from dotenv import load_dotenv
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze as raw_metrics
from prettytable import PrettyTable
import google.generativeai as genai
import javalang
import esprima
import pycparser

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
    'python': ['def ', 'import ', 'print('],
    'javascript': ['function ', 'const ', 'let ', 'var '],
    'java': ['public ', 'class ', 'static ', 'void '],
    'c': ['#include', 'printf(', 'scanf('],
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
    scores = {
        lang: sum(len(re.findall(re.escape(kw), code)) for kw in keywords)
        for lang, keywords in _LANGUAGE_KEYWORDS.items()
    }
    top_lang, top_score = max(scores.items(), key=lambda x: x[1])
    if top_score == 0 or list(scores.values()).count(top_score) > 1:
        return 'unknown'
    return top_lang

# --- Standard Metrics ---
def standard_metrics(code: str, funcs: int, loc: int, time_c: int = None) -> dict:
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

# --- Language-specific Analyzers ---
@register('python')
def analyze_python(code: str) -> dict:
    try:
        raw = raw_metrics(code)
        cc = cc_visit(code)
        tree = ast.parse(code)
        funcs = sum(isinstance(n, ast.FunctionDef) for n in ast.walk(tree))

        tbl = PrettyTable(["Function", "Complexity", "LOC", "Nesting"])
        time_c = 0
        for r in cc:
            depth = getattr(r, 'nested_blocks', 0)
            loc = r.endline - r.lineno + 1
            tbl.add_row([r.name, r.complexity, loc, depth])
            time_c += r.complexity

        return {
            'language': 'python',
            **standard_metrics(code, funcs, raw.loc, time_c),
            'mi': mi_visit(code, True),
            'table': tbl
        }
    except Exception as e:
        raise ValueError("Python parser failed. Please ensure your code is valid Python.") from e

@register('javascript')
def analyze_js(code: str) -> dict:
    try:
        tree = esprima.parseScript(code)
        funcs = sum(isinstance(node, esprima.nodes.FunctionDeclaration) for node in tree.body)
        loc = code.count('\n') + 1
        return {
            'language': 'javascript',
            **standard_metrics(code, funcs, loc)
        }
    except Exception as e:
        raise ValueError("JavaScript parser failed. Ensure the code uses correct JavaScript syntax.") from e

@register('java')
def analyze_java(code: str) -> dict:
    try:
        tree = javalang.parse.parse(code)
        funcs = sum(1 for _, n in tree.filter(javalang.tree.MethodDeclaration))
        loc = code.count('\n') + 1
        return {
            'language': 'java',
            **standard_metrics(code, funcs, loc)
        }
    except Exception as e:
        raise ValueError("Java parser failed. Submit only valid Java code.") from e

@register('c')
def analyze_c(code: str) -> dict:
    parser = pycparser.CParser()
    try:
        astree = parser.parse(code)
        funcs = sum(isinstance(n, pycparser.c_ast.FuncDef) for n in astree.ext)
        loc = code.count('\n') + 1
        return {
            'language': 'c',
            **standard_metrics(code, funcs, loc)
        }
    except pycparser.plyparser.ParseError as e:
        raise ValueError("C parser failed. Please ensure it's strictly C syntax.") from e

# --- AI Summary Generator ---
def ai_analysis(code: str, lang: str) -> str:
    if not API_KEY:
        return 'Skipped AI analysis.'
    prompt = textwrap.dedent(f"""
        Analyze this {lang} code briefly: summary, time/space complexity, refactoring areas and refactored code.
        Don't give out long explanations, just a clear and brief summary.

        {code}
    """)
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        return model.generate_content(prompt).text.strip()
    except Exception as e:
        return f"AI error: {e}"

# --- Entry Point for GUI ---
def run_analysis(code: str) -> dict:
    lang = detect_language(code)
    if lang == 'unknown':
        raise ValueError("Ambiguous or mixed languages detected. Submit code in one language only.")

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            native_future = executor.submit(ANALYZERS[lang], code)
            ai_future = executor.submit(ai_analysis, code, lang)
            res = native_future.result()
            return {
                'native_analysis': res,
                'ai_insights': ai_future.result()
            }
    except Exception as e:
        raise RuntimeError(f"Analysis error: {e}")
