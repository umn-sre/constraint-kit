# SRE Metric and Dimension Naming Standards

Hierarchical names let the Splunk Analytics tool group metrics into a
browsable tree, and let `mstats` wildcard a whole family at once
(`metric_name="iam.shibboleth.ldap.*"`). Names that don't follow the
hierarchy still ingest fine — they just land as unnavigable leaves that
nobody finds, which is how metrics end up unused.

## Metric name format

```
[CESI/ITAC unit].[app or namespace].[intermediate names].[entity][UnitOfMeasure]
```

Rules:

- Start at the highest level (the CESI/ITAC unit), then get more specific.
- Dot (`.`) is the path separator. Use it consistently.
- Character set: `[a-zA-Z0-9.]`. No spaces, colons, slashes, or hyphens.
- Underscores are technically delimiters too, and the Analytics tool will
  group on them — but prefer dots for hierarchy and camelCase for
  readability within a segment, so the tree has one meaning of "level".
- Add the entity being measured, then the measurement, then concatenate the
  unit of measure onto the end.

## Unit and measurement suffixes

Suffix the measurement so a consumer knows what they're charting without
asking:

| Kind | Suffix |
| --- | --- |
| Count of things in this interval | `Count` |
| Accumulated / monotonic counter | `Total` |
| Statistical aggregate | `Avg`, `Max`, `Min`, `StdDev` |
| Units | `Sec`, `Ms`, `Pct`, `Kb`, `Mb`, `Bytes`, `PerSec`, `PerMin` |

Suffixes compose: `responseAvgSec` is the average response time in seconds,
`memorySizeKbAvg` is average memory in KB.

## Worked examples

Identity's Shibboleth service:

```
iam.shibboleth.ldap.okCount
iam.shibboleth.ldap.failedCount
iam.shibboleth.ldap.responseAvgSec
iam.shibboleth.duo.count
iam.shibboleth.duo.responseAvgSec
```

Note what this buys: `iam.shibboleth.*` charts the whole service,
`iam.shibboleth.ldap.*` charts one dependency, and the `Count`/`Sec`
suffixes mean the tree self-documents.

## Dimensions

Dimensions are string labels used to filter, group, and aggregate metrics —
and they're how ITSI matches data to entities. The test for whether
something is a dimension: **if doing arithmetic on its values would mean
something, it's a measurement, not a dimension.** `queueDepth` is a
measurement. `queueName` is a dimension.

Naming:

- Character set `[a-zA-Z0-9]`; avoid `-` and `_` (vendors will use them
  anyway — don't be surprised, just don't add more).
- camelCase for multi-word names.
- Keep the set stable. Dimension churn fragments historical series.

Commonly used dimension names — reuse these rather than inventing synonyms,
so cross-service dashboards can group on the same key:

```
entity  host  instance  environment  role  campus  building  floor
room    rack  cloudProvider  cloudRegion  containerId
```

`entity` matters most: it's what ITSI keys entity discovery on, so it
should hold the stable identifier of the thing being measured.

## Cardinality

Every distinct combination of dimension values creates a new time series.
Dimensions with unbounded values — request IDs, user IDs, full URLs, raw
timestamps, exception messages — will blow up cardinality and make queries
crawl. If a value is unique per event, it belongs in an event log, not in a
metric dimension.

## Index and source

- Indexes are created by SRE and follow `umn_[cesiUnit]`.
- `source` should identify the emitter (e.g. `ent:psoft:cdcJob`) so
  troubleshooting can tell which script wrote which series.
- `sourcetype` for JSON metric POSTs is conventionally `httpevent`.
- `source="summaryDataForItsi"` is reserved: it's the magic value that
  routes on-prem Splunk data to ITSI. Don't use it for direct HEC sends.
