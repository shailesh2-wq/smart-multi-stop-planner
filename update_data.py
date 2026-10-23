import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_defaults = '''const DEFAULT_DESTINATIONS = [
  { id: "d1", name: "Dentist Appointment", address: "77 Clinic Rd", priority: "must", duration: 45, openTime: "09:00", closeTime: "17:00", preferredArrival: "10:30", lat: 37.785, lng: -122.420 },
  { id: "d2", name: "City College", address: "142 University Ave", priority: "important", duration: 120, openTime: "08:00", closeTime: "18:00", preferredArrival: "12:00", lat: 37.725, lng: -122.450 },
  { id: "d5", name: "Harbor Market", address: "9 Dockside Ln", priority: "flexible", duration: 45, openTime: "09:00", closeTime: "16:00", preferredArrival: "14:00", lat: 37.808, lng: -122.413 },
  { id: "d4", name: "Pulse Fitness", address: "220 River Rd", priority: "important", duration: 60, openTime: "06:00", closeTime: "21:00", preferredArrival: "15:30", lat: 37.750, lng: -122.420 },
  { id: "d3", name: "Green Fork Cafe", address: "58 Market St", priority: "must", duration: 60, openTime: "11:00", closeTime: "22:00", preferredArrival: "17:30", lat: 37.760, lng: -122.400 },
];'''

code = re.sub(r'const DEFAULT_DESTINATIONS = \[.*?\];', new_defaults, code, flags=re.DOTALL)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
