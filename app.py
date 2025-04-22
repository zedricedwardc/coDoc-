import ast
import os
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze
from prettytable import PrettyTable
import google.generativeai as genai
import javalang
import esprima
import pycparser


genai.configure(api_key="AIzaSyC6vbEUaUYQk1RG1Dvou_Un-3D4e7axN9w")

def detect_language(code):
    if 'def ' in code or 'import ' in code:
        return 'python'
    elif 'function ' in code or 'const ' in code:
        return 'javascript'
    elif 'class ' in code and 'public ' in code:
        return 'java'
    elif '#include' in code:
        return 'c'
    else:
        return 'unknown'

def analyze_python_code(code):
    cc_results = cc_visit(code)
    mi_score = mi_visit(code, True)
    raw = analyze(code)

    tree = ast.parse(code)
    func_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])

    table = PrettyTable(["Function", "Complexity", "LOC", "Nesting Depth"])
    for result in cc_results:
        nested_depth = getattr(result, 'nested_blocks', 0)
        table.add_row([result.name, result.complexity, result.endline - result.lineno + 1, nested_depth])

    time_complexity = sum(result.complexity for result in cc_results)

    space_complexity = raw.sloc + raw.lloc

    return {
        "mi_score": mi_score,
        "loc": raw.loc,
        "lloc": raw.lloc,
        "sloc": raw.sloc,
        "comments": raw.comments,
        "multi": raw.multi,
        "blank": raw.blank,
        "functions": func_count,
        "complexity_table": table,
        "time_complexity": time_complexity,
        "space_complexity": space_complexity
    }
    
def analyze_java_code(code):
    tree = javalang.parse.parse(code)
    func_count = sum(1 for _, node in tree.filter(javalang.tree.MethodDeclaration))
    lines = len(code.splitlines())
    
    time_complexity = func_count * 2 


    space_complexity = lines * 1 

    return {
        "functions": func_count,
        "loc": lines,
        "time_complexity": time_complexity,
        "space_complexity": space_complexity
    }

def analyze_javascript_code(code):
    tree = esprima.parseScript(code)
    func_count = sum(1 for node in tree.body if isinstance(node, esprima.nodes.FunctionDeclaration))
    lines = len(code.splitlines())

    time_complexity = func_count * 2

    space_complexity = lines * 1  
    return {
        "functions": func_count,
        "loc": lines,
        "time_complexity": time_complexity,
        "space_complexity": space_complexity
    }

def analyze_c_code(code):
    parser = pycparser.CParser()
    try:
        ast = parser.parse(code)
    except:
        return {"error": "Unable to parse C code."}

    func_count = len([n for n in ast.ext if isinstance(n, pycparser.c_ast.FuncDef)])
    lines = len(code.splitlines())

    time_complexity = func_count * 2  
    
    space_complexity = lines * 1 
    return {
        "functions": func_count,
        "loc": lines,
        "time_complexity": time_complexity,
        "space_complexity": space_complexity
    }

def get_ai_analysis_summary(code, language):
    prompt = f"""
You are a code quality assistant. Analyze the following {language} code and give:
- A summary of code complexity in just 1-2 sentences
- Time and Space Complexity
- Areas that might need refactoring in bullet points
- Specific recommendations

Code:
{code}
"""
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text.strip()

def get_ai_refactor_suggestion(code, language):
    prompt = f"Refactor this {language} code to improve readability and reduce complexity:\n\n{code}"
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text.strip()

def run_analyzer_from_code(code):
    language = detect_language(code)
    print(f"\n🔍 Detected Language: {language}\n")

    if language == 'python':
        results = analyze_python_code(code)
        print(f"Maintainability Index: {results['mi_score']:.2f}")
        print(f"Total Lines: {results['loc']}, Logical LOC: {results['lloc']}, SLOC: {results['sloc']}")
        print(f"Comment Lines: {results['comments']}, Functions: {results['functions']}")
        print(results['complexity_table'])
        print(f"Time Complexity Estimate: O({results['time_complexity']})")
        print(f"Space Complexity Estimate: O({results['space_complexity']})")
    elif language == 'java':
        results = analyze_java_code(code)
        print(f"Functions: {results['functions']}, Total Lines: {results['loc']}")
        print(f"Time Complexity Estimate: O({results['time_complexity']})")
        print(f"Space Complexity Estimate: O({results['space_complexity']})")
    elif language == 'javascript':
        results = analyze_javascript_code(code)
        print(f"Functions: {results['functions']}, Total Lines: {results['loc']}")
        print(f"Time Complexity Estimate: O({results['time_complexity']})")
        print(f"Space Complexity Estimate: O({results['space_complexity']})")
    elif language == 'c':
        results = analyze_c_code(code)
        if "error" in results:
            print(results["error"])
        else:
            print(f"Functions: {results['functions']}, Total Lines: {results['loc']}")
            print(f"Time Complexity Estimate: O({results['time_complexity']})")
            print(f"Space Complexity Estimate: O({results['space_complexity']})")
    else:
        print("No native analyzer for this language. Using AI fallback.\n")
        results = {}

    print("\n🧠 AI Summary of Code:")
    print(get_ai_analysis_summary(code, language))

    print("\n⚙️ AI-Suggested Refactor (Optional):")
    print(get_ai_refactor_suggestion(code, language))
if __name__ == "__main__":
    while True:
        print("Paste your code below (type END on a new line to finish or EXIT to quit):")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            if line.strip().upper() == "EXIT":
                exit()
            lines.append(line)
        user_code = "\n".join(lines)
        run_analyzer_from_code(user_code)
