# When Direct HEC Isn't Possible

Read this only after establishing that the service can't POST metrics
itself. Each of these paths trades freshness or robustness for reach, so
pick the highest one on the list that actually fits.

## 1. Edge Processor

Use when the data exists but doesn't match SRE's naming standards and you
can't change the producer — vendor appliances, third-party exporters,
existing UMN collection sources, a Splunk add-on's output, or events that
need converting to metrics.

The service filters at the source and sends to the Edge Processor; SRE
builds the pipeline (in collaboration with the service team) that reshapes
names and dimensions to standard before forwarding to Splunk Cloud. Endpoints
and token requirements are in `endpoints.md`.

Cost of this path: the transformation lives in a pipeline SRE maintains
rather than in the service's own code, so a change to the producer's output
means a pipeline change request, not a pull request.

## 2. Splunk add-ons

Use for OS- and platform-level metrics that a supported add-on already
collects. Add-ons give automatic entity discovery and merging, plus a set
of predefined KPIs with configurable thresholds — real value you'd
otherwise hand-build.

Supported today: Unix and Linux, Microsoft Windows, F5 Big-IP, Citrix
Netscaler, Microsoft SQL Server, Oracle Database, NetApp Data ONTAP, EMC
VNX, Microsoft Hyper-V, VMware, Apache Web Server, Microsoft IIS, Tomcat,
IBM WebSphere Application Server.

Collection rides on the on-prem Universal Forwarder infrastructure operated
by UIS Log Management (ULM). Where the add-on isn't installed yet, it needs
an SRE backlog item — check before promising a timeline. Other Splunkbase
add-ons are evaluated case by case.

Do not hand-build OS metrics that an add-on already provides; the add-on's
entity model is what ITSI expects.

## 3. On-prem Splunk → ITSI via `mcollect`

Use when the data is already in on-prem Splunk Enterprise and only needs
shuttling to ITSI.

Build a scheduled report that extracts fields, treats measurements as
floats and labels as string dimensions, assigns a hierarchical
`metric_prefix`, projects only the needed fields with `| table`, and calls
`| mcollect`. The `source` value is the routing key — with
`source="summaryDataForItsi"`, the Splunk input tier forwards the data to
ITSI within seconds.

```
[your spl search]
| eval metric_prefix="mcs.<service>."
| table _time entity metric_prefix <metrics> <dimensions>
| mcollect split=true source="summaryDataForItsi" index="umn_<cesiUnit>"
    prefix_field=metric_prefix entity <dimensions>
```

Requirements and gotchas:

- The index must exist in **both** on-prem and Splunk Cloud. SRE requests
  the on-prem index from ULM (Splunk ULM) as needed.
- Arriving in Splunk Cloud, the sourcetype will be `mcollect_stash`.
- Note the trailing dot on `metric_prefix` — without it, names concatenate
  wrong.
- Only fields named after `prefix_field=` are treated as dimensions;
  everything else in the table is treated as a measurement.
- Schedule no more often than every 5 minutes. The data is stale by
  definition when it lands.

## 4. Event data to the Edge Processor

Last resort. Events are converted to metrics downstream, which means both
the scheduling delay above *and* fragility: application logging changes
break the extraction silently. Treat any log-derived metric as technical
debt with a plan to replace it with a direct emit.
