# 3xui-sync — Руководство пользователя

Инструмент для массового добавления клиентов в панель [3X-UI](https://github.com/MHSanaei/3x-ui). Скрипты добавляют пользователей сразу во все inbound-ы и генерируют единую ссылку на подписку, работающую по всем протоколам.

В проекте два скрипта:
- `fetch_users.py` — считывает уже существующих клиентов из inbound-а панели и сохраняет их в `users.json`
- `add_users.py` — берёт пользователей из `users.json` и добавляет каждого во все inbound-ы панели

---

## Шаг 1. Установка Python и pip

Откройте терминал и выполните:

```bash
sudo apt update
sudo apt install -y python3 python3-pip
```

Проверьте, что Python установлен:

```bash
python3 --version
```

---

## Шаг 2. Скачайте проект

```bash
sudo apt install -y git
git clone https://github.com/your-username/3xui-sync.git
cd 3xui-sync
```

---

## Шаг 3. Установите зависимости

```bash
pip3 install -r requirements.txt
```

---

## Шаг 4. Настройте подключение к панели

Откройте файл `.env` в любом текстовом редакторе:

```bash
nano .env
```

Заполните значения:

```env
PANEL_URL=https://ваш-домен.com
WEB_BASE_PATH=/ваш-base-path
PANEL_USERNAME=ваш-логин
PANEL_PASSWORD=ваш-пароль
SUBSCRIPTION_PATH=/ваш-sub-path
```

- `PANEL_URL` — адрес вашей панели 3X-UI, например `https://example.com`
- `WEB_BASE_PATH` — путь к панели, если вы меняли его в настройках (например `/admin`). Оставьте пустым, если не меняли
- `PANEL_USERNAME` и `PANEL_PASSWORD` — логин и пароль администратора панели
- `SUBSCRIPTION_PATH` — путь для подписок, указан в настройках панели (например `/sub`)

Сохраните файл: `Ctrl+O`, затем `Enter`, затем `Ctrl+X`.

Загрузите переменные в текущую сессию терминала:

```bash
export $(grep -v '^#' .env | xargs)
```

> Эту команду нужно выполнять каждый раз при открытии нового терминала перед запуском скриптов.

---

## Шаг 5. Узнайте ID нужного inbound-а

Запустите скрипт без аргументов — он покажет список всех inbound-ов:

```bash
python3 fetch_users.py
```

Пример вывода:

```
[OK] Logged in
Available inbounds:
  [1] vless-reality (vless)
  [2] vmess-ws (vmess)
  [3] trojan-tcp (trojan)

Usage: python fetch_users.py <inbound_id>
```

Запомните ID нужного inbound-а (число в квадратных скобках).

---

## Шаг 6. Экспортируйте пользователей из inbound-а

Передайте ID inbound-а аргументом. Например, для inbound с ID `1`:

```bash
python3 fetch_users.py 1
```

Скрипт создаст файл `users.json` со всеми клиентами из этого inbound-а:

```json
{
  "users": [
    {
      "email": "alice",
      "subscription": "abc123",
      "expireDays": 25,
      "limitIp": 3,
      "totalGb": 0
    }
  ]
}
```

Вы можете отредактировать этот файл вручную — добавить новых пользователей или изменить параметры существующих:

```bash
nano users.json
```

| Поле | Описание |
|---|---|
| `email` | Уникальное имя клиента |
| `subscription` | ID подписки — одинаковый для всех inbound-ов одного пользователя |
| `expireDays` | Срок действия в днях (`0` — бессрочно) |
| `limitIp` | Максимальное количество одновременных подключений (`0` — без ограничений) |
| `totalGb` | Лимит трафика в байтах (`0` — без ограничений) |

---

## Шаг 7. Добавьте пользователей во все inbound-ы

```bash
python3 add_users.py
```

Скрипт добавит каждого пользователя из `users.json` во все inbound-ы панели. По окончании выведет таблицу с ссылками на подписки:

```
============================================================
SUBSCRIPTION REPORT
============================================================
  alice
    UUID : 3f2a1b...
    URL  : https://ваш-домен.com/ваш-sub-path/abc123
============================================================
```

Ссылку из поля `URL` можно передать пользователю — она работает сразу по всем протоколам.

---

## Типичные ошибки

**`[ERR] Login failed: [404]`**
Неверный `WEB_BASE_PATH` в `.env`. Попробуйте оставить его пустым или уточните путь в настройках панели.

**`[ERR] Login failed: [200]` с `success: false`**
Неверный логин или пароль в `PANEL_USERNAME` / `PANEL_PASSWORD`.

**`ModuleNotFoundError: No module named 'requests'`**
Зависимости не установлены. Выполните `pip3 install -r requirements.txt`.

**`KeyError: 'PANEL_URL'`**
Переменные окружения не загружены. Выполните `export $(grep -v '^#' .env | xargs)`.
