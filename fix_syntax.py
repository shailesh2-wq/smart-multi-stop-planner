import re
with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = re.sub(r'\} \$\{diff < 0 \? "early" : "late"\}\`;\n\s*\}\n\s*\}', '', code)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
