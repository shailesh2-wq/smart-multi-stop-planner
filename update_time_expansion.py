import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Insert computeRecoveryOptions
compute_recovery = '''  const computeRecoveryOptions = (destinations, st, et, m, provider) => {
    const baseSt = toMin(st);
    const baseEt = toMin(et);
    
    let optEarlier = null;
    let earlierSt = null;
    for (let i = 15; i <= 240; i += 15) {
      if (baseSt - i < 0) continue;
      const testSt = toClock(baseSt - i);
      const r = buildItinerary(destinations, testSt, et, m, provider);
      if (r.excluded.length === 0) { 
        optEarlier = i; 
        earlierSt = testSt;
        break; 
      }
    }
    
    let optLater = null;
    let laterEt = null;
    for (let i = 15; i <= 240; i += 15) {
      if (baseEt + i > 1440) continue;
      const testEt = toClock(baseEt + i);
      const r = buildItinerary(destinations, st, testEt, m, provider);
      if (r.excluded.length === 0) { 
        optLater = i; 
        laterEt = testEt;
        break; 
      }
    }
    
    let optBoth = null;
    let bothSt = null;
    let bothEt = null;
    if (optEarlier === null && optLater === null) {
      for (let i = 30; i <= 360; i += 30) {
        const half = i / 2;
        if (baseSt - half < 0 || baseEt + half > 1440) continue;
        const testSt = toClock(baseSt - half);
        const testEt = toClock(baseEt + half);
        const r = buildItinerary(destinations, testSt, testEt, m, provider);
        if (r.excluded.length === 0) { 
          optBoth = i; 
          bothSt = testSt;
          bothEt = testEt;
          break; 
        }
      }
    }
    
    return { 
      earlier: optEarlier ? { val: optEarlier, st: earlierSt, label: `Start at ${earlierSt} (${formatDuration(optEarlier)} earlier)` } : null,
      later: optLater ? { val: optLater, et: laterEt, label: `Finish at ${laterEt} (${formatDuration(optLater)} later)` } : null,
      both: optBoth ? { val: optBoth, st: bothSt, et: bothEt, label: `Start at ${bothSt} and finish at ${bothEt}` } : null
    };
  };

  const runOptimize'''

code = code.replace('  const runOptimize', compute_recovery)

# 2. Update runOptimize to attach recoveryOptions
run_optimize_replacement = '''      const r = buildItinerary(d, st, et, m, travelProvider);
      if (r.excluded.length > 0) {
        r.recoveryOptions = computeRecoveryOptions(d, st, et, m, travelProvider);
      } else {
        r.recoveryOptions = { earlier: null, later: null, both: null };
      }
      setResult(r);'''

code = code.replace(
    '''      const r = buildItinerary(d, st, et, m, travelProvider);
      setResult(r);''',
    run_optimize_replacement
)

# 3. Replace handleStartEarlier & handleExtendEnd with handleTimeRecovery
old_handlers = re.search(r'  const handleStartEarlier = \(\) => \{.*?\n  \};\n\n  const handleExtendEnd = \(\) => \{.*?\n  \};', code, flags=re.DOTALL)
if old_handlers:
    new_handlers = '''  const handleTimeRecovery = (newSt, newEt, msg) => {
    if (!window.confirm(`Are you sure you want to apply this change?\\n\\nProposed adjustment: ${msg}`)) return;
    
    const effSt = newSt || startTime;
    const effEt = newEt || endTime;
    if (newSt) setStartTime(effSt);
    if (newEt) setEndTime(effEt);
    
    runOptimize(destinations.filter(d => !d.userExcluded), effSt, effEt, mode).then(r => {
      if (r) {
        const stillFails = r.excluded.length > 0;
        const status = stillFails ? "However, the plan still needs attention." : "All 5 destinations now fit in your day.";
        setRecoveryMsg(`${msg}. ${status}`);
      }
    });
  };'''
    code = code.replace(old_handlers.group(0), new_handlers)
else:
    print("Could not find old handlers.")

