"""FastAPI entry point — RAND Survey Web App.

Routes: auth, upload, processing (SSE), dashboard, report generation.
"""

import asyncio
import json
import os
import sys
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

load_dotenv(override=True)

# Windows asyncio fix for SSE/uvicorn
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    StreamingResponse,
    FileResponse,
    JSONResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from web.auth import check_password, set_session_cookie, clear_session_cookie, require_auth, is_authenticated
from web.job_store import (
    create_job,
    get_job,
    update_observation,
    get_image_path,
    list_jobs,
    update_job_status,
    save_processed_observation,
)
from src.parser import parse_pptx
from src.processor import process_report

app = FastAPI(title="RAND Survey Tool")

# Static files & templates
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "web" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "web" / "templates"))

# Thread pool for CPU/IO-bound processing
executor = ThreadPoolExecutor(max_workers=2)


# ──────────────────────────── Auth Routes ────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if is_authenticated(request):
        return RedirectResponse("/upload", status_code=302)
    return RedirectResponse("/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse("/upload", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
async def login_submit(request: Request, password: str = Form(...)):
    if check_password(password):
        response = RedirectResponse("/upload", status_code=302)
        set_session_cookie(response)
        return response
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid password"},
        status_code=401,
    )


@app.post("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=302)
    clear_session_cookie(response)
    return response


# ──────────────────────────── Upload Routes ────────────────────────────

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    redirect = require_auth(request)
    if redirect:
        return redirect
    jobs = list_jobs()
    return templates.TemplateResponse("upload.html", {"request": request, "jobs": jobs})


@app.post("/upload")
async def upload_submit(request: Request, file: UploadFile):
    redirect = require_auth(request)
    if redirect:
        return redirect

    if not file.filename.endswith(".pptx"):
        return JSONResponse({"error": "Please upload a .pptx file"}, status_code=400)

    # Save uploaded file
    job_id = str(uuid.uuid4())
    job_dir = BASE_DIR / "jobs" / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    pptx_path = job_dir / "upload.pptx"
    content = await file.read()
    pptx_path.write_bytes(content)

    # Parse PPTX and extract images
    report = parse_pptx(str(pptx_path))

    # Save extracted images to disk
    images_dir = job_dir / "images"
    images_dir.mkdir(exist_ok=True)

    observations_data = []
    for obs in report.observations:
        image_filename = None
        if obs.image_bytes:
            image_filename = f"obs_{obs.obs_number}.png"
            (images_dir / image_filename).write_bytes(obs.image_bytes)

        observations_data.append({
            "slide_index": obs.slide_index,
            "obs_number": obs.obs_number,
            "section_name": obs.section_name,
            "raw_text": obs.raw_text,
            "image_filename": image_filename,
        })

    # Create job record
    create_job(job_id, {
        "id": job_id,
        "status": "uploaded",
        "filename": file.filename,
        "building_name": report.building_name,
        "address": report.address,
        "observation_count": len(report.observations),
        "observations": observations_data,
        "processed_observations": [],
        "progress": {"current": 0, "total": len(report.observations)},
    })

    return JSONResponse({"job_id": job_id})


# ──────────────────────────── Processing Routes ────────────────────────────

@app.get("/processing/{job_id}", response_class=HTMLResponse)
async def processing_page(request: Request, job_id: str):
    redirect = require_auth(request)
    if redirect:
        return redirect
    job = get_job(job_id)
    if not job:
        return RedirectResponse("/upload", status_code=302)
    return templates.TemplateResponse("processing.html", {"request": request, "job": job})


@app.get("/stream/{job_id}")
async def stream_processing(request: Request, job_id: str):
    """SSE endpoint — runs Claude processing with progress callbacks."""
    job = get_job(job_id)
    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)

    if job["status"] == "completed":
        async def already_done():
            yield f"data: {json.dumps({'type': 'complete', 'message': 'Processing already complete'})}\n\n"
        return StreamingResponse(already_done(), media_type="text/event-stream")

    async def event_generator():
        loop = asyncio.get_event_loop()
        queue = asyncio.Queue()

        def progress_callback(current, total, obs_number, status, obs_data=None, cost_usd=0.0):
            """Called from processor thread — pushes events to async queue."""
            asyncio.run_coroutine_threadsafe(
                queue.put({
                    "type": "progress",
                    "current": current,
                    "total": total,
                    "obs_number": obs_number,
                    "status": status,
                    "cost_usd": round(cost_usd, 4),
                }),
                loop,
            )
            # Save processed observation to job.json as it completes
            if obs_data:
                save_processed_observation(job_id, obs_data)

        def run_processing():
            """Run in thread pool to avoid blocking event loop."""
            from src.parser import parse_pptx
            from src.processor import process_report

            job_dir = BASE_DIR / "jobs" / job_id
            pptx_path = job_dir / "upload.pptx"

            report = parse_pptx(str(pptx_path))
            update_job_status(job_id, "processing")

            report = process_report(report, progress_callback=progress_callback)

            # Save all processed observations
            processed_list = []
            for po in report.processed_observations:
                obs_dict = {
                    "slide_index": po.slide_index,
                    "obs_number": po.obs_number,
                    "section_name": po.section_name,
                    "raw_text": po.raw_text,
                    "caption": po.caption,
                    "system": po.system,
                    "component": po.component,
                    "location": po.location,
                    "condition": po.condition,
                    "prose": po.prose,
                    "recommendation": po.recommendation,
                    "priority": po.priority,
                    "cost_low": po.cost_low,
                    "cost_high": po.cost_high,
                    "flags": po.flags,
                }
                processed_list.append(obs_dict)

            job_data = get_job(job_id)
            job_data["processed_observations"] = processed_list
            job_data["status"] = "completed"
            from web.job_store import _save_job
            _save_job(job_id, job_data)

            asyncio.run_coroutine_threadsafe(
                queue.put({"type": "complete", "message": "Processing complete"}),
                loop,
            )

        # Start processing in background thread
        loop.run_in_executor(executor, run_processing)

        # Stream events to client
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=300)
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("type") == "complete":
                    break
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ──────────────────────────── Dashboard Routes ────────────────────────────

