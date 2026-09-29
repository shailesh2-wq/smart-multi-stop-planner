import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('} Search, Check,\n} from "lucide-react";', '  Search, Check,\n} from "lucide-react";')

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
