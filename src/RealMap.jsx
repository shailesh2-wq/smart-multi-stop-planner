import React, { useEffect, useState, useMemo } from 'react';
import { GoogleMap, useLoadScript, Marker, Polyline, InfoWindow } from '@react-google-maps/api';
import { PRIORITY_META } from './App';

const mapContainerStyle = {
  width: '100%',
  height: '100%',
};

// Default center to SF if no stops
const defaultCenter = { lat: 37.7749, lng: -122.4194 };

export default function RealMap({ result, destinations, hoveredId, selectedId, onHoverDest, onSelectDest, apiKey }) {
  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: apiKey,
  });

  const [map, setMap] = useState(null);

  const activeStops = result ? result.stops.map(s => s.dest) : [];
  const excludedStops = result ? result.excluded.map(e => e.dest) : [];
  
  // Home is a fixed location for demo
  const homeNode = { id: "home", lat: 37.7749, lng: -122.4194 };

  // Fit bounds when stops change or on request
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
  }, [map, activeStops, excludedStops, isLoaded]);

  const onLoad = React.useCallback(function callback(map) {
    setMap(map);
  }, []);

  const onUnmount = React.useCallback(function callback(map) {
    setMap(null);
  }, []);

  if (loadError) return <div className="p-4 text-red-500">Error loading maps</div>;
  if (!isLoaded) return <div className="p-4">Loading map...</div>;

  // Build polyline path
  const path = [homeNode];
  activeStops.forEach(stop => {
    if (stop.lat && stop.lng) path.push({ lat: stop.lat, lng: stop.lng });
  });

  return (
    <GoogleMap
      mapContainerStyle={mapContainerStyle}
      center={defaultCenter}
      zoom={12}
      onLoad={onLoad}
      onUnmount={onUnmount}
      options={{
        disableDefaultUI: true,
        zoomControl: true,
        styles: [
          { featureType: "poi", elementType: "labels", stylers: [{ visibility: "off" }] }
        ]
      }}
    >
      <Polyline
        path={path}
        options={{
          strokeColor: "#123E85",
          strokeOpacity: 0.8,
          strokeWeight: 4,
          icons: [{ icon: { path: window.google.maps.SymbolPath.FORWARD_CLOSED_ARROW }, offset: '50%' }]
        }}
      />

      {/* Home Marker */}
      <Marker
        position={{ lat: homeNode.lat, lng: homeNode.lng }}
        icon={{
          path: window.google.maps.SymbolPath.CIRCLE,
          fillColor: "#14181F",
          fillOpacity: 1,
          strokeWeight: 0,
          scale: 12,
        }}
        label={{ text: "H", color: "white", fontSize: "12px", fontWeight: "bold" }}
      />

      {/* Active Stops */}
      {activeStops.map((stop, i) => {
        if (!stop.lat || !stop.lng) return null;
        const isHovered = hoveredId === stop.id;
        const isSelected = selectedId === stop.id;
        const scale = isHovered || isSelected ? 16 : 12;
        const meta = PRIORITY_META[stop.priority] || { dot: "#6B7280" };

        return (
          <Marker
            key={`active-${stop.id}`}
            position={{ lat: stop.lat, lng: stop.lng }}
            onClick={() => onSelectDest(stop.id)}
            onMouseOver={() => onHoverDest(stop.id)}
            onMouseOut={() => onHoverDest(null)}
            icon={{
              path: window.google.maps.SymbolPath.CIRCLE,
              fillColor: meta.dot,
              fillOpacity: 1,
              strokeColor: "white",
              strokeWeight: 2,
              scale,
            }}
            label={{ text: String(i + 1), color: "white", fontSize: "12px", fontWeight: "bold" }}
            zIndex={isSelected ? 1000 : 100}
          />
        );
      })}

      {/* Excluded Stops */}
      {excludedStops.map((stop) => {
        if (!stop.lat || !stop.lng) return null;
        const isHovered = hoveredId === stop.id;
        const isSelected = selectedId === stop.id;
        const scale = isHovered || isSelected ? 12 : 10;

        return (
          <Marker
            key={`excluded-${stop.id}`}
            position={{ lat: stop.lat, lng: stop.lng }}
            onClick={() => onSelectDest(stop.id)}
            onMouseOver={() => onHoverDest(stop.id)}
            onMouseOut={() => onHoverDest(null)}
            icon={{
              path: window.google.maps.SymbolPath.CIRCLE,
              fillColor: "white",
              fillOpacity: 0.6,
              strokeColor: "#9CA3AF",
              strokeWeight: 2,
              scale,
            }}
            label={{ text: "X", color: "#6B7280", fontSize: "10px", fontWeight: "bold" }}
            zIndex={10}
          />
        );
      })}
    </GoogleMap>
  );
}
