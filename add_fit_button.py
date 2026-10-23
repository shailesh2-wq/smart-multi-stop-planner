import re

with open('src/MapContainer.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_header = '''        <div className="flex items-center justify-between p-4 border-b border-gray-100 bg-white z-10 shrink-0">
          <div className="flex items-center gap-3">
            <h2 className="font-bold text-gray-900">Map</h2>
            <span className="text-sm text-green-600 font-medium">Live Google Maps Routing</span>
          </div>
          <button 
            onClick={() => window.dispatchEvent(new CustomEvent('fitAllStops'))}
            className="text-xs font-medium px-3 py-1.5 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-md transition-colors text-gray-700"
          >
            Fit all stops
          </button>
        </div>'''

code = re.sub(
    r'<div className="flex items-center justify-between p-4 border-b border-gray-100 bg-white z-10 shrink-0">.*?</div>\n        </div>',
    new_header,
    code,
    flags=re.DOTALL
)

with open('src/MapContainer.jsx', 'w', encoding='utf-8') as f:
    f.write(code)

with open('src/RealMap.jsx', 'r', encoding='utf-8') as f:
    real_map = f.read()

real_map_update = '''  // Fit bounds when stops change or on request
  useEffect(() => {
    const doFitBounds = () => {
      if (map && isLoaded) {
        const bounds = new window.google.maps.LatLngBounds();
        bounds.extend({ lat: homeNode.lat, lng: homeNode.lng });
        
        activeStops.forEach(stop => {
          if (stop.lat && stop.lng) bounds.extend({ lat: stop.lat, lng: stop.lng });
        });
        excludedStops.forEach(stop => {
          if (stop.lat && stop.lng) bounds.extend({ lat: stop.lat, lng: stop.lng });
        });
        
        if (!bounds.isEmpty()) {
          map.fitBounds(bounds);
          // Add some padding
          const listener = window.google.maps.event.addListener(map, "idle", function() {
             if (map.getZoom() > 14) map.setZoom(14);
             window.google.maps.event.removeListener(listener);
          });
        }
      }
    };
    
    doFitBounds();
    
    window.addEventListener('fitAllStops', doFitBounds);
    return () => window.removeEventListener('fitAllStops', doFitBounds);
  }, [map, activeStops, excludedStops, isLoaded]);'''

real_map = re.sub(
    r'  // Fit bounds when stops change\n  useEffect\(\(\) => \{.*?\n  \}, \[map, activeStops, excludedStops, isLoaded\]\);',
    real_map_update,
    real_map,
    flags=re.DOTALL
)

with open('src/RealMap.jsx', 'w', encoding='utf-8') as f:
    f.write(real_map)
