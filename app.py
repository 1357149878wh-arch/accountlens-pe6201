"""Streamlit demonstration interface for AccountLens."""

from __future__ import annotations

import os
from datetime import date

from dotenv import load_dotenv

from accountlens.baseline.rules import infer_roles
from accountlens.config import DEFAULT_ABSTENTION_THRESHOLD, DEFAULT_DATA_DIR, PROJECT_ROOT
from accountlens.intelligence import (
    aggregate_cross_team_activity,
    build_decision_chain,
    decision_chain_graphviz,
    detect_risk_signals,
    filter_recent_interactions,
)
from accountlens.io import load_dataset, read_json
from accountlens.reporting import build_briefing_pdf, build_slack_summary


FULL_TITLE = "Enterprise Account Decision-Chain Mapping & Cross-Team Intelligence Aggregation Assistant"


def _role_rows(chain) -> list[dict]:
    return [
        {
            "contact": node.name,
            "title": node.title,
            "decision_role": node.role.value,
            "confidence": f"{node.confidence:.0%}",
            "review_status": node.review_status,
            "evidence": ", ".join(node.evidence_ids),
        }
        for node in chain.nodes
    ]


def _briefing_key(account_id: str) -> str:
    return f"briefing::{account_id}"


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    try:
        import streamlit as st
    except ImportError as exc:
        raise SystemExit("Streamlit is not installed. Run: python -m pip install -e .") from exc

    st.set_page_config(page_title="AccountLens", page_icon="🔎", layout="wide")
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.8rem; padding-bottom: 3rem;}
        .accountlens-kicker {color:#2563eb; font-size:.8rem; font-weight:700; letter-spacing:.08em;}
        .accountlens-title {font-size:2rem; font-weight:750; line-height:1.15; color:#0f172a; margin:.25rem 0;}
        .accountlens-subtitle {color:#475569; margin-bottom:1.2rem;}
        .risk-high {border-left:4px solid #dc2626; padding:.65rem .85rem; background:#fef2f2; margin:.4rem 0;}
        .risk-medium {border-left:4px solid #d97706; padding:.65rem .85rem; background:#fffbeb; margin:.4rem 0;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="accountlens-kicker">ACCOUNTLENS · PE6201 END-OF-COURSE PROJECT</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="accountlens-title">{FULL_TITLE}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="accountlens-subtitle">Evidence-grounded meeting preparation for Key Account Managers.</div>',
        unsafe_allow_html=True,
    )

    if not (DEFAULT_DATA_DIR / "accounts.jsonl").exists():
        st.warning("Synthetic data has not been generated yet.")
        st.code("python -m accountlens.data.generate")
        st.stop()

    dataset = load_dataset(DEFAULT_DATA_DIR)
    manifest = read_json(DEFAULT_DATA_DIR / "manifest.json")
    reference_date = date.fromisoformat(manifest["reference_date"])
    account_by_id = {row["account_id"]: row for row in dataset["accounts"]}

    with st.sidebar:
        st.header("Meeting preparation")
        selected_id = st.selectbox(
            "Fictional enterprise account",
            sorted(account_by_id),
            format_func=lambda account_id: f"{account_id} - {account_by_id[account_id]['name']}",
        )
        st.caption("Primary user: Key Account Manager with less than 15 minutes to prepare.")
        st.divider()
        st.markdown("**Responsible-use boundary**")
        st.caption("Advisory only. Never automate outreach or treat inferred power relationships as verified facts.")
        human_confirmed = st.checkbox("I will verify conclusions with the account team")

    account = account_by_id[selected_id]
    contacts = [row for row in dataset["contacts"] if row["account_id"] == selected_id]
    all_interactions = [row for row in dataset["interactions"] if row["account_id"] == selected_id]
    recent_interactions = filter_recent_interactions(all_interactions, reference_date, days=30)

    feedback_labels = {
        row["event_id"]: f"{row['event_id']} · {row['date']} · {row['internal_team']} · {row['subject']}"
        for row in recent_interactions
    }
    with st.expander("Relevance feedback - exclude events from this briefing", expanded=False):
        excluded_ids = st.multiselect(
            "Mark source events as not relevant",
            options=list(feedback_labels),
            format_func=lambda event_id: feedback_labels[event_id],
            help="This feedback affects only the current session and is not written to disk.",
        )
    active_interactions = [row for row in recent_interactions if row["event_id"] not in set(excluded_ids)]

    baseline_predictions = infer_roles(contacts, active_interactions)
    active_event_ids = tuple(row["event_id"] for row in active_interactions)
    saved_state = st.session_state.get(_briefing_key(selected_id))
    saved_run = (
        saved_state["run"]
        if saved_state and saved_state.get("event_ids") == active_event_ids
        else None
    )
    predictions = saved_run.briefing.decision_roles if saved_run else baseline_predictions
    chain = build_decision_chain(
        selected_id,
        contacts,
        predictions,
        threshold=DEFAULT_ABSTENTION_THRESHOLD,
    )
    team_activity = aggregate_cross_team_activity(active_interactions)
    deterministic_risks = detect_risk_signals(active_interactions)

    metrics = st.columns(5)
    metrics[0].metric("Stage", account["stage"].replace("_", " ").title())
    metrics[1].metric("Annual value", f"${account['annual_value_usd']:,}")
    metrics[2].metric("Contacts", len(contacts))
    metrics[3].metric("30-day events", len(active_interactions))
    metrics[4].metric("Teams active", len(team_activity))

    overview_tab, intelligence_tab, briefing_tab, evidence_tab = st.tabs(
        ["Decision chain", "Cross-team intelligence", "Account briefing", "Evidence & governance"]
    )

    with overview_tab:
        st.subheader("Likely decision workflow")
        st.caption(
            "Edges are workflow hypotheses inferred from validated decision roles. They are not verified reporting lines or personal power claims."
        )
        signatory_candidates = [node for node in chain.nodes if node.role.value == "economic_buyer"]
        if signatory_candidates:
            selected_signatory = max(signatory_candidates, key=lambda node: node.confidence)
            st.info(
                f"Likely commercial signatory: {selected_signatory.name} "
                f"({selected_signatory.confidence:.0%}). Verify with the account team before use."
            )
        else:
            st.warning("Likely commercial signatory: not identified. Human follow-up is required.")
        if chain.edges:
            st.graphviz_chart(decision_chain_graphviz(chain), width="stretch")
        else:
            st.info("Not enough supported roles to draw a decision workflow.")
        if chain.missing_roles:
            st.warning("Missing or unconfirmed roles: " + ", ".join(role.value for role in chain.missing_roles))
        st.dataframe(_role_rows(chain), width="stretch", hide_index=True)
        with st.expander("Relationship hypotheses and evidence"):
            st.dataframe(
                [edge.model_dump(mode="json") for edge in chain.edges],
                width="stretch",
                hide_index=True,
            )

    with intelligence_tab:
        left, right = st.columns([1.15, 1])
        with left:
            st.subheader("Ranked cross-team activity")
            st.caption(f"Inclusive 30-day window ending {reference_date.isoformat()}.")
            st.dataframe(
                [item.model_dump(mode="json") for item in team_activity],
                width="stretch",
                hide_index=True,
            )
        with right:
            st.subheader("Deterministic risk alerts")
            if deterministic_risks:
                for risk in deterministic_risks:
                    css_class = "risk-high" if risk.severity == "high" else "risk-medium"
                    st.markdown(
                        f'<div class="{css_class}"><b>{risk.category.replace("_", " ").title()}</b><br>'
                        f'{risk.description}<br><small>Evidence: {", ".join(risk.event_ids)} · Human confirmation required</small></div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No explicit unresolved-ticket, unanswered-email, or competitor signal was found.")

    with briefing_tab:
        st.subheader("One-page Account Panorama Briefing")
        if os.getenv("OPENAI_API_KEY"):
            if st.button(
                "Generate evidence-grounded AI briefing",
                type="primary",
                disabled=not human_confirmed,
                help="Confirm the responsible-use boundary in the sidebar first.",
            ):
                from accountlens.pipeline.llm import run_briefing

                with st.spinner("Retrieving, filtering, inferring, validating and assembling the briefing..."):
                    try:
                        run = run_briefing(account, contacts, active_interactions, experiment="M2")
                        st.session_state[_briefing_key(selected_id)] = {
                            "run": run,
                            "event_ids": active_event_ids,
                        }
                        st.rerun()
                    except Exception as exc:  # User-facing demo boundary.
                        st.error(str(exc))
        else:
            st.info("The rules workflow is ready. Add OPENAI_API_KEY to enable the AI briefing.")

        if saved_run:
            run = saved_run
            st.success(
                f"Evidence validation passed · {run.usage.latency_seconds:.2f}s · "
                f"estimated USD {run.usage.estimated_cost_usd:.4f}"
            )
            refreshed_chain = build_decision_chain(selected_id, contacts, run.briefing.decision_roles)

            role_col, risk_col, action_col = st.columns(3)
            with role_col:
                st.markdown("**Decision roles**")
                for role in run.briefing.decision_roles:
                    label = role.role.value.replace("_", " ").title()
                    st.write(f"{label}: {role.confidence:.0%}" + (" · review" if role.abstained else ""))
            with risk_col:
                st.markdown("**AI-supported risks**")
                for risk in run.briefing.risks:
                    st.write(f"{risk.severity.upper()} · {risk.description}")
                if not run.briefing.risks:
                    st.write("No additional AI-supported risk.")
            with action_col:
                st.markdown("**Next actions**")
                for index, action in enumerate(run.briefing.recommended_actions[:2], 1):
                    st.write(f"{index}. {action.action}")

            pdf_bytes = build_briefing_pdf(
                account,
                run.briefing,
                refreshed_chain,
                team_activity,
                deterministic_risks,
            )
            slack_text = build_slack_summary(
                account,
                run.briefing,
                refreshed_chain,
                team_activity,
                deterministic_risks,
            )
            download_left, download_right = st.columns(2)
            download_left.download_button(
                "Download one-page PDF",
                data=pdf_bytes,
                file_name=f"{selected_id}_account_panorama.pdf",
                mime="application/pdf",
                width="stretch",
            )
            download_right.download_button(
                "Download Slack-ready summary",
                data=slack_text,
                file_name=f"{selected_id}_slack_summary.md",
                mime="text/markdown",
                width="stretch",
            )
            with st.expander("Limitations and run metadata"):
                st.write(run.briefing.limitations)
                st.json(run.usage.model_dump(mode="json"))

    with evidence_tab:
        st.subheader("Evidence register")
        st.caption(
            "Raw source text is hidden by default. The demo uses fictional records only; API calls use store=False and logs contain metadata only."
        )
        st.dataframe(
            [
                {
                    "event_id": row["event_id"],
                    "date": row["date"],
                    "team": row["internal_team"],
                    "channel": row["channel"],
                    "subject": row["subject"],
                    "status": row["status"],
                }
                for row in active_interactions
            ],
            width="stretch",
            hide_index=True,
        )
        with st.expander("Show fictional raw source content"):
            st.dataframe(active_interactions, width="stretch", hide_index=True)
        st.markdown("**Governance controls**")
        st.markdown(
            "- Synthetic data only; no real client names, email addresses or customer records.\n"
            "- Evidence IDs are validated before output is accepted.\n"
            "- Low-confidence or unsupported roles are marked for human review.\n"
            "- Decision-chain edges are explicitly labelled as hypotheses.\n"
            "- The assistant never sends messages or changes CRM data."
        )


if __name__ == "__main__":
    main()
