import React from 'react';
import RealMap from './RealMap';
import IllustrativeCityMap from './IllustrativeCityMap';

export default function MapContainer(props) {
  // Check for both Next.js and Vite env var conventions
  const apiKey = (typeof process !== 'undefined' && process.env && process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY) 
                 || (import.meta && import.meta.env && import.meta.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY)
                 || (import.meta && import.meta.env && import.meta.env.VITE_GOOGLE_MAPS_API_KEY);

  if (apiKey) {
    return (
      <div className="flex flex-col w-full h-full bg-[#F1F3F6] overflow-hidden">
                <div className="flex items-center justify-between p-4 border-b border-gray-100 bg-white z-10 shrink-0">
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
        </div>
        <div className="relative flex-1 w-full h-full">
          <RealMap {...props} apiKey={apiKey} />
        </div>
      </div>
    );
  }

  // Fallback to Synthetic
  return (
    <div className="relative w-full h-full">

      <IllustrativeCityMap {...props} />
    </div>
  );
}
