import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_pool = '''    const mustLeft = remaining.filter((d) => d.priority === "must");
    const importantLeft = remaining.filter((d) => d.priority === "important");
    const pool = mustLeft.length > 0 ? mustLeft : (importantLeft.length > 0 ? importantLeft : remaining);'''

code = code.replace(
    '''    const mustLeft = remaining.filter((d) => d.priority === "must");
    const pool = mustLeft.length > 0 ? mustLeft : remaining;''',
    new_pool
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
