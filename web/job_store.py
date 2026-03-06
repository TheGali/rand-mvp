"""Job storage — read/write job JSON files + image serving.

Each job lives in jobs/{uuid}/ with a job.json file and images/ directory.
No database needed — JSON files are simple and debuggable.
"""

import json
from pathlib import Path

JOBS_DIR = Path(__file__).resolve().parent.parent / "jobs"


def _job_path(job_id: str) -> Path:
    return JOBS_DIR / job_id / "job.json"


def _save_job(job_id: str, data: dict):
    path = _job_path(job_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def create_job(job_id: str, data: dict):
    _save_job(job_id, data)


def get_job(job_id: str) -> dict | None:
    path = _job_path(job_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def update_job_status(job_id: str, status: str):
    job = get_job(job_id)
    if job:
        job["status"] = status
        _save_job(job_id, job)


def save_processed_observation(job_id: str, obs_data: dict):
    """Append or update a processed observation in the job."""
    job = get_job(job_id)
    if not job:
        return

    # Update or append
    existing = next(
        (i for i, o in enumerate(job["processed_observations"])
         if o["obs_number"] == obs_data["obs_number"]),
        None,
    )
    if existing is not None:
        job["processed_observations"][existing] = obs_data
    else:
        job["processed_observations"].append(obs_data)

    job["progress"]["current"] = len(job["processed_observations"])
    _save_job(job_id, job)


def update_observation(job_id: str, obs_number: str, updates: dict) -> bool:
    """Update specific fields of a processed observation."""
    job = get_job(job_id)
    if not job:
        return False

    for obs in job["processed_observations"]:
        if obs["obs_number"] == obs_number:
            # Only update allowed editable fields
            editable = {
                "caption", "system", "component", "location", "condition",
                "prose", "recommendation", "funding_label", "priority", "cost_low", "cost_high",
                "approved", "approved_by", "approved_at",
                "flags_reviewed", "estimate_info",
            }
            for key, value in updates.items():
                if key in editable:
                    obs[key] = value
            _save_job(job_id, job)
            return True

    return False


def get_image_path(job_id: str, obs_number: str) -> Path | None:
    """Return the path to an observation's extracted image."""
    images_dir = JOBS_DIR / job_id / "images"
    # Try the standard naming convention
    img_path = images_dir / f"obs_{obs_number}.png"
    if img_path.exists():
        return img_path
    return None


def list_jobs() -> list[dict]:
    """List all jobs, most recent first."""
    if not JOBS_DIR.exists():
        return []

    jobs = []
    for job_dir in sorted(JOBS_DIR.iterdir(), reverse=True):
        job_file = job_dir / "job.json"
        if job_file.exists():
            try:
                data = json.loads(job_file.read_text(encoding="utf-8"))
                jobs.append({
                    "id": data.get("id", job_dir.name),
                    "filename": data.get("filename", ""),
                    "building_name": data.get("building_name", ""),
                    "status": data.get("status", "unknown"),
                    "observation_count": data.get("observation_count", 0),
                })
            except (json.JSONDecodeError, OSError):
                continue

    return jobs
