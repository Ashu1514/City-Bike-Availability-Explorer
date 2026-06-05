import folium
import random
from app import myloc
DEFAULT_COLOR = "#555555"




def build_map(stations=[]):
    """Stations mode — color pins by bike availability."""
    avg_lat = sum(s['latitude'] for s in stations) / len(stations) if len(stations) > 0 else myloc[0] or 1
    avg_lon = sum(s['longitude'] for s in stations) / len(stations) if len(stations) > 0 else myloc[1] or 1


    if len(stations) != 0:
        min_lat = min(s['latitude'] for s in stations)
        max_lat = max(s['latitude'] for s in stations)
        min_lon = min(s['longitude'] for s in stations)
        max_lon = max(s['longitude'] for s in stations)
        padding = 0.02

        sw = [min_lat - padding, min_lon - padding]
        ne = [max_lat + padding, max_lon + padding]

        m = folium.Map(
            location=[avg_lat, avg_lon],
            zoom_start=13,
            min_zoom=12,
            max_zoom=18,
        )

        # Inject JS to lock map to city bounds — prevents dragging to other cities
        lock_js = f"""
        <script>
        window.addEventListener('load', function() {{
            setTimeout(function() {{
                var mapDiv = document.querySelector('.folium-map');
                if (!mapDiv) return;
                var mapId = mapDiv.id;
                var map = window[mapId];
                if (!map) return;
                var bounds = L.latLngBounds(
                    L.latLng({sw[0]}, {sw[1]}),
                    L.latLng({ne[0]}, {ne[1]})
                );
                map.setMaxBounds(bounds);
                map.options.maxBoundsViscosity = 1.0;
            }}, 500);
        }});
        </script>
        """
        m.get_root().html.add_child(folium.Element(lock_js))

        for station in stations:
            bikes    = station['available_bikes']
            capacity = station['capacity']
            docks    = station['available_docks']
            lat      = station['latitude']
            lon      = station['longitude']
            sid      = str(lat) + str(lon)   # unique id for the address div

            if bikes == 0:
                color = "red"
            elif bikes <= 3:
                color = "orange"
            else:
                color = "green"

            popup_html = f"""
            <div style="font-family:Arial; min-width:180px;">
                <b>📍 {station['name']}</b><br><br>
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
                tooltip=f"{station['name']} — {bikes} bikes",
                icon=folium.Icon(color=color, icon="bicycle", prefix="fa"),
            ).add_to(m)

        return m._repr_html_()
    else :
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)
        return m._repr_html_()



def build_vehicle_map(vehicles, vehicle_type_colors, vtype_names, vehicle_specs):
    """
    Vehicles mode:
    - Dots scattered randomly in a box
    - Clicking shows vehicle SPECS + street address button
    - Falls back gracefully if vehicle_types_available is missing
    """
    
    valid_vehicles = [v for v in vehicles if v.get("lat") and v.get("lon")]

    if not valid_vehicles:
        return None
    

    avg_lat = sum(v["lat"] for v in valid_vehicles) / len(valid_vehicles)
    avg_lon = sum(v["lon"] for v in valid_vehicles) / len(valid_vehicles)


    min_lat = min(v["lat"] for v in valid_vehicles)
    max_lat = max(v["lat"] for v in valid_vehicles)
    min_lon = min(v["lon"] for v in valid_vehicles)
    max_lon = max(v["lon"] for v in valid_vehicles)
    padding = 0.02

    sw = [min_lat - padding, min_lon - padding]
    ne = [max_lat + padding, max_lon + padding]

    m = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=13,
        min_zoom=12,
        max_zoom=18,
    )

    # Lock map to city bounds
    lock_js = f"""
    <script>
    window.addEventListener('load', function() {{
        setTimeout(function() {{
            var mapDiv = document.querySelector('.folium-map');
            if (!mapDiv) return;
            var mapId = mapDiv.id;
            var map = window[mapId];
            if (!map) return;
            var bounds = L.latLngBounds(
                L.latLng({sw[0]}, {sw[1]}),
                L.latLng({ne[0]}, {ne[1]})
            );
            map.setMaxBounds(bounds);
            map.options.maxBoundsViscosity = 1.0;
        }}, 500);
    }});
    </script>
    """
    m.get_root().html.add_child(folium.Element(lock_js))

    rng = random.Random()

    for vehicle in vehicles:
        lat   = vehicle["lat"]
        lon   = vehicle["lon"]
        if not lat or not lon:
            continue
        sid   = str(lat) + str(lon)
        vid   = vehicle.get("vehicle_type_id", "")
        name  = vtype_names.get(vid, vid)
        color = vehicle_type_colors.get(vid, DEFAULT_COLOR)
        specs = vehicle_specs.get(vid, {})

        # Address button with self-contained JS (works inside Folium iframe)
        address_btn = f"""
        <div id="addr-{sid}" style="font-size:12px; color:#555; margin-top:8px;">
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
        """

        # Build popup with specs per vehicle type + address button
        specs_sections = ""

        form_factor    = specs.get("form_factor", "—").replace("_", " ").title()
        propulsion     = specs.get("propulsion_type", "—").replace("_", " ").title()
        max_range      = specs.get("max_range_meters", None)
        max_speed      = specs.get("max_permitted_speed", None)
        wheel_count    = specs.get("wheel_count", None)
        rider_capacity = specs.get("rider_capacity", None)

        range_str  = f"{int(max_range/1000)} km" if max_range else "—"
        speed_str  = f"{max_speed} km/h" if max_speed else "—"
        wheels_str = str(wheel_count) if wheel_count else "—"
        riders_str = str(rider_capacity) if rider_capacity else "—"

        specs_sections += f"""
        <div style="
            border-left: 4px solid {color};
            padding: 8px 10px;
            margin-bottom: 10px;
            background: #f9f9f9;
            border-radius: 0 6px 6px 0;">
            <div style="display:flex; align-items:center; gap:6px; margin-bottom:6px;">
                <span style="display:inline-block; width:12px; height:12px;
                    border-radius:50%; background:{color};"></span>
                <b style="font-size:13px;">{name}</b>
            </div>
            <table style="font-size:12px; width:100%;">
                <tr>
                    <td style="color:#666; padding:2px 0;">🚲 Type</td>
                    <td style="font-weight:bold; padding-left:10px;">{form_factor}</td>
                </tr>
                <tr>
                    <td style="color:#666; padding:2px 0;">⚡ Propulsion</td>
                    <td style="font-weight:bold; padding-left:10px;">{propulsion}</td>
                </tr>
                <tr>
                    <td style="color:#666; padding:2px 0;">📏 Max Range</td>
                    <td style="font-weight:bold; padding-left:10px;">{range_str}</td>
                </tr>
                <tr>
                    <td style="color:#666; padding:2px 0;">🏎️ Max Speed</td>
                    <td style="font-weight:bold; padding-left:10px;">{speed_str}</td>
                </tr>
                <tr>
                    <td style="color:#666; padding:2px 0;">🛞 Wheels</td>
                    <td style="font-weight:bold; padding-left:10px;">{wheels_str}</td>
                </tr>
                <tr>
                    <td style="color:#666; padding:2px 0;">👤 Riders</td>
                    <td style="font-weight:bold; padding-left:10px;">{riders_str}</td>
                </tr>
            </table>
        </div>
        """

        popup_html = f"""
        <div style="font-family:Arial; min-width:220px; max-width:280px;">
            <b style="font-size:14px;">📍 {name or form_factor}</b>
            <hr style="margin:6px 0;">
            {specs_sections}
            {address_btn}
        </div>
        """

        # Build scattered dots
        rng.seed(name or form_factor)

        icon_html = f"""
            <div style="
                background-color: {color};
                width: 12px;
                height: 12px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 2px solid white;
                box-shadow: 0 2px 6px rgba(0,0,0,0.35);
            ">
            </div>
            """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=name or form_factor,
            icon=folium.DivIcon(html=icon_html),
            color=color
        ).add_to(m)

    return m._repr_html_()