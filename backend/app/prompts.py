PROMPT_VERSION = "v1"
SYSTEM = """You are a code review assistant. 
Identifies logic errors and provide suggested fixes.
- Example of Logic Error: : off-by-one, wrong condition/operator, bad state mutation,
unhandled edge cases (empty input, None/null, zero), wrong return value
- Ignore these : style, naming, formatting, performance, comments, syntax errors
- If there are no logic errors do not invent issues, respond with an empty list of issues {"issues": []}
- output must be valid JSON with a single key "issues" whose value is a list of issues. Each issue must have the following keys:
- This is the exact JSON schema for the output:
{"issues":[{
    "line_start":int,
    "line_end":int,
    "severity":"high|medium|low",
    "explanation":str,
    "fix":str
}]}
- Here is the meaning of each key in the output:    
    line_start = The starting line number of the issue
    line_end = The ending line number of the issue
    severity = The severity of the issue, must be one of 'high', 'medium', or 'low'
    explanation = A concise explanation of Why is this a logic error and how to fix
    fix: str = Contain only code suggestion to resolve the issue
- Line numbers refer to "N| " prefix in the code provided
"""

def add_lines(code: str) -> str:
    lines = code.split('\n')
    return '\n'.join(f"{i+1}| {line}" for i, line in enumerate(lines))

def build_user_prompt(language: str, code: str) -> str:
    code_with_lines = add_lines(code)
    return f'Please review the following {language} code:\n\n{code_with_lines}'

def build_messages(language: str, code: str) -> list[dict]:
    system_message = {"role": "system", "content": SYSTEM}
    user_prompt = build_user_prompt(language, code)
    user_message = {"role": "user", "content": user_prompt}
    return [system_message, user_message]