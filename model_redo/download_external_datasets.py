#!/usr/bin/env python3
"""Download the reviewed external cyanobacteria/cyanotoxin datasets.

The downloader is restartable: completed files are skipped, partial HTTP/FTP
downloads use ``.part`` files, and every run writes a machine-readable manifest.
Only public, official/archive endpoints selected in the dataset review are used.
"""

from __future__ import annotations

import argparse
import csv
import ftplib
import hashlib
import html
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "external_raw"
MANIFEST_DIR = OUT / "_manifests"
USER_AGENT = "iGEM-DryLab-dataset-downloader/1.0 (public research data)"
SSL_CONTEXT = ssl.create_default_context()


SCIENCEBASE = {
    # Priority A: field microcystin/cyanotoxin observations with useful covariates.
    "USGS_Texas_2016_2019": "10.5066/P9ASYKM7",
    "USGS_Texas_2020_2021": "10.5066/P9JUFV65",
    "USGS_LakeOntario_2023": "10.5066/P14NJ5EO",
    "USGS_Ohio_Fluorescence_Calibration": "10.5066/P9CDF76E",
    # Priority B: additional paired field observations and model-validation data.
    "USGS_Sacramento_SanJoaquin_Delta": "10.5066/P96L1RTV",
    "USGS_Five_River_Basins": "10.5066/P94LAHHM",
    "USGS_National_Park_Service_Cyanotoxins": "10.5066/P1KATYJH",
    "USGS_Clinch_River_Cyanotoxins": "10.5066/P13KVOSA",
    "USGS_Tennessee_Reservoirs": "10.5066/P13Q2TD5",
    "USGS_Large_Rivers_2017_Microcystin": "10.5066/P9TID1VX",
    "USGS_Large_Rivers_2018_Microcystin": "10.5066/P98RPC1E",
    "USGS_Large_Rivers_2019_Microcystin": "10.5066/P99I27T4",
    "USGS_CyAN_FIELD": "10.5066/P90GMHSM",
    "USGS_Oregon_Cascades_Cyanotoxins": "10.5066/P96VPGH7",
    # Biological companion releases for the large-river toxin observations.
    "USGS_Large_Rivers_2017_Phytoplankton": "10.5066/P9EYP85Z",
    "USGS_Large_Rivers_2017_Phytoplankton_Tally": "10.5066/P9KKN921",
    "USGS_Large_Rivers_2018_Phytoplankton": "10.5066/P9N4Q9HG",
}

NCEI_ACCESSIONS = {
    "NOAA_GLERL_Lake_Erie_2012_present": [
        "0187718", "0190201", "0190729", "0194301", "0194302",
        "0209116", "0254720", "0276355", "0292222", "0293514",
        "0303633",
    ],
    "NCEI_Lake_Pontchartrain_2020": ["0251826"],
}

DIRECT = {
    "USGS_NLA_2007_Microcystin": [
        ("ds929_appendixes.xls", "https://pubs.usgs.gov/ds/0929/ds929_appendixes.xls"),
        ("ds929.pdf", "https://pubs.usgs.gov/ds/0929/ds929.pdf"),
    ],
}

DATA_GOV_PACKAGES = {
    "EPA_CyAN_NLA_Microcystin_Model": "data-for-satellites-predict-lakes-at-risk-from-cyanobacteria-and-microcystin-toxins",
    "EPA_20_Reservoirs_1987_2018": "1987-2018-cyanobacteria-and-water-quality-data-for-20-reservoirs",
}

FRANCE_API = (
    "https://www.data.gouv.fr/api/1/datasets/"
    "resultats-du-controle-sanitaire-des-eaux-de-baignade-naturelle-vis-a-vis-"
    "des-parametres-relatifs-aux-cyanobacteries-et-aux-cyanotoxines/"
)
ALBERTA_API = (
    "https://open.canada.ca/data/api/3/action/package_show"
    "?id=76a54113-1381-4824-b39c-2b32d2dfc652"
)
FIGSHARE_ARTICLE_API = "https://api.figshare.com/v2/articles/28507061"
FIGSHARE_FILES = [
    ("Pond Chemistry_metadata.pdf", 56354, "https://ndownloader.figshare.com/files/52789208"),
    ("Pond Chemistry_metadata.txt", 6362, "https://ndownloader.figshare.com/files/52789205"),
    ("Pond Chemistry_data.xlsx", 323385, "https://ndownloader.figshare.com/files/52789271"),
    ("Pond Chemistry_data.csv", 185955, "https://ndownloader.figshare.com/files/52793957"),
]
DRYAD_FILES_API = "https://datadryad.org/api/v2/versions/306247/files?per_page=100"


