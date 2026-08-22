import streamlit as st
import pandas as pd
import io
from docx import Document

# Page Setup
st.set_page_config(page_title="Complivox Global RegTech", layout="wide")

# Jurisdiction-specific Statutory & SEC Configurations
JURISDICTION_CONFIGS = {
    "India (CDSCO / MDR 2017)": {
        "forms": ["Form MD-14 (Import)", "Form MD-7 (Mfg Class A/B)", "Form MD-8 (Mfg Class C/D)", "SUGAM 3.0 Filing"],
        "checklist": [
            {"Requirement": "Device Master File (Appendix II)", "Status": "⚠️ In Review", "Standard": "Fourth Schedule"},
            {"Requirement": "Plant Master File (PMF)", "Status": "✅ Ready", "Standard": "Part III Rule 20"},
            {"Requirement": "ISO 13485:2016 Certification", "Status": "✅ Verified", "Standard": "QMS Statutory"},
            {"Requirement": "Biocompatibility & Animal Study", "Status": "❌ Missing", "Standard": "ISO 10993"}
        ],
        "sec_queries": [
            {
                "deficiency": "Lack of Indian Clinical Population Equivalence Data",
                "risk_level": "High (Class C/D)",
                "statutory_reference": "MDR 2017 Part III (Clinical Investigation)",
                "recommended_defense": "Submit GHTF-harmonized overseas clinical evaluation along with waiver justification under Rule 60(1)."
            },
            {
                "deficiency": "Incomplete Accelerated vs Real-time Shelf-Life Stability Reports",
                "risk_level": "Medium",
                "statutory_reference": "ISO 11607 & ASTM F1980",
                "recommended_defense": "Attach ongoing real-time aging protocol with intermediate 6-month accelerated degradation testing logs."
            },
            {
                "deficiency": "Residual Risk Acceptability Matrix for Critical Components",
                "risk_level": "High",
                "statutory_reference": "ISO 14971:2019 Clause 7.4",
                "recommended_defense": "Provide quantified Benefit-Risk analysis justifying residual toxicity threshold for patient contact materials."
            }
        ]
    },
    "USA (US FDA - 510k / PMA)": {
        "forms": ["510(k) Premarket Notification", "De Novo Classification", "PMA (Class III)", "eSTAR XML Schema"],
        "checklist": [
            {"Requirement": "Substantial Equivalence (SE) Rationale", "Status": "✅ Verified", "Standard": "21 CFR 807.87"},
            {"Requirement": "Design History File (DHF) Traceability", "Status": "⚠️ In Review", "Standard": "21 CFR 820.30"},
            {"Requirement": "Software Lifecycle (SaMD)", "Status": "✅ Ready", "Standard": "IEC 62304 / FDA Guidance"},
            {"Requirement": "Human Factors & Usability Engineering", "Status": "❌ Missing", "Standard": "ANSI/AAMI HE75"}
        ],
        "sec_queries": [
            {
                "deficiency": "Refusal to Accept (RTA): Insufficient Bench Performance Testing vs Predicate",
                "risk_level": "High",
                "statutory_reference": "FDA 510(k) Third-Party Guidance",
                "recommended_defense": "Execute side-by-side mechanical fatigue testing with identical cycle parameters to predicate standard."
            },
            {
                "deficiency": "Cybersecurity Bill of Materials (CBOM) Traceability Gap",
                "risk_level": "Medium",
                "statutory_reference": "Section 524B FD&C Act",
                "recommended_defense": "Attach software architecture SBOM with static code analysis vulnerabilities log."
            }
        ]
    },
    "EU (CE MDR 2017/745)": {
        "forms": ["Annex II Technical Documentation", "Annex III Post-Market Surveillance", "GSPR Checklist", "EUDAMED Registration"],
        "checklist": [
            {"Requirement": "General Safety and Performance (GSPR)", "Status": "✅ Ready", "Standard": "Annex I Essential Regs"},
            {"Requirement": "Clinical Evaluation Report (CER)", "Status": "⚠️ Missing PMCF", "Standard": "MEDDEV 2.7/1 rev 4"},
            {"Requirement": "Risk Management File", "Status": "✅ Ready", "Standard": "ISO 14971:2019"},
            {"Requirement": "Periodic Safety Update Report (PSUR)", "Status": "❌ Needs Template", "Standard": "Article 86 MDR"}
        ],
        "sec_queries": [
            {
                "deficiency": "Notified Body Scrutiny: Insufficient Post-Market Clinical Follow-up (PMCF) Rationale",
                "risk_level": "High",
                "statutory_reference": "MDR Annex XIV Part B",
                "recommended_defense": "Submit prospective PMCF registry protocol targeting 5-year patient outcome data."
            },
            {
                "deficiency": "State-of-the-Art (SOTA) Literature Search Filter String Deficiencies",
                "risk_level": "Medium",
                "statutory_reference": "MDCG 2020-6",
                "recommended_defense": "Re-run systematic literature search including PRISMA flowchart and adverse database logs."
            }
        ]
    }
}

