import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Change Harbor Market's closeTime from 16:00 to 19:00
code = code.replace(
    'id: "d5", name: "Harbor Market", address: "9 Dockside Ln", priority: "flexible", duration: 45, openTime: "09:00", closeTime: "16:00"',
    'id: "d5", name: "Harbor Market", address: "9 Dockside Ln", priority: "flexible", duration: 45, openTime: "09:00", closeTime: "19:00"'
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