@dataclass
class Record:
    dataset: str
    source_url: str
    local_path: str
    status: str
    size_bytes: int = 0
    sha256: str = ""
    note: str = ""


records: list[Record] = []


def safe_name(value: str, fallback: str = "file") -> str:
    value = urllib.parse.unquote(value).strip().replace("\\", "_").replace("/", "_")
    value = re.sub(r"[<>:\"|?*\x00-\x1f]", "_", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value[:180] or fallback


def request(url: str, headers: dict[str, str] | None = None) -> urllib.request.Request:
    merged = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        merged.update(headers)
    return urllib.request.Request(url, headers=merged)


def fetch_bytes(url: str, attempts: int = 4) -> tuple[bytes, str]:
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request(url), timeout=90, context=SSL_CONTEXT) as response:
                return response.read(), response.geturl()
        except Exception as exc:  # network errors are reported in the manifest
            last = exc
            time.sleep(min(2 ** attempt, 8))
    raise RuntimeError(f"GET failed after {attempts} attempts: {url}: {last}")


def fetch_json(url: str) -> tuple[dict[str, Any], str]:
    body, final_url = fetch_bytes(url)
    return json.loads(body.decode("utf-8-sig")), final_url


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_record(dataset: str, url: str, path: Path, status: str, note: str = "") -> None:
    size = path.stat().st_size if path.exists() and path.is_file() else 0
    records.append(Record(dataset, url, str(path.relative_to(ROOT)), status, size, "", note))
    print(f"[{status:10}] {dataset}: {path.name} ({size:,} bytes)", flush=True)


