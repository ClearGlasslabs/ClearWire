# Gumroad page — CLEARGLASS Guardian (rewritten)

Replaces clearglassinc.gumroad.com/l/NET (currently CAD$2,900, "Quantum
Speed Edition Advanced Security Monitoring & System Hardening Platform").

---

## Title (≤60 chars)

```
Windows Security Audit Tool for IT Consultants
```

## Subtitle (~250 chars)

```
A PowerShell script that audits Windows security posture in 90 seconds:
Defender, firewall, updates, failed logins, suspicious processes,
network devices. Outputs a branded HTML report you can hand to your
client. One-time payment.
```

## Pricing (USD, switch from CAD)

| Tier | Price | Use case |
|---|---|---|
| Personal | $49 | Audit your own machine |
| **Pro** ⭐ | **$99** | + 6 mo updates + setup video |
| Consultant | $249 | + 5-machine site license + custom-branded HTML reports (resell to clients) |

Discount code `LAUNCH50` → 50% off, expires in 7 days.

## Cover image

- 1280×720, dark background
- Centered: cropped screenshot of the actual HTML report's score circle ("87/100 GOOD")
- Top-right: "Windows Security Audit · One-Time Payment"
- Bottom: "Built for IT consultants and one-person shops"

## Hero bullets

```
✅ Audits 10 security categories in 90 seconds
✅ HTML report with overall score + findings + recommendations
✅ Real-time threat monitoring mode (cycles every 60s)
✅ Network device discovery via ARP scan
✅ Fail-login analysis from Windows Security Event Log
✅ Consultant tier: re-brand the report and resell to your clients
✅ One-time payment, no subscription, runs on your machine
```

## Description body

```
If you're an IT consultant, MSP, or solo IT operator auditing small
businesses, you know the script-cobbling routine: piece together
Get-MpComputerStatus, Get-NetFirewallProfile, a few Get-WinEvent
queries, dump it to CSV, hand-format something the client will
actually read.

This is that script, finished.

Run it on a Windows machine with admin rights. In 90 seconds you get:

- A 0-100 security score with explanation
- Critical / Warning / Info findings with concrete recommendations
- Real Defender, firewall, update, and service status
- Failed logins from the last 24 hours, with source IP and account
- Suspicious processes (known hacking tools, unusual paths, high CPU)
- ARP-based network device list with MAC vendor lookup
- An HTML report you can hand to a client or attach to a quote

═══════════════════════════════════════════════
WHAT'S INSIDE
═══════════════════════════════════════════════

  • CLEARGLASS_GUARDIAN.ps1 — the full script (~1,500 lines)
  • Setup video (Pro and Consultant tiers) — 12 minutes
  • Sample HTML report — see the output before you buy
  • Customization guide — how to extend the checks for your clients

═══════════════════════════════════════════════
TIER COMPARISON
═══════════════════════════════════════════════

  PERSONAL ($49)
  ✓ Run it on your own machine
  ✓ HTML report
  ✓ Email support

  PRO ($99)
  ✓ Everything in Personal
  ✓ 6 months of updates as Windows event IDs / WMI shifts
  ✓ Setup walkthrough video
  ✓ Discord access for buyers

  CONSULTANT ($249)
  ✓ Everything in Pro
  ✓ 5-machine site license (run on multiple client laptops)
  ✓ Custom-branded HTML report — your logo, your colors
  ✓ "Powered by ClearGlass" footer is removable
  ✓ Resell rights: charge your clients for the audit, keep 100%

═══════════════════════════════════════════════
WHO THIS IS FOR
═══════════════════════════════════════════════

  ✓ IT consultants doing security audits for SMBs
  ✓ MSPs onboarding new clients (run it on every machine in week 1)
  ✓ Solo founders / one-person IT teams self-auditing
  ✓ Anyone who needs to hand a non-technical client a credible report

═══════════════════════════════════════════════
WHO THIS IS NOT FOR
═══════════════════════════════════════════════

  ✗ Enterprises needing centralized SIEM/EDR — use Defender for Endpoint
  ✗ Mac or Linux environments — Windows only
  ✗ Anyone needing real-time alerting to a SOC — this is a point-in-time audit
  ✗ Anyone wanting agentless cloud scanning — it runs locally with admin rights

If you fall in that second list, save your money. The free Microsoft
Security Compliance Toolkit will do most of what you need.

═══════════════════════════════════════════════
HONEST LIMITS
═══════════════════════════════════════════════

  • Windows only. Tested on Win10 / Win11 / Server 2019+.
  • Requires PowerShell 5.1+ and admin rights.
  • Reads Windows event log, registry, and WMI — does NOT install agents.
  • The "real-time monitoring" mode runs in your terminal — close it,
    monitoring stops. This is not a replacement for SIEM.
  • Network device scan uses ARP — only sees devices on the same subnet.

If those limits matter for your use case, this isn't the right tool.

═══════════════════════════════════════════════
GUARANTEE
═══════════════════════════════════════════════

30 days. Run it, look at the HTML report, decide if it saves you time.
If not, reply to your purchase email — full refund, no questions.

═══════════════════════════════════════════════
WHAT BUYERS SAY
═══════════════════════════════════════════════

[Insert 3 testimonials here when available. Until then, delete this
section. Empty testimonial blocks hurt more than no section.]

═══════════════════════════════════════════════
FAQ
═══════════════════════════════════════════════

Q: Does this work on Windows 11?
A: Yes. Tested on 22H2, 23H2, 24H2, and Server 2019/2022.

Q: Do I need to install anything?
A: No. It's a single .ps1 file. PowerShell 5.1+ is built into Windows.

Q: Will Defender flag it?
A: Sometimes. The script reads security event logs and probes Defender
   state, which can trigger heuristics. Sign it with your own cert or
   add an exclusion for your audit folder. Instructions in the setup video.

Q: Can I run it on a client's machine without their permission?
A: No. Don't. This requires admin rights on a Windows system. Always
   get written authorization before running on machines you don't own.
   Personal license is for your own systems; Consultant is for client
   work where you have an audit engagement.

Q: How is this different from a vulnerability scanner like Nessus?
A: Different scope. Nessus probes for known CVEs across the network.
   Guardian audits the security posture of the host it's running on —
   configuration, hardening, event logs. Use both, not either.

Q: Is the source visible?
A: Yes. PowerShell is plain text. You can read every line before
   running. That's a feature.

Q: Will you keep updating it?
A: Pro and Consultant tiers get 6 months of updates. After that it
   keeps working — Windows security APIs are stable — but new event
   IDs and threat signatures won't be added without a renewal.

═══════════════════════════════════════════════

→ Get instant download. 30-day refund. No subscription.
```

## CTA button

```
Get the Audit Tool — $99
```

## Post-purchase content (Gumroad delivery)

```
Thanks. Three steps:

1. Download the .zip — contains:
   - CLEARGLASS_GUARDIAN.ps1
   - Sample HTML report
   - Customization guide (PDF)
   - Setup video link (Pro / Consultant only)

2. Open PowerShell as Administrator. From the script's folder:

      powershell -ExecutionPolicy Bypass -File .\CLEARGLASS_GUARDIAN.ps1

3. From the menu, pick option 1 (Full Security Baseline Assessment).
   Then option 10 to export the HTML report.

If the script is flagged by Defender, that's because it reads security
event logs and probes Defender's own state. Add the audit folder as an
exclusion or sign the script with your own cert. The setup video
(included in Pro and Consultant) walks through both.

Reply to this email if anything's broken or unclear. I read every one.

— [Your name]

P.S. After you've used it on a real audit, a one-line testimonial
helps me a lot. If it didn't deliver, reply and I'll refund — no
friction.
```

## Tags / categories on Gumroad

```
windows, powershell, security, audit, it-consultant, msp,
sysadmin, defender, firewall, hardening, soc, blue-team
```

## What to remove from the existing page

- All "Quantum Speed Edition" / "Advanced ... Platform" language
- Any claim of capabilities the script doesn't actually have (no AI,
  no quantum, no agentic, no real-time SIEM)
- Stock cybersecurity hero images of glowing locks
- The CAD $2,900 price tag — switch to USD tiered pricing above

## Pre-launch checklist

- [ ] Cover image with the actual HTML report screenshot
- [ ] 90-second screen recording: launch script → run option 1 → open HTML report
- [ ] 3-tier pricing live in USD
- [ ] LAUNCH50 discount created with 7-day expiry
- [ ] 30-day refund toggle ON
- [ ] FAQ accurate (especially Defender-flag question — buyers will hit this)
- [ ] Sample HTML report uploaded as a free preview asset
- [ ] First 5 free Consultant licenses sent to MSP friends for testimonials