@app.get("/dashboard/{job_id}", response_class=HTMLResponse)
async def dashboard_page(request: Request, job_id: str):
    redirect = require_auth(request)
    if redirect:
        return redirect
    job = get_job(job_id)
    if not job:
        return RedirectResponse("/upload", status_code=302)
    return templates.TemplateResponse("dashboard.html", {"request": request, "job": job})


@app.get("/image/{job_id}/{obs_number}")
async def serve_image(job_id: str, obs_number: str):
    """Serve extracted slide photo."""
    img_path = get_image_path(job_id, obs_number)
    if img_path and img_path.exists():
        return FileResponse(str(img_path), media_type="image/png")
    return JSONResponse({"error": "Image not found"}, status_code=404)


@app.patch("/observation/{job_id}/{obs_number}")
async def update_obs(request: Request, job_id: str, obs_number: str):
    """Save edited observation fields back to job.json."""
    redirect = require_auth(request)
    if redirect:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    body = await request.json()
    success = update_observation(job_id, obs_number, body)
    if success:
        return JSONResponse({"status": "saved"})
    return JSONResponse({"error": "Observation not found"}, status_code=404)


@app.get("/api/job/{job_id}")
async def get_job_api(request: Request, job_id: str):
    """Return job data as JSON for Alpine.js."""
    redirect = require_auth(request)
    if redirect:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    job = get_job(job_id)
    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    return JSONResponse(job)


# ──────────────────────────── Report Routes ────────────────────────────

@app.post("/report/{job_id}/pptx")
async def generate_pptx_report(request: Request, job_id: str):
    redirect = require_auth(request)
    if redirect:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    job = get_job(job_id)
    if not job or job["status"] != "completed":
        return JSONResponse({"error": "Job not ready"}, status_code=400)

    from web.pptx_report_writer import generate_pptx_report as gen_pptx
    job_dir = BASE_DIR / "jobs" / job_id
    output_path = job_dir / "report.pptx"
    gen_pptx(job, str(job_dir), str(output_path))

    return FileResponse(
        str(output_path),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"RAND_Report_{job.get('building_name', 'Survey')}.pptx",
    )


@app.post("/report/{job_id}/pdf")
async def generate_pdf_report(request: Request, job_id: str):
    redirect = require_auth(request)
    if redirect:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    job = get_job(job_id)
    if not job or job["status"] != "completed":
        return JSONResponse({"error": "Job not ready"}, status_code=400)

    from web.pdf_writer import generate_pdf_report as gen_pdf
    job_dir = BASE_DIR / "jobs" / job_id
    output_path = job_dir / "report.pdf"
    gen_pdf(job, str(job_dir), str(output_path))

    return FileResponse(
        str(output_path),
        media_type="application/pdf",
        filename=f"RAND_Report_{job.get('building_name', 'Survey')}.pdf",
    )
