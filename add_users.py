import json
import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import requests

PANEL_URL = os.environ["PANEL_URL"]
WEB_BASE_PATH = os.environ.get("WEB_BASE_PATH", "")
USERNAME = os.environ["PANEL_USERNAME"]
PASSWORD = os.environ["PANEL_PASSWORD"]
SUBSCRIPTION_PATH = os.environ["SUBSCRIPTION_PATH"]

DEFAULT_TOTAL_GB = 20 * 1024**3
DEFAULT_EXPIRY_DAYS = 30
DEFAULT_LIMIT_IP = 3
COMMENT = "Создано через API — общий sub"


@dataclass
class User:
    email: str
    subscription: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    expireDays: int = DEFAULT_EXPIRY_DAYS
    limitIp: int = DEFAULT_LIMIT_IP
    totalGb: int = DEFAULT_TOTAL_GB

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            email=data["email"],
            subscription=data.get("subscription", uuid.uuid4().hex[:16]),
            expireDays=data.get("expireDays", DEFAULT_EXPIRY_DAYS),
            limitIp=data.get("limitIp", DEFAULT_LIMIT_IP),
            totalGb=data.get("totalGb", DEFAULT_TOTAL_GB),
        )

    @property
    def expiry_time_ms(self) -> int:
        if self.expireDays <= 0:
            return 0
        return int((datetime.now() + timedelta(days=self.expireDays)).timestamp() * 1000)


def check_response(resp: requests.Response, context: str) -> dict:
    data = resp.json()
    if resp.status_code != 200 or data.get("success") is False:
        print(f"[ERR] {context}: [{resp.status_code}] {resp.text}")
        sys.exit(1)
    return data


def main() -> None:
    with open("users.json") as f:
        users = [User.from_dict(u) for u in json.load(f)["users"]]
    print(f"[INFO] Loaded {len(users)} users")

    session = requests.Session()
    base_api = f"{PANEL_URL}{WEB_BASE_PATH}/panel/api"

    check_response(
        session.post(f"{PANEL_URL}{WEB_BASE_PATH}/login", json={"username": USERNAME, "password": PASSWORD}),
        "Ошибка логина",
    )
    print("[OK] Logged in")

    inbounds = check_response(
        session.get(f"{base_api}/inbounds/list"), "Ошибка получения inbounds"
    ).get("obj", [])
    print(f"[OK] Found {len(inbounds)} inbounds")

    report: list[dict] = []

    for user in users:
        client_uuid = str(uuid.uuid4())
        print(f"\n[USER] Processing {user.email}")

        success_count = 0
        for inbound in inbounds:
            inbound_id = inbound["id"]
            remark = inbound.get("remark", "Без названия")

            client = {
                "id": client_uuid,
                "flow": "",
                "email": f"{user.email}-{remark}",
                "limitIp": user.limitIp,
                "totalGB": user.totalGb,
                "expiryTime": user.expiry_time_ms,
                "enable": True,
                "tgId": "",
                "subId": user.subscription,
                "comment": COMMENT,
                "reset": 0,
            }

            resp = session.post(
                f"{base_api}/inbounds/addClient",
                json={"id": inbound_id, "settings": json.dumps({"clients": [client]})},
            )

            if resp.status_code == 200 and resp.json().get("success"):
                print(f"  [OK] Added to inbound {inbound_id} ({remark})")
                success_count += 1
            else:
                print(f"  [ERR] Failed inbound {inbound_id} ({remark}): {resp.text}")

        print(f"  [DONE] {success_count}/{len(inbounds)} inbounds | UUID: {client_uuid} | Sub: {user.subscription}")
        report.append({"email": user.email, "uuid": client_uuid, "sub_url": f"{PANEL_URL}{SUBSCRIPTION_PATH}/{user.subscription}"})

    print("\n" + "=" * 60)
    print("SUBSCRIPTION REPORT")
    print("=" * 60)
    for entry in report:
        print(f"  {entry['email']}")
        print(f"    UUID : {entry['uuid']}")
        print(f"    URL  : {entry['sub_url']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
