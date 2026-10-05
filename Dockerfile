FROM python:3.12-slim

# No .pyc clutter; flush logs immediately (otherwise `docker logs` lags behind).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies first, in their own layer: rebuilds after a code-only change
# reuse the cached pip install instead of re-downloading everything.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Gather static files into /app/staticfiles at BUILD time. Needs no environment
# variables: settings default to DEBUG on, which skips the production-only checks.
RUN python manage.py collectstatic --noinput

# Don't run as root inside the container.
RUN useradd --system --uid 10001 --no-create-home app
USER app

EXPOSE 8000

# One image, two jobs: this default runs the website; the poller overrides the
# command with `python manage.py poll_live`.
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "oh_holo_django.asgi:application"]