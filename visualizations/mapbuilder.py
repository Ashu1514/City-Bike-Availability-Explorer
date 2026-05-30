import folium
import random

DEFAULT_COLOR = "#555555"


def build_map(stations):
    """Stations mode — color pins by bike availability."""
    avg_lat = sum(s['latitude'] for s in stations) / len(stations)
    avg_lon = sum(s['longitude'] for s in stations) / len(stations)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)

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

def build_vehicle_map(stations, vehicle_type_colors, vtype_names, vehicle_specs):
    """
    Vehicles mode:
    - Dots scattered randomly in a box
    - Clicking shows vehicle SPECS + street address button
    - Falls back gracefully if vehicle_types_available is missing
    """
    avg_lat = sum(s["latitude"] for s in stations) / len(stations)
    avg_lon = sum(s["longitude"] for s in stations) / len(stations)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)

    rng = random.Random()

    has_vehicle_type_data = any(
        len(s.get("vehicle_types", [])) > 0
        for s in stations
    )

    for station in stations:
        vtypes = station.get("vehicle_types") or []
        active_types = [vt for vt in vtypes if vt.get("count", 0) > 0]
        bikes = station["available_bikes"]
        lat   = station["latitude"]
        lon   = station["longitude"]
        sid   = str(lat) + str(lon)

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

        # ── CASE 1: No vehicle type data (older feeds) ──
        if not has_vehicle_type_data:
            if bikes == 0:
                continue

            dot_color = "#27ae60" if bikes > 3 else "#e67e22" if bikes > 0 else "#e74c3c"

            popup_html = f"""
            <div style="font-family:Arial; min-width:200px;">
                <b style="font-size:14px;">📍 {station['name']}</b>
                <hr style="margin:6px 0;">
                <div style="
                    background:#f9f9f9;
                    border-left:4px solid {dot_color};
                    padding:8px 10px;
                    border-radius:0 6px 6px 0;">
                    <p style="font-size:12px; color:#666; margin-bottom:4px;">
                        ⚠️ No detailed vehicle type info available.
                    </p>
                    <table style="font-size:12px;">
                        <tr>
                            <td style="color:#666;">🚲 Bikes available</td>
                            <td style="font-weight:bold; padding-left:10px;">{bikes}</td>
                        </tr>
                        <tr>
                            <td style="color:#666;">🅿️ Empty docks</td>
                            <td style="font-weight:bold; padding-left:10px;">{station['available_docks']}</td>
                        </tr>
                        <tr>
                            <td style="color:#666;">📦 Capacity</td>
                            <td style="font-weight:bold; padding-left:10px;">{station['capacity']}</td>
                        </tr>
                    </table>
                </div>
                {address_btn}
            </div>
            """

            rng.seed(station["name"])
            box_size = 60
            dot_size = 9
            dot_spans = ""
            for _ in range(min(bikes, 20)):
                x = rng.randint(0, box_size - dot_size)
                y = rng.randint(0, box_size - dot_size)
                dot_spans += f"""<span style="
                    position:absolute; left:{x}px; top:{y}px;
                    width:{dot_size}px; height:{dot_size}px;
                    border-radius:50%; background:{dot_color};
                    border:1px solid white; opacity:0.9;"></span>"""

            dots_html = f"""
            <div style="position:relative; width:{box_size}px; height:{box_size}px;">
                {dot_spans}
            </div>"""

            icon = folium.DivIcon(
                html=dots_html,
                icon_size=(box_size, box_size),
                icon_anchor=(box_size // 2, box_size // 2),
            )

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=station["name"],
                icon=icon,
            ).add_to(m)
            continue

        # ── CASE 2: Vehicle type data exists ──
        if bikes == 0 or not active_types:
            continue

        # Build popup with specs per vehicle type + address button
        specs_sections = ""
        for vt in active_types:
            vid   = vt.get("vehicle_type_id", "")
            name  = vtype_names.get(vid, vid)
            color = vehicle_type_colors.get(vid, DEFAULT_COLOR)
            specs = vehicle_specs.get(vid, {})

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
            <b style="font-size:14px;">📍 {station['name']}</b>
            <hr style="margin:6px 0;">
            {specs_sections}
            {address_btn}
        </div>
        """

        # Build scattered dots
        box_size = 100
        dot_size = 9
        rng.seed(station["name"])
        dot_spans = ""
        for vt in active_types:
            vid   = vt.get("vehicle_type_id", "")
            count = vt.get("count", 0)
            color = vehicle_type_colors.get(vid, DEFAULT_COLOR)
            for _ in range(count):
                x = rng.randint(0, box_size - dot_size)
                y = rng.randint(0, box_size - dot_size)
                dot_spans += f"""<span style="
                    position:absolute; left:{x}px; top:{y}px;
                    width:{dot_size}px; height:{dot_size}px;
                    border-radius:50%; background:{color};
                    border:1px solid white; opacity:0.9;"></span>"""

        dots_html = f"""
        <div style="position:relative; width:{box_size}px; height:{box_size}px;">
            {dot_spans}
        </div>"""

        icon = folium.DivIcon(
            html=dots_html,
            icon_size=(box_size, box_size),
            icon_anchor=(box_size // 2, box_size // 2),
        )

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=station["name"],
            icon=icon,
        ).add_to(m)

    return m._repr_html_()
