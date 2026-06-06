from collections import Counter


def prepare_vehicle_type_chart_obj(
    vehicles,
    vehicle_type_names,
    vehicle_colors,
    limit=5
):
    """
    Prepare top vehicle type distribution pie chart object.

    Pie chart uses count values internally, but labels show percentages.
    """

    vehicle_type_counter = Counter()

    for vehicle in vehicles:
        vehicle_type_id = vehicle.get("vehicle_type_id")

        if not vehicle_type_id:
            continue

        vehicle_type_counter[vehicle_type_id] += 1

    vehicle_chart = []

    for vehicle_type_id, count in vehicle_type_counter.items():
        if count <= 1:
            continue
        vehicle_chart.append({
            "vehicle_type_id": vehicle_type_id,
            "name": vehicle_type_names.get(vehicle_type_id) or "E-SCOOTER",
            "count": count,
            "color": vehicle_colors.get(vehicle_type_id) or "#999999"
        })

    vehicle_chart.sort(key=lambda x: x["count"], reverse=True)
    # vehicle_chart = vehicle_chart[:limit]

    top_total = sum(item["count"] for item in vehicle_chart)

    labels = []
    data = []
    background_colors = []

    for item in vehicle_chart:
        percentage = 0

        if top_total > 0:
            percentage = round((item["count"] / top_total) * 100, 1)

        labels.append(f"{item['name']} ({percentage}%)")
        data.append(item["count"])
        background_colors.append(item["color"])

    return {
        "type": "pie",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": "Vehicles",
                "data": data,
                "backgroundColor": background_colors,
                "borderColor": "#ffffff",
                "borderWidth": 2
            }]
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {
                "legend": {
                    "display": True,
                    "position": "bottom",
                    "labels": {
                        "font": {
                            "size": 10
                        },
                        "boxWidth": 12,
                        "boxHeight": 12,
                        "padding": 10
                    }
                },
                "tooltip": {
                    "enabled": True
                }
            }
        }
    }

def prepare_station_chart_obj(stations, limit=50):
    """
    Prepare top stations by available bikes bar chart object.

    Returns Chart.js object:
    {
        "type": "bar",
        "data": {...},
        "options": {...}
    }
    """

    station_chart = []

    for station in stations:
        available_bikes = station.get("available_bikes") or 0

        if available_bikes <= 0:
            continue

        station_chart.append({
            "name": station.get("name") or "Unknown Station",
            "bikes": available_bikes
        })

    station_chart.sort(key=lambda x: x["bikes"], reverse=True)
    station_chart = station_chart[:limit]

    labels = [item["name"] for item in station_chart]
    data = [item["bikes"] for item in station_chart]

    return {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": "Bikes Available",
                "data": data,
                "backgroundColor": "#2c7be5",
                "borderColor": "#1a63c5",
                "borderWidth": 1,
                "borderRadius": 4
            }]
        },
        "options": {
            "indexAxis": "y",
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {
                "legend": {
                    "display": False
                },
                "tooltip": {
                    "enabled": True
                }
            },
            "scales": {
                "x": {
                    "beginAtZero": True,
                    "title": {
                        "display": True,
                        "text": "Bikes Available",
                        "font": {
                            "size": 11
                        }
                    },
                    "ticks": {
                        "font": {
                            "size": 10
                        }
                    }
                },
                "y": {
                    "ticks": {
                        "font": {
                            "size": 10
                        }
                    }
                }
            }
        }
    }