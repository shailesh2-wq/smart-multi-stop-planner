import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add import if missing
if 'DEMO_MAP_LOCATIONS' not in code:
    code = code.replace(
        'import { nodeForId, getShortestPath } from "./cityNetwork";',
        'import { nodeForId, getShortestPath } from "./cityNetwork";\nimport { DEMO_MAP_LOCATIONS } from "./data/demoMapLocations";'
    )

# Replace the saveDestination logic to use DEMO_MAP_LOCATIONS
old_save = '''      const BASE_COORDS = [
        { lat: 37.785, lng: -122.405 }, // Location 1
        { lat: 37.795, lng: -122.415 }, // Location 2
        { lat: 37.775, lng: -122.425 }  // Location 3
      ];

      const coord = BASE_COORDS[baseIndex];'''

new_save = '''      const coord = DEMO_MAP_LOCATIONS[baseIndex];'''

code = code.replace(old_save, new_save)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
