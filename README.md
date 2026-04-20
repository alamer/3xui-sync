# 3xui-sync

[Русская документация](README_RU.md)

Bulk client provisioning for [3X-UI](https://github.com/MHSanaei/3x-ui) panels. Reads a list of users from `users.json` and adds each one to every configured inbound simultaneously, using a shared `subId` so a single subscription URL covers all protocols.

## Requirements

```bash
pip install -r requirements.txt
```

## Scripts

### `fetch_users.py` — export clients from an inbound

Connects to the panel, reads all clients from a specific inbound, and writes them to `users.json`.

```bash
# list available inbounds
python fetch_users.py

# export clients from inbound with id=1
python fetch_users.py 1
```

### `add_users.py` — add users to all inbounds

Reads `users.json` and adds each user to every inbound on the panel.

```bash
python add_users.py
```

After processing, a subscription report is printed:

```
============================================================
SUBSCRIPTION REPORT
============================================================
  alice
    UUID : 3f2a1b...
    URL  : https://yourdomain.com/your-sub-path/your-sub-id-here
============================================================
```

## Setup

1. Fill in `.env`:

```env
PANEL_URL=https://yourdomain.com
WEB_BASE_PATH=/your-base-path      # leave empty if not set
PANEL_USERNAME=admin
PANEL_PASSWORD=secret
SUBSCRIPTION_PATH=/your-sub-path
```

2. Load env and run:

```bash
export $(grep -v '^#' .env | xargs) && python fetch_users.py
export $(grep -v '^#' .env | xargs) && python add_users.py
```

## `users.json` format

```json
{
  "users": [
    {
      "email": "alice",
      "subscription": "your-sub-id-here",
      "expireDays": 30,
      "limitIp": 3,
      "totalGb": 0
    }
  ]
}
```

| Field | Description |
|---|---|
| `email` | Unique client identifier. Each inbound gets `{email}-{inbound_remark}` |
| `subscription` | Shared sub ID across all inbounds — used for the unified subscription URL |
| `expireDays` | Days until expiry (`0` = never) |
| `limitIp` | Max simultaneous connections (`0` = unlimited) |
| `totalGb` | Data cap in bytes (`0` = unlimited) |

Fields `expireDays`, `limitIp`, and `totalGb` fall back to the defaults in `add_users.py` if omitted.
