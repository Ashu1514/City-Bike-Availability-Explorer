import folium
import random

DEFAULT_COLOR = "#555555"


def build_map(stations):
    """Stations mode — color pins by bike availability."""
    avg_lat = sum(s["latitude"] for s in stations) / len(stations)
    avg_lon = sum(s["longitude"] for s in stations) / len(stations)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)

    for station in stations:
        bikes    = station["available_bikes"]
        capacity = station["capacity"]
        docks    = station["available_docks"]
        lat      = station["latitude"]
        lon      = station["longitude"]
        sid      = str(lat) + str(lon)   # unique id for the address div

        if bikes == 0:
            color = "red"
        elif bikes <= 3:
            color = "orange"
        else:
            color = "green"

        popup_html = f"""
        <div style="font-family:Arial; min-width:180px;">
            <b>📍 {station["name"][0]["text"]}</b><br><br>
            🚲 <b>Bikes available:</b> {bikes}<br>
            🅿️ <b>Empty docks:</b> {docks}<br>
            📦 <b>Total capacity:</b> {capacity}<br>
            {'✅ Open for renting' if station['is_renting'] else '❌ Not renting'}
            <br><br>
            <div id="addr-{sid}" style="font-size:12px; color:#555;">
                <button
                    onclick="
                        event.stopPropagation();
                        var div = document.getElementById('addr-{sid}');
                        div.innerHTML = '⏳ Loading...';
                        fetch('/address?lat={lat}&lon={lon}')
                            .then(function(r){{ return r.json(); }})
                            .then(function(d){{ div.innerHTML = '📍 ' + d.address; }})
                            .catch(function(){{ div.innerHTML = '❌ Could not load'; }});
                    "
                    style="
                        padding:4px 10px;
                        background:#2c7be5;
                        color:white;
                        border:none;
                        border-radius:4px;
                        cursor:pointer;
                        font-size:12px;">
                    📍 Load Street Address
                </button>
            </div>
        </div>
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{station["name"][0]["text"]} — {bikes} bikes",
            icon=folium.Icon(color=color, icon="bicycle", prefix="fa"),
        ).add_to(m)

    return m._repr_html_()