import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_score_logic = '''    let preferredPenalty = 0;
    let preferredBonus = 0;
    if (d.preferredArrival) {
      const prefMin = toMin(d.preferredArrival);
      const diff = Math.abs(arrival - prefMin);
      // Treat preferred arrival as an optimization objective
      preferredPenalty = diff * 0.8;
      if (diff < 30) preferredBonus = 30 - diff;
    }
    const cost = travel + wait * 1.5 + priorityPenalty - urgencyBonus + preferredPenalty - preferredBonus;'''

code = re.sub(
    r'    let preferredBonus = 0;\s*if \(d\.preferredArrival\) \{\s*const diff = Math\.abs\(arrival - toMin\(d\.preferredArrival\)\);\s*preferredBonus = Math\.max\(0, 60 - diff\) \* 0\.8;\s*\}\s*const cost = travel \+ wait \* 1\.5 \+ priorityPenalty - urgencyBonus - preferredBonus;',
    new_score_logic,
    code,
    flags=re.DOTALL
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
