"""Search scholarly metadata and download a curated open-access evidence set.

The generated files are reproducible research artefacts. The script deliberately
keeps broad search results separate from the curated set used in the model plan.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import quote

import requests


ROOT = Path(__file__).resolve().parents[2]
REF_ROOT = ROOT / "model_redo_v2" / "references"
PAPER_ROOT = REF_ROOT / "papers"
SEARCH_JSON = REF_ROOT / "literature_search_results.json"
SEARCH_CSV = REF_ROOT / "literature_search_results.csv"
MANIFEST_JSON = REF_ROOT / "paper_download_manifest.json"
MANIFEST_CSV = REF_ROOT / "paper_download_manifest.csv"

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": "IGEM-DryLab-literature-audit/1.0 (academic model planning)",
        "Accept": "application/json,text/html,application/pdf,*/*",
    }
)


SEARCH_QUERIES = [
    "tabular foundation model regression TabICL TabPFN",
    "tabular machine learning benchmark beyond IID temporal group shift",
    "TabM parameter efficient ensembling tabular deep learning",
    "TabR retrieval augmented tabular deep learning",
    "RealMLP better by default tabular data",
    "TALENT tabular deep learning benchmark",
    "gradient boosted trees versus deep learning tabular data",
    "probabilistic regression NGBoost tabular",
    "conformalized quantile regression",
    "conformal prediction covariate shift",
    "distributionally robust optimization group shift",
    "WILDS in the wild distribution shifts benchmark",
    "interval censored regression machine learning",
    "left censored environmental concentration Tobit model",
    "microcystin concentration prediction machine learning water quality",
    "microcystin LR environmental predictors",
    "cyanotoxin forecasting machine learning lake",
    "cyanobacterial bloom prediction systematic review freshwater",
    "harmful algal blooms inland waters 2024",
    "microcystin remote sensing water quality prediction",
]


CURATED_PAPERS = [
    {
        "key": "tabiclv2_2026",
        "title": "TabICLv2: A better, faster, scalable, and open tabular foundation model",
        "year": 2026,
        "status": "ICML 2026 / arXiv",
        "url": "https://arxiv.org/abs/2602.11139",
        "pdf_url": "https://arxiv.org/pdf/2602.11139",
        "relevance": "Open high-performance tabular foundation model; regression, missing values and quantile fine-tuning challenger.",
    },
    {
        "key": "tabicl_2025",
        "title": "TabICL: A Tabular Foundation Model for In-Context Learning on Large Data",
        "year": 2025,
        "status": "ICML 2025",
        "url": "https://arxiv.org/abs/2502.05564",
        "pdf_url": "https://arxiv.org/pdf/2502.05564",
        "relevance": "Foundation-model baseline for medium-sized tabular regression.",
    },
    {
        "key": "beyond_iid_2026",
        "title": "Beyond IID: How General Are Tabular Foundation Models, Really?",
        "year": 2026,
        "status": "arXiv preprint",
        "url": "https://arxiv.org/abs/2606.30410",
        "pdf_url": "https://arxiv.org/pdf/2606.30410",
        "relevance": "Direct evidence for temporal/grouped validation and limits of IID leaderboard conclusions.",
    },
    {
        "key": "tabarena_2025",
        "title": "TabArena: A Living Benchmark for Machine Learning on Tabular Data",
        "year": 2025,
        "status": "NeurIPS 2025 Datasets & Benchmarks",
        "url": "https://arxiv.org/abs/2506.16791",
        "pdf_url": "https://arxiv.org/pdf/2506.16791",
        "relevance": "Broad modern comparison of tuned trees, neural models and tabular foundation models.",
    },
    {
        "key": "tabm_2025",
        "title": "TabM: Advancing Tabular Deep Learning with Parameter-Efficient Ensembling",
        "year": 2025,
        "status": "ICLR 2025",
        "url": "https://arxiv.org/abs/2410.24210",
        "pdf_url": "https://arxiv.org/pdf/2410.24210",
        "relevance": "Efficient trainable deep ensemble candidate for multi-task and custom censor-aware losses.",
    },
    {
        "key": "tabr_2024",
        "title": "TabR: Tabular Deep Learning Meets Nearest Neighbors",
        "year": 2024,
        "status": "ICLR 2024",
        "url": "https://arxiv.org/abs/2307.14338",
        "pdf_url": "https://arxiv.org/pdf/2307.14338",
        "relevance": "Retrieval model candidate; also highlights leakage risk when nearby site/time records cross folds.",
    },
    {
        "key": "realmlp_2024",
        "title": "Better by default: Strong pre-tuned MLPs and boosted trees on tabular data",
        "year": 2024,
        "status": "NeurIPS 2024",
        "url": "https://arxiv.org/abs/2407.04491",
        "pdf_url": "https://arxiv.org/pdf/2407.04491",
        "relevance": "Strong reproducible MLP and tree defaults, useful as a no-HPO benchmark.",
    },
    {
        "key": "talent_2024",
        "title": "A Closer Look at Deep Learning Methods on Tabular Datasets",
        "year": 2024,
        "status": "arXiv / TALENT benchmark",
        "url": "https://arxiv.org/abs/2407.00956",
        "pdf_url": "https://arxiv.org/pdf/2407.00956",
        "relevance": "Large empirical audit of tabular deep-learning methods and preprocessing choices.",
    },
    {
        "key": "tabpfn_nature_2025",
        "title": "Accurate predictions on small data with a tabular foundation model",
        "year": 2025,
        "status": "Nature",
        "url": "https://doi.org/10.1038/s41586-024-08328-6",
        "pdf_url": "https://www.nature.com/articles/s41586-024-08328-6.pdf",
        "relevance": "High-level evidence for prior-data fitted networks; practical use requires license and access review.",
    },
    {
        "key": "tabpfn3_2026",
        "title": "TabPFN-3: Technical Report",
        "year": 2026,
        "status": "arXiv technical report",
        "url": "https://arxiv.org/abs/2605.13986",
        "pdf_url": "https://arxiv.org/pdf/2605.13986",
        "relevance": "Current large-scale TabPFN generation; research comparison only until weight licensing and authenticated access are accepted.",
    },
    {
        "key": "tree_vs_dl_2022",
        "title": "Why do tree-based models still outperform deep learning on typical tabular data?",
        "year": 2022,
        "status": "NeurIPS 2022",
        "url": "https://arxiv.org/abs/2207.08815",
        "pdf_url": "https://arxiv.org/pdf/2207.08815",
        "relevance": "Supports retaining tuned tree baselines for irregular heterogeneous environmental tables.",
    },
    {
        "key": "ft_transformer_2021",
        "title": "Revisiting Deep Learning Models for Tabular Data",
        "year": 2021,
        "status": "NeurIPS 2021",
        "url": "https://arxiv.org/abs/2106.11959",
        "pdf_url": "https://arxiv.org/pdf/2106.11959",
        "relevance": "Reference transformer baseline; now primarily a controlled comparator.",
    },
    {
        "key": "ngboost_2020",
        "title": "NGBoost: Natural Gradient Boosting for Probabilistic Prediction",
        "year": 2020,
        "status": "ICML 2020",
        "url": "https://proceedings.mlr.press/v119/duan20a.html",
        "pdf_url": "https://proceedings.mlr.press/v119/duan20a/duan20a.pdf",
        "relevance": "Distributional-regression benchmark for calibrated concentration uncertainty.",
    },
    {
        "key": "cqr_2019",
        "title": "Conformalized Quantile Regression",
        "year": 2019,
        "status": "NeurIPS 2019",
        "url": "https://arxiv.org/abs/1905.03222",
        "pdf_url": "https://arxiv.org/pdf/1905.03222",
        "relevance": "Finite-sample marginal uncertainty intervals around heterogeneous quantile models.",
    },
    {
        "key": "conformal_covariate_shift_2019",
        "title": "Conformal Prediction Under Covariate Shift",
        "year": 2019,
        "status": "NeurIPS 2019",
        "url": "https://arxiv.org/abs/1904.06019",
        "pdf_url": "https://arxiv.org/pdf/1904.06019",
        "relevance": "Basis for uncertainty calibration when deployment covariates differ from training.",
    },
    {
        "key": "group_dro_2020",
        "title": "Distributionally Robust Neural Networks for Group Shifts: On the Importance of Regularization for Worst-Case Generalization",
        "year": 2020,
        "status": "ICLR 2020",
        "url": "https://arxiv.org/abs/1911.08731",
        "pdf_url": "https://arxiv.org/pdf/1911.08731",
        "relevance": "Worst-source training objective for unbalanced datasets and geographic groups.",
    },
    {
        "key": "wilds_2021",
        "title": "WILDS: A Benchmark of in-the-Wild Distribution Shifts",
        "year": 2021,
        "status": "ICML 2021",
        "url": "https://arxiv.org/abs/2012.07421",
        "pdf_url": "https://arxiv.org/pdf/2012.07421",
        "relevance": "Evaluation design for realistic source, geographic and temporal distribution shifts.",
    },
    {
        "key": "inland_habs_2024",
        "title": "Harmful algal blooms in inland waters",
        "year": 2024,
        "status": "Nature Reviews Earth & Environment",
        "url": "https://doi.org/10.1038/s43017-024-00578-2",
        "pdf_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11849997/pdf/nihms-2041063.pdf",
        "relevance": "Domain review connecting nutrients, climate, hydrology, monitoring and toxin risk.",
    },
    {
        "key": "microcystin_multisource_2019",
        "title": "Combining national and state data improves predictions of microcystin concentration",
        "year": 2019,
        "status": "Harmful Algae",
        "url": "https://doi.org/10.1016/j.hal.2019.02.009",
        "pdf_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7147962/pdf/nihms-1585874.pdf",
        "relevance": "Direct domain evidence that combining data sources can improve toxin models while requiring source-aware evaluation.",
    },
    {
        "key": "microcystin_rf_2025",
        "title": "Investigating the Relationship Between Microcystin Concentrations and Water Quality Parameters in Three Agricultural Irrigation Ponds Using Random Forest",
        "year": 2025,
        "status": "Water",
        "url": "https://doi.org/10.3390/w17162361",
        "pdf_url": "https://www.mdpi.com/2073-4441/17/16/2361/pdf",
        "relevance": "Recent task-specific tree-model study; useful for feature hypotheses, not a universal architecture ranking.",
    },
    {
        "key": "global_bloom_frequency_2025",
        "title": "Global elevation of algal bloom frequency in large lakes over the past two decades",
        "year": 2025,
        "status": "National Science Review",
        "url": "https://doi.org/10.1093/nsr/nwaf011",
        "pdf_url": "https://academic.oup.com/nsr/article-pdf/12/6/nwaf011/63103531/nwaf011.pdf",
        "relevance": "Recent global remote-sensing evidence; supports satellite/seasonal context as a separate feature panel.",
    },
]


def inverted_abstract_to_text(inv: dict | None) -> str:
    if not inv:
        return ""
    positions: list[tuple[int, str]] = []
    for word, indices in inv.items():
        positions.extend((int(i), word) for i in indices)
    return " ".join(word for _, word in sorted(positions))


def search_openalex(query: str, per_page: int = 12) -> list[dict]:
    params = {
        "search": query,
        "per-page": per_page,
        "select": "id,doi,title,publication_year,publication_date,cited_by_count,primary_location,best_oa_location,open_access,authorships,abstract_inverted_index,type",
    }
    response = SESSION.get("https://api.openalex.org/works", params=params, timeout=60)
    response.raise_for_status()
    rows = []
    for rank, work in enumerate(response.json().get("results", []), start=1):
        primary = work.get("primary_location") or {}
        oa = work.get("best_oa_location") or {}
        authors = [a.get("author", {}).get("display_name") for a in work.get("authorships", [])]
        rows.append(
            {
                "query": query,
                "rank": rank,
                "openalex_id": work.get("id"),
                "doi": work.get("doi"),
                "title": work.get("title"),
                "publication_year": work.get("publication_year"),
                "publication_date": work.get("publication_date"),
                "cited_by_count": work.get("cited_by_count"),
                "type": work.get("type"),
                "authors": "; ".join(a for a in authors if a),
                "landing_page_url": primary.get("landing_page_url") or oa.get("landing_page_url"),
                "pdf_url": oa.get("pdf_url") or primary.get("pdf_url"),
                "is_open_access": (work.get("open_access") or {}).get("is_oa"),
                "abstract": inverted_abstract_to_text(work.get("abstract_inverted_index")),
            }
        )
    return rows


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")


def download_pdf(paper: dict) -> dict:
    output = PAPER_ROOT / f"{paper['year']}_{safe_name(paper['key'])}.pdf"
    result = dict(paper)
    result.update({"file": str(output.relative_to(ROOT)).replace("\\", "/"), "downloaded": False})
    try:
        if output.exists() and output.read_bytes()[:4] == b"%PDF":
            payload = output.read_bytes()
            result.update(
                {
                    "downloaded": True,
                    "status_detail": "existing_valid_pdf",
                    "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }
            )
            return result
        response = SESSION.get(paper["pdf_url"], timeout=120, allow_redirects=True)
        response.raise_for_status()
        payload = response.content
        content_type = response.headers.get("content-type", "")
        if not payload.startswith(b"%PDF"):
            raise ValueError(f"not a PDF: content-type={content_type}, prefix={payload[:20]!r}")
        output.write_bytes(payload)
        result.update(
            {
                "downloaded": True,
                "status_detail": "downloaded",
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "resolved_url": response.url,
            }
        )
    except Exception as exc:  # keep the search reproducible even when a host blocks automation
        result.update({"status_detail": f"failed: {type(exc).__name__}: {exc}", "bytes": 0, "sha256": ""})
    return result


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    REF_ROOT.mkdir(parents=True, exist_ok=True)
    PAPER_ROOT.mkdir(parents=True, exist_ok=True)

    search_rows: list[dict] = []
    for index, query in enumerate(SEARCH_QUERIES, start=1):
        print(f"[{index}/{len(SEARCH_QUERIES)}] OpenAlex: {query}")
        try:
            search_rows.extend(search_openalex(query))
        except Exception as exc:
            search_rows.append({"query": query, "rank": 0, "error": f"{type(exc).__name__}: {exc}"})
        time.sleep(0.15)

    SEARCH_JSON.write_text(json.dumps(search_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(SEARCH_CSV, search_rows)

    manifest = []
    for index, paper in enumerate(CURATED_PAPERS, start=1):
        print(f"[{index}/{len(CURATED_PAPERS)}] PDF: {paper['title']}")
        manifest.append(download_pdf(paper))
        time.sleep(0.5)
    MANIFEST_JSON.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(MANIFEST_CSV, manifest)
    success = sum(bool(row["downloaded"]) for row in manifest)
    print(f"Search rows: {len(search_rows)}; PDFs: {success}/{len(manifest)}")


if __name__ == "__main__":
    main()
