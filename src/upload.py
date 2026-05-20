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


def ftp_upload_all(file_paths: list[str], platform: str = "adobe-stock") -> tuple[int, int]:
    """
    FTP upload supporting adobe-stock and freepik platforms.
    For freepik, it implements secure FTPS with standard FTP fallback.
    """
    cfg = get_config()
    
    if platform == "adobe-stock":
        adobe_cfg = cfg.adobe
        console.print(f"[yellow]⚠ FTP upload skipped for Adobe Stock: {adobe_cfg.ftp.host} is deprecated.[/yellow]")
        console.print("[yellow]  Use --submit flag for browser-based file upload + metadata fill.[/yellow]")
        return 0, len(file_paths)

    elif platform == "freepik":
        ftp_cfg = cfg.freepik.ftp
        if not ftp_cfg.host or not ftp_cfg.username or not ftp_cfg.password:
            console.print("[yellow]⚠ Freepik FTP credentials not configured. Skipping upload.[/yellow]")
            return 0, len(file_paths)

        console.print(f"\n[bold]📤 Uploading {len(file_paths)} files to Freepik FTP ({ftp_cfg.host})...[/bold]")
        
        success = 0
        failed = 0
        
        try:
            # Try FTPS (Explicit TLS) first for security
            try:
                ftp = ftplib.FTP_TLS()
                ftp.connect(ftp_cfg.host, ftp_cfg.port, timeout=30)
                ftp.login(ftp_cfg.username, ftp_cfg.password)
                ftp.prot_p()  # Secure transfer channel
                console.print(f"  [green]✓[/green] Connected via FTPS (Secure)")
            except Exception as e:
                console.print(f"  [dim]FTPS connection failed ({e}), trying standard FTP...[/dim]")
                ftp = ftplib.FTP()
                ftp.connect(ftp_cfg.host, ftp_cfg.port, timeout=30)
                ftp.login(ftp_cfg.username, ftp_cfg.password)
                console.print(f"  [green]✓[/green] Connected via standard FTP")
                
            for fp in file_paths:
                path = Path(fp)
                if not path.exists():
                    console.print(f"  [red]✗[/red] File not found: {fp}")
                    failed += 1
                    continue
                
                console.print(f"  Uploading {path.name}...")
                with open(path, "rb") as f:
                    ftp.storbinary(f"STOR {path.name}", f)
                console.print(f"  [green]✓[/green] Uploaded successfully")
                success += 1
                
            ftp.quit()
        except Exception as e:
            console.print(f"  [red]✗ FTP error: {e}[/red]")
            failed += len(file_paths) - success
            
        console.print(f"[bold green]✓ Freepik FTP upload complete: {success} succeeded, {failed} failed[/bold green]")
        return success, len(file_paths)
        
    return 0, len(file_paths)
