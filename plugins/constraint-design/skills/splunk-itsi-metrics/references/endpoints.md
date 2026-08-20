# Endpoints, Payload Shape, and Tokens

## ITSI HEC endpoints (the default target)

| Use | URL |
| --- | --- |
| Multiple data lines (batched JSON — use this) | `https://http-inputs.itsi-umn.splunkcloud.com:443/services/collector` |
| Single event | `https://http-inputs.itsi-umn.splunkcloud.com:443/services/collector/event` |
| Raw data | `https://http-inputs.itsi-umn.splunkcloud.com:443/services/collector/raw` |

Post a JSON list of payloads to `/services/collector`. `/raw` skips JSON
parsing and is the wrong endpoint for structured metrics — posting there is
a common cause of "my data never showed up."

## Edge Processor endpoints

Used when data needs reshaping before it reaches Splunk Cloud (see
`alternate-paths.md`). SRE builds the pipelines; SRE also adds the HEC token
to the Edge Processor. Token auth is required here too.

| | TST | PRD |
| --- | --- | --- |
| JSON events | `https://sre-itsi-dev-edge-01.oit.umn.edu:8088/services/collector` | `https://sre-splunk-prd-edge-01.oit.umn.edu:8088/services/collector` |
| Raw | `https://sre-itsi-dev-edge-01.oit.umn.edu:8088/services/collector/raw` | `https://sre-splunk-prd-edge-01.oit.umn.edu:8088/services/collector/raw` |

Develop against TST first. It's the same shape, and a naming mistake caught
there doesn't leave junk series in the production metric tree.

## Payload shape

```json
[
  {
    "time": 1755100000,
    "event": "metric",
    "source": "ent:psoft:cdcJob",
    "sourcetype": "httpevent",
    "host": "psoft-cdc-01.oit.umn.edu",
    "fields": {
      "environment": "prd",
      "role": "extractor",
      "entity": "psoft-cdc-01",
      "metric_name:ents.psoft.cdc.rowsProcessedTotal": 14820,
      "metric_name:ents.psoft.cdc.lagSec": 3.2
    }
  }
]
```

Key points:

- `"event": "metric"` is what tells Splunk this is metric data.
- Measurements are `fields` keys prefixed `metric_name:`, with **numeric**
  values. A number sent as a string ingests without error and is useless —
  cast to float at the source.
- Dimensions are plain string keys in the same `fields` object.
- One payload can carry many measurements as long as they share the same
  dimensions and timestamp. Measurements with different dimensions need
  separate payloads in the same list.
- `time` is epoch seconds for when the measurement was taken.

## Auth

```
Authorization: Splunk <HEC token>
```

The literal word `Splunk`, not `Bearer`. Tokens and indexes are created by
SRE and shared with the service team when access is granted; the team does
not self-provision them.

Keep tokens out of code, images, and tfvars. Read from an environment
variable populated by the project's existing secret store — GitHub Actions
secrets, Azure Key Vault, OCI Vault, or a Databricks secret scope. Rotate
the same way you'd rotate any write credential to a shared platform, and
scope one token per emitting service where possible so a leak can be
revoked without taking down everyone else's telemetry.

TLS verification stays on. If a cert error appears, fix the trust store
rather than disabling verification.

## Size limits

| Target | Max per request |
| --- | --- |
| Splunk Cloud HEC | 2 GB |
| On-prem Splunk | ~5 MB |

These are ceilings, not targets. Batch to a few hundred KB — big enough to
amortize connection cost, small enough that a retry is cheap and a partial
failure loses little.

## Verification

1. [Analytics Workspace](https://itsi.itsi-umn.splunkcloud.com/en-US/app/search/analytics_workspace)
2. Metrics → **+ Add new filter** → pick the index → **Apply**
3. Expand the CESI unit node down to the metric
4. Split by a dimension to confirm dimensions arrived as labels

Failure checklist when nothing appears: token not authorized for the index;
value wasn't numeric; illegal character in the name; posted to `/raw`;
`event` wasn't `"metric"`; or the timestamp was far enough off that the data
landed outside the time window you're looking at.
