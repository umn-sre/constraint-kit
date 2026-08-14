#!/usr/bin/env python3
"""Send Splunk-format metrics to UMN SRE's ITSI HEC, and validate names
against SRE's naming standards.

Stdlib only, so it drops into any project (containers, Databricks jobs,
GitHub Actions steps, OCI VMs) without adding a dependency.

Library use:

    from itsi_hec import MetricSender

    sender = MetricSender(url=ITSI_URL, token=os.environ["ITSI_HEC_TOKEN"],
                          source="ent:psoft:cdcJob")
    sender.add(metrics={"ents.psoft.cdc.lagSec": 3.2},
               dimensions={"environment": "prd", "entity": "psoft-cdc-01"})
    sender.flush()

CLI use:

    python itsi_hec.py validate --names iam.shibboleth.ldap.okCount
    python itsi_hec.py validate --file metric_names.txt
    python itsi_hec.py send --payload-file batch.json --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request

ITSI_HEC_URL = "https://http-inputs.itsi-umn.splunkcloud.com:443/services/collector"
EDGE_TST_URL = "https://sre-itsi-dev-edge-01.oit.umn.edu:8088/services/collector"
EDGE_PRD_URL = "https://sre-splunk-prd-edge-01.oit.umn.edu:8088/services/collector"

# Ceilings are 2GB (cloud) / ~5MB (on-prem). Chunk far below both: a retry
# should be cheap and a partial failure should lose little.
MAX_CHUNK_BYTES = 512 * 1024

UNIT_SUFFIXES = (
    "Count", "Total", "Avg", "Max", "Min", "StdDev",
    "Sec", "Ms", "Pct", "Kb", "Mb", "Bytes", "PerSec", "PerMin",
)

_METRIC_LEGAL = re.compile(r"^[a-zA-Z0-9.]+$")
_DIM_LEGAL = re.compile(r"^[a-zA-Z0-9]+$")

# Dimension names that are really measurements hiding in a label.
_MEASUREMENT_WORDS = (
    "count", "total", "avg", "sum", "size", "sec", "ms", "pct",
    "bytes", "rate", "latency", "duration",
)

# Dimension names with unbounded value spaces — cardinality hazards.
_HIGH_CARDINALITY = (
    "requestid", "traceid", "sessionid", "userid", "uuid", "guid",
    "url", "path", "query", "message", "timestamp", "email",
)


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def validate_metric_name(name: str) -> list[tuple[str, str]]:
    """Return [(level, message)] where level is 'error' or 'warn'.

    Errors mean Splunk will misbehave or the name is unusable. Warnings mean
    it will ingest but won't fit the tree other services live in.
    """
    out: list[tuple[str, str]] = []
    if not name:
        return [("error", "empty metric name")]
    if not _METRIC_LEGAL.match(name):
        bad = sorted({c for c in name if not re.match(r"[a-zA-Z0-9.]", c)})
        out.append(("error", f"illegal character(s) {bad!r}; allowed set is [a-zA-Z0-9.]"))
    if name.startswith(".") or name.endswith("."):
        out.append(("error", "leading or trailing dot"))
    if ".." in name:
        out.append(("error", "empty path segment ('..')"))
    if "_" in name:
        out.append(("warn", "underscore used; prefer dots for hierarchy and camelCase within a segment"))

    segments = [s for s in name.split(".") if s]
    if len(segments) < 3:
        out.append(("warn", "fewer than 3 segments; expected [unit].[app].[entity][Unit] at minimum"))
    if segments:
        leaf = segments[-1]
        if not leaf.endswith(UNIT_SUFFIXES):
            out.append(("warn", f"leaf '{leaf}' has no unit/measurement suffix "
                                f"(e.g. {', '.join(UNIT_SUFFIXES[:6])}...)"))
        if leaf and leaf[0].isupper():
            out.append(("warn", f"leaf '{leaf}' starts uppercase; use camelCase starting lowercase"))
    if name != name.strip():
        out.append(("error", "leading or trailing whitespace"))
    return out


def validate_dimension_name(name: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if not name:
        return [("error", "empty dimension name")]
    if not _DIM_LEGAL.match(name):
        out.append(("warn", f"'{name}' outside recommended set [a-zA-Z0-9]; "
                            "hyphens/underscores are discouraged (vendors use them anyway)"))
    low = name.lower()
    if any(low.endswith(w) or low == w for w in _MEASUREMENT_WORDS):
        out.append(("warn", f"'{name}' reads like a measurement; if arithmetic on its "
                            "values would mean something, it belongs in metric_name, not fields"))
    if any(h in low for h in _HIGH_CARDINALITY):
        out.append(("warn", f"'{name}' looks unbounded; high-cardinality dimensions "
                            "fragment series and slow queries — send it as an event instead"))
    return out


def report(names: list[str], dimensions: list[str]) -> int:
    """Print a human-readable review. Returns count of errors."""
    errors = 0
    for label, items, fn in (("Metric", names, validate_metric_name),
                             ("Dimension", dimensions, validate_dimension_name)):
        for item in items:
            findings = fn(item)
            if not findings:
                print(f"  OK    {label.lower()}: {item}")
                continue
            for level, msg in findings:
                if level == "error":
                    errors += 1
                print(f"  {level.upper():5} {label.lower()}: {item}\n        {msg}")
    return errors


# --------------------------------------------------------------------------
# Sending
# --------------------------------------------------------------------------

class MetricSender:
    """Accumulates metric payloads and POSTs them to a HEC endpoint.

    flush() does not raise by default: telemetry must never take down the
    service it measures. It returns True on success and logs otherwise.
    """

    def __init__(self, url: str = ITSI_HEC_URL, token: str | None = None,
                 source: str = "custom:metrics", sourcetype: str = "httpevent",
                 host: str | None = None, timeout: float = 10.0,
                 retries: int = 2, raise_on_error: bool = False,
                 verify_tls: bool = True):
        self.url = url
        self.token = token or os.environ.get("ITSI_HEC_TOKEN", "")
        self.source = source
        self.sourcetype = sourcetype
        self.host = host or socket.gethostname()
        self.timeout = timeout
        self.retries = retries
        self.raise_on_error = raise_on_error
        self.verify_tls = verify_tls
        self.payloads: list[dict] = []

    def add(self, metrics: dict[str, float], dimensions: dict[str, str] | None = None,
            timestamp: float | None = None, host: str | None = None) -> dict:
        """Queue one payload. All metrics here share these dimensions and time.

        Measurements with different dimensions need separate add() calls.
        """
        fields: dict[str, object] = {}
        for k, v in (dimensions or {}).items():
            fields[k] = str(v)
        for name, value in metrics.items():
            if value is None:
                continue
            # Cast explicitly: a numeric string ingests silently and is useless.
            fields[f"metric_name:{name}"] = float(value)
        payload = {
            "time": int(timestamp if timestamp is not None else time.time()),
            "event": "metric",
            "source": self.source,
            "sourcetype": self.sourcetype,
            "host": host or self.host,
            "fields": fields,
        }
        self.payloads.append(payload)
        return payload

    def _chunks(self) -> list[list[dict]]:
        chunks, current, size = [], [], 0
        for p in self.payloads:
            encoded = len(json.dumps(p).encode("utf-8")) + 1
            if current and size + encoded > MAX_CHUNK_BYTES:
                chunks.append(current)
                current, size = [], 0
            current.append(p)
            size += encoded
        if current:
            chunks.append(current)
        return chunks

    def _post(self, body: list[dict]) -> None:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            self.url, data=data, method="POST",
            headers={"Authorization": f"Splunk {self.token}",
                     "Content-Type": "application/json"},
        )
        ctx = None if self.verify_tls else ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as resp:
            resp.read()

    def flush(self) -> bool:
        """Send and clear the queue. Returns False if anything failed."""
        if not self.payloads:
            return True
        if not self.token:
            self._problem("no HEC token set (ITSI_HEC_TOKEN); nothing sent")
            self.payloads.clear()
            return False
        ok = True
        for chunk in self._chunks():
            for attempt in range(self.retries + 1):
                try:
                    self._post(chunk)
                    break
                except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
                    if attempt == self.retries:
                        ok = False
                        self._problem(f"send failed after {attempt + 1} attempts: {exc}")
                    else:
                        time.sleep(2 ** attempt)
        self.payloads.clear()
        return ok

    def _problem(self, msg: str) -> None:
        if self.raise_on_error:
            raise RuntimeError(f"itsi_hec: {msg}")
        print(f"itsi_hec: {msg}", file=sys.stderr)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.flush()
        return False


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _read_names(args) -> list[str]:
    names = list(args.names or [])
    if args.file:
        with open(args.file) as fh:
            names += [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    return names


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="check metric/dimension names against SRE standards")
    v.add_argument("--names", nargs="*", default=[])
    v.add_argument("--dimensions", nargs="*", default=[])
    v.add_argument("--file", help="file of metric names, one per line")

    s = sub.add_parser("send", help="POST a JSON payload file (or stdin) to a HEC endpoint")
    s.add_argument("--payload-file", help="JSON list of payloads; '-' for stdin")
    s.add_argument("--url", default=ITSI_HEC_URL)
    s.add_argument("--token-env", default="ITSI_HEC_TOKEN")
    s.add_argument("--source", default="custom:metrics")
    s.add_argument("--dry-run", action="store_true", help="print the body instead of sending")

    args = parser.parse_args(argv)

    if args.cmd == "validate":
        names = _read_names(args)
        if not names and not args.dimensions:
            print("nothing to validate", file=sys.stderr)
            return 2
        errors = report(names, args.dimensions)
        print(f"\n{len(names)} metric name(s), {len(args.dimensions)} dimension(s); {errors} error(s).")
        return 1 if errors else 0

    # send
    raw = sys.stdin.read() if args.payload_file in (None, "-") else open(args.payload_file).read()
    body = json.loads(raw)
    if isinstance(body, dict):
        body = [body]

    if args.dry_run:
        print(json.dumps(body, indent=2))
        print(f"\n-- dry run: would POST {len(body)} payload(s) to {args.url}", file=sys.stderr)
        return 0

    sender = MetricSender(url=args.url, token=os.environ.get(args.token_env, ""),
                          source=args.source)
    sender.payloads = body
    return 0 if sender.flush() else 1


if __name__ == "__main__":
    raise SystemExit(main())
