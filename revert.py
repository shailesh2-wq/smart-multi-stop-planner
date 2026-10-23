import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Remove computeRecoveryOptions
code = re.sub(r'  const computeRecoveryOptions = \(.*?\n  };\n\n  const runOptimize', '  const runOptimize', code, flags=re.DOTALL)

# 2. Revert runOptimize
code = re.sub(
    r'      const r = buildItinerary\(d, st, et, m, travelProvider\);\n      if \(r\.excluded\.length > 0\) \{.*?\n      \} else \{.*?\n      \}\n      setResult\(r\);',
    '      const r = buildItinerary(d, st, et, m, travelProvider);\n      setResult(r);',
    code,
    flags=re.DOTALL
)

# 3. Restore handleStartEarlier and handleExtendEnd
new_handlers = '''  const handleStartEarlier = () => {
    const next = toClock(toMin(startTime) - 60);
    setStartTime(next);
    runOptimize(destinations.filter(d => !d.userExcluded), next, endTime, mode).then(r => {
      if (r) {
        const stillFails = r.excluded.some(e => e.dest.priority === "must");
        const status = stillFails ? "However, the plan still needs attention." : "The conflict was resolved and the plan now fits.";
        setRecoveryMsg(`Start time changed from ${startTime} to ${next}, gaining 1 hour. The route has been recalculated. ${status}`);
      }
    });
  };

  const handleExtendEnd = () => {
    const next = toClock(toMin(endTime) + 60);
    setEndTime(next);
    runOptimize(destinations.filter(d => !d.userExcluded), startTime, next, mode).then(r => {
      if (r) {
        const stillFails = r.excluded.some(e => e.dest.priority === "must");
        const status = stillFails ? "However, the plan still needs attention." : "The conflict was resolved and the plan now fits.";
        setRecoveryMsg(`Your end time was extended from ${endTime} to ${next}, gaining 1 hour. The route has been recalculated. ${status}`);
      }
    });
  };'''

code = re.sub(r'  const handleTimeRecovery = \(.*?\n  };\n', new_handlers + '\n', code, flags=re.DOTALL)

# 4. Revert ConflictBanner Component
old_conflict_banner = '''function ConflictBanner({ result, windowMinutes, onRemoveFlexible, onStartEarlier, onExtendEnd, hasFlexible }) {
  const mustExcludes = result.excluded.filter(e => e.dest.priority === "must");
  if (result.excluded.length === 0) return null;

  return (
    <div className="bg-orange-50 border border-orange-200 rounded-md p-3 mb-4">
      <div className="flex items-start gap-2 mb-3">
        <AlertTriangle size={16} className="text-orange-600 mt-0.5" />
        <div>
          <h3 className="text-sm font-bold text-orange-900">
            {mustExcludes.length > 0 
              ? `Must Visit Conflict: ${mustExcludes.map(e => e.dest.name).join(", ")} cannot fit.` 
              : "Schedule Alert: Some requested destinations cannot fit."}
          </h3>
          <p className="text-xs text-orange-800 mt-1">
            Your available window is {formatDuration(windowMinutes)}, but scheduling these stops requires at least {formatDuration(result.estimatedTotalNeeded)} 
            {result.estimatedTotalNeeded > windowMinutes ? ` (a ${formatDuration(result.estimatedTotalNeeded - windowMinutes)} shortage)` : ""}.
          </p>
        </div>
      </div>
      <div className="text-[10px] font-bold tracking-wider mb-2 text-orange-800/70">RECOVERY ACTIONS</div>
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between p-2 rounded border border-orange-200 bg-white">
          <div className="flex-1 pr-4">
            <div className="text-sm font-medium text-gray-900">Remove a Flexible stop</div>
            <div className="text-xs text-gray-500 mt-0.5">
              {hasFlexible 
                ? "Skip a flexible destination to free up time for your higher-priority stops." 
                : "No Flexible destinations are available to remove. Change a destination's priority."}
            </div>
          </div>
          <button 
            onClick={onRemoveFlexible} 
            disabled={!hasFlexible}
            className="text-xs font-medium px-3 py-1.5 rounded whitespace-nowrap"
            style={{ backgroundColor: hasFlexible ? COLOR.warn : "#E5E7EB", color: hasFlexible ? "#fff" : "#9CA3AF" }}
          >
            Skip flexible
          </button>
        </div>
        <div className="flex items-center justify-between p-2 rounded border border-orange-200 bg-white">
          <div className="flex-1 pr-4">
            <div className="text-sm font-medium text-gray-900">Expand your time window</div>
            <div className="text-xs text-gray-500 mt-0.5">
              Add more time to your day. (Ensure destinations are open during the new hours).
            </div>
          </div>
          <div className="flex gap-2">
            <button 
              onClick={onStartEarlier} 
              className="text-xs font-medium px-3 py-1.5 rounded whitespace-nowrap bg-orange-100 text-orange-800 hover:bg-orange-200 transition-colors"
            >
              Start earlier
            </button>
            <button 
              onClick={onExtendEnd} 
              className="text-xs font-medium px-3 py-1.5 rounded whitespace-nowrap bg-orange-100 text-orange-800 hover:bg-orange-200 transition-colors"
            >
              End later
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}'''

