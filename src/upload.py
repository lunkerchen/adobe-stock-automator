"""
FTP 上傳模組 (Stub)

備註：Adobe Stock 的 FTP 上傳服務已不活躍。
目前建議使用 Browser 模式（--submit）直接透過網頁上傳。

如果未來 Adobe 恢復 FTP 服務，修改 host 即可。
"""

from __future__ import annotations

import ftplib
from pathlib import Path

from rich.console import Console

from .config import get_config

console = Console()


def ftp_upload_all(file_paths: list[str]) -> tuple[int, int]:
    """
    FTP upload stub.
    FTP contributor upload has been deprecated by Adobe.
    Use --submit flag for browser-based upload instead.
    """
    cfg = get_config().adobe
    console.print(f"[yellow]⚠ FTP upload skipped: {cfg.ftp.host} is not available.[/yellow]")
    console.print("[yellow]  Use --submit flag for browser-based file upload + metadata fill.[/yellow]")
    return 0, len(file_paths)
