import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add addNavNode to import
code = code.replace(
    'import { nodeForId, getShortestPath } from "./cityNetwork";',
    'import { nodeForId, getShortestPath, addNavNode } from "./cityNetwork";'
)

# Update saveDestination to also call addNavNode
old_save = '''      const coord = DEMO_MAP_LOCATIONS[baseIndex];
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
    }'''

new_save = '''      const coord = DEMO_MAP_LOCATIONS[baseIndex];
      // Offset by 0.003 degrees (~300m) per cycle to prevent exact overlap
      const offsetLat = coord.lat + (cycle * 0.003);
      const offsetLng = coord.lng + (cycle * 0.003);
      
      // Synthetic map offsets (approx 20px per cycle)
      const offsetX = coord.x + (cycle * 20);
      const offsetY = coord.y + (cycle * 20);

      const newId = genId();
      addNavNode(newId, offsetX, offsetY, form.name);

      const added = { 
        ...form, 
        id: newId,
        isCustom: true,
        lat: offsetLat,
        lng: offsetLng,
        x: offsetX,
        y: offsetY,
        userExcluded: false
      };
      next = [...destinations, added];
      setSelectedId(added.id);
    }'''

code = code.replace(old_save, new_save)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
