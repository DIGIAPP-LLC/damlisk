import json

from damlisk.output.finding import Finding


def render_text(findings: list[Finding]) -> str:
    if not findings:
        return "No findings."
    lines = [f"[{f.impact.value}] {f.check} {f.where}\n    {f.message}" for f in findings]
    return "\n".join([*lines, f"{len(findings)} finding(s)."])


def render_json(findings: list[Finding], pretty: bool = False) -> str:
    data = {"success": True, "findings": [f.to_json() for f in findings]}
    return json.dumps(data, indent=2 if pretty else None)
