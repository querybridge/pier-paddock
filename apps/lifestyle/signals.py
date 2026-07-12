"""Phase 6 — ping IndexNow (Bing/Yandex/Seznam/…) when a page is published.

Inert until settings.INDEXNOW_KEY is set. Runs in a daemon thread with a short
timeout so a slow endpoint never blocks the editor's publish action.
"""
import json
import threading
import urllib.request
from urllib.parse import urlparse

from django.conf import settings
from wagtail.signals import page_published


def _ping(url, host):
    payload = json.dumps({
        "host": host,
        "key": settings.INDEXNOW_KEY,
        "keyLocation": "https://%s/%s.txt" % (host, settings.INDEXNOW_KEY),
        "urlList": [url],
    }).encode()
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow", data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"})
    try:  # pragma: no cover - network, best-effort
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


def indexnow_on_publish(sender, instance, **kwargs):
    if not settings.INDEXNOW_KEY:
        return
    try:
        url = instance.full_url
        host = urlparse(url).netloc if url else ""
    except Exception:
        return
    if url and host:
        threading.Thread(target=_ping, args=(url, host), daemon=True).start()


page_published.connect(indexnow_on_publish, dispatch_uid="lifestyle_indexnow")
