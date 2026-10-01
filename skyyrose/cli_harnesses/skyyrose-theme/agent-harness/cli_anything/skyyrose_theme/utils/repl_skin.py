"""
REPL skin for cli-anything-skyyrose-theme.

Rose-gold / dark theme matching the SkyyRose brand palette.
Uses ANSI escape codes only (no external color library dependency).
"""

from __future__ import annotations

import shutil
from typing import Any

# ---------------------------------------------------------------------------
# ANSI escape codes
# ---------------------------------------------------------------------------

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"

# Rose gold palette
_ROSE_GOLD = "\033[38;2;183;110;121m"  # #B76E79
_GOLD = "\033[38;2;212;175;55m"  # #D4AF37
_CRIMSON = "\033[38;2;220;20;60m"  # #DC143C
_SILVER = "\033[38;2;192;192;192m"  # #C0C0C0
_SOFT_PURPLE = "\033[38;2;180;140;200m"  # muted purple accent
_WHITE = "\033[38;2;240;240;240m"
_DIM_WHITE = "\033[38;2;160;160;160m"

# Status colors
_GREEN = "\033[38;2;80;200;120m"
_YELLOW = "\033[38;2;255;200;60m"
_RED = "\033[38;2;220;60;60m"
_CYAN = "\033[38;2;80;200;220m"

# Box-drawing characters
_TL = "╭"
_TR = "╮"
_BL = "╰"
_BR = "╯"
_H = "─"
_V = "│"
_CROSS = "┼"

# Icon
_ICON = f"{_ROSE_GOLD}{_BOLD}◆{_RESET}"
_BULLET = f"{_ROSE_GOLD}•{_RESET}"


# ---------------------------------------------------------------------------
# ReplSkin
# ---------------------------------------------------------------------------


class ReplSkin:
    """Renders themed output for the skyyrose-theme REPL."""

    def __init__(self, software: str = "skyyrose-theme") -> None:
        self.software = software
        self._width = min(shutil.get_terminal_size().columns, 80)

    def _hr(self, char: str = _H) -> str:
        return char * self._width

    def print_banner(self, version: str = "") -> None:
        """Print the startup banner."""
        ver_str = f"  v{version}" if version else ""
        title = f"SkyyRose Theme CLI{ver_str}"
        tagline = ""

        print()
        print(f"  {_ROSE_GOLD}{_BOLD}{_TL}{self._hr()}{_TR}{_RESET}")
        pad = (self._width - len(title)) // 2
        print(
            f"  {_ROSE_GOLD}{_V}{_RESET}"
            + " " * pad
            + f"{_BOLD}{_WHITE}{title}{_RESET}"
            + " " * (self._width - pad - len(title))
            + f"{_ROSE_GOLD}{_V}{_RESET}"
        )
        pad2 = (self._width - len(tagline)) // 2
        print(
            f"  {_ROSE_GOLD}{_V}{_RESET}"
            + " " * pad2
            + f"{_DIM_WHITE}{_DIM}{tagline}{_RESET}"
            + " " * (self._width - pad2 - len(tagline))
            + f"{_ROSE_GOLD}{_V}{_RESET}"
        )
        print(f"  {_ROSE_GOLD}{_BOLD}{_BL}{self._hr()}{_BR}{_RESET}")
        print(
            f"\n  {_DIM_WHITE}Type {_ROSE_GOLD}help{_DIM_WHITE} for commands, {_ROSE_GOLD}exit{_DIM_WHITE} to quit.{_RESET}\n"
        )

    def prompt(self) -> str:
        """Return the REPL prompt string."""
        return f"{_ROSE_GOLD}{_BOLD}◆ skyyrose{_RESET} {_DIM_WHITE}›{_RESET} "

    def success(self, message: str) -> None:
        print(f"  {_GREEN}{_BOLD}✓{_RESET}  {message}")

    def error(self, message: str) -> None:
        print(f"  {_RED}{_BOLD}✗{_RESET}  {_RED}{message}{_RESET}")

    def warning(self, message: str) -> None:
        print(f"  {_YELLOW}{_BOLD}⚠{_RESET}  {_YELLOW}{message}{_RESET}")

    def info(self, message: str) -> None:
        print(f"  {_CYAN}{_BOLD}ℹ{_RESET}  {message}")

    def status(self, key: str, value: str, ok: bool | None = None) -> None:
        """Print a key: value status line with optional pass/fail indicator."""
        if ok is True:
            indicator = f"{_GREEN}✓{_RESET}"
        elif ok is False:
            indicator = f"{_RED}✗{_RESET}"
        else:
            indicator = f"{_DIM_WHITE}·{_RESET}"
        print(f"  {indicator}  {_DIM_WHITE}{key:<24}{_RESET}{value}")

    def table(self, rows: list[dict[str, Any]], headers: list[str] | None = None) -> None:
        """Print a simple table from a list of dicts."""
        if not rows:
            self.info("No results.")
            return

        cols = headers or list(rows[0].keys())
        widths = {c: len(c) for c in cols}
        for row in rows:
            for c in cols:
                widths[c] = max(widths[c], len(str(row.get(c, ""))))

        sep = "  " + "  ".join(_H * (widths[c] + 2) for c in cols)
        header_line = "  " + "  ".join(f"{_BOLD}{_ROSE_GOLD}{c:<{widths[c]}}{_RESET}" for c in cols)

        print()
        print(header_line)
        print(sep)
        for row in rows:
            line = "  " + "  ".join(
                f"{_WHITE}{str(row.get(c, '')):<{widths[c]}}{_RESET}" for c in cols
            )
            print(line)
        print()

    def print_manifest(
        self, manifest: dict[str, Any], title: str = "STOP — Confirm before proceeding"
    ) -> None:
        """Print a STOP-AND-SHOW confirmation manifest."""
        print()
        print(f"  {_CRIMSON}{_BOLD}{'━' * (self._width - 2)}{_RESET}")
        print(f"  {_CRIMSON}{_BOLD}{title}{_RESET}")
        print(f"  {_CRIMSON}{_BOLD}{'━' * (self._width - 2)}{_RESET}")
        for k, v in manifest.items():
            print(f"  {_DIM_WHITE}{k:<20}{_RESET}{_WHITE}{v}{_RESET}")
        print(f"  {_CRIMSON}{_BOLD}{'━' * (self._width - 2)}{_RESET}")
        print()

    def print_goodbye(self) -> None:
        print(f"\n  {_DIM_WHITE}Goodbye. \n")
