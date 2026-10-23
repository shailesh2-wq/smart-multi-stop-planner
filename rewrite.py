import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_results_panel = '''function ResultsPanel({ result, mode, hoveredLeg, setHoveredLeg, onEditDest }) {
  const { stops } = result;

  return (
    <div className="rounded-md overflow-hidden bg-white shadow-sm" style={{ border: `1px solid ${COLOR.line}` }}>
      <SummaryBar result={result} mode={mode} onEditDest={onEditDest} />
      <div className="px-4 py-3 bg-gray-50/50" style={{ borderTop: `1px solid ${COLOR.line}` }}>
        <h3 className="text-[10px] font-bold tracking-wider mb-2" style={{ color: COLOR.inkSoft }}>OPTIMIZED ROUTE</h3>
        <div className="space-y-0">
          <TimelineRow time={toClock(result.startMin)} label="Start from Home" kind="depart" />
          {stops.map((s, i) => {
            const u = i === 0 ? "home" : stops[i - 1].dest.id;
            const v = s.dest.id;
            return (
              <React.Fragment key={s.dest.id}>
                <div
                  onMouseEnter={() => setHoveredLeg({ u, v })}
                  onMouseLeave={() => setHoveredLeg(null)}
                  style={{ backgroundColor: hoveredLeg && hoveredLeg.u === u && hoveredLeg.v === v ? '#F3F4F6' : 'transparent', borderRadius: 4 }}
                >
                  <TimelineRow
                    time={`+${formatDuration(s.travel)}`}
                    label={`Travel - ${formatDuration(s.travel)} - ~${travelProvider.getTravel(u, v, mode).km} km`}
                    kind="travel"
                  />
                </div>
              <TimelineRow time={toClock(s.arrival)} label={s.dest.name} kind="arrive" priority={s.dest.priority}
                meta={`${formatDuration(s.dest.duration)}${s.wait > 0 ? ` waited ${formatDuration(s.wait)} for opening` : ""}`}  deviation={s.preferredDeviation} />
              {i < stops.length - 1 && (
                <TimelineRow time={toClock(s.departure)} label={`Leave ${s.dest.name}`} kind="depart" />
              )}
            </React.Fragment>
          );
          })}
        </div>
      </div>
    </div>
  );
}'''

code = re.sub(r'function ResultsPanel\(\{.*?\} \);\n\}', new_results_panel, code, flags=re.DOTALL)
with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