def http_download(
    dataset: str,
    url: str,
    path: Path,
    expected: int | None = None,
    attempts: int = 5,
    timeout: int = 180,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0 and (expected is None or path.stat().st_size == expected):
        add_record(dataset, url, path, "existing")
        return

    part = path.with_name(path.name + ".part")
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if curl:
        offset = part.stat().st_size if part.exists() else 0
        command = [
            curl,
            "--location",
            "--fail",
            "--silent",
            "--show-error",
            "--retry",
            str(max(0, attempts - 1)),
            "--retry-delay",
            "2",
            "--retry-all-errors",
            "--connect-timeout",
            str(min(timeout, 60)),
            "--speed-limit",
            "1",
            "--speed-time",
            str(max(60, timeout)),
            "--user-agent",
            USER_AGENT,
        ]
        if offset:
            command.extend(["--continue-at", "-"])
        command.extend(["--output", str(part), url])
        try:
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
            if completed.returncode != 0:
                raise IOError(completed.stderr.strip() or f"curl exit code {completed.returncode}")
            if expected is not None and part.stat().st_size != expected:
                raise IOError(f"size mismatch: expected {expected}, got {part.stat().st_size}")
            os.replace(part, path)
            add_record(dataset, url, path, "downloaded")
        except Exception as exc:
            add_record(dataset, url, path, "failed", str(exc))
        return

    last: Exception | None = None
    for attempt in range(attempts):
        try:
            offset = part.stat().st_size if part.exists() else 0
            headers = {"Range": f"bytes={offset}-"} if offset else {}
            with urllib.request.urlopen(request(url, headers), timeout=timeout, context=SSL_CONTEXT) as response:
                response_status = getattr(response, "status", response.getcode())
                mode = "ab" if offset and response_status == 206 else "wb"
                with part.open(mode) as handle:
                    while True:
                        block = response.read(1024 * 1024)
                        if not block:
                            break
                        handle.write(block)
            if expected is not None and part.stat().st_size != expected:
                raise IOError(f"size mismatch: expected {expected}, got {part.stat().st_size}")
            os.replace(part, path)
            add_record(dataset, url, path, "downloaded")
            return
        except urllib.error.HTTPError as exc:
            if exc.code == 416 and part.exists() and (expected is None or part.stat().st_size == expected):
                os.replace(part, path)
                add_record(dataset, url, path, "downloaded", "completed partial file")
                return
            last = exc
        except Exception as exc:
            last = exc
        time.sleep(min(2 ** attempt, 16))
    add_record(dataset, url, path, "failed", str(last))


def sciencebase_id(doi: str) -> str:
    _, final_url = fetch_bytes(f"https://doi.org/{doi}")
    match = re.search(r"/item/([0-9a-f]{24})", final_url)
    if not match:
        raise ValueError(f"ScienceBase item ID not found after resolving {doi}: {final_url}")
    return match.group(1)


def sciencebase_items(item_id: str) -> Iterable[tuple[dict[str, Any], str]]:
    seen: set[str] = set()
    queue: list[tuple[str, str]] = [(item_id, "")]
    while queue:
        current, relative = queue.pop(0)
        if current in seen:
            continue
        seen.add(current)
        item, _ = fetch_json(f"https://www.sciencebase.gov/catalog/item/{current}?format=json")
        yield item, relative
        children, _ = fetch_json(
            "https://www.sciencebase.gov/catalog/items?"
            + urllib.parse.urlencode({"parentId": current, "format": "json", "max": 1000})
        )
        for child in children.get("items", []):
            child_id = str(child.get("id", ""))
            if not child_id:
                continue
            # Keep well below Windows MAX_PATH once nested under the dataset.
            title = safe_name(str(child.get("title") or child_id), child_id)[:80]
            queue.append((child_id, str(Path(relative) / f"{title}__{child_id[-6:]}")))


def download_sciencebase(dataset: str, doi: str) -> None:
    base = OUT / dataset
    try:
        item_id = sciencebase_id(doi)
        found = 0
        for item, relative in sciencebase_items(item_id):
            for entry in item.get("files", []):
                url = entry.get("downloadUri") or entry.get("url")
                if not url:
                    continue
                name = safe_name(str(entry.get("name") or Path(urllib.parse.urlparse(url).path).name))
                expected = entry.get("size")
                expected = int(expected) if str(expected).isdigit() else None
                if name == "Phytoplankton_Tally.xlsx" or (expected is not None and expected > 500_000_000):
                    path = base / relative / name
                    records.append(Record(dataset, str(url), str(path.relative_to(ROOT)), "failed", note=f"official endpoint reported {expected} bytes, ignored HTTP Range, and repeatedly reset the full transfer; skipped after failed 67 MiB attempt"))
                    print(f"[failed    ] {dataset}: {name} (non-resumable {expected:,}-byte file)", flush=True)
                    found += 1
                    continue
                http_download(dataset, str(url), base / relative / name, expected)
                found += 1
        if not found:
            records.append(Record(dataset, f"https://doi.org/{doi}", str(base.relative_to(ROOT)), "failed", note="ScienceBase item contained no downloadable files"))
    except Exception as exc:
        records.append(Record(dataset, f"https://doi.org/{doi}", str(base.relative_to(ROOT)), "failed", note=str(exc)))
        print(f"[failed    ] {dataset}: {exc}", flush=True)


def ftp_entries(ftp: ftplib.FTP, remote: str) -> list[tuple[str, dict[str, str]]]:
    entries: list[tuple[str, dict[str, str]]] = []
    try:
        for name, facts in ftp.mlsd(remote):
            if name not in {".", ".."}:
                entries.append((name, facts))
    except ftplib.error_perm:
        old = ftp.pwd()
        ftp.cwd(remote)
        names = [Path(name).name for name in ftp.nlst()]
        ftp.cwd(old)
        for name in names:
            child = remote.rstrip("/") + "/" + name
            try:
                ftp.cwd(child)
                entries.append((name, {"type": "dir"}))
                ftp.cwd(old)
            except ftplib.error_perm:
                entries.append((name, {"type": "file"}))
    return entries


def ftp_walk(ftp: ftplib.FTP, remote: str) -> Iterable[tuple[str, int | None]]:
    for name, facts in ftp_entries(ftp, remote):
        child = remote.rstrip("/") + "/" + name
        kind = facts.get("type")
        if kind == "dir":
            yield from ftp_walk(ftp, child)
        elif kind == "file":
            size = int(facts["size"]) if facts.get("size", "").isdigit() else None
            yield child, size
        elif not kind:
            try:
                old = ftp.pwd()
                ftp.cwd(child)
                ftp.cwd(old)
                yield from ftp_walk(ftp, child)
            except ftplib.error_perm:
                try:
                    size = ftp.size(child)
                except ftplib.all_errors:
                    size = None
                yield child, size


def ftp_download(
    dataset: str,
    ftp: ftplib.FTP,
    remote: str,
    local: Path,
    expected: int | None,
    record_failure: bool = True,
) -> bool:
    url = "ftp://ftp-oceans.ncei.noaa.gov" + remote
    local.parent.mkdir(parents=True, exist_ok=True)
    if local.exists() and local.stat().st_size > 0 and (expected is None or local.stat().st_size == expected):
        add_record(dataset, url, local, "existing")
        return True
    part = local.with_name(local.name + ".part")
    offset = part.stat().st_size if part.exists() else 0
    try:
        with part.open("ab" if offset else "wb") as handle:
            try:
                ftp.retrbinary(f"RETR {remote}", handle.write, blocksize=1024 * 1024, rest=offset or None)
            except ftplib.error_perm:
                if not offset:
                    raise
                handle.close()
                part.unlink(missing_ok=True)
                with part.open("wb") as fresh:
                    ftp.retrbinary(f"RETR {remote}", fresh.write, blocksize=1024 * 1024)
        if expected is not None and part.stat().st_size != expected:
            raise IOError(f"size mismatch: expected {expected}, got {part.stat().st_size}")
        os.replace(part, local)
        add_record(dataset, url, local, "downloaded")
        return True
    except Exception as exc:
        if record_failure:
            add_record(dataset, url, local, "failed", str(exc))
        return False


def download_ncei(dataset: str, accession: str) -> None:
    landing = f"https://www.ncei.noaa.gov/archive/accession/{accession}"
    try:
        curl = shutil.which("curl.exe") or shutil.which("curl")
        if curl:
            fetched = subprocess.run(
                [curl, "-4", "--insecure", "--location", "--fail", "--silent", "--show-error", "--retry", "3", "--connect-timeout", "30", "--max-time", "120", landing],
                capture_output=True,
                check=False,
            )
            if fetched.returncode != 0:
                raise IOError(fetched.stderr.decode("utf-8", "replace").strip() or f"curl exit code {fetched.returncode}")
            html = fetched.stdout
        else:
            html, _ = fetch_bytes(landing)
        urls = re.findall(rb"ftp://ftp-oceans\.ncei\.noaa\.gov(/[^\"'<>\s]+)", html)
        decoded = [urllib.parse.unquote(value.decode("utf-8")) for value in urls]
        roots = [value for value in decoded if f"/{accession}/" in value]
        if not roots:
            raise ValueError("official FTP archive URL not found on NCEI accession page")
        root = min(roots, key=len).split(f"/{accession}/", 1)[0] + f"/{accession}/"
        tasks: list[tuple[str, Path, int | None]] = []
        with ftplib.FTP("ftp-oceans.ncei.noaa.gov", timeout=180) as ftp:
            ftp.login()
            top = ftp_entries(ftp, root)
            version_dirs = [name for name, facts in top if facts.get("type") == "dir" and re.fullmatch(r"\d+(?:\.\d+)+", name)]
            selected: list[str] = []
            if version_dirs:
                selected.append(max(version_dirs, key=lambda value: tuple(int(x) for x in value.split("."))))
            selected.extend(name for name, facts in top if facts.get("type") == "file")
            if not selected:
                selected = [name for name, _ in top]
            base = OUT / dataset / accession
            for name in selected:
                remote = root.rstrip("/") + "/" + name
                facts = next((facts for entry, facts in top if entry == name), {})
                if facts.get("type") == "dir" or name in version_dirs:
                    for remote_file, size in ftp_walk(ftp, remote):
                        relative = remote_file[len(root):]
                        tasks.append((remote_file, base / Path(relative), size))
                else:
                    size = int(facts["size"]) if facts.get("size", "").isdigit() else None
                    tasks.append((remote, base / name, size))

        def download_batch(batch: list[tuple[str, Path, int | None]]) -> None:
            ftp_worker: ftplib.FTP | None = None
            try:
                for remote_file, local_file, size in batch:
                    for attempt in range(3):
                        if ftp_worker is None:
                            ftp_worker = ftplib.FTP("ftp-oceans.ncei.noaa.gov", timeout=180)
                            ftp_worker.login()
                        ok = ftp_download(
                            dataset,
                            ftp_worker,
                            remote_file,
                            local_file,
                            size,
                            record_failure=attempt == 2,
                        )
                        if ok:
                            break
                        try:
                            ftp_worker.close()
                        except ftplib.all_errors:
                            pass
                        ftp_worker = None
            finally:
                if ftp_worker is not None:
                    try:
                        ftp_worker.quit()
                    except ftplib.all_errors:
                        ftp_worker.close()

        worker_count = min(4, len(tasks) or 1)
        batches = [tasks[index::worker_count] for index in range(worker_count)]
        with ThreadPoolExecutor(max_workers=worker_count) as pool:
            futures = [pool.submit(download_batch, batch) for batch in batches if batch]
            for future in as_completed(futures):
                future.result()
    except Exception as exc:
        base = OUT / dataset / accession
        records.append(Record(dataset, landing, str(base.relative_to(ROOT)), "failed", note=str(exc)))
        print(f"[failed    ] {dataset}/{accession}: {exc}", flush=True)


def download_direct() -> None:
    for dataset, resources in DIRECT.items():
        for name, url in resources:
            http_download(dataset, url, OUT / dataset / name)


def download_figshare_georgia() -> None:
    """Inventory the four source files; direct access is blocked by the host WAF here."""
    dataset = "USDA_Georgia_Farm_Ponds"
    try:
        for raw_name, expected, url in FIGSHARE_FILES:
            name = safe_name(raw_name)
            path = OUT / dataset / name
            if path.exists() and path.stat().st_size == expected:
                add_record(dataset, str(url), path, "existing")
            else:
                records.append(Record(dataset, str(url), str(path.relative_to(ROOT)), "failed", note=f"official Figshare download host returned HTTP 403/WAF challenge; expected {expected} bytes"))
                print(f"[failed    ] {dataset}: {name} (Figshare WAF)", flush=True)
    except Exception as exc:
        records.append(Record(dataset, FIGSHARE_ARTICLE_API, str((OUT / dataset).relative_to(ROOT)), "failed", note=str(exc)))
        print(f"[failed    ] {dataset}: {exc}", flush=True)


def download_dryad() -> None:
    """Inventory Dryad files; the host currently rejects its own public downloads."""
    dataset = "Dryad_Uruguay_Rio_de_la_Plata"
    try:
        payload, _ = fetch_json(DRYAD_FILES_API)
        entries = payload.get("_embedded", {}).get("stash:files", [])
        for entry in entries:
            file_id_match = re.search(r"/files/(\d+)", str(entry.get("_links", {}).get("self", {}).get("href", "")))
            if not file_id_match:
                continue
            url = f"https://datadryad.org/downloads/file_stream/{file_id_match.group(1)}"
            name = safe_name(str(entry.get("path") or entry.get("id")))
            expected = int(entry["size"]) if str(entry.get("size", "")).isdigit() else None
            path = OUT / dataset / name
            if path.exists() and path.stat().st_size == expected:
                add_record(dataset, url, path, "existing")
            else:
                records.append(Record(dataset, url, str(path.relative_to(ROOT)), "failed", note=f"Dryad public download returned HTTP 403; aggregate ZIP returned an invalid AWS signature; expected {expected} bytes"))
                print(f"[failed    ] {dataset}: {name} (Dryad WAF)", flush=True)
    except Exception as exc:
        records.append(Record(dataset, DRYAD_FILES_API, str((OUT / dataset).relative_to(ROOT)), "failed", note=str(exc)))
        print(f"[failed    ] {dataset}: {exc}", flush=True)


def download_data_gov() -> None:
    for dataset, package_id in DATA_GOV_PACKAGES.items():
        api = "https://catalog.data.gov/api/3/action/package_show?" + urllib.parse.urlencode({"id": package_id})
        try:
            try:
                payload, _ = fetch_json(api)
                resources = payload.get("result", {}).get("resources", [])
            except Exception:
                # data.gov's 2026 catalog migration removed the CKAN endpoint,
                # while the dataset HTML still exposes the official EPA files.
                page = f"https://catalog.data.gov/dataset/{package_id}"
                body, _ = fetch_bytes(page)
                source = html.unescape(body.decode("utf-8", "replace"))
                urls = sorted(set(re.findall(r"https?://[^\"'<>\s]+?\.(?:csv|xlsx)(?:\?[^\"'<>\s]*)?", source, re.I)))
                resources = [
                    {"url": url, "name": Path(urllib.parse.urlparse(url).path).name, "format": Path(urllib.parse.urlparse(url).path).suffix.lstrip(".")}
                    for url in urls
                ]
            jobs: list[tuple[str, str, Path, int | None]] = []
            for index, resource in enumerate(resources, start=1):
                url = resource.get("url")
                if not url:
                    continue
                fmt = str(resource.get("format", "")).lower()
                if fmt in {"html", "web page", "landing page"}:
                    continue
                raw_name = resource.get("name") or Path(urllib.parse.urlparse(url).path).name or f"resource_{index}"
                name = safe_name(str(raw_name), f"resource_{index}")
                suffix = Path(urllib.parse.urlparse(url).path).suffix
                if not Path(name).suffix and suffix:
                    name += suffix
                expected = resource.get("size")
                expected = int(expected) if str(expected).isdigit() else None
                jobs.append((dataset, str(url), OUT / dataset / name, expected))
            with ThreadPoolExecutor(max_workers=min(6, len(jobs) or 1)) as pool:
                futures = [pool.submit(http_download, *job) for job in jobs]
                for future in as_completed(futures):
                    future.result()
        except Exception as exc:
            records.append(Record(dataset, api, str((OUT / dataset).relative_to(ROOT)), "failed", note=str(exc)))
            print(f"[failed    ] {dataset}: {exc}", flush=True)


def download_france() -> None:
    dataset = "France_Cyanobacteria_Cyanotoxins_2021_2025"
    try:
        payload, _ = fetch_json(FRANCE_API)
        jobs: list[tuple[str, str, Path, int | None]] = []
        for index, resource in enumerate(payload.get("resources", []), start=1):
            # The immutable static URL is more reliable for large files than
            # the API redirect endpoint and remains covered by the resource ID.
            url = resource.get("url") or resource.get("latest")
            if not url:
                continue
            title = safe_name(str(resource.get("title") or f"resource_{index}"), f"resource_{index}")
            if not Path(title).suffix:
                title += ".csv"
            expected = resource.get("filesize")
            expected = int(expected) if str(expected).isdigit() else None
            jobs.append((dataset, str(url), OUT / dataset / title, expected))
        with ThreadPoolExecutor(max_workers=min(7, len(jobs) or 1)) as pool:
            futures = [pool.submit(http_download, *job) for job in jobs]
            for future in as_completed(futures):
                future.result()
    except Exception as exc:
        records.append(Record(dataset, FRANCE_API, str((OUT / dataset).relative_to(ROOT)), "failed", note=str(exc)))
        print(f"[failed    ] {dataset}: {exc}", flush=True)


def download_alberta() -> None:
    dataset = "Alberta_Cyanobacteria_Bloom_Surveillance"
    try:
        payload, _ = fetch_json(ALBERTA_API)
        for index, resource in enumerate(payload.get("result", {}).get("resources", []), start=1):
            url = resource.get("url")
            fmt = str(resource.get("format", "")).lower()
            if not url or fmt in {"html", "web page", "landing page"}:
                continue
            name = safe_name(str(resource.get("name") or f"resource_{index}"), f"resource_{index}")
            suffix = Path(urllib.parse.urlparse(url).path).suffix
            if not Path(name).suffix:
                name += suffix or ("." + fmt if fmt else "")
            path = OUT / dataset / name
            if path.exists() and path.stat().st_size > 0:
                add_record(dataset, str(url), path, "existing")
            else:
                records.append(Record(dataset, str(url), str(path.relative_to(ROOT)), "failed", note="open.alberta.ca file host returned a Cloudflare challenge (HTTP 403)"))
                print(f"[failed    ] {dataset}: {name} (Cloudflare challenge)", flush=True)
    except Exception as exc:
        records.append(Record(dataset, ALBERTA_API, str((OUT / dataset).relative_to(ROOT)), "failed", note=str(exc)))
        print(f"[failed    ] {dataset}: {exc}", flush=True)


def validate_archives() -> None:
    for record in records:
        if record.status == "failed":
            continue
        path = ROOT / record.local_path
        if path.suffix.lower() in {".zip", ".xlsx", ".docx"}:
            try:
                with zipfile.ZipFile(path) as archive:
                    bad = archive.testzip()
                if bad:
                    record.status = "failed"
                    record.note = f"corrupt ZIP/Office member: {bad}"
            except zipfile.BadZipFile as exc:
                record.status = "failed"
                record.note = f"invalid ZIP/Office archive: {exc}"


def finalize_hashes() -> None:
    for index, record in enumerate(records, start=1):
        path = ROOT / record.local_path
        if record.status != "failed" and path.exists() and path.is_file():
            record.sha256 = sha256(path)
            record.size_bytes = path.stat().st_size
        if index % 25 == 0:
            print(f"[hash      ] {index}/{len(records)} files", flush=True)


def cleanup_stale_parts() -> None:
    """Remove only empty retry artifacts and the known invalid interrupted Dryad ZIP."""
    invalid_dryad = OUT / "Dryad_Uruguay_Rio_de_la_Plata" / "dryad_9w0vt4bpz.zip.part"
    for path in OUT.rglob("*.part"):
        if path.stat().st_size == 0 or path == invalid_dryad:
            path.unlink(missing_ok=True)


def inventory_existing_files() -> None:
    """Build a network-free, checksum-complete inventory of the final corpus."""
    for path in sorted(OUT.rglob("*")):
        if (
            not path.is_file()
            or MANIFEST_DIR in path.parents
            or path.suffix == ".part"
            or path.relative_to(OUT).parts[0].startswith("_")
        ):
            continue
        relative_to_out = path.relative_to(OUT)
        dataset = relative_to_out.parts[0] if len(relative_to_out.parts) > 1 else "external_raw"
        records.append(
            Record(
                dataset=dataset,
                source_url="see source-specific download manifest",
                local_path=str(path.relative_to(ROOT)),
                status="existing",
                size_bytes=path.stat().st_size,
                note="final local inventory",
            )
        )


def write_manifests(started: str, suffix: str = "") -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d")
    suffix = f"_{safe_name(suffix)}" if suffix else ""
    json_path = MANIFEST_DIR / f"full_download_manifest_{stamp}{suffix}.json"
    csv_path = MANIFEST_DIR / f"full_download_manifest_{stamp}{suffix}.csv"
    md_path = MANIFEST_DIR / f"full_download_report_{stamp}{suffix}.md"
    summary: dict[str, dict[str, int]] = {}
    for record in records:
        item = summary.setdefault(record.dataset, {"files": 0, "bytes": 0, "failed": 0, "downloaded": 0, "existing": 0})
        item["files"] += 1
        item["bytes"] += record.size_bytes
        item["failed"] += int(record.status == "failed")
        if record.status in {"downloaded", "existing"}:
            item[record.status] += 1
    payload = {
        "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "output_root": str(OUT),
        "summary": summary,
        "records": [asdict(record) for record in records],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(records[0]).keys()) if records else list(Record.__annotations__))
        writer.writeheader()
        writer.writerows(asdict(record) for record in records)
    total_bytes = sum(item["bytes"] for item in summary.values())
    failed = sum(item["failed"] for item in summary.values())
    lines = [
        "# 外部数据集全量下载报告",
        "",
        f"- 开始时间（UTC）：{started}",
        f"- 完成时间（UTC）：{payload['finished_utc']}",
        f"- 本次清单文件数：{len(records)}",
        f"- 清单总容量：{total_bytes / 1024 / 1024:.2f} MiB",
        f"- 失败记录：{failed}",
        "",
        "| 数据集 | 文件数 | 容量（MiB） | 新下载 | 已存在 | 失败 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for dataset, item in sorted(summary.items()):
        lines.append(
            f"| {dataset} | {item['files']} | {item['bytes'] / 1024 / 1024:.2f} | "
            f"{item['downloaded']} | {item['existing']} | {item['failed']} |"
        )
    failures = [record for record in records if record.status == "failed"]
    if failures:
        lines.extend(["", "## 失败项", ""])
        for record in failures:
            lines.append(f"- `{record.dataset}` — {record.source_url} — {record.note}")
    lines.extend([
        "",
        "## 说明",
        "",
        "- NCEI 按每个 accession 的最新版本目录下载，并保留根目录元数据 XML；不重复保存旧修订版本。",
        "- ZIP 文件已执行完整性测试；全部文件计算 SHA-256，详见同名 JSON/CSV 清单。",
        "- 原始数据不做内容改写，便于后续溯源、替换和重新训练。",
    ])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[manifest  ] {md_path}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-sciencebase", action="store_true")
    parser.add_argument("--skip-ncei", action="store_true")
    parser.add_argument("--manifest-suffix", default="")
    parser.add_argument("--ncei-france-only", action="store_true")
    parser.add_argument("--sciencebase-only", action="store_true")
    parser.add_argument("--pontchartrain-only", action="store_true")
    parser.add_argument("--inventory-only", action="store_true")
    parser.add_argument("--direct-only", action="store_true", help="retry non-ScienceBase, non-NCEI direct/catalog sources")
    parser.add_argument("--ncei-accession", help="download one NOAA NCEI accession")
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    OUT.mkdir(parents=True, exist_ok=True)

    if args.inventory_only:
        cleanup_stale_parts()
        inventory_existing_files()
        validate_archives()
        finalize_hashes()
        write_manifests(started, args.manifest_suffix or "inventory")
        print(f"Finished inventory: {len(records)} files", flush=True)
        return 0

    if args.direct_only:
        download_direct()
        download_figshare_georgia()
        download_dryad()
        download_data_gov()
        download_alberta()
        cleanup_stale_parts()
        validate_archives()
        finalize_hashes()
        write_manifests(started, args.manifest_suffix or "direct_retry")
        failures = sum(record.status == "failed" for record in records)
        print(f"Finished direct retry: {len(records)} records, {failures} failures", flush=True)
        return 1 if failures else 0

    if args.ncei_accession:
        dataset = "NOAA_GLERL_Lake_Erie_2012_present"
        for attempt in range(3):
            record_start = len(records)
            download_ncei(dataset, args.ncei_accession)
            new_records = records[record_start:]
            if not any(record.status == "failed" for record in new_records):
                break
            if attempt < 2:
                del records[record_start:]
                print(f"[retry     ] {dataset}/{args.ncei_accession}: attempt {attempt + 2}/3", flush=True)
                time.sleep(2)
        cleanup_stale_parts()
        validate_archives()
        finalize_hashes()
        write_manifests(started, args.manifest_suffix or "ncei_retry")
        failures = sum(record.status == "failed" for record in records)
        print(f"Finished NCEI accession retry: {len(records)} records, {failures} failures", flush=True)
        return 1 if failures else 0

    if not args.ncei_france_only and not args.sciencebase_only:
        download_direct()
        download_figshare_georgia()
        download_dryad()
        download_data_gov()
        download_alberta()
    if args.sciencebase_only:
        for dataset, doi in SCIENCEBASE.items():
            download_sciencebase(dataset, doi)
    elif not args.ncei_france_only and not args.skip_sciencebase:
        for dataset, doi in SCIENCEBASE.items():
            download_sciencebase(dataset, doi)
    if not args.sciencebase_only and not args.skip_ncei:
        for dataset, accessions in NCEI_ACCESSIONS.items():
            if args.pontchartrain_only and dataset != "NCEI_Lake_Pontchartrain_2020":
                continue
            for accession in accessions:
                for attempt in range(3):
                    record_start = len(records)
                    download_ncei(dataset, accession)
                    new_records = records[record_start:]
                    if not any(record.status == "failed" for record in new_records):
                        break
                    if attempt < 2:
                        del records[record_start:]
                        print(f"[retry     ] {dataset}/{accession}: attempt {attempt + 2}/3", flush=True)
                        time.sleep(2)
    # This source is bandwidth-limited from China; run its annual files in
    # parallel after higher-priority paired field datasets are secured.
    if not args.sciencebase_only:
        download_france()

    cleanup_stale_parts()
    validate_archives()
    finalize_hashes()
    write_manifests(started, args.manifest_suffix)
    failures = sum(record.status == "failed" for record in records)
    print(f"Finished: {len(records)} records, {failures} failures", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
