import folium
from folium.plugins import HeatMap
import webbrowser
import os
from geopy.distance import geodesic

# --- CONFIGURATION: HARARE WAR ROOM ---
CITY_CENTER = [-17.795, 31.08]
ZOOM_START = 11

# --- 1. THE SUPPLY (Verified Assets & Competitors) ---
terrace_assets = [
    # 1. THE NORTHERN CLUSTER (Premium)
    {
        "name": "Borrowdale Village Walk", 
        "loc": [-17.761731382494474, 31.0869205512889], 
        "status": "Operational (Anchor: Pick n Pay)"
    },
    {
        "name": "Highland Park (Ph1 & Ph2)", 
        "loc": [-17.79684412486667, 31.099360549725017], 
        "status": "Operational (Anchor: Pick n Pay)"
    },
    {
        "name": "Cardinal's Corner", 
        "loc": [-17.77865594513171, 31.12673240285413], 
        "status": "Development (Anchor: Spar)"
    },
    
    # 2. THE AVENUES / CBD CLUSTER
    {
        "name": "Chinamano Corner", 
        "loc": [-17.81768105658674, 31.047830339643234], 
        "status": "Operational (Anchor: Puma)"
    },

    # 3. THE WESTERN CLUSTER
    {
        "name": "Greenfields Retail Centre", 
        "loc": [-17.829955899263425, 31.02520161080814], 
        "status": "Operational (Belvedere)"
    }
]

competitors = [
    {"name": "Sam Levy's Village", "loc": [-17.75947146725432, 31.089577529841723]},
    {"name": "Avondale Shopping Centre", "loc": [-17.80244358127244, 31.03841003353702]},
    {"name": "Westgate Shopping Mall", "loc": [-17.763000088225223, 30.978995487512506]},
    {"name": "Arundel Village", "loc": [-17.76306483626415, 31.0508650642185]},
    {"name": "Greendale Shopping Centre", "loc": [-17.81903580403664, 31.12130568352962]},
    {"name": "Chisipite Shopping Centre", "loc": [-17.78309145353249, 31.119837242771922]}
]

# --- 2. THE DEMAND (Residential Heatmap Data) ---
# Simulating "Roof Counts" in high-growth zones
residential_density = [
    [-17.7200, 31.1300, 1.0], # Borrowdale Brooke (High Income)
    [-17.7800, 31.0500, 0.8], # Mt Pleasant / Vainona
    [-17.8800, 31.2400, 0.9], # Ruwa / Zimre (Massive Growth Node)
    [-17.7800, 30.9500, 0.9], # Madokero / Westgate Area (Expansion)
    [-17.8300, 31.1000, 0.7], # Greendale / Msasa
    [-18.006715106442986, 31.080902528010935, 0.8], # Chitungwiza (High Density)
]

# --- 3. THE GAP HUNTER (Potential Sites to Test) ---
potential_sites = [
    {"name": "Opportunity A: Ruwa Growth Point", "loc": [-17.885, 31.245]},
    {"name": "Opportunity B: Madokero Estate", "loc": [-17.785, 30.955]},
    {"name": "Opportunity C: Pomona City", "loc": [-17.730, 31.080]}
]

def check_viability(site_loc):
    """Returns distance to nearest mall & True if > 3km gap."""
    all_malls = terrace_assets + competitors
    min_dist = float('inf')
    
    for mall in all_malls:
        dist = geodesic(site_loc, mall['loc']).km
        if dist < min_dist:
            min_dist = dist
            
    return min_dist, min_dist > 3.0  # Viable if > 3km gap

def generate_map():
    m = folium.Map(location=CITY_CENTER, zoom_start=ZOOM_START, tiles="CartoDB dark_matter")

    # A. Draw Heatmap (Where the people live)
    HeatMap(residential_density, radius=25, blur=15, 
            gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}).add_to(m)

    # B. Plot Existing Assets (Blue)
    for site in terrace_assets:
        popup_html = f"<div style='width:150px'><b>{site['name']}</b><br>{site['status']}</div>"
        folium.Marker(site["loc"], popup=popup_html, icon=folium.Icon(color="blue", icon="building", prefix="fa")).add_to(m)
        folium.Circle(site["loc"], radius=3000, color="#0066cc", fill=False).add_to(m)

    # C. Plot Competitors (Red)
    for site in competitors:
        folium.Marker(site["loc"], popup=site["name"], icon=folium.Icon(color="red", icon="shopping-cart", prefix="fa")).add_to(m)
        folium.Circle(site["loc"], radius=3000, color="#ff0000", fill=False).add_to(m)

    # D. Run Gap Hunter Algorithm
    print("\n🔎 EXECUTING SPATIAL ALGORITHM...")
    for site in potential_sites:
        dist, is_viable = check_viability(site["loc"])
        
        if is_viable:
            print(f"✅ FOUND: {site['name']} (Gap: {dist:.1f}km)")
            folium.Marker(
                site["loc"],
                popup=f"<b>RECOMMENDED SITE</b><br>{site['name']}<br>Nearest Mall: {dist:.1f}km away",
                icon=folium.Icon(color="green", icon="star", prefix="fa")
            ).add_to(m)
        else:
            print(f"❌ REJECTED: {site['name']} (Gap: {dist:.1f}km)")
            folium.Marker(
                site["loc"],
                popup="Rejected: Too Congested",
                icon=folium.Icon(color="gray", icon="ban", prefix="fa")
            ).add_to(m)

    output_file = "harare_gap_hunter.html"
    m.save(output_file)
    print(f"🚀 Map Generated: {output_file}")
    webbrowser.open('file://' + os.path.realpath(output_file))

if __name__ == "__main__":
    generate_map()