"""Ten hand-authored accounts matching the instructor's requested evidence shape."""

from __future__ import annotations

import hashlib
from datetime import date, timedelta
from pathlib import Path

from accountlens.io import write_json, write_jsonl


ROLE_KEYS = (
    "champion",
    "economic_buyer",
    "technical_evaluator",
    "procurement_legal",
    "end_user",
    "unknown",
)


SCENARIOS = [
    {
        "account_id": "TA-001", "name": "Northstar Health Systems", "industry": "Healthcare Technology",
        "stage": "commercial_review", "annual_value_usd": 420000, "signatory": "economic_buyer",
        "contacts": {
            "champion": ("Maya Chen", "Transformation Director", "Operations"),
            "economic_buyer": ("Elena Park", "Chief Financial Officer", "Finance"),
            "technical_evaluator": ("Victor Tan", "Enterprise Architect", "Technology"),
            "procurement_legal": ("Laura Gomez", "Procurement Manager", "Procurement"),
            "end_user": ("Noah Lim", "Clinical Operations Lead", "Clinical Operations"),
            "unknown": ("Iris Wong", "Programme Coordinator", "Administration"),
        },
        "emails": [
            ("Budget case review", "champion", ["economic_buyer"], ["procurement_legal", "technical_evaluator"], "Elena has final approval for the USD 420,000 commitment. Maya attached the ROI case for her decision."),
            ("Approval conditions", "economic_buyer", ["champion"], ["procurement_legal"], "I will provide final commercial sign-off after the security issue is closed and the savings case is confirmed."),
        ],
        "meeting": ("Executive investment review", ["champion", "economic_buyer", "technical_evaluator", "procurement_legal"], "Elena chaired the investment decision. Laura confirmed that Procurement will execute the contract only after Elena approves."),
        "tickets": [
            ("Identity integration failure", "technical_evaluator", "high", "open", "Single sign-on testing is failing and blocks production approval."),
            ("Training environment access", "end_user", "medium", "closed", "Access was restored and the user group completed the workflow test."),
        ],
        "crm": ("Commercial authority confirmed", ["champion", "economic_buyer"], "The account team confirmed Elena as the final commercial approver."),
    },
    {
        "account_id": "TA-002", "name": "Meridian Freight Group", "industry": "Logistics",
        "stage": "contracting", "annual_value_usd": 360000, "signatory": "economic_buyer",
        "contacts": {
            "champion": ("Jon Bell", "Network Improvement Lead", "Operations"),
            "economic_buyer": ("Marcus Lee", "Regional General Manager", "Executive Office"),
            "technical_evaluator": ("Sara Kim", "Platform Director", "Technology"),
            "procurement_legal": ("Olivia Grant", "Commercial Counsel", "Legal"),
            "end_user": ("Ethan Cole", "Depot Supervisor", "Frontline Operations"),
            "unknown": ("Nina Shah", "Executive Assistant", "Administration"),
        },
        "emails": [
            ("Regional funding decision", "champion", ["economic_buyer"], ["technical_evaluator", "procurement_legal"], "Marcus controls the regional investment budget and must approve the purchase before Legal can execute documents."),
            ("Signature sequence", "procurement_legal", ["champion"], ["economic_buyer"], "I can sign the framework paperwork as counsel, but Marcus is the commercial decision maker and must authorise the commitment first."),
        ],
        "meeting": ("Regional steering meeting", ["champion", "economic_buyer", "technical_evaluator", "procurement_legal", "end_user"], "Marcus requested the final cost case and stated that he will approve or decline the regional rollout."),
        "tickets": [
            ("Depot scanner latency", "end_user", "high", "open", "Scanner latency remains above the agreed threshold at two depots."),
            ("Route data export", "technical_evaluator", "low", "closed", "The export format was corrected and accepted by the platform team."),
        ],
        "crm": ("Legal signer is not budget owner", ["economic_buyer", "procurement_legal"], "Olivia may execute the document, but Marcus owns the final commercial approval."),
    },
    {
        "account_id": "TA-003", "name": "Apex Precision Manufacturing", "industry": "Manufacturing",
        "stage": "commercial_review", "annual_value_usd": 610000, "signatory": "economic_buyer",
        "contacts": {
            "champion": ("Leo Martins", "Continuous Improvement Manager", "Operations"),
            "economic_buyer": ("Priya Nair", "Investment Committee Chair", "Corporate Strategy"),
            "technical_evaluator": ("Hugo Stein", "Automation Architect", "Engineering"),
            "procurement_legal": ("Rachel Adams", "Vendor Manager", "Procurement"),
            "end_user": ("Samir Das", "Plant Operations Manager", "Operations"),
            "unknown": ("Tara Evans", "Project Analyst", "PMO"),
        },
        "emails": [
            ("Committee decision pack", "champion", ["economic_buyer"], ["technical_evaluator", "procurement_legal"], "Priya chairs the committee and holds delegated authority for the final investment decision."),
            ("Vendor onboarding versus approval", "procurement_legal", ["champion"], ["economic_buyer"], "Vendor onboarding is complete. That does not authorise spend; Priya's committee decision is still required."),
        ],
        "meeting": ("Capital allocation committee", ["economic_buyer", "champion", "technical_evaluator", "end_user"], "Priya asked the final questions on payback period and recorded that the commitment requires her approval."),
        "tickets": [
            ("PLC connector timeout", "technical_evaluator", "high", "open", "The pilot connector times out during peak production cycles."),
            ("Operator dashboard labels", "end_user", "medium", "closed", "Dashboard terminology was revised after operator feedback."),
        ],
        "crm": ("Delegated investment authority", ["economic_buyer"], "Priya is the named final approver for capital purchases in this programme."),
    },
    {
        "account_id": "TA-004", "name": "Lumina Digital Bank", "industry": "Financial Services",
        "stage": "technical_validation", "annual_value_usd": 780000, "signatory": "economic_buyer",
        "contacts": {
            "champion": ("Alice Ng", "Digital Transformation Lead", "Strategy"),
            "economic_buyer": ("David Wong", "Chief Operating Officer", "Executive Office"),
            "technical_evaluator": ("Farah Ali", "Information Security Director", "Security"),
            "procurement_legal": ("Martin Price", "Head of Legal Operations", "Legal"),
            "end_user": ("Chloe Davis", "Service Operations Manager", "Operations"),
            "unknown": ("Ryan Teo", "Corporate Affairs Adviser", "Corporate Affairs"),
        },
        "emails": [
            ("Operational investment approval", "champion", ["economic_buyer"], ["technical_evaluator", "procurement_legal"], "David owns the operating budget and is the only executive authorised to approve this programme."),
            ("Contract execution clarification", "procurement_legal", ["economic_buyer"], ["champion"], "Legal will countersign the agreement after David gives final commercial approval; countersigning does not transfer budget authority."),
        ],
        "meeting": ("Risk and investment review", ["economic_buyer", "champion", "technical_evaluator", "procurement_legal"], "David deferred the final decision until Farah closes the data-residency exception."),
        "tickets": [
            ("Data residency exception", "technical_evaluator", "critical", "open", "A production data flow uses a region that is not yet approved."),
            ("Agent desktop timeout", "end_user", "medium", "closed", "The timeout was fixed in the latest test build."),
        ],
        "crm": ("COO decision pending security", ["economic_buyer", "technical_evaluator"], "David remains the final approver; the open security exception is the gating issue."),
    },
    {
        "account_id": "TA-005", "name": "Helix Enterprise Software", "industry": "Enterprise Software",
        "stage": "contracting", "annual_value_usd": 295000, "signatory": "economic_buyer",
        "contacts": {
            "champion": ("Benjamin Ho", "Revenue Operations Director", "Sales Operations"),
            "economic_buyer": ("Sofia Chen", "Finance Director", "Finance"),
            "technical_evaluator": ("Amir Khan", "Integration Lead", "Technology"),
            "procurement_legal": ("Julia Ross", "Procurement Counsel", "Procurement"),
            "end_user": ("Megan Ford", "Customer Success Manager", "Customer Success"),
            "unknown": ("Peter Low", "Communications Manager", "Corporate Affairs"),
        },
        "emails": [
            ("ROI approval request", "champion", ["economic_buyer"], ["technical_evaluator", "procurement_legal"], "Sofia must approve the financial case before the annual subscription can be committed."),
            ("Purchase order sequence", "economic_buyer", ["procurement_legal"], ["champion"], "I will release final approval after the revised liability clause arrives. Julia can issue the purchase order afterward."),
        ],
        "meeting": ("Commercial close meeting", ["champion", "economic_buyer", "procurement_legal", "end_user"], "Sofia accepted the ROI but retained final approval until the liability change is complete."),
        "tickets": [
            ("CRM synchronisation duplicates", "technical_evaluator", "high", "open", "Duplicate account records remain in the synchronisation test."),
            ("Renewal dashboard filter", "end_user", "low", "closed", "The filter behaviour now matches the user workflow."),
        ],
        "crm": ("Finance approval outstanding", ["economic_buyer", "procurement_legal"], "Sofia is the commercial signatory; Julia owns contracting steps."),
    },
    {
        "account_id": "TA-006", "name": "BlueHarbor Energy Services", "industry": "Energy Services",
        "stage": "commercial_review", "annual_value_usd": 540000, "signatory": "economic_buyer",
        "contacts": {
            "champion": ("Nora Jensen", "Asset Transformation Lead", "Operations"),
            "economic_buyer": ("Omar Rahman", "Business Unit President", "Executive Office"),
            "technical_evaluator": ("Kenji Sato", "Industrial Systems Architect", "Engineering"),
            "procurement_legal": ("Diana Moore", "Category Manager", "Procurement"),
            "end_user": ("Luis Ortega", "Field Service Supervisor", "Field Operations"),
            "unknown": ("Emma Reed", "Sustainability Adviser", "Corporate Affairs"),
        },
        "emails": [
            ("Business unit commitment", "champion", ["economic_buyer"], ["procurement_legal", "technical_evaluator"], "Omar has final authority for commitments above USD 500,000 in this business unit."),
            ("Tender completion", "procurement_legal", ["champion"], ["economic_buyer"], "The tender is complete, but award requires Omar's final approval before I can release the purchase order."),
        ],
        "meeting": ("Asset programme board", ["economic_buyer", "champion", "technical_evaluator", "end_user"], "Omar requested evidence that the open telemetry issue will not affect field operations before approving."),
        "tickets": [
            ("Telemetry packet loss", "technical_evaluator", "high", "open", "Packet loss exceeds the pilot acceptance threshold at one offshore site."),
            ("Mobile checklist layout", "end_user", "medium", "closed", "The field checklist was simplified and approved by supervisors."),
        ],
        "crm": ("Final approval with business unit president", ["economic_buyer"], "Omar is the named final commercial approver for the programme."),
    },
    {
        "account_id": "TA-007", "name": "Cedar Retail Holdings", "industry": "Retail",
        "stage": "commercial_review", "annual_value_usd": 330000, "signatory": "economic_buyer",
        "contacts": {
            "champion": ("Hannah Brooks", "Omnichannel Programme Lead", "Digital"),
            "economic_buyer": ("Daniel Ortiz", "Chief Financial Officer", "Finance"),
            "technical_evaluator": ("Wei Zhang", "Retail Technology Manager", "Technology"),
            "procurement_legal": ("Claire Brown", "Senior Buyer", "Procurement"),
            "end_user": ("Isaac Miller", "Store Operations Manager", "Operations"),
            "unknown": ("Lena Fischer", "Brand Partnerships Lead", "Marketing"),
        },
        "emails": [
            ("Funding request for store rollout", "champion", ["economic_buyer"], ["technical_evaluator", "procurement_legal"], "Daniel owns the transformation budget and must sign off the store rollout funding."),
            ("Supplier award recommendation", "procurement_legal", ["economic_buyer"], ["champion"], "I recommend the supplier award, but Daniel makes the final commercial decision."),
        ],
        "meeting": ("Store rollout approval", ["champion", "economic_buyer", "technical_evaluator", "procurement_legal", "end_user"], "Daniel asked for a revised deployment schedule and retained final approval."),
        "tickets": [
            ("Point-of-sale API rate limit", "technical_evaluator", "high", "open", "The test integration is exceeding the point-of-sale API limit."),
            ("Store manager permissions", "end_user", "medium", "closed", "Permission groups were updated and accepted by store operations."),
        ],
        "crm": ("CFO approval required", ["economic_buyer", "champion"], "Daniel is the commercial signatory for the proposed rollout."),
    },
    {
        "account_id": "TA-008", "name": "Quantum Mobility Labs", "industry": "Mobility Technology",
        "stage": "contracting", "annual_value_usd": 470000, "signatory": "economic_buyer",
        "contacts": {
            "champion": ("Lucas Meyer", "Fleet Innovation Lead", "Innovation"),
            "economic_buyer": ("Mei Lin", "Senior Vice President Transformation", "Executive Office"),
            "technical_evaluator": ("Arjun Rao", "Connected Vehicle Architect", "Engineering"),
            "procurement_legal": ("Sophie Laurent", "Legal Counsel", "Legal"),
            "end_user": ("Tom Becker", "Fleet Control Manager", "Operations"),
            "unknown": ("Yuki Mori", "Research Partnerships Manager", "Research"),
        },
        "emails": [
            ("Delegated approval authority", "champion", ["economic_buyer"], ["technical_evaluator", "procurement_legal"], "Mei holds delegated authority to approve this transformation contract without a board vote."),
            ("Legal signature versus decision", "procurement_legal", ["champion"], ["economic_buyer"], "I may apply the electronic legal signature, but Mei must first approve the commercial commitment."),
        ],
        "meeting": ("Transformation contract review", ["economic_buyer", "champion", "technical_evaluator", "procurement_legal"], "Mei approved the commercial direction subject to closure of the vehicle-data ticket."),
        "tickets": [
            ("Vehicle data consent flag", "technical_evaluator", "critical", "open", "Consent status is not propagated to one downstream analytics service."),
            ("Fleet alert localisation", "end_user", "low", "closed", "Alert wording was localised and accepted by fleet controllers."),
        ],
        "crm": ("Delegated commercial signatory", ["economic_buyer"], "Mei is recorded as the delegated final commercial approver."),
    },
    {
        "account_id": "TA-009", "name": "Atlas Communications", "industry": "Telecommunications",
        "stage": "technical_validation", "annual_value_usd": 690000, "signatory": "economic_buyer",
        "contacts": {
            "champion": ("Zara Ahmed", "Customer Platform Director", "Product"),
            "economic_buyer": ("Nathan Brooks", "Chief Financial Officer", "Finance"),
            "technical_evaluator": ("Eric Chua", "Cloud Security Lead", "Security"),
            "procurement_legal": ("Monica Silva", "Strategic Sourcing Director", "Procurement"),
            "end_user": ("Paul Green", "Contact Centre Manager", "Operations"),
            "unknown": ("Rita Das", "Public Policy Manager", "Corporate Affairs"),
        },
        "emails": [
            ("Enterprise platform funding", "champion", ["economic_buyer"], ["technical_evaluator", "procurement_legal"], "Nathan is the final approver for the enterprise platform budget and requires the risk exceptions to be closed."),
            ("Sourcing recommendation", "procurement_legal", ["economic_buyer"], ["champion"], "Sourcing supports the award, but Nathan retains the decision and commercial sign-off."),
        ],
        "meeting": ("Executive risk review", ["champion", "economic_buyer", "technical_evaluator", "procurement_legal"], "Nathan stated that he will decide after Eric confirms the encryption control."),
        "tickets": [
            ("Encryption key rotation", "technical_evaluator", "critical", "open", "The test tenant is not rotating encryption keys at the required interval."),
            ("Agent search relevance", "end_user", "medium", "closed", "Search tuning improved relevance and passed user acceptance."),
        ],
        "crm": ("CFO owns final decision", ["economic_buyer", "technical_evaluator"], "Nathan is the final commercial signatory pending security closure."),
    },
    {
        "account_id": "TA-010", "name": "Solstice Pharma Operations", "industry": "Pharmaceuticals",
        "stage": "contracting", "annual_value_usd": 515000, "signatory": "economic_buyer",
        "contacts": {
            "champion": ("Emily Carter", "Quality Transformation Director", "Quality"),
            "economic_buyer": ("Aisha Patel", "Country General Manager", "Executive Office"),
            "technical_evaluator": ("Marco Rossi", "Validated Systems Lead", "Technology"),
            "procurement_legal": ("Fiona Clark", "Contracts Director", "Legal"),
            "end_user": ("George Evans", "Quality Operations Manager", "Operations"),
            "unknown": ("Nadia Ibrahim", "Medical Affairs Coordinator", "Medical Affairs"),
        },
        "emails": [
            ("Country investment approval", "champion", ["economic_buyer"], ["technical_evaluator", "procurement_legal"], "Aisha has final country-level authority for the proposed USD 515,000 commitment."),
            ("Contract signature route", "procurement_legal", ["economic_buyer"], ["champion"], "I will execute the contract after Aisha approves the investment; Legal execution is not the commercial decision."),
        ],
        "meeting": ("Validated system investment board", ["economic_buyer", "champion", "technical_evaluator", "procurement_legal", "end_user"], "Aisha requested closure of the audit-trail issue before giving final approval."),
        "tickets": [
            ("Audit trail timestamp mismatch", "technical_evaluator", "critical", "open", "The validation test found inconsistent timestamps in the audit trail."),
            ("Batch review screen", "end_user", "medium", "closed", "The revised screen passed the user acceptance script."),
        ],
        "crm": ("General manager is commercial signatory", ["economic_buyer", "procurement_legal"], "Aisha owns the final commercial approval; Fiona owns legal execution."),
    },
]


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _event_date(offset: int) -> str:
    return (date(2026, 8, 1) + timedelta(days=offset)).isoformat()


