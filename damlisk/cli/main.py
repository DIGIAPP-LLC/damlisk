import sys
from pathlib import Path

import click
from loguru import logger

from damlisk import __version__
from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.detectors.all_detectors import DETECTORS
from damlisk.exceptions import DamliskException
from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex
from damlisk.output.finding import Finding, Impact
from damlisk.output.formats import render_json, render_text

_TRACEBACK = click.option(
    "--traceback", is_flag=True, help="Show a Python traceback on error instead of a short message."
)
_DAR_ARG = click.argument("dar_path", type=click.Path(exists=True, path_type=Path))
_LEVELS = [i.name.lower() for i in Impact]


def _split(value: str | None) -> set[str]:
    return {item.strip() for item in (value or "").split(",") if item.strip()}


def select_detectors(detect: str | None, exclude: str | None) -> list[type[AbstractDetector]]:
    wanted, skipped = _split(detect), _split(exclude)
    unknown = (wanted | skipped) - {d.ARGUMENT for d in DETECTORS}
    if unknown:
        raise click.BadParameter(f"unknown detector(s): {', '.join(sorted(unknown))}")
    return [d for d in DETECTORS if d.ARGUMENT in (wanted or {d.ARGUMENT}) - skipped]


def _load(dar_path: Path, traceback: bool) -> Dar:
    try:
        return Dar.load(dar_path)
    except DamliskException as err:
        if traceback:
            raise
        logger.error(str(err))
        sys.exit(2)


def _fails(findings: list[Finding], fail_on: str) -> bool:
    return fail_on != "none" and any(
        f.impact.rank <= Impact[fail_on.upper()].rank for f in findings
    )


@click.group(invoke_without_command=True)
@click.version_option(__version__, "--version", "-V", prog_name="damlisk")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Damlisk: static analyzer for Daml-LF packages (.dar)."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command("scan")
@_DAR_ARG
@click.option("--detect", default=None, help="Comma-separated detectors to run (default: all).")
@click.option("--exclude", default=None, help="Comma-separated detectors to skip.")
@click.option("--json", "as_json", is_flag=True, help="Output findings as JSON.")
@click.option(
    "--pretty-json", "pretty", is_flag=True, help="Output JSON in pretty (indented) format."
)
@click.option(
    "--fail-on",
    type=click.Choice([*_LEVELS, "none"]),
    default="none",
    show_default=True,
    help="Exit with code 1 if a finding of this impact or higher is reported.",
)
@_TRACEBACK
def scan_cmd(
    dar_path: Path,
    detect: str | None,
    exclude: str | None,
    as_json: bool,
    pretty: bool,
    fail_on: str,
    traceback: bool,
) -> None:
    """Run detectors over the main package of DAR_PATH."""
    detectors = select_detectors(detect, exclude)
    index = PackageIndex(_load(dar_path, traceback))
    findings = [f for det in detectors for f in det(index).detect()]
    click.echo(render_json(findings, pretty) if as_json or pretty else render_text(findings))
    if _fails(findings, fail_on):
        sys.exit(1)


@cli.command("info")
@_DAR_ARG
@_TRACEBACK
def info_cmd(dar_path: Path, traceback: bool) -> None:
    """Show packages, Daml-LF versions and declarations of DAR_PATH."""
    dar = _load(dar_path, traceback)
    main, mods = dar.main, dar.main.modules
    rows = (
        ("main", f"{main.name} {main.version} (LF {main.lf_ver}) {main.pkg_id}"),
        ("sdk", dar.sdk or "unknown"),
        ("modules", len(mods)),
        ("templates", sum(len(m.templates) for m in mods)),
        ("choices", sum(len(t.choices) for m in mods for t in m.templates)),
        ("interfaces", sum(len(m.interfaces) for m in mods)),
        ("interface instances", len(main.extras.implements)),
        ("exceptions", len(main.extras.exceptions)),
        ("values", sum(len(m.values) for m in mods)),
        ("packages", len(dar.packages)),
    )
    for label, value in rows:
        click.echo(f"{label}: {value}")
    for pkg in sorted(dar.packages, key=lambda p: (p.name, p.version)):
        click.echo(f"  {pkg.name} {pkg.version} (LF {pkg.lf_ver})")


@cli.command("list-detectors")
def list_detectors_cmd() -> None:
    """List available detectors."""
    for d in DETECTORS:
        click.echo(f"{d.ARGUMENT:<24} {d.IMPACT.value:<14} {d.CONFIDENCE.value:<8} {d.HELP}")
