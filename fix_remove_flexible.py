import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_remove = '''  const handleRemoveFlexible = () => {
    const flexibleStops = destinations.filter(d => d.priority === "flexible" && !d.userExcluded);
    if (flexibleStops.length === 0) return;

    let bestTarget = null;
    let bestScore = -Infinity;

    for (const f of flexibleStops) {
      const nextDest = destinations.filter(d => !d.userExcluded && d.id !== f.id);
      const r = buildItinerary(nextDest, startTime, endTime, mode, travelProvider);
      
      const mustExcludes = r.excluded.filter(e => e.dest.priority === "must").length;
      const importantExcludes = r.excluded.filter(e => e.dest.priority === "important").length;
      const totalExcludes = r.excluded.length;
      
      // Heavily penalize Must excludes, then Important, then total, then travel time
      const score = -(mustExcludes * 100000) - (importantExcludes * 1000) - (totalExcludes * 10) - r.totalTravel;
      
      if (score > bestScore) {
        bestScore = score;
        bestTarget = f;
      }
    }
    
    const target = bestTarget || flexibleStops[flexibleStops.length - 1];
    
    const next = destinations.map((d) => d.id === target.id ? { ...d, userExcluded: true } : d);
    setDestinations(next);
    
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode).then(r => {
      if (r) {
        const stillFails = r.excluded.some(e => e.dest.priority === "must");
        const status = stillFails ? "However, the plan still needs attention." : "The conflict was resolved and the plan now fits.";
        setRecoveryMsg(`${target.name} (Flexible) was removed from this plan to make room for higher-priority destinations. ${status}`);
      }
    });
  };'''

code = re.sub(r'  const handleRemoveFlexible = \(\) => \{.*?\n  \};', new_remove, code, flags=re.DOTALL)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
