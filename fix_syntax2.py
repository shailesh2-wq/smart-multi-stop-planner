import re
with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('preferredDeviation = `${formatDuration(absDiff) ${diff < 0 ? "early" : "late"}`;', 'preferredDeviation = `${formatDuration(absDiff)} ${diff < 0 ? "early" : "late"}`;')

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
