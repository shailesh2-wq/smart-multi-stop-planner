import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Restore the render block for DestinationEditor
old_render = '''      {editorOpen && !editingId && (
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

new_render = '''      {editorOpen && (
        <DestinationEditor
          initial={editingDest ? { ...editingDest, duration: String(editingDest.duration) } : null}
          onSave={saveDestination}
          onCancel={closeEditor}
        />
      )}'''

code = code.replace(old_render, new_render)

# 2. Update saveDestination with cycling logic
old_save = '''  const saveDestination = (form) => {
    let next;
    if (editingId) {
      next = destinations.map((d) => (d.id === editingId ? { ...d, ...form } : d));
      setSelectedId(editingId);
    } else {
      const added = { ...form, id: genId() };
      next = [...destinations, added];
      setSelectedId(added.id);
    }
    setDestinations(next);
    setEditorOpen(false);
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode);
  };'''

new_save = '''  const saveDestination = (form) => {
    let next;
    if (editingId) {
      next = destinations.map((d) => (d.id === editingId ? { ...d, ...form } : d));
      setSelectedId(editingId);
    } else {
      const customCount = destinations.filter(d => d.isCustom).length;
      const baseIndex = customCount % 3;
      const cycle = Math.floor(customCount / 3);

      const BASE_COORDS = [
        { lat: 37.785, lng: -122.405 }, // Location 1
        { lat: 37.795, lng: -122.415 }, // Location 2
        { lat: 37.775, lng: -122.425 }  // Location 3
      ];

      const coord = BASE_COORDS[baseIndex];
      // Offset by 0.003 degrees (~300m) per cycle to prevent exact overlap
      const offsetLat = coord.lat + (cycle * 0.003);
      const offsetLng = coord.lng + (cycle * 0.003);

      const added = { 
        ...form, 
        id: genId(),
        isCustom: true,
        lat: offsetLat,
        lng: offsetLng,
        userExcluded: false
      };
      next = [...destinations, added];
      setSelectedId(added.id);
    }
    setDestinations(next);
    setEditorOpen(false);
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode);
  };'''

code = code.replace(old_save, new_save)

# 3. Remove DemoLocationSelector component
code = re.sub(r'function DemoLocationSelector\(\{.*?\} \);\n\}', '', code, flags=re.DOTALL)
# 4. Remove addDemoLocation function
code = re.sub(r'  const addDemoLocation = \(loc\) => \{.*?\n  \};\n', '', code, flags=re.DOTALL)
# 5. Clean up imports (remove demoLocations)
code = code.replace("import { DEMO_LOCATIONS } from './data/demoLocations';", "")

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
