import requests  # type: ignore[import-unresolved]

print("Iniciando consulta à API...")

response = requests.get(
    "https://api.meersens.com/environment/public/weather/history",
    headers={"apikey": "TASHQxcxqNgqwqSe2VEXJXX8gXziRgWK"},
    params={
        "lat": -22.9071,
        "lng": -47.0632,
        "from": "2026-09-01T15:00:00Z",
        "to": "2026-09-11T15:02:02Z",
        "page": 0,
    },
)

print(response.status_code)
print(response.json())
