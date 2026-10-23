import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_conflict = '''function ConflictBanner({ result, windowMinutes, onRemoveFlexible, onStartEarlier, onExtendEnd, hasFlexible }) {
  const mustExcludes = result.excluded.filter(e => e.dest.priority === "must");
  const importantExcludes = result.excluded.filter(e => e.dest.priority === "important");
  const flexibleExcludes = result.excluded.filter(e => e.dest.priority === "flexible");
  
  const totalNeeded = result.estimatedTotalNeeded;
  const deficit = totalNeeded - windowMinutes;
  
  // Analyze if extending helps
  // Extending helps if the deficit exists and the excluded destinations don't strictly close before the new extended time.
  // For simplicity without re-simulating the entire day, we offer standard 1-hour extensions if deficit > 0.
  const canExtend = deficit > 0;
  
  return (
    <div className="rounded-md mb-4" style={{ border: \1px solid \\, backgroundColor: COLOR.warnSoft }}>
      <div className="flex items-start gap-2.5 px-3 py-3 border-b border-orange-200/50">
        <AlertTriangle size={18} color={COLOR.warn} className="mt-0.5 shrink-0" />
        <div className="flex-1">
          <div className="text-sm font-semibold" style={{ color: COLOR.warn }}>
            {mustExcludes.length > 0 
              ? \Must Visit Conflict: \ cannot fit.\
              : \Schedule Alert: Some requested destinations cannot fit.\
            }
          </div>
          <div className="text-xs mt-1" style={{ color: "#9A5012", lineHeight: 1.5 }}>
            Your available window is {formatDuration(windowMinutes)}, but scheduling these stops requires at least {formatDuration(totalNeeded)} (a {formatDuration(deficit)} shortage).
          </div>
        </div>
      </div>
      
      <div className="px-3 py-3 bg-orange-50/30">
        <div className="text-[10px] font-bold tracking-wider mb-2 text-orange-800/70">RECOVERY ACTIONS</div>
        <div className="flex flex-col gap-2">
          
          {/* Action A: Remove Flexible */}
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

          {/* Action B & C: Extend Window */}
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
                className="text-xs font-medium px-3 py-1.5 rounded whitespace-nowrap bg-orange-50 text-orange-700 hover:bg-orange-100 transition-colors"
              >
                Start earlier
              </button>
              <button 
                onClick={onExtendEnd} 
                className="text-xs font-medium px-3 py-1.5 rounded whitespace-nowrap bg-orange-50 text-orange-700 hover:bg-orange-100 transition-colors"
              >
                End later
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}'''

code = re.sub(r'function ConflictBanner\(\{.*?\} \);\n\}', new_conflict, code, flags=re.DOTALL)
with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
