import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add Search, Check to lucide-react imports
if 'Search' not in code:
    code = code.replace('from "lucide-react";', 'Search, Check,\n} from "lucide-react";')

selector_code = '''import { DEMO_LOCATIONS } from './data/demoLocations';

function DemoLocationSelector({ onAdd, onCancel, existingIds }) {
  const [search, setSearch] = React.useState("");

  const filtered = DEMO_LOCATIONS.filter(loc => 
    loc.name.toLowerCase().includes(search.toLowerCase()) || 
    loc.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md flex flex-col overflow-hidden max-h-[85vh]">
        <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
          <h2 className="font-bold text-gray-900">Add a destination</h2>
          <button onClick={onCancel} className="text-gray-400 hover:text-gray-600 transition-colors">
            <X size={20} />
          </button>
        </div>
        <div className="p-4 border-b border-gray-100">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input 
              type="text" 
              placeholder="Search demo locations..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            />
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          {filtered.length === 0 ? (
            <div className="p-8 text-center text-gray-500 text-sm">No locations found matching your search.</div>
          ) : (
            <div className="flex flex-col gap-2">
              {filtered.map(loc => {
                const isAdded = existingIds.includes(loc.id);
                return (
                  <div key={loc.id} className="p-3 rounded-lg border border-gray-100 hover:border-blue-200 hover:bg-blue-50/30 transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <div className="font-semibold text-gray-900 text-sm">{loc.name}</div>
                        <div className="text-xs text-gray-500 mt-0.5">{loc.category}</div>
                      </div>
                      <button 
                        onClick={() => !isAdded && onAdd(loc)}
                        disabled={isAdded}
                        className="text-xs font-medium px-3 py-1.5 rounded-full transition-colors flex items-center gap-1"
                        style={{ 
                          backgroundColor: isAdded ? '#f3f4f6' : '#E0E7FF', 
                          color: isAdded ? '#9ca3af' : '#3730A3',
                          cursor: isAdded ? 'not-allowed' : 'pointer'
                        }}
                      >
                        {isAdded ? (
                          <><Check size={14} /> Added</>
                        ) : (
                          <><Plus size={14} /> Add to route</>
                        )}
                      </button>
                    </div>
                    <div className="text-xs text-gray-600 flex items-center gap-3 mt-2 pt-2 border-t border-gray-50">
                      <span className="flex items-center gap-1"><Clock size={12} className="text-gray-400"/> {loc.openTime} - {loc.closeTime}</span>
                      <span className="flex items-center gap-1"><Timer size={12} className="text-gray-400"/> {loc.duration} min</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
'''

if 'function DemoLocationSelector' not in code:
    code = code.replace('function DestinationEditor', selector_code + '\nfunction DestinationEditor')

# Add the addDemoLocation function inside App component
add_demo_fn = '''
  const addDemoLocation = (loc) => {
    const next = [...destinations, { ...loc, userExcluded: false }];
    setDestinations(next);
    setEditorOpen(false);
    setRecoveryMsg(`Added ${loc.name} to your route.`);
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode);
  };
'''
if 'const addDemoLocation =' not in code:
    code = code.replace('  const removeDestination = (id) => {', add_demo_fn + '\n  const removeDestination = (id) => {')

# Modify the render logic in App to show DemoLocationSelector for adding
code = code.replace(
    '''      {editorOpen && (
        <DestinationEditor
          initial={editingDest ? { ...editingDest, duration: String(editingDest.duration) } : null}
          onSave={saveDestination}
          onCancel={closeEditor}
        />
      )}''',
    '''      {editorOpen && !editingId && (
        <DemoLocationSelector
          existingIds={destinations.map(d => d.id)}
          onAdd={addDemoLocation}
          onCancel={closeEditor}
        />
      )}
      {editorOpen && editingId && (
        <DestinationEditor
          initial={editingDest ? { ...editingDest, duration: String(editingDest.duration) } : null}
          onSave={saveDestination}
          onCancel={closeEditor}
        />
      )}'''
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
