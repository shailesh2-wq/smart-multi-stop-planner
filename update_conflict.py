import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_conflict = '''function ConflictBanner({ result, windowMinutes, onRemoveFlexible, onStartEarlier, onExtendEnd, hasFlexible }) {
  const mustExcludes = result.excluded.filter(e => e.dest.priority === "must");
  const blocked = mustExcludes.length > 0;
  
  const totalNeeded = result.estimatedTotalNeeded;
  const deficit = totalNeeded > windowMinutes ? totalNeeded - windowMinutes : 0;
  
  const statusTitle = blocked 
    ? `Blocked Plan: ${mustExcludes.length} Must Visit destination${mustExcludes.length > 1 ? 's' : ''} cannot fit.`
    : `Partially Feasible Plan: ${result.excluded.length} destination${result.excluded.length > 1 ? 's' : ''} cannot fit.`;
  
  return (
    <div className="rounded-md mb-4 shadow-sm" style={{ border: `1px solid ${blocked ? COLOR.warn : COLOR.inkSoft}`, backgroundColor: blocked ? COLOR.warnSoft : "#F9FAFB" }}>
      <div className="flex items-start gap-2.5 px-3 py-3 border-b border-gray-200/50">
        <AlertTriangle size={18} color={blocked ? COLOR.warn : COLOR.inkSoft} className="mt-0.5 shrink-0" />
        <div className="flex-1">
          <div className="text-sm font-semibold" style={{ color: blocked ? COLOR.warn : COLOR.ink }}>
            {statusTitle}
          </div>
          <div className="text-xs mt-1" style={{ color: blocked ? "#9A5012" : COLOR.inkSoft, lineHeight: 1.5 }}>
            <strong>{result.stops.length}</strong> scheduled, <strong>{result.excluded.length}</strong> not scheduled.<br/>
            Available time: {formatDuration(windowMinutes)}. Estimated time required: {formatDuration(totalNeeded)} 
            {deficit > 0 ? ` (shortage of ${formatDuration(deficit)}).` : '.'}
          </div>
          <div className="mt-2 space-y-1">
            {result.excluded.map(e => (
              <div key={e.dest.id} className="text-xs flex items-center gap-1.5" style={{ color: blocked ? "#7A4108" : COLOR.inkSoft }}>
                • <strong>{e.dest.name}</strong> ({PRIORITY_META[e.dest.priority].label}): {e.reason}
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div className="px-3 py-3" style={{ backgroundColor: blocked ? "rgba(255, 237, 213, 0.4)" : "rgba(243, 244, 246, 0.4)" }}>
        <div className="text-[10px] font-bold tracking-wider mb-2" style={{ color: blocked ? "rgba(154, 80, 18, 0.7)" : COLOR.muted }}>RECOVERY ACTIONS</div>
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
                Add more time to your day. (Ensure destinations are open during the new hours).
              </div>
            </div>
            <div className="flex gap-2">
              <button 
                onClick={onStartEarlier} 
                className="text-xs font-medium px-3 py-1.5 rounded whitespace-nowrap transition-colors"
                style={{ backgroundColor: blocked ? "#fff7ed" : "#f3f4f6", color: blocked ? "#c2410c" : "#374151" }}
              >
                Start earlier
              </button>
              <button 
                onClick={onExtendEnd} 
                className="text-xs font-medium px-3 py-1.5 rounded whitespace-nowrap transition-colors"
                style={{ backgroundColor: blocked ? "#fff7ed" : "#f3f4f6", color: blocked ? "#c2410c" : "#374151" }}
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

code = re.sub(
    r'function ConflictBanner\(\{.*?\} \);\n\}',
    new_conflict,
    code,
    flags=re.DOTALL
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
