import re

with open('src/MapContainer.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

amber_banner = '''      <div className="absolute top-0 left-0 right-0 bg-amber-100 border-b border-amber-200 px-4 py-2 flex items-center justify-between z-20">
        <div className="flex items-center gap-2 text-amber-800 text-xs font-semibold">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          SYNTHETIC MODE: Google Maps API key missing.
        </div>
        <span className="text-amber-700/80 text-[10px] uppercase tracking-wider font-bold">Demo Data</span>
      </div>'''

code = code.replace(amber_banner, '')

with open('src/MapContainer.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