def build_teacher_aligned_dataset() -> dict[str, list[dict]]:
    accounts: list[dict] = []
    contacts: list[dict] = []
    interactions: list[dict] = []
    role_truth: list[dict] = []
    critical_truth: list[dict] = []
    emails: list[dict] = []
    meetings: list[dict] = []
    tickets: list[dict] = []
    crm_notes: list[dict] = []

    for account_number, scenario in enumerate(SCENARIOS, 1):
        account_id = scenario["account_id"]
        contact_ids = {role: f"TCON-{account_number:03d}-{index:02d}" for index, role in enumerate(ROLE_KEYS, 1)}
        accounts.append(
            {
                "account_id": account_id,
                "name": scenario["name"],
                "industry": scenario["industry"],
                "stage": scenario["stage"],
                "annual_value_usd": scenario["annual_value_usd"],
                "true_signatory_contact_id": contact_ids[scenario["signatory"]],
            }
        )
        for role in ROLE_KEYS:
            name, title, department = scenario["contacts"][role]
            seniority = "executive" if role == "economic_buyer" else "director" if "Director" in title else "manager"
            contacts.append(
                {
                    "contact_id": contact_ids[role],
                    "account_id": account_id,
                    "name": name,
                    "title": title,
                    "department": department,
                    "seniority": seniority,
                }
            )
            role_truth.append({"contact_id": contact_ids[role], "account_id": account_id, "role": role})

        event_index = 1
        for email_index, (subject, sender, to_roles, cc_roles, body) in enumerate(scenario["emails"], 1):
            event_id = f"TEVT-{account_number:03d}-{event_index:02d}"
            event_index += 1
            thread_id = f"THREAD-{account_number:03d}-{email_index:02d}"
            sender_id = contact_ids[sender]
            to_ids = [contact_ids[role] for role in to_roles]
            cc_ids = [contact_ids[role] for role in cc_roles]
            row = {
                "event_id": event_id, "account_id": account_id, "date": _event_date(9 + account_number),
                "channel": "email", "internal_team": "Sales", "participant_ids": _unique([sender_id, *to_ids, *cc_ids]),
                "subject": subject, "content": body, "status": "sent", "thread_id": thread_id,
                "sender_id": sender_id, "to_ids": to_ids, "cc_ids": cc_ids,
                "meeting_id": None, "attendee_ids": [], "internal_attendees": [], "ticket_id": None, "priority": None,
            }
            interactions.append(row)
            emails.append(row)
            if email_index == 2:
                critical_truth.append({"event_id": event_id, "account_id": account_id, "category": "signatory_evidence", "importance": "high"})

        meeting_subject, attendee_roles, meeting_content = scenario["meeting"]
        event_id = f"TEVT-{account_number:03d}-{event_index:02d}"
        event_index += 1
        attendee_ids = [contact_ids[role] for role in attendee_roles]
        meeting_row = {
            "event_id": event_id, "account_id": account_id, "date": _event_date(14 + account_number),
            "channel": "meeting", "internal_team": "Presales", "participant_ids": attendee_ids,
            "subject": meeting_subject, "content": meeting_content, "status": "completed", "thread_id": None,
            "sender_id": None, "to_ids": [], "cc_ids": [], "meeting_id": f"MEET-{account_number:03d}",
            "attendee_ids": attendee_ids, "internal_attendees": ["Key Account Manager", "Presales Engineer"],
            "ticket_id": None, "priority": None,
        }
        interactions.append(meeting_row)
        meetings.append(meeting_row)
        critical_truth.append({"event_id": event_id, "account_id": account_id, "category": "signatory_evidence", "importance": "high"})

        for ticket_index, (subject, requester, priority, status, content) in enumerate(scenario["tickets"], 1):
            event_id = f"TEVT-{account_number:03d}-{event_index:02d}"
            event_index += 1
            requester_id = contact_ids[requester]
            ticket_row = {
                "event_id": event_id, "account_id": account_id, "date": _event_date(17 + account_number + ticket_index),
                "channel": "ticket", "internal_team": "Customer Success", "participant_ids": [requester_id],
                "subject": subject, "content": content, "status": status, "thread_id": None, "sender_id": None,
                "to_ids": [], "cc_ids": [], "meeting_id": None, "attendee_ids": [], "internal_attendees": [],
                "ticket_id": f"TICKET-{account_number:03d}-{ticket_index:02d}", "priority": priority,
            }
            interactions.append(ticket_row)
            tickets.append(ticket_row)
            if status == "open":
                critical_truth.append({"event_id": event_id, "account_id": account_id, "category": "service_risk", "importance": "high"})

        crm_subject, crm_roles, crm_content = scenario["crm"]
        event_id = f"TEVT-{account_number:03d}-{event_index:02d}"
        crm_row = {
            "event_id": event_id, "account_id": account_id, "date": _event_date(23 + account_number),
            "channel": "crm_note", "internal_team": "Sales", "participant_ids": [contact_ids[role] for role in crm_roles],
            "subject": crm_subject, "content": crm_content, "status": "completed", "thread_id": None,
            "sender_id": None, "to_ids": [], "cc_ids": [], "meeting_id": None, "attendee_ids": [],
            "internal_attendees": [], "ticket_id": None, "priority": None,
        }
        interactions.append(crm_row)
        crm_notes.append(crm_row)

    return {
        "accounts": accounts,
        "contacts": contacts,
        "interactions": interactions,
        "role_truth": role_truth,
        "critical_truth": critical_truth,
        "emails": emails,
        "meetings": meetings,
        "tickets": tickets,
        "crm_notes": crm_notes,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_teacher_aligned_dataset(dataset: dict[str, list[dict]], output_dir: Path) -> dict:
    files = {
        "accounts.jsonl": dataset["accounts"],
        "contacts.jsonl": dataset["contacts"],
        "interactions.jsonl": dataset["interactions"],
        "role_ground_truth.jsonl": dataset["role_truth"],
        "critical_event_ground_truth.jsonl": dataset["critical_truth"],
        "emails.jsonl": dataset["emails"],
        "meetings.jsonl": dataset["meetings"],
        "tickets.jsonl": dataset["tickets"],
        "crm_notes.jsonl": dataset["crm_notes"],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, rows in files.items():
        write_jsonl(output_dir / filename, rows)
    account_ids = [row["account_id"] for row in dataset["accounts"]]
    write_json(output_dir / "splits.json", {"teacher_validation": account_ids})
    manifest = {
        "dataset": "teacher_aligned_10",
        "hand_authored": True,
        "schema_version": 1,
        "counts": {key: len(value) for key, value in dataset.items()},
        "requirements": {
            "accounts": 10,
            "email_threads_per_account": 2,
            "cc_lists_required": True,
            "meetings_per_account": 1,
            "attendee_lists_required": True,
            "tickets_per_account": 2,
            "true_signatory_required": True,
        },
        "sha256": {filename: _sha256(output_dir / filename) for filename in files},
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest
