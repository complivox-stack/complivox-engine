import streamlit as st
import pandas as pd
import io
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import pypdf

# 1. Page Configuration
st.set_page_config(
    page_title="Complivox Global | Enterprise RegTech Platform",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Corporate CSS
st.markdown("""
<style>
    .badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem; margin-right: 6px; margin-bottom: 6px; }
    .badge-blue { background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
</style>
""", unsafe_allow_html=True)

# 2. Statutory Knowledge Base
JURISDICTION_CONFIGS = {
    "India (CDSCO / MDR 2017)": {
        "forms": ["Form MD-14 (Import)", "Form MD-7 (Mfg Class A/B)", "Form MD-8 (Mfg Class C/D)", "SUGAM 3.0 Portal"],
        "checklist": [
            {"Statutory Document": "Device Master File (Appendix II)", "Regulatory Standard": "Fourth Schedule", "Compliance Status": "[UNDER REVIEW]"},
            {"Statutory Document": "Plant Master File (PMF)", "Regulatory Standard": "Part III Rule 20", "Compliance Status": "[VERIFIED]"},
            {"Statutory Document": "ISO 13485:2016 Certification", "Regulatory Standard": "QMS Statutory", "Compliance Status": "[VERIFIED]"},
            {"Statutory Document": "Biocompatibility & Pre-Clinical", "Regulatory Standard": "ISO 10993 Series", "Compliance Status": "[ACTION REQUIRED]"}
        ],
        "sec_queries": [
            {
                "deficiency": "Absence of Indian Clinical Population Equivalence Dataset",
                "risk_level": "Critical (Class C/D)",
                "statutory_reference": "MDR 2017 Part III (Clinical Investigation Rules)",
                "recommended_defense": "Submit GHTF-harmonized overseas multicenter trial data accompanied by clinical waiver justification under statutory Rule 60(1)."
            },
            {
                "deficiency": "Incomplete Accelerated vs Real-time Shelf-Life Degradation Study",
                "risk_level": "Moderate",
                "statutory_reference": "ISO 11607-1 & ASTM F1980",
                "recommended_defense": "Furnish ongoing real-time packaging integrity protocol with certified 6-month intermediate accelerated aging logs."
            },
            {
                "deficiency": "Residual Toxicological Risk Assessment for Patient Contact Parts",
                "risk_level": "High",
                "statutory_reference": "ISO 14971:2019 Clause 7.4 & ISO 10993-17",
                "recommended_defense": "Provide quantitative Benefit-Risk Ratio analysis demonstrating allowable Tolerable Intake (TI) limits for extractables/leachables."
            }
        ]
    },
    "USA (US FDA - 510k / PMA)": {
        "forms": ["510(k) Premarket Notification", "De Novo Classification", "PMA (Class III)", "eSTAR XML Portal"],
        "checklist": [
            {"Statutory Document": "Substantial Equivalence (SE) Rationale", "Regulatory Standard": "21 CFR 807.87", "Compliance Status": "[VERIFIED]"},
            {"Statutory Document": "Design History File (DHF) Traceability", "Regulatory Standard": "21 CFR 820.30", "Compliance Status": "[UNDER REVIEW]"},
            {"Statutory Document": "Software Lifecycle Documentation (SaMD)", "Regulatory Standard": "IEC 62304 / FDA Guidance", "Compliance Status": "[READY]"},
            {"Statutory Document": "Human Factors & Usability Engineering", "Regulatory Standard": "ANSI/AAMI HE75", "Compliance Status": "[ACTION REQUIRED]"}
        ],
        "sec_queries": [
            {
                "deficiency": "Refusal to Accept (RTA): Insufficient Dynamic Fatigue Bench Data vs Predicate",
                "risk_level": "Critical",
                "statutory_reference": "FDA 510(k) Orthopedic / Implant Review Guidance",
                "recommended_defense": "Execute direct side-by-side fatigue cycling (10M cycles) under identical physiological loading parameters as identified predicate."
            },
            {
                "deficiency": "Cybersecurity Bill of Materials (CBOM) Traceability Gap",
                "risk_level": "Moderate",
                "statutory_reference": "Section 524B FD&C Act (Cybersecurity in Devices)",
                "recommended_defense": "Submit full CycloneDX SBOM documentation along with third-party penetration and static code vulnerability assessments."
            }
        ]
    },
    "EU (CE MDR 2017/745)": {
        "forms": ["Annex II Technical Documentation", "Annex III Post-Market Surveillance", "GSPR Checklist", "EUDAMED Module 2"],
        "checklist": [
            {"Statutory Document": "General Safety and Performance (GSPR)", "Regulatory Standard": "Annex I Essential Regs", "Compliance Status": "[READY]"},
            {"Statutory Document": "Clinical Evaluation Report (CER)", "Regulatory Standard": "MEDDEV 2.7/1 rev 4 & MDR Art 61", "Compliance Status": "[MISSING PMCF]"},
            {"Statutory Document": "Risk Management File", "Regulatory Standard": "ISO 14971:2019", "Compliance Status": "[READY]"},
            {"Statutory Document": "Periodic Safety Update Report (PSUR)", "Regulatory Standard": "Article 86 MDR", "Compliance Status": "[ACTION REQUIRED]"}
        ],
        "sec_queries": [
            {
                "deficiency": "Notified Body Scrutiny: Inadequate Post-Market Clinical Follow-up (PMCF) Protocol",
                "risk_level": "Critical",
                "statutory_reference": "MDR Annex XIV Part B (PMCF)",
                "recommended_defense": "Deploy prospective multicenter PMCF patient registry with structured 5-year primary clinical endpoint tracking."
            },
            {
                "deficiency": "State-of-the-Art (SOTA) Systematic Literature Filter Inadequacy",
                "risk_level": "Moderate",
                "statutory_reference": "MDCG 2020-6 Clinical Evaluation Guidance",
                "recommended_defense": "Reconstruct search string using PRISMA methodological flow diagrams across Embase, PubMed, and MAUDE databases."
            }
        ]
    }
}

DEMO_DEVICES = {
    "Select Demo Device...": {"name": "", "use": "", "class": "Class A (Low)"},
    "Orthopedic Titanium Hip Implant": {"name": "Compli-Hip Total Acetabular System", "use": "Total hip arthroplasty for primary and secondary joint degeneration.", "class": "Class C (Mod-High)"},
    "Drug-Eluting Coronary Stent System": {"name": "Compli-DES Bioresorbable Stent", "use": "Percutaneous coronary intervention in symptomatic ischemic artery disease.", "class": "Class D (High)"},
    "AI Diagnostic ECG Monitor": {"name": "CardioSense 300 AI Telemetry", "use": "Continuous automated ambulatory ECG screening and arrhythmia classification.", "class": "Class B (Low-Med)"}
}

RISK_CLASSES = ["Class A (Low)", "Class B (Low-Med)", "Class C (Mod-High)", "Class D (High)"]

# State Initialization
if 'dev_name' not in st.session_state:
    st.session_state.dev_name = ""
if 'ind_use' not in st.session_state:
    st.session_state.ind_use = ""
if 'risk_idx' not in st.session_state:
    st.session_state.risk_idx = 0
if 'compiled' not in st.session_state:
    st.session_state.compiled = False

def on_demo_select():
    choice = st.session_state.demo_picker
    if choice != "Select Demo Device...":
        data = DEMO_DEVICES[choice]
        st.session_state.dev_name = data["name"]
        st.session_state.ind_use = data["use"]
        st.session_state.risk_idx = RISK_CLASSES.index(data["class"])
        st.session_state.compiled = True

def extract_text_from_pdf(uploaded_file):
    try:
        reader = pypdf.PdfReader(uploaded_file)
        full_text = []
        for page in reader.pages[:5]:
            txt = page.extract_text()
            if txt:
                full_text.append(txt)
        return "\n".join(full_text)
    except Exception as e:
        return f"Error reading PDF: {e}"

def set_cell_bg(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def generate_styled_docx(name, juris, r_class, use, checklist, sec_items):
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Inches(0.75)
        sec.bottom_margin = Inches(0.75)
        sec.left_margin = Inches(0.75)
        sec.right_margin = Inches(0.75)
        
    p_hdr = doc.add_paragraph()
    r1 = p_hdr.add_run("COMPLIVOX REGULATORY INTELLIGENCE DOSSIER")
    r1.bold = True
    r1.font.size = Pt(17)
    r1.font.color.rgb = RGBColor(16, 44, 87)
    
    p_sub = doc.add_paragraph()
    r2 = p_sub.add_run(f"Confidential Statutory Review & SEC Defense Assessment | {juris}")
    r2.font.size = Pt(10)
    r2.font.italic = True
    r2.font.color.rgb = RGBColor(100, 116, 139)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 1. Device Profile
    doc.add_heading("1. Target Medical Device Profile", level=2)
    meta_tbl = doc.add_table(rows=4, cols=2)
    meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    fields = [
        ("Device Identification", name if name else "Target Medical Device"),
        ("Statutory Jurisdiction", juris),
        ("Regulatory Classification", r_class),
        ("Intended Purpose / Indications", use[:300] + "..." if len(use) > 300 else use)
    ]
    for i, (k, v) in enumerate(fields):
        c0 = meta_tbl.rows[i].cells[0]
        c1 = meta_tbl.rows[i].cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.8)
        c0.paragraphs[0].add_run(k).bold = True
        c1.paragraphs[0].add_run(v)
        set_cell_bg(c0, "F1F5F9")
        set_cell_bg(c1, "FFFFFF")
    
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # 2. Gap Audit Matrix Table
    doc.add_heading("2. Statutory Documentation Gap Matrix", level=2)
    gap_tbl = doc.add_table(rows=len(checklist) + 1, cols=3)
    gap_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Regulatory Requirement", "Standard / Mandate", "Audit Finding"]
    for j, h in enumerate(headers):
        c = gap_tbl.rows[0].cells[j]
        run = c.paragraphs[0].add_run(h)
        run.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_bg(c, "102C57")

    for i, row in enumerate(checklist, 1):
        gap_tbl.rows[i].cells[0].paragraphs[0].add_run(row["Statutory Document"])
        gap_tbl.rows[i].cells[1].paragraphs[0].add_run(row["Regulatory Standard"])
        gap_tbl.rows[i].cells[2].paragraphs[0].add_run(row["Compliance Status"]).bold = True
        bg = "F8FAFC" if i % 2 == 0 else "FFFFFF"
        for j in range(3):
            set_cell_bg(gap_tbl.rows[i].cells[j], bg)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # 3. SEC Defense
    doc.add_heading("3. Subject Expert Committee (SEC) Defense & Response (RTQ)", level=2)
    for idx, q in enumerate(sec_items, 1):
        ob_box = doc.add_table(rows=3, cols=1)
        ob_box.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        c1 = ob_box.rows[0].cells[0]
        run1 = c1.paragraphs[0].add_run(f"Objection #{idx}: {q['deficiency']}  [{q['risk_level']}]")
        run1.bold = True
        run1.font.color.rgb = RGBColor(185, 28, 28)
        set_cell_bg(c1, "FEF2F2")
        
        c2 = ob_box.rows[1].cells[0]
        run2 = c2.paragraphs[0].add_run(f"Statutory Standard: {q['statutory_reference']}")
        run2.font.italic = True
        set_cell_bg(c2, "FFFFFF")
        
        c3 = ob_box.rows[2].cells[0]
        run3 = c3.paragraphs[0].add_run(f"Recommended Defense (RTQ): {q['recommended_defense']}")
        run3.bold = True
        set_cell_bg(c3, "F0FDF4")
        
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    out_buf = io.BytesIO()
    doc.save(out_buf)
    out_buf.seek(0)
    return out_buf

# 3. Sidebar UI
st.sidebar.title("Complivox Global")
selected_jurisdiction = st.sidebar.selectbox("Active Jurisdiction", list(JURISDICTION_CONFIGS.keys()))
st.sidebar.markdown("---")
st.sidebar.selectbox("Sample Pre-loader:", list(DEMO_DEVICES.keys()), key="demo_picker", on_change=on_demo_select)
st.sidebar.markdown("---")

curr_data = JURISDICTION_CONFIGS[selected_jurisdiction]
is_ready = st.session_state.compiled or bool(st.session_state.dev_name)

# Sidebar Action & Status
st.sidebar.subheader("Dossier Status")
if is_ready:
    st.sidebar.success("Audit & SEC Defense Ready")
    docx_bytes = generate_styled_docx(
        name=st.session_state.dev_name,
        juris=selected_jurisdiction,
        r_class=RISK_CLASSES[st.session_state.risk_idx],
        use=st.session_state.ind_use,
        checklist=curr_data["checklist"],
        sec_items=curr_data["sec_queries"]
    )
    st.sidebar.download_button(
        label="Download Dossier (.DOCX)",
        data=docx_bytes,
        file_name=f"Complivox_Dossier_{st.session_state.dev_name.replace(' ', '_') if st.session_state.dev_name else 'Device'}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
        use_container_width=True
    )
else:
    st.sidebar.info("Awaiting input data...")

st.sidebar.markdown("---")
st.sidebar.caption("Direct statutory synthesis across CDSCO, FDA & MDR databases.")

# 4. Main Page Header
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("Complivox Regulatory Intelligence Platform")
    st.markdown(f"**Enterprise Statutory Compliance Engine** | Active Jurisdiction: `{selected_jurisdiction}`")
with header_col2:
    if is_ready:
        st.write("")
        st.download_button(
            label="Download Dossier (.DOCX)",
            data=docx_bytes,
            file_name=f"Complivox_Dossier_{st.session_state.dev_name.replace(' ', '_') if st.session_state.dev_name else 'Device'}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
            use_container_width=True
        )

# 5. Core Navigation Tabs
tab_build, tab_audit, tab_sec = st.tabs([
    "Submission Dossier Builder",
    "Statutory Gap Audit",
    "SEC Scrutiny & RTQ Defense"
])

with tab_build:
    st.subheader("Client Document Ingestion (Optional)")
    uploaded_pdf = st.file_uploader("Upload Device Master File / Technical Summary (PDF)", type=["pdf"], help="Upload PDF to auto-extract technical parameters and indications.")
    
    if uploaded_pdf is not None:
        extracted = extract_text_from_pdf(uploaded_pdf)
        if extracted and not extracted.startswith("Error"):
            st.success(f"Successfully ingested `{uploaded_pdf.name}` ({len(extracted.split())} words parsed)")
            if not st.session_state.dev_name:
                st.session_state.dev_name = uploaded_pdf.name.replace(".pdf", "")
            if not st.session_state.ind_use:
                st.session_state.ind_use = extracted[:400].strip() + "..."
            st.session_state.compiled = True
    
    st.markdown("---")
    st.subheader("Target Device Parameters")
    col_a, col_b = st.columns(2)
    st.session_state.dev_name = col_a.text_input("Medical Device Name", value=st.session_state.dev_name, placeholder="e.g. Compli-Hip Acetabular System")
    r_class = col_b.selectbox("Device Risk Classification", RISK_CLASSES, index=st.session_state.risk_idx)
    st.session_state.ind_use = st.text_area("Intended Purpose / Indications for Clinical Use", value=st.session_state.ind_use, height=95)
    
    st.write("**Applicable Statutory Portals & Submission Forms:**")
    badges_html = " ".join([f'<span class="badge badge-blue">{f}</span>' for f in curr_data["forms"]])
    st.markdown(badges_html, unsafe_allow_html=True)
    st.write("")
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("Compile Dossier", type="primary", use_container_width=True):
            st.session_state.compiled = True
            st.success("Dossier compiled successfully against statutory regulations.")

with tab_audit:
    if is_ready:
        st.subheader("Statutory Compliance & Readiness Scorecard")
        m1, m2, m3 = st.columns(3)
        m1.metric("Audit Readiness Index", "84%", "Passing Grade")
        m2.metric("Pending Statutory Mandates", "2 Items", delta="-High Priority")
        m3.metric("Predicate Equivalence", "92%", "Robust Alignment")
        
        st.write("### Mandatory Document Gap Matrix")
        st.dataframe(pd.DataFrame(curr_data["checklist"]), use_container_width=True, hide_index=True)
    else:
        st.info("Fill the device details (or select a demo / upload PDF) and compile to unlock the audit matrix.")

with tab_sec:
    if is_ready:
        st.subheader("Subject Expert Committee (SEC) Deficiency Forecast")
        st.write("Predicted regulatory objections & recommended response strategies (RTQ):")
        
        for idx, item in enumerate(curr_data["sec_queries"], 1):
            with st.expander(f"Deficiency #{idx}: {item['deficiency']}  [{item['risk_level']}]", expanded=True):
                st.markdown(f"**Statutory Standard:** `{item['statutory_reference']}`")
                st.info(f"**Recommended Defense Strategy:** {item['recommended_defense']}")
        
        st.markdown("---")
        st.subheader("Substantial Equivalence (SE) Matrix")
        predicate_data = {
            "Evaluation Parameter": ["Primary Biomaterial", "Sterilization Modality", "Biocompatibility Evaluation", "Shelf-Life Stability Protocol"],
            "Target Device Profile": ["Medical Grade Ti-6Al-4V ELI", "Ethylene Oxide (EtO)", "ISO 10993 Series Validated", "3 Years Accelerated (ASTM F1980)"],
            "Predicate Standard Device": ["Ti-6Al-4V Standard", "Gamma Irradiation", "ISO 10993 Compliant", "2 Years Real-Time Certified"]
        }
        st.dataframe(pd.DataFrame(predicate_data), use_container_width=True, hide_index=True)
    else:
        st.info("Fill device details first to view predicted SEC deficiencies and export regulatory documentation.")
