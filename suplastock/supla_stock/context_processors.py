from __future__ import annotations

from datetime import datetime, timezone as dt_timezone
from functools import lru_cache
from pathlib import Path
import subprocess

from django.conf import settings
from django.utils import timezone


def _coerce_datetime(raw_value: str) -> datetime | None:
    value = (raw_value or '').strip()
    if not value:
        return None

    # ISO 8601 (incluindo sufixo Z).
    try:
        normalized = value.replace('Z', '+00:00')
        dt = datetime.fromisoformat(normalized)
        if timezone.is_naive(dt):
            return timezone.make_aware(dt, timezone.get_current_timezone())
        return timezone.localtime(dt, timezone.get_current_timezone())
    except ValueError:
        pass

    known_formats = (
        '%d/%m/%Y %H:%M',
        '%d/%m/%Y',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
    )
    for fmt in known_formats:
        try:
            dt = datetime.strptime(value, fmt)
            return timezone.make_aware(dt, timezone.get_current_timezone())
        except ValueError:
            continue

    return None


def _find_git_commit_datetime() -> datetime | None:
    base_dir = Path(settings.BASE_DIR)
    candidate_dirs = (base_dir, base_dir.parent)

    for cwd in candidate_dirs:
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%ct'],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=2,
                check=True,
            )
            raw_unix_ts = (result.stdout or '').strip()
            if not raw_unix_ts:
                continue
            dt_utc = datetime.fromtimestamp(int(raw_unix_ts), tz=dt_timezone.utc)
            return timezone.localtime(dt_utc, timezone.get_current_timezone())
        except Exception:
            continue

    return None


@lru_cache(maxsize=1)
def _resolve_footer_last_update() -> tuple[str, bool]:
    manual_value = str(getattr(settings, 'APP_LAST_UPDATE', '') or '').strip()
    if manual_value:
        parsed_manual = _coerce_datetime(manual_value)
        if parsed_manual is not None:
            return parsed_manual.strftime('%d/%m/%Y %H:%M'), True
        return manual_value, True

    git_dt = _find_git_commit_datetime()
    if git_dt is not None:
        return git_dt.strftime('%d/%m/%Y %H:%M'), True

    return 'Indisponível', False


def footer_metadata(request):
    last_update_label, has_last_update = _resolve_footer_last_update()
    return {
        'footer_current_year': timezone.localdate().year,
        'footer_dev_name': str(
            getattr(settings, 'FOOTER_DEV_NAME', 'VK Software')
        ).strip() or 'VK Software',
        'footer_dev_url': str(
            getattr(
                settings,
                'FOOTER_DEV_URL',
                'https://vk-software-site-institucional.vercel.app/',
            )
        ).strip() or 'https://vk-software-site-institucional.vercel.app/',
        'footer_last_update_label': last_update_label,
        'footer_last_update_available': has_last_update,
    }
