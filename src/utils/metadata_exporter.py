import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path


logger = logging.getLogger(__name__)

EXPORT_VERSION = "metadata_jsonl_sample_v0.1"
EXPORT_PATH = Path("metadata_exports") / "download_metadata_sample.jsonl"
EXPORT_DIR = Path("metadata_exports")


def _nested_dict(value):
    return value if isinstance(value, dict) else {}


def _first_value(*values):
    for value in values:
        if value is not None:
            return value
    return None


def _safe_export_name(export_name):
    name = str(export_name or "").strip() or "user_profile_metadata_sample"
    name = Path(name).name
    if name.endswith(".jsonl"):
        name = name[:-6]
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._-")
    return name or "user_profile_metadata_sample"


def _metadata_sample(metadata, source=None, local_file_path=None):
    if not isinstance(metadata, dict):
        metadata = {}

    statistics = _nested_dict(metadata.get("statistics"))
    video = _nested_dict(metadata.get("video"))
    video_statistics = _nested_dict(video.get("statistics"))
    author = _nested_dict(metadata.get("author"))

    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "export_version": EXPORT_VERSION,
        "source": source or metadata.get("source") or metadata.get("_source") or "single_download",
        "aweme_id": metadata.get("aweme_id"),
        "desc": metadata.get("desc"),
        "create_time": metadata.get("create_time"),
        "digg_count": _first_value(
            metadata.get("digg_count"),
            statistics.get("digg_count"),
            video_statistics.get("digg_count"),
        ),
        "comment_count": _first_value(
            metadata.get("comment_count"),
            statistics.get("comment_count"),
            video_statistics.get("comment_count"),
        ),
        "collect_count": _first_value(
            metadata.get("collect_count"),
            statistics.get("collect_count"),
            video_statistics.get("collect_count"),
        ),
        "share_count": _first_value(
            metadata.get("share_count"),
            statistics.get("share_count"),
            video_statistics.get("share_count"),
        ),
        "author_nickname": _first_value(
            metadata.get("author_nickname"),
            author.get("nickname"),
            metadata.get("author_name"),
        ),
        "author_sec_uid": _first_value(metadata.get("author_sec_uid"), author.get("sec_uid")),
        "author_uid": _first_value(metadata.get("author_uid"), author.get("uid")),
        "local_file_path": str(local_file_path) if local_file_path else None,
        "raw_keys": sorted(str(key) for key in metadata.keys()),
    }


def append_metadata_sample(metadata, local_file_path=None):
    """Append a slim metadata sample without interrupting the caller."""
    try:
        EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with EXPORT_PATH.open("a", encoding="utf-8") as file:
            sample = _metadata_sample(metadata, local_file_path=local_file_path)
            file.write(json.dumps(sample, ensure_ascii=False, separators=(",", ":")) + "\n")
        return True
    except Exception as error:
        logger.warning("metadata sample export failed: %s", error)
        return False


def append_metadata_records(records, export_name=None, source="user_profile_metadata"):
    export_path = EXPORT_DIR / f"{_safe_export_name(export_name)}.jsonl"
    exported_count = 0

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    with export_path.open("a", encoding="utf-8") as file:
        for record in records or []:
            if not isinstance(record, dict):
                continue
            sample = _metadata_sample(record, source=source)
            file.write(json.dumps(sample, ensure_ascii=False, separators=(",", ":")) + "\n")
            exported_count += 1

    return export_path, exported_count