DEMO_DEVICES = {
    "Select Demo Device...": {"name": "", "use": "", "class": "Class A (Low)"},
    "Orthopedic Titanium Hip Implant": {"name": "Compli-Hip Total Joint", "use": "Total hip arthroplasty for severe joint degeneration.", "class": "Class C (Mod-High)"},
    "Drug-Eluting Coronary Stent System": {"name": "Compli-DES Stent", "use": "Percutaneous coronary intervention in symptomatic ischemic disease.", "class": "Class D (High)"},
    "AI Diagnostic ECG Monitor": {"name": "CardioSense 300", "use": "Continuous automated ECG screening and arrhythmia classification.", "class": "Class B (Low-Med)"}
}

# Session State Initialization
if 'device_name' not in st.session_state:
    st.session_state.device_name = ""
    st.session_state.intended_use = ""

def load_demo_data():
    sel = st.session_state.selected_demo
    if sel != "Select Demo Device...":
        st.session_state.device_name = DEMO_DEVICES[sel]["name"]
        st.session_state.intended_use = DEMO_DEVICES[sel]["use"]

# Sidebar Setup
st.sidebar.title("Complivox Global")
selected_jurisdiction = st.sidebar.selectbox("Regulatory Jurisdiction", list(JURISDICTION_CONFIGS.keys()))
st.sidebar.markdown("---")
st.sidebar.selectbox("⚡ 1-Click Sample Pre-loader:", list(DEMO_DEVICES.keys()), key="selected_demo", on_change=load_demo_data)

st.sidebar.markdown("---")
st.sidebar.info("💼 **Enterprise Regulatory Intelligence**\nComplivox Regulatory Engine active for statutory automation.")

# Main Interface
st.title("Complivox Regulatory Intelligence Platform")
st.caption(f"Active Statutory Framework: **{selected_jurisdiction}**")

active_data = JURISDICTION_CONFIGS[selected_jurisdiction]

tab1, tab2, tab3 = st.tabs(["📋 Submission Builder", "🔍 Statutory Gap Audit", "⚖️ SEC Scrutiny & Deficiency Forecast"])

with tab1:
    col1, col2 = st.columns(2)
    device_name = col1.text_input("Medical Device Name", value=st.session_state.device_name)
    risk_class = col2.selectbox("Device Risk Classification", ["Class A (Low)", "Class B (Low-Med)", "Class C (Mod-High)", "Class D (High)"])
    intended_use = st.text_area("Intended Purpose / Indications for Use", value=st.session_state.intended_use, height=100)
    
    st.write("**Applicable Statutory Filing Portals & Forms:**")
    st.write(", ".join([f"`{f}`" for f in active_data["forms"]]))
    
    if st.button("Generate Regulatory Intelligence Dossier"):
        st.session_state.dossier_ready = True
        st.success("Dossier compiled successfully across selected regulatory framework.")

with tab2:
    if st.session_state.get('dossier_ready'):
        st.subheader("Statutory Compliance & Readiness Scorecard")
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Audit Readiness Index", "84%", "Passing Grade")
        col_m2.metric("Pending Statutory Mandates", "2 Items", delta="-High Priority")
        
        st.write("### Mandatory Document Gap Matrix")
        st.table(pd.DataFrame(active_data["checklist"]))
    else:
        st.info("Fill device details and click 'Generate Regulatory Intelligence Dossier' to unlock analysis.")

with tab3:
    if st.session_state.get('dossier_ready'):
        st.subheader("Subject Expert Committee (SEC) Deficiency Forecaster")
        st.write("Predicted regulatory objections & recommended response strategies (RTQ):")
        
        for idx, item in enumerate(active_data["sec_queries"], 1):
            with st.expander(f"⚠️ Deficiency #{idx}: {item['deficiency']} ({item['risk_level']})", expanded=True):
                st.write(f"**Statutory Rule:** `{item['statutory_reference']}`")
                st.info(f"**Recommended Defense Strategy:** {item['recommended_defense']}")
        
        st.markdown("---")
        st.subheader("Substantial Equivalence Matrix")
        comp_table = {
            "Evaluation Parameter": ["Primary Material", "Sterilization Method", "Biocompatibility Standards", "Shelf-Life Stability"],
            "Target Device": ["Medical Grade Ti-6Al-4V", "Ethylene Oxide (EtO)", "ISO 10993 Series Passed", "3 Years Accelerated"],
            "Predicate Standard": ["Ti-6Al-4V ELI", "Gamma Irradiation", "ISO 10993 Compliant", "2 Years Real-Time"]
        }
        st.table(pd.DataFrame(comp_table))
        
        # Word Document Export Generation
        doc = Document()
        doc.add_heading(f"Regulatory Dossier - {device_name if device_name else 'Medical Device'}", 0)
        doc.add_paragraph(f"Jurisdiction: {selected_jurisdiction}")
        doc.add_paragraph(f"Risk Class: {risk_class}")
        doc.add_paragraph(f"Intended Use: {intended_use}")
        
        doc.add_heading("SEC Deficiency Forecaster & RTQ Strategy", level=1)
        for q in active_data["sec_queries"]:
            doc.add_paragraph(f"• Query: {q['deficiency']} [{q['risk_level']}]")
            doc.add_paragraph(f"  Statutory Ref: {q['statutory_reference']}")
            doc.add_paragraph(f"  Defense Strategy: {q['recommended_defense']}")
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        st.download_button(
            label="📥 Download Full Regulatory Dossier with SEC Defense (.DOCX)",
            data=buffer,
            file_name=f"{device_name if device_name else 'Device'}_Regulatory_Dossier.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.info("Generate dossier first to view SEC scrutiny forecast and export documentation.")
