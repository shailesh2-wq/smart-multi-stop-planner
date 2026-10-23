import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_summary = '''function SummaryBar({ result, mode, onEditDest, destinations }) {
  const { stops, excluded, totalTravel, totalActivity, totalWait, lastFinish, endMin, startMin } = result;
  
  const userExcluded = destinations.filter(d => d.userExcluded);
  const totalRequested = destinations.length;
  
  const mustStops = stops.filter(s => s.dest.priority === "must").length;
  const importantStops = stops.filter(s => s.dest.priority === "important").length;
  const flexibleStops = stops.filter(s => s.dest.priority === "flexible").length;

  const mustExcludes = excluded.filter(e => e.dest.priority === "must");
  
  const available = endMin - startMin;
  const buffer = endMin - lastFinish;
  
  let statusText = "Fits your day";
  let statusColor = COLOR.success;
  let StatusIcon = CheckCircle2;
  
  if (mustExcludes.length > 0) {
    statusText = "Needs attention";
    statusColor = COLOR.warn;
    StatusIcon = AlertTriangle;
  } else if (excluded.length > 0) {
    statusText = "Partially planned";
    statusColor = COLOR.inkSoft;
    StatusIcon = Info;
  } else if (stops.length === 0 && excluded.length > 0) {
    statusText = "No feasible plan";
    statusColor = COLOR.warn;
    StatusIcon = AlertTriangle;
  }

  return (
    <div className="flex flex-col">
      <div className="px-4 py-3 flex items-center gap-2 border-b border-gray-100" style={{ backgroundColor: statusText === "Needs attention" || statusText === "No feasible plan" ? COLOR.warnSoft : (excluded.length > 0 ? "#F3F4F6" : "#ECFDF5") }}>
        <StatusIcon size={16} color={statusColor} />
        <span className="text-sm font-semibold" style={{ color: statusColor }}>{statusText}</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 border-b border-gray-100 divide-x divide-y sm:divide-y-0 divide-gray-100 bg-gray-50/50">
        <div className="px-4 py-3"><div className="text-[10px] font-bold text-gray-500 tracking-wide uppercase mb-1">Status Overview</div>
          <div className="text-xs text-gray-700 leading-tight">
            <div><strong>{totalRequested}</strong> Requested</div>
            <div><strong>{stops.length}</strong> Scheduled</div>
            {userExcluded.length > 0 && <div className="text-gray-500">{userExcluded.length} Excluded by you</div>}
            {excluded.length > 0 && <div className="text-orange-600">{excluded.length} Unable to schedule</div>}
          </div>
        </div>
        <div className="px-4 py-3"><div className="text-[10px] font-bold text-gray-500 tracking-wide uppercase mb-1">Scheduled by Priority</div>
          <div className="text-xs text-gray-700 leading-tight">
            <div><strong>{mustStops}</strong> Must Visit</div>
            <div><strong>{importantStops}</strong> Important</div>
            <div><strong>{flexibleStops}</strong> Flexible</div>
          </div>
        </div>
        <div className="px-4 py-3"><div className="text-[10px] font-bold text-gray-500 tracking-wide uppercase mb-1">Time Breakdown</div>
          <div className="text-xs text-gray-700 leading-tight">
            <div>Travel: <strong>{formatDuration(totalTravel)}</strong></div>
            <div>Activity: <strong>{formatDuration(totalActivity)}</strong></div>
            {totalWait > 0 && <div>Wait: <strong>{formatDuration(totalWait)}</strong></div>}
          </div>
        </div>
        <div className="px-4 py-3"><div className="text-[10px] font-bold text-gray-500 tracking-wide uppercase mb-1">Capacity</div>
          <div className="text-xs text-gray-700 leading-tight">
            <div>Available: <strong>{formatDuration(available)}</strong></div>
            <div style={{ color: buffer < 0 ? COLOR.warn : COLOR.success }}>Buffer: <strong>{buffer >= 0 ? formatDuration(buffer) : "Over by " + formatDuration(Math.abs(buffer))}</strong></div>
          </div>
        </div>
      </div>

      {excluded.length > 0 && (
        <div className="px-4 py-3 bg-white space-y-3">
          <div className="text-[10px] font-bold text-red-600 tracking-wide uppercase">Unable to schedule</div>
          {excluded.map((e, idx) => (
            <div key={idx} className="flex flex-col gap-1.5 p-3 rounded bg-red-50/50 border border-red-100">
              <div className="flex items-center justify-between">
                <div className="text-sm font-semibold text-gray-900">{e.dest.name} <span className="text-xs font-normal text-gray-500 ml-1">({PRIORITY_META[e.dest.priority].label})</span></div>
                <button onClick={() => onEditDest(e.dest)} className="text-xs font-medium text-blue-600 hover:underline">Edit Stop</button>
              </div>
              <div className="text-xs text-gray-600 leading-relaxed">{e.reason}</div>
              {e.dest.priority === "must" && (
                <div className="mt-1 pt-2 border-t border-red-100 text-[11px] font-medium text-red-700 flex items-center gap-1.5">
                  <Lightbulb size={12} />
                  Suggestion: Edit the stop to reduce duration, mark as flexible, or expand your day window.
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}'''

code = re.sub(r'function SummaryBar\(\{.*?\} \);\n\}', new_summary, code, flags=re.DOTALL)
code = code.replace('<SummaryBar result={result} mode={mode} onEditDest={onEditDest} />', '<SummaryBar result={result} mode={mode} onEditDest={onEditDest} destinations={destinations} />')

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
