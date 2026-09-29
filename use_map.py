import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('import IllustrativeCityMap from "./IllustrativeCityMap";', 'import MapContainer from "./MapContainer";')
code = code.replace('<IllustrativeCityMap', '<MapContainer')
code = code.replace('export const PRIORITY_META', 'export const PRIORITY_META') # Make sure it's exported
if 'export const PRIORITY_META' not in code:
    code = code.replace('const PRIORITY_META =', 'export const PRIORITY_META =')

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
