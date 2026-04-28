import requests
try:
    response = requests.get("http://localhost:8000/api/v1/parking/parking_spaces/statistics/")
    data = response.json()
    print("Response code:", data.get("code"))
    print("\nBy Floor:")
    for floor, stats in data.get("data", {}).items():
        print(f"\n{floor}:")
        print(f"  occupied: {stats[\"occupied\"]}")
        print(f"  maintenance: {stats[\"maintenance\"]}")
        print(f"  reserved: {stats[\"reserved\"]}")
        print(f"  free_charging: {stats[\"free_charging\"]}")
        print(f"  free_regular: {stats[\"free_regular\"]}")
        print(f"  total: {stats[\"total\"]}")
    print("\nGlobal Statistics:")
    all_stats = {k: 0 for k in ["occupied", "maintenance", "reserved", "free_charging", "free_regular", "total"]}
    for stats in data.get("data", {}).values():
        for k in all_stats:
            all_stats[k] += stats[k]
    for k, v in all_stats.items():
        print(f"  {k}: {v}")
except Exception as e:
    print(f"requests failed: {e}")
    import urllib.request, json
    try:
        response = urllib.request.urlopen("http://localhost:8000/api/v1/parking/parking_spaces/statistics/")
        data = json.loads(response.read())
        print("Response code:", data.get("code"))
        print("\nBy Floor:")
        for floor, stats in data.get("data", {}).items():
            print(f"\n{floor}:")
            print(f"  occupied: {stats[\"occupied\"]}")
            print(f"  maintenance: {stats[\"maintenance\"]}")
            print(f"  reserved: {stats[\"reserved\"]}")
            print(f"  free_charging: {stats[\"free_charging\"]}")
            print(f"  free_regular: {stats[\"free_regular\"]}")
            print(f"  total: {stats[\"total\"]}")
        print("\nGlobal Statistics:")
        all_stats = {k: 0 for k in ["occupied", "maintenance", "reserved", "free_charging", "free_regular", "total"]}
        for stats in data.get("data", {}).values():
            for k in all_stats:
                all_stats[k] += stats[k]
        for k, v in all_stats.items():
            print(f"  {k}: {v}")
    except Exception as e2:
        print(f"urllib also failed: {e2}")
