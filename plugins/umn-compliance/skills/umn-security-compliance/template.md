# Security Compliance Procedures — {{PROJECT_NAME}}

**Classification:** {{SECURITY_LEVEL}} Risk, {{USER_SCOPE}} Application
**Data Classification:** {{DATA_CLASSIFICATION}}
**Policy Reference:** [University Information Security Policy](https://policy.umn.edu/it/securedata)
**Last Reviewed:** {{YYYY-MM-DD}}

This document inventories all security policy requirements across 16 categories as they pertain to the technologies and services used in this project ({{TECH_STACK_SUMMARY}}). Each requirement is categorized as:

- **Compliant** — already addressed in the current design
- **Design Change Needed** — requires a modification to the spec/plan
- **Procedural** — recurring operational task (annual review, documentation, training)
- **Not Applicable** — does not apply to this project's technology/architecture

---

## 1. Authentication, Access, and Account Management (AAAM)

### Compliant

| ID | Requirement | How Addressed |
|---|---|---|
| AAAM.X.NN | <Requirement summary from policy> | <Concrete project-specific implementation detail> |

### Design Change Needed

| ID | Requirement | Gap |
|---|---|---|
| AAAM.X.NN | <Requirement summary> | **Gap:** <What is missing>. <Recommended fix>. |

### Procedural (Annual/Recurring)

| ID | Requirement | Frequency | Procedure |
|---|---|---|---|
| AAAM.X.NN | <Requirement summary> | Annual | <Specific procedure tied to this project's resources> |

### Not Applicable

(Use a single narrative paragraph with justification, OR a small table with a Reason column. Only include this subsection if applicable.)

---

## 2. Change Management (CM)

(Same Compliant / Design Change Needed / Procedural / Not Applicable structure as Section 1. Omit subsections that are empty.)

---

## 3. Data Center Security (DCS)

(Often Not Applicable for cloud-only PaaS projects — document delegation to cloud provider's compliance certifications.)

---

## 4. Data Storage and Backup & Recovery (DSBR)

---

## 5. Encryption (E)

---

## 6. Information Security Awareness, Education and Training (SA)

(Almost always Procedural — annual training and policy review.)

---

## 7. Log Management (LM)

---

## 8. Media Sanitization (MS)

(Often Not Applicable for cloud-only projects — document delegation.)

---

## 9. Network Firewall (NF)

---

## 10. Network Management (NM)

---

## 11. Security Patch Management (SPM)

---

## 12. Software Development (SD)

---

## 13. Systems and Device Management (SDM)

---

## 14. Technical Vulnerability Management (TVM)

---

## 15. Vendor/Supplier Management (VSM)

(Almost always Procedural — vendor contract reviews, SOC 2 attestation reviews.)

---

## 16. Virus/Malware Protection (VPM)

(Often Not Applicable for serverless/PaaS — document delegation to cloud provider.)

---

## Design Changes Required

Based on the compliance review, the following design changes are recommended:

### 1. <Short Title> ({{POLICY_ID}})

<Description of gap>

```hcl
# Or whatever language fits the change — terraform, yaml, python, etc.
<Concrete code/config snippet showing the proposed change>
```

### 2. <Short Title> ({{POLICY_ID}})

...

(One subsection per gap. If there are no gaps, write: "No design changes required at this time.")

---

## Annual Compliance Calendar

| Month | Activity | Policy References |
|---|---|---|
| January | Review access controls and RBAC assignments | AAAM.C.04, AAAM.D.03, NM.B.11 |
| February | Conduct vulnerability scan review | TVM.A.03, TVM.B.01 |
| March | Review encryption key management plan | E.A.01, E.A.02, E.A.03 |
| April | Review change management process | CM.A.01, CM.B.01, CM.B.02 |
| May | Review backup and recovery plans; test restoration | DSBR.C.04, NM.E.02, NM.E.03, SDM.E.02, SDM.E.03 |
| June | Review network and system hardening configurations | NM.C.09, SDM.B.10, NF.A.05 |
| July | Verify security awareness training completion | SA.A.01, SA.B.01 |
| August | Review vendor compliance attestations | VSM.B.01 |
| September | Review service account and managed identity access | AAAM.F.01, AAAM.F.02 |
| October | Review software development procedures and decommission plan | SD.A.01, SD.B.05, SD.F.04 |
| November | Review log management, anomaly severity, and retention | LM.C.02, LM.E.01, LM.C.05 |
| December | Review data storage procedures and media sanitization | DSBR.A.05, MS.A.06 |

**Weekly:** <Project-specific high-severity anomaly review> (LM.E.02)

**Monthly:** <Project-specific vulnerability scanning> (TVM.B.01)

**Per Event:** Rotate encryption keys on staff changes (E.A.10), remediate high severity vulnerabilities within 30 days (TVM.B.03), document remediation actions (LM.E.04)

---

## Template Notes (Remove Before Publishing)

- Replace every `{{PLACEHOLDER}}` with project-specific content
- Within each standard, omit any subsection (Compliant / Gap / Procedural / N/A) that has no entries
- Cite specific resource names from the project (terraform resource names, Azure/AWS service names, repos) — generic descriptions are not useful for an annual review
- The full sample produced for a Medium-Risk Multi-User Azure project lives at `docs/superpowers/security-compliance.md` in the sre-itsi-azure-metrics repo — refer to it for tone, phrasing, and the level of specificity expected
