import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add ScenarioPanel component
scenario_panel = '''function ScenarioPanel({ onSelectScenario }) {
  return (
    <div className="bg-white rounded-md border border-gray-200 p-3 mb-6 shadow-sm">
      <h3 className="text-xs font-bold text-gray-500 mb-2 uppercase tracking-wide">Try a scenario (Demo)</h3>
      <div className="flex flex-col gap-2">
        <button onClick={() => onSelectScenario('A')} className="text-left text-xs font-medium px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition-colors">A: Balanced Day</button>
        <button onClick={() => onSelectScenario('B')} className="text-left text-xs font-medium px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition-colors">B: Must Visit Conflict</button>
        <button onClick={() => onSelectScenario('C')} className="text-left text-xs font-medium px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition-colors">C: Flexible Recovery</button>
      </div>
    </div>
  );
}

'''
if 'function ScenarioPanel' not in code:
    code = code.replace('function DestinationRow', scenario_panel + 'function DestinationRow')

# 2. Add recoveryMsg state to App
if 'const [recoveryMsg, setRecoveryMsg]' not in code:
    code = code.replace('const [insight, setInsight] = useState("");', 'const [insight, setInsight] = useState("");\n  const [recoveryMsg, setRecoveryMsg] = useState(null);')

# 3. Add onSelectScenario handler to App
scenario_handler = '''
  const handleScenario = (type) => {
    setRecoveryMsg(null);
    let newDestinations = [...DEFAULT_DESTINATIONS].map(d => ({...d, userExcluded: false}));
    if (type === 'A') {
      setStartTime("09:00");
      setEndTime("18:00");
      newDestinations[0].priority = "must";
      newDestinations[1].priority = "important";
      newDestinations[2].priority = "flexible";
      newDestinations[3].priority = "important";
      newDestinations[4].priority = "must";
    } else if (type === 'B') {
      setStartTime("09:00");
      setEndTime("13:00");
      newDestinations.forEach(d => d.priority = "must");
    } else if (type === 'C') {
      setStartTime("09:00");
      setEndTime("13:00");
      newDestinations[0].priority = "must";
      newDestinations[1].priority = "must";
      newDestinations[2].priority = "flexible";
      newDestinations[3].priority = "must";
      newDestinations[4].priority = "must";
    }
    setDestinations(newDestinations);
    runOptimize(newDestinations.filter(d => !d.userExcluded), type === 'A' ? "09:00" : "09:00", type === 'A' ? "18:00" : "13:00", mode);
  };
'''
if 'const handleScenario =' not in code:
    code = code.replace('const handleRestore =', scenario_handler + '\n  const handleRestore =')

# 4. Insert ScenarioPanel and RecoveryMsg in the sidebar
sidebar_additions = '''
          <ScenarioPanel onSelectScenario={handleScenario} />
          {recoveryMsg && (
            <div className="mb-6 p-3 rounded-md bg-blue-50 border border-blue-200 flex items-start gap-2">
              <Info size={16} className="text-blue-600 mt-0.5 shrink-0" />
              <div className="text-xs font-medium text-blue-900">{recoveryMsg}</div>
            </div>
          )}
'''
if 'ScenarioPanel onSelectScenario' not in code:
    code = code.replace('          {/* Header Text */}', sidebar_additions + '          {/* Header Text */}')

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