code = re.sub(r'function ConflictBanner\(\{.*?\} \);\n\}', old_conflict_banner, code, flags=re.DOTALL)

# 5. Fix ConflictBanner invocation in App
code = re.sub(
    r'<ConflictBanner \n                    result=\{result\} \n                    windowMinutes=\{windowMinutes\} \n                    startTime=\{startTime\}\n                    endTime=\{endTime\}\n                    onRemoveFlexible=\{handleRemoveFlexible\} \n                    onTimeRecovery=\{handleTimeRecovery\}\n                    hasFlexible=\{hasFlexible\}\n                  />',
    '<ConflictBanner result={result} windowMinutes={windowMinutes} onRemoveFlexible={handleRemoveFlexible} onStartEarlier={handleStartEarlier} onExtendEnd={handleExtendEnd} hasFlexible={hasFlexible} />',
    code
)

# 6. Revert handleRemoveFlexible
old_remove = '''  const handleRemoveFlexible = () => {
    const excludedFlexible = result.excluded.find((e) => e.dest.priority === "flexible");
    const target = excludedFlexible ? excludedFlexible.dest : [...destinations].reverse().find((d) => d.priority === "flexible" && !d.userExcluded);
    if (!target) return;
    const next = destinations.map((d) => d.id === target.id ? { ...d, userExcluded: true } : d);
    setDestinations(next);
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode).then(r => {
      if (r) {
        const stillFails = r.excluded.some(e => e.dest.priority === "must");
        const status = stillFails ? "However, the plan still needs attention." : "The conflict was resolved and the plan now fits.";
        setRecoveryMsg(`${target.name} was removed from the active itinerary because it was marked Flexible. The revised plan has been recalculated. ${status}`);
      }
    });
  };'''

code = re.sub(r'  const handleRemoveFlexible = \(\) => \{.*?\n  \};\n', old_remove + '\n', code, flags=re.DOTALL)

# 7. Revert pool logic
code = re.sub(
    r'    const mustLeft = remaining\.filter\(\(d\) => d\.priority === "must"\);\n    const importantLeft = remaining\.filter\(\(d\) => d\.priority === "important"\);\n    const pool = mustLeft\.length > 0 \? mustLeft : \(importantLeft\.length > 0 \? importantLeft : remaining\);',
    '    const mustLeft = remaining.filter((d) => d.priority === "must");\n    const pool = mustLeft.length > 0 ? mustLeft : remaining;',
    code
)

# 8. Revert preferredBonus scoring
code = re.sub(
    r'    let preferredPenalty = 0;\n    let preferredBonus = 0;\n    if \(d\.preferredArrival\) \{\n      const prefMin = toMin\(d\.preferredArrival\);\n      const diff = Math\.abs\(arrival - prefMin\);\n      // Treat preferred arrival as an optimization objective\n      preferredPenalty = diff \* 0\.8;\n      if \(diff < 30\) preferredBonus = 30 - diff;\n    \}\n    const cost = travel \+ wait \* 1\.5 \+ priorityPenalty - urgencyBonus \+ preferredPenalty - preferredBonus;',
    '    let preferredBonus = 0;\n    if (d.preferredArrival) {\n      const diff = Math.abs(arrival - toMin(d.preferredArrival));\n      preferredBonus = Math.max(0, 60 - diff) * 0.8;\n    }\n    const cost = travel + wait * 1.5 + priorityPenalty - urgencyBonus - preferredBonus;',
    code
)

# 9. Revert Harbor Market closeTime to 16:00
code = code.replace(
    'id: "d5", name: "Harbor Market", address: "9 Dockside Ln", priority: "flexible", duration: 45, openTime: "09:00", closeTime: "19:00"',
    'id: "d5", name: "Harbor Market", address: "9 Dockside Ln", priority: "flexible", duration: 45, openTime: "09:00", closeTime: "16:00"'
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