# 4. Update success message in handleRemoveFlexible to match prompt
code = code.replace(
    'const status = stillFails ? "However, the plan still needs attention." : "The conflict was resolved and the plan now fits.";',
    'const status = stillFails ? "However, the plan still needs attention." : "All 5 destinations now fit in your day.";'
)

# 5. Update ConflictBanner invocation in App
code = code.replace(
    '''                  <ConflictBanner 
                    result={result} 
                    windowMinutes={windowMinutes} 
                    onRemoveFlexible={handleRemoveFlexible} 
                    onStartEarlier={handleStartEarlier}
                    onExtendEnd={handleExtendEnd}
                    hasFlexible={hasFlexible}
                  />''',
    '''                  <ConflictBanner 
                    result={result} 
                    windowMinutes={windowMinutes} 
                    startTime={startTime}
                    endTime={endTime}
                    onRemoveFlexible={handleRemoveFlexible} 
                    onTimeRecovery={handleTimeRecovery}
                    hasFlexible={hasFlexible}
                  />'''
)

# 6. Replace ConflictBanner component
new_conflict_banner = '''function ConflictBanner({ result, windowMinutes, startTime, endTime, onRemoveFlexible, onTimeRecovery, hasFlexible }) {
  const { excluded, estimatedTotalNeeded, recoveryOptions } = result;
  const mustExcludes = excluded.filter(e => e.dest.priority === "must");
  const blocked = mustExcludes.length > 0;
  
  const deficit = estimatedTotalNeeded > windowMinutes ? estimatedTotalNeeded - windowMinutes : 0;
  
  const statusTitle = excluded.length === 1 
    ? "One destination is missing from your plan"
    : `${excluded.length} destinations are missing from your plan`;
  
  return (
    <div className="rounded-md mb-4 shadow-sm" style={{ border: `1px solid ${blocked ? COLOR.warn : COLOR.inkSoft}`, backgroundColor: blocked ? COLOR.warnSoft : "#F9FAFB" }}>
      <div className="flex items-start gap-2.5 px-3 py-3 border-b border-gray-200/50">
        <AlertTriangle size={18} color={blocked ? COLOR.warn : COLOR.inkSoft} className="mt-0.5 shrink-0" />
        <div className="flex-1">
          <div className="text-sm font-semibold" style={{ color: blocked ? COLOR.warn : COLOR.ink }}>
            {statusTitle}
          </div>
          <div className="text-xs mt-1" style={{ color: blocked ? "#9A5012" : COLOR.inkSoft, lineHeight: 1.5 }}>
            <strong>{result.stops.length}</strong> scheduled, <strong>{excluded.length}</strong> not scheduled.<br/>
            Available time: {formatDuration(windowMinutes)}. Estimated time required: {formatDuration(estimatedTotalNeeded)} 
            {deficit > 0 ? ` (shortage of ${formatDuration(deficit)}).` : '.'}
          </div>
          <div className="mt-2 space-y-2">
            {excluded.map(e => (
              <div key={e.dest.id} className="text-xs p-2 rounded bg-white border" style={{ borderColor: blocked ? "#fed7aa" : "#e5e7eb" }}>
                <div className="font-semibold" style={{ color: COLOR.ink }}>{e.dest.name} <span className="font-normal text-gray-500">({PRIORITY_META[e.dest.priority].label})</span></div>
                <div className="text-gray-600 mt-0.5"><span className="font-medium text-gray-700">Status:</span> Unable to schedule</div>
                <div className="text-gray-600 mt-0.5"><span className="font-medium text-gray-700">Reason:</span> {e.reason}</div>
                <div className="text-gray-500 mt-1 pt-1 border-t border-gray-100 flex items-center justify-between">
                  <span>Duration: {formatDuration(e.dest.duration)}</span>
                  <span>Hours: {e.dest.openTime} - {e.dest.closeTime}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div className="px-3 py-3" style={{ backgroundColor: blocked ? "rgba(255, 237, 213, 0.4)" : "rgba(243, 244, 246, 0.4)" }}>
        <div className="text-[10px] font-bold tracking-wider mb-2" style={{ color: blocked ? "rgba(154, 80, 18, 0.7)" : COLOR.muted }}>RECOVERY OPTIONS</div>
        <div className="flex flex-col gap-2">
          
          <div className="flex items-center justify-between p-2 rounded border bg-white shadow-sm" style={{ borderColor: blocked ? "#fed7aa" : "#e5e7eb" }}>
            <div className="flex-1 pr-4">
              <div className="text-sm font-medium text-gray-900">Remove a Flexible stop</div>
              <div className="text-xs text-gray-500 mt-0.5">
                {hasFlexible 
                  ? "Skip a flexible destination to free up time for your higher-priority stops." 
                  : "No Flexible destinations are available to remove."}
              </div>
            </div>
            <button 
              onClick={onRemoveFlexible} 
              disabled={!hasFlexible}
              className="text-xs font-medium px-3 py-1.5 rounded whitespace-nowrap transition-colors"
              style={{ backgroundColor: hasFlexible ? (blocked ? COLOR.warn : COLOR.ink) : "#E5E7EB", color: hasFlexible ? "#fff" : "#9CA3AF" }}
            >
              Skip flexible
            </button>
          </div>

          <div className="flex items-center justify-between p-2 rounded border bg-white shadow-sm" style={{ borderColor: blocked ? "#fed7aa" : "#e5e7eb" }}>
            <div className="flex-1 pr-4">
              <div className="text-sm font-medium text-gray-900">Expand your time window</div>
              <div className="text-xs text-gray-500 mt-0.5">
                {(!recoveryOptions?.earlier && !recoveryOptions?.later && !recoveryOptions?.both) 
                 ? "Expanding your time window cannot resolve this conflict due to strict opening/closing hours or duration limits."
                 : "Adjust your schedule to fit the remaining destinations."}
              </div>
            </div>
            <div className="flex flex-col gap-1.5 items-end">
              {recoveryOptions?.earlier && (
                <button 
                  onClick={() => onTimeRecovery(recoveryOptions.earlier.st, null, recoveryOptions.earlier.label)} 
                  className="text-xs font-medium px-3 py-1.5 rounded whitespace-nowrap transition-colors hover:bg-orange-100"
                  style={{ backgroundColor: blocked ? "#fff7ed" : "#f3f4f6", color: blocked ? "#c2410c" : "#374151", border: `1px solid ${blocked ? '#fed7aa' : '#e5e7eb'}` }}
                >
                  {recoveryOptions.earlier.label}
                </button>
              )}
              {recoveryOptions?.later && (
                <button 
                  onClick={() => onTimeRecovery(null, recoveryOptions.later.et, recoveryOptions.later.label)} 
                  className="text-xs font-medium px-3 py-1.5 rounded whitespace-nowrap transition-colors hover:bg-orange-100"
                  style={{ backgroundColor: blocked ? "#fff7ed" : "#f3f4f6", color: blocked ? "#c2410c" : "#374151", border: `1px solid ${blocked ? '#fed7aa' : '#e5e7eb'}` }}
                >
                  {recoveryOptions.later.label}
                </button>
              )}
              {!recoveryOptions?.earlier && !recoveryOptions?.later && recoveryOptions?.both && (
                <button 
                  onClick={() => onTimeRecovery(recoveryOptions.both.st, recoveryOptions.both.et, recoveryOptions.both.label)} 
                  className="text-xs font-medium px-3 py-1.5 rounded whitespace-nowrap transition-colors hover:bg-orange-100"
                  style={{ backgroundColor: blocked ? "#fff7ed" : "#f3f4f6", color: blocked ? "#c2410c" : "#374151", border: `1px solid ${blocked ? '#fed7aa' : '#e5e7eb'}` }}
                >
                  {recoveryOptions.both.label}
                </button>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}'''

code = re.sub(r'function ConflictBanner\(\{.*?\} \);\n\}', new_conflict_banner, code, flags=re.DOTALL)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
