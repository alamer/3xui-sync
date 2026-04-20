import json
import os
import sys
from datetime import datetime, timezone

import requests

PANEL_URL = os.environ["PANEL_URL"]
WEB_BASE_PATH = os.environ.get("WEB_BASE_PATH", "")
USERNAME = os.environ["PANEL_USERNAME"]
PASSWORD = os.environ["PANEL_PASSWORD"]


def check_response(resp: requests.Response, context: str) -> dict:
    data = resp.json()
    if resp.status_code != 200 or data.get("success") is False:
        print(f"[ERR] {context}: [{resp.status_code}] {resp.text}")
        sys.exit(1)
    return data


def expiry_ms_to_days(expiry_ms: int) -> int:
    if expiry_ms <= 0:
        return 0
    remaining = (expiry_ms / 1000) - datetime.now(tz=timezone.utc).timestamp()
    return max(0, int(remaining / 86400))


def main() -> None:
    session = requests.Session()
    base_api = f"{PANEL_URL}{WEB_BASE_PATH}/panel/api"

    check_response(
        session.post(f"{PANEL_URL}{WEB_BASE_PATH}/login", json={"username": USERNAME, "password": PASSWORD}),
        "Login failed",
    )
    print("[OK] Logged in")

    inbounds = check_response(session.get(f"{base_api}/inbounds/list"), "Failed to fetch inbounds").get("obj", [])

    if not inbounds:
        print("[ERR] No inbounds found")
        sys.exit(1)

    # Pick inbound
    if len(sys.argv) >= 2:
        target_id = int(sys.argv[1])
        inbound = next((i for i in inbounds if i["id"] == target_id), None)
        if inbound is None:
            print(f"[ERR] Inbound with id={target_id} not found")
            sys.exit(1)
    else:
        print("\nAvailable inbounds:")
        for i in inbounds:
            print(f"  [{i['id']}] {i.get('remark', '—')} ({i.get('protocol', '?')})")
        print("\nUsage: python fetch_users.py <inbound_id>")
        sys.exit(0)

    remark = inbound.get("remark", "—")
    settings = json.loads(inbound.get("settings", "{}"))
    clients = settings.get("clients", [])

    print(f"[OK] Inbound {target_id} ({remark}): {len(clients)} clients found")

    users = []
    for client in clients:
        users.append({
            "email": client["email"],
            "subscription": client.get("subId", ""),
            "expireDays": expiry_ms_to_days(client.get("expiryTime", 0)),
            "limitIp": client.get("limitIp", 0),
            "totalGb": client.get("totalGB", 0),
        })

    with open("users.json", "w") as f:
        json.dump({"users": users}, f, indent=2)

    print(f"[DONE] Written {len(users)} users to users.json")


if __name__ == "__main__":
    main()
