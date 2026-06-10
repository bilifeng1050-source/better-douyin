import json
import logging
from datetime import datetime, timezone
from pathlib import Path


logger = logging.getLogger(__name__)

EXPORT_VERSION = "metadata_jsonl_sample_v0.1"
EXPORT_PATH = Path("metadata_exports") / "download_metadata_sample.jsonl"


def _nested_dict(value):
    return value if isinstance(value, dict) else {}


def _first_value(*values):
    for value in values:
        if value is not None:
            return value
    return None


def append_metadata_sample(metadata, local_file_path=None):
    """Append a slim metadata sample without interrupting the caller."""
    try:
        if not isinstance(metadata, dict):
            metadata = {}

        statistics = _nested_dict(metadata.get("statistics"))
        author = _nested_dict(metadata.get("author"))

        sample = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "export_version": EXPORT_VERSION,
            "source": metadata.get("source") or metadata.get("_source") or "single_download",
            "aweme_id": metadata.get("aweme_id"),
            "desc": metadata.get("desc"),
            "create_time": metadata.get("create_time"),
            "digg_count": _first_value(metadata.get("digg_count"), statistics.get("digg_count")),
            "comment_count": _first_value(metadata.get("comment_count"), statistics.get("comment_count")),
            "collect_count": _first_value(metadata.get("collect_count"), statistics.get("collect_count")),
            "share_count": _first_value(metadata.get("share_count"), statistics.get("share_count")),
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

        EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with EXPORT_PATH.open("a", encoding="utf-8") as file:
            file.write(json.dumps(sample, ensure_ascii=False, separators=(",", ":")) + "\n")
        return True
    except Exception as error:
        logger.warning("metadata sample export failed: %s", error)
        return False
