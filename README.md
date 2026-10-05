Change vtuber list by editing seed_data.py and adding css
Seed data from the vtuber list with 
    python manage.py seed_data
Import holodex api key as such:
    export HOLODEX_API_KEY=your_key_here      # macOS/Linux
    $env:HOLODEX_API_KEY = "your_key_here"    # Windows PowerShell
Start redis for testing:
    docker run -d -p 6379:6379 --name oh-holo-redis redis:7
Test redis with:
    docker exec -it oh-holo-redis redis-cli ping

## Deploying somewhere real

Two Django settings need your actual domain before this app will work outside localhost:

### 1. ALLOWED_HOSTS
Django refuses to serve HTTP requests — and Channels refuses WebSocket
connections — for any hostname not in this list. The `DEBUG=True` shortcut
that auto-allows `localhost`/`127.0.0.1` does NOT apply once `DEBUG=False`,
which it must be in production.

In `config/settings.py`:
```python
ALLOWED_HOSTS = ["vtubers.example.com"]
```
Symptom if you forget this: every page request returns Django's
"DisallowedHost" error page, and the browser console shows the WebSocket
connection closing immediately after opening.

### 2. CSRF_TRUSTED_ORIGINS
A related but separate setting — needed once the site is served over HTTPS,
for anything that submits a form (the admin login, for example). Without it,
POST requests get rejected even though GET requests work fine.
```python
CSRF_TRUSTED_ORIGINS = ["https://vtubers.example.com"]
```

Both take real domains, not IP addresses, once you're behind a reverse proxy
with a DNS name pointed at it.