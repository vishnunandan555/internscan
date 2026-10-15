"""Terminal formatting and dashboard display for the scraper."""
import os
import sys
import time

# Auto-detect color support: enabled if tty or FORCE_COLOR is set, disabled if NO_COLOR
COLOR_ENABLED = (
    (sys.stdout.isatty() or os.environ.get("FORCE_COLOR"))
    and not os.environ.get("NO_COLOR")
)


def _c(code: str, text: str) -> str:
    if not COLOR_ENABLED:
        return text
    return f"\033[{code}m{text}\033[0m"


def green(t: str) -> str:
    return _c("32;1", t)


def red(t: str) -> str:
    return _c("31;1", t)


def yellow(t: str) -> str:
    return _c("33;1", t)


def cyan(t: str) -> str:
    return _c("36;1", t)


def magenta(t: str) -> str:
    return _c("35;1", t)


def bold(t: str) -> str:
    return _c("1", t)


def dim(t: str) -> str:
    return _c("2", t)


def status_ok(name: str, duration: float, n_postings: int, n_interns: int, n_india: int) -> str:
    badge = green("[OK]  ")
    dur = dim(f"({duration:4.1f}s)")
    details = f"{n_postings:>4} postings, {n_interns:>2} interns, {bold(str(n_india))} roles"
    padded_name = f"{name:<24}"
    return f"{badge} {bold(padded_name)} {dur} {details}"


def status_fail(name: str, duration: float, err: str) -> str:
    badge = red("[FAIL]")
    dur = dim(f"({duration:4.1f}s)")
    short_err = str(err).split("\n")[0][:60]
    padded_name = f"{name:<24}"
    return f"{badge} {bold(padded_name)} {dur} {red(short_err)}"


def status_skip(name: str, reason: str) -> str:
    badge = yellow("[SKIP]")
    padded_name = f"{name:<24}"
    return f"{badge} {bold(padded_name)} {dim(reason)}"


def print_dashboard(total_duration: float, succeeded: set, failed: dict,
                    added: list, closed: list, reopened: list,
                    all_india_jobs: list, is_dry_run: bool = False):
    width = 68
    print("\n" + bold("=" * width))
    title = "SCRAPER RUN COMPLETE"
    if is_dry_run:
        title += " (DRY RUN — NO FILES MODIFIED)"
    print(bold(cyan(f"  {title}")) + dim(f" ({total_duration:.1f}s)"))
    print(bold("=" * width))

    n_succ = len(succeeded)
    n_fail = len(failed)
    total_cos = n_succ + n_fail

    succ_text = green(f"{n_succ} succeeded")
    fail_text = red(f"{n_fail} failed") if n_fail else dim("0 failed")
    print(f" Companies:  {total_cos} total | {succ_text} | {fail_text}")

    live_text = bold(str(len(all_india_jobs)))
    add_text = green(f"+{len(added)} new")
    close_text = red(f"-{len(closed)} closed")
    reopen_text = yellow(f"~{len(reopened)} reopened") if reopened else dim("0 reopened")
    print(f" Listings:   {live_text} active verified | {add_text} | {close_text} | {reopen_text}")
    print(bold("-" * width))

    if added:
        print(bold(green("\n  New Listings Discovered:")))
        for j in added:
            loc = j.get("city_tag") or "India"
            cat = f"[{j.get('category', 'Tech')}]"
            comp_str = f"{j['company']:<18}"
            print(f"   + {bold(comp_str)} {j['title']} {cyan(loc)} {dim(cat)}")
            print(f"     {dim(j.get('url', ''))}")

    if is_dry_run and all_india_jobs:
        print(bold(cyan("\n  Active Listings Preview (First 10):")))
        for j in all_india_jobs[:10]:
            loc = getattr(j, "city_tag", None) or "India"
            cat = f"[{getattr(j, 'category', 'Tech')}]"
            comp_str = f"{j.company:<18}"
            print(f"   • {bold(comp_str)} {j.title} {cyan(loc)} {dim(cat)}")
            print(f"     {dim(j.url)}")
        if len(all_india_jobs) > 10:
            print(dim(f"   ... and {len(all_india_jobs) - 10} more listings."))

    if failed:
        print(bold(red("\n  Failed Companies:")))
        for name, err in sorted(failed.items()):
            short_err = str(err).split("\n")[0][:70]
            name_str = f"{name:<18}"
            print(f"   × {bold(name_str)} {red(short_err)}")

    print(bold("=" * width) + "\n")
