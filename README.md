# 3xui-sync

Bulk client provisioning for [3X-UI](https://github.com/MHSanaei/3x-ui) panels. Reads a list of users from `users.json` and adds each one to every configured inbound simultaneously, using a shared `subId` so a single subscription URL covers all protocols.

## Requirements

```bash
pip install requests
```

## Setup

1. Copy `.env` and fill in your panel details:

```env
PANEL_URL=https://yourdomain.com
WEB_BASE_PATH=/your-base-path      # leave empty if not set
PANEL_USERNAME=admin
PANEL_PASSWORD=secret
SUBSCRIPTION_PATH=/your-sub-path   # path prefix for subscription URLs
```

2. Edit `users.json`:

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

## Run

```bash
export $(grep -v '^#' .env | xargs) && python add_users.py
```

After all users are processed, a subscription report is printed:

```
============================================================
SUBSCRIPTION REPORT
============================================================
  alice
    UUID : 3f2a1b...
    URL  : https://yourdomain.com/your-sub-path/your-sub-id-here
============================================================
```
