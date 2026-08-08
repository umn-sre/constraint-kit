# UMN Information Security Policy Standards (16 Appendices)

Source: https://policy.umn.edu/it/securedata (Appendix section)

These are the 16 categories that MUST appear as numbered top-level sections in the compliance output document, in this order:

| # | Code | Standard Name | Policy URL |
|---|------|---------------|------------|
| 1 | AAAM | Authentication, Access, and Account Management | https://policy.umn.edu/it/securedata-appaaam |
| 2 | CM | Change Management | https://policy.umn.edu/it/securedata-appf |
| 3 | DCS | Data Center Security | https://policy.umn.edu/it/securedata-appg |
| 4 | DSBR | Data Storage and Backup & Recovery | https://policy.umn.edu/it/securedata-appdsbr |
| 5 | E | Encryption | https://policy.umn.edu/it/securedata-appi |
| 6 | SA | Information Security Awareness, Education and Training (a.k.a. ISAET) | https://policy.umn.edu/it/securedata-appl |
| 7 | LM | Log Management | https://policy.umn.edu/it/securedata-appm |
| 8 | MS | Media Sanitization | https://policy.umn.edu/it/securedata-appo |
| 9 | NF | Network Firewall | https://policy.umn.edu/it/securedata-appq |
| 10 | NM | Network Management | https://policy.umn.edu/it/securedata-appp |
| 11 | SPM | Security Patch Management | https://policy.umn.edu/it/securedata-apps |
| 12 | SD | Software Development | https://policy.umn.edu/it/securedata-appsd |
| 13 | SDM | Systems and Device Management | https://policy.umn.edu/it/securedata-appsdm |
| 14 | TVM | Technical Vulnerability Management | https://policy.umn.edu/it/securedata-appt |
| 15 | VSM | Vendor/Supplier Management | https://policy.umn.edu/it/securedata-appw |
| 16 | VPM | Virus/Malware Protection Management | https://policy.umn.edu/it/securedata-appvpm |

## Data Classification Levels

Source: https://policy.umn.edu/it/dataclassification

| Classification | Description |
|---|---|
| **Public** | Available to the public upon request. Minimal harm risk from loss. |
| **Private-Restricted** | Not public; available within the institution to those with a business need (e.g., student grades, FERPA-covered records). |
| **Private-Highly Restricted** | Accessible only to those with a legitimate need to know. Loss can cause significant personal, institutional, or other harm (e.g., SSN, medical, HIPAA, PCI). |

## Security Levels

| Level | Applies To |
|---|---|
| **Low** | Public or non-sensitive data; integrity/availability are primary concerns. |
| **Medium** | Private-Restricted data; loss could cause personal or institutional harm. |
| **High** | Private-Highly Restricted data; damage reasonably expected from a breach. |

## Multi-User vs Single-User

Compliance documents typically include a user-scope qualifier alongside classification (e.g., "Medium Risk, Multi-User Application"). Determine this from the project:
- **Single-user**: Only one identity ever interacts with the system (rare; typically a personal tool).
- **Multi-user**: Multiple distinct identities (people, services, teams) interact with the system. Most cloud applications are multi-user.

When in doubt, ask the user — or default to multi-user with a note.

## Fetching Each Standard

When generating a compliance review, fetch each appendix to enumerate its requirement IDs (e.g., `AAAM.A.01`, `CM.A.02`). Each appendix lists requirements grouped by sub-categories (A, B, C, ...) with numeric sub-IDs. Use the URLs above with WebFetch.

Tip: fetch multiple appendices in parallel where possible to keep latency low.
