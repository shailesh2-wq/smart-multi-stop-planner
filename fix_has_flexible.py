with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'const hasFlexible = destinations.some((d) => d.priority === "flexible");', 
    'const hasFlexible = destinations.some((d) => d.priority === "flexible" && !d.userExcluded);'
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
