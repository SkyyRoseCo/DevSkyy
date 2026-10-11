"""
scripts.flux_lora.upload — Upload a dataset zip to HuggingFace Hub.

Public API
----------
show_upload_stopandshow(zip_path, repo_id) -> None
upload_zip(zip_path, repo_id, *, private, path_in_repo, confirmed) -> str

Security contract (mirrors trainer.py)
---------------------------------------
confirmed=False → raise RequiresConfirmationError BEFORE any network call.
Token is loaded at runtime via load_dotenv; never hardcoded.
Returned URL validated with config.is_https_url before returning.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import HfApi, hf_hub_url

from scripts.flux_lora import RequiresConfirmationError
from scripts.flux_lora.config import is_https_url

# Repo-root .env.hf, wherever the checkout lives (scripts/flux_lora/upload.py → parents[2]).
_ENV_HF = str(Path(__file__).resolve().parents[2] / ".env.hf")
_TOKEN_VARS = ("HF_TOKEN", "HUGGINGFACE_API_TOKEN")


# ---------------------------------------------------------------------------
# Token helper (isolated so tests can patch it cleanly)
# ---------------------------------------------------------------------------


def _get_hf_token() -> str:
    """
    Load HF token from .env.hf at runtime (never hardcoded).

    Reads HF_TOKEN then HUGGINGFACE_API_TOKEN from the environment,
    loading the repository's .env.hf first if it exists.

    Raises
    ------
    RuntimeError
        If no token is found in the environment after loading.
    """
    load_dotenv(_ENV_HF, override=False)
    for var in _TOKEN_VARS:
        token = os.environ.get(var, "").strip()
        if token:
            return token
    raise RuntimeError(
        f"HuggingFace token not found. Set {_TOKEN_VARS[0]} or {_TOKEN_VARS[1]} "
        f"in the environment or in {_ENV_HF}."
    )


# ---------------------------------------------------------------------------
# STOP-AND-SHOW helper
# ---------------------------------------------------------------------------


def show_upload_stopandshow(zip_path: str | Path, repo_id: str) -> None:
    """
    Print a STOP-AND-SHOW confirmation block before an upload.

    Parameters
    ----------
    zip_path:
        Path to the zip file that will be uploaded.
    repo_id:
        HuggingFace dataset repo ID (e.g. "skyyrose/skyyrose-lora-dataset").
    """
    p = Path(zip_path)
    try:
        size_bytes = p.stat().st_size
        size_str = f"{size_bytes:,} bytes"
    except FileNotFoundError:
        size_str = "(file not found)"

    sep = "=" * 60
    print(sep)
    print("STOP — Confirm before proceeding:")
    print()
    print("  Action     : HuggingFace dataset upload")
    print(f"  File       : {p.resolve()}")
    print(f"  Size       : {size_str}")
    print(f"  Repo       : {repo_id}")
    print("  Visibility : public")
    print()
    print("  Proceed? [y/N]")
    print(sep)


# ---------------------------------------------------------------------------
# Main upload function
# ---------------------------------------------------------------------------


def upload_zip(
    zip_path: str | Path,
    repo_id: str,
    *,
    private: bool = False,
    path_in_repo: str | None = None,
    confirmed: bool = False,
) -> str:
    """
    Upload a dataset zip to a HuggingFace Hub dataset repository.

    Parameters
    ----------
    zip_path:
        Local path to the zip file to upload.
    repo_id:
        HuggingFace repo ID (e.g. "skyyrose/skyyrose-lora-dataset").
    private:
        Whether to create the repo as private (default False).
    path_in_repo:
        Filename to use inside the repo (defaults to zip file's name).
    confirmed:
        Must be True to proceed. If False, raises RequiresConfirmationError
        BEFORE any network call or token access.

    Returns
    -------
    str
        Public HTTPS resolve URL for the uploaded file.

    Raises
    ------
    RequiresConfirmationError
        If confirmed=False (raised before any network call).
    RuntimeError
        If HF token is missing.
    ValueError
        If the resolved URL is not a valid https URL.
    """
    # SECURITY GATE — must be first, before token load or any network call
    if not confirmed:
        raise RequiresConfirmationError(
            "upload_zip requires explicit confirmation. "
            "Call show_upload_stopandshow(), get 'y' from the user, "
            "then re-call with confirmed=True."
        )

    token = _get_hf_token()

    p = Path(zip_path).resolve()
    filename = path_in_repo or p.name

    api = HfApi()
    api.create_repo(
        repo_id=repo_id,
        repo_type="dataset",
        exist_ok=True,
        private=private,
        token=token,
    )

    api.upload_file(
        path_or_fileobj=str(p),
        path_in_repo=filename,
        repo_id=repo_id,
        repo_type="dataset",
        token=token,
    )

    resolve_url = hf_hub_url(
        repo_id=repo_id,
        filename=filename,
        repo_type="dataset",
    )

    if not is_https_url(resolve_url):
        raise ValueError(
            f"HuggingFace returned a non-https URL: {resolve_url!r}. "
            "Refusing to return an insecure URL."
        )

    return resolve_url
