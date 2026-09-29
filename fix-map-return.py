import re

with open('src/IllustrativeCityMap.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

bad_pattern = r'<span className="text-amber.*?<svg'
replacement = '<div className="relative flex-1 w-full h-full overflow-hidden">\n        <svg'

code = re.sub(r'\s*<span className="text-amber.*?</div>\s*<div className="relative.*?<svg', '\n      ' + replacement, code, flags=re.DOTALL)

with open('src/IllustrativeCityMap.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
