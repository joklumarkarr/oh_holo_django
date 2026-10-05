import signal
import threading
import time

from django.core.management.base import BaseCommand
from django.db import close_old_connections
from django.utils import timezone

from tracker.sync import poll_live_once, refresh_slow_all


class Command(BaseCommand):
    help = "Long-running poller: one batched Holodex call per cycle, broadcasting only what changed."

    def add_arguments(self, parser):
        parser.add_argument("--interval", type=int, default=60,
                            help="Seconds between live-status polls (default 60).")
        parser.add_argument("--slow-interval", type=int, default=3600,
                            help="Seconds between subscriber-count/past-stream refreshes (default 3600).")
        parser.add_argument("--once", action="store_true",
                            help="Run a single cycle and exit (handy for testing).")

    def log(self, message):
        self.stdout.write(f"[{timezone.localtime():%H:%M:%S}] {message}")
        self.stdout.flush()

    def handle(self, *args, **options):
        stop = threading.Event()
        # Without these handlers, a container's PID 1 silently ignores SIGTERM
        # and `docker stop` / Kubernetes would wait out the grace period and
        # then SIGKILL us. Setting the Event wakes the sleep below immediately.
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda *_: stop.set())

        interval = options["interval"]
        slow_interval = options["slow_interval"]
        next_slow = 0.0   # 0 = "due immediately", so the first cycle fills in counts + past streams
        failures = 0
        self.log(f"poll_live started: live every {interval}s, slow refresh every {slow_interval}s")

        while not stop.is_set():
            now = time.monotonic()
            try:
                # Long-lived process: drop DB connections that the server has closed
                # (e.g. Postgres restarted) instead of failing forever on a dead one.
                close_old_connections()

                if now >= next_slow:
                    changed = refresh_slow_all()
                    next_slow = now + slow_interval
                    self.log(f"slow refresh done ({len(changed)} changed)")

                changed = poll_live_once()
                if changed:
                    self.log(f"live poll: changed -> {', '.join(changed)}")
                elif options["verbosity"] >= 2:
                    self.log("live poll: no changes")
                failures = 0
            except Exception as e:
                failures += 1
                self.stderr.write(f"[{timezone.localtime():%H:%M:%S}] poll failed ({failures} in a row): {e!r}")

            if options["once"]:
                break
            # Normal: wait `interval`. After failures: back off (2x, 4x, ...) up to 10 minutes.
            delay = min(interval * 2 ** failures, 600) if failures else interval
            stop.wait(delay)

        self.log("poll_live stopped")