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
    page_title="Complivox Global | Enterprise RegTech RIM Platform",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Corporate CSS
st.markdown("""
<style>
    .badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem; margin-right: 6px; margin-bottom: 6px; }
    .badge-blue { background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
    .badge-green { background-color: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }
</style>
""", unsafe_allow_html=True)

# 2. Comprehensive Multi-Domain Statutory Database
REGULATORY_DATABASE = {
    "Medical Devices & IVDs": {
        "India (CDSCO / MDR 2017)": {
            "forms": ["Form MD-14 (Import)", "Form MD-7 (Mfg Class A/B)", "Form MD-8 (Mfg Class C/D)", "SUGAM 3.0 Portal"],
            "classes": ["Class A (Low)", "Class B (Low-Med)", "Class C (Mod-High)", "Class D (High)"],
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
            ],
            "predicate_matrix": {
                "Evaluation Parameter": ["Primary Biomaterial", "Sterilization Modality", "Biocompatibility Evaluation", "Shelf-Life Stability Protocol"],
                "Target Profile": ["Medical Grade Ti-6Al-4V ELI", "Ethylene Oxide (EtO)", "ISO 10993 Series Validated", "3 Years Accelerated (ASTM F1980)"],
                "Benchmark Standard": ["Ti-6Al-4V Standard", "Gamma Irradiation", "ISO 10993 Compliant", "2 Years Real-Time Certified"]
            }
        },
        "USA (US FDA - 510k / PMA)": {
            "forms": ["510(k) Premarket Notification", "De Novo Classification", "PMA (Class III)", "eSTAR XML Portal"],
            "classes": ["Class I (Exempt/510k)", "Class II (510k)", "Class III (PMA)"],
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
            ],
            "predicate_matrix": {
                "Evaluation Parameter": ["Device Design", "Biocompatibility", "Bench Fatigue", "Cybersecurity Baseline"],
                "Target Profile": ["Anatomical Contour Fit", "ISO 10993-1 / FDA Guidance", "10 Million Cycles Passed", "Section 524B Compliant SBOM"],
                "Benchmark Standard": ["Standard Predicate Fit", "ISO 10993 Compliant", "5 Million Cycles Certified", "NIST Traceable Baseline"]
            }
        },
        "EU (CE MDR 2017/745)": {
            "forms": ["Annex II Technical Documentation", "Annex III Post-Market Surveillance", "GSPR Checklist", "EUDAMED Module 2"],
            "classes": ["Class I", "Class IIa", "Class IIb", "Class III"],
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
            ],
            "predicate_matrix": {
                "Evaluation Parameter": ["GSPR Traceability", "Equivalence Route", "Clinical Evidence Level", "PMCF Plan"],
                "Target Profile": ["Full Annex I Gap Audit", "Technical Equivalence Dossier", "Prospective Human Data", "Active 5-Year Registry"],
                "Benchmark Standard": ["MDD Legacy Clearance", "Literature Equivalence", "Retrospective Cohort", "Literature Vigilance Only"]
            }
        }
    },
    "Pharmaceuticals, APIs & Biologics": {
        "India (CDSCO / NDCT Rules 2019)": {
            "forms": ["Form 40 (Import Registration)", "Form 28 (Mfg Allopathic)", "Form CT-23 (Permission for New Drug)", "Form CT-06 (CT Approval)"],
            "classes": ["New Chemical Entity (NCE)", "Subsequent New Drug (SND)", "Fixed Dose Combination (FDC)", "Active Pharmaceutical Ingredient (API)"],
            "checklist": [
                {"Statutory Document": "eCTD Module 3 (Quality & CMC)", "Regulatory Standard": "ICH M4Q / Schedule M", "Compliance Status": "[VERIFIED]"},
                {"Statutory Document": "Bioequivalence (BE) Study Report", "Regulatory Standard": "NDCT 2019 Table 1", "Compliance Status": "[READY]"},
                {"Statutory Document": "Accelerated & Real-time Stability Data", "Regulatory Standard": "ICH Q1A (Zone IVb: 30°C/75% RH)", "Compliance Status": "[UNDER REVIEW]"},
                {"Statutory Document": "Genotoxic Impurity Profiling", "Regulatory Standard": "ICH M7 (R1)", "Compliance Status": "[ACTION REQUIRED]"}
            ],
            "sec_queries": [
                {
                    "deficiency": "Requirement for Local Phase III Clinical Trial in Indian Population",
                    "risk_level": "Critical (NCE/SND)",
                    "statutory_reference": "NDCT Rules 2019 Rule 75 & Schedule II",
                    "recommended_defense": "Apply for local Phase III clinical trial waiver citing orphan designation, unmet medical need, and global Phase III safety parity in GHTF countries."
                },
                {
                    "deficiency": "Inadequate Zone IVb Real-Time Stability Data for Climatic Zone Compatibility",
                    "risk_level": "High",
                    "statutory_reference": "CDSCO Stability Guidelines & ICH Q1A (R2)",
                    "recommended_defense": "Submit committed 12-month real-time testing stability data at 30°C ± 2°C / 75% RH ± 5% RH accompanied by 6-month accelerated degradation stress reports."
                },
                {
                    "deficiency": "Absence of Nitrosamine Impurity Risk Assessment and Purge Rationale",
                    "risk_level": "High",
                    "statutory_reference": "ICH Q3A/B & CDSCO Nitrosamine Advisory",
                    "recommended_defense": "Furnish detailed Step 1 Confirmatory testing logs with LC-MS/MS quantification demonstrating levels strictly below 0.03 ppm (or acceptable intake limits)."
                }
            ],
            "predicate_matrix": {
                "Evaluation Parameter": ["Dosage Form & Strength", "Dissolution In-Vitro Profile", "Impurity Profile (ICH Q3A/B)", "Stability Specification"],
                "Target Profile": ["Immediate Release Tablet (100mg)", "f2 similarity > 65% across pH 1.2, 4.5, 6.8", "Specified Impurities < 0.15%", "Zone IVb (30°C/75% RH) Validated"],
                "Benchmark Standard": ["Reference Listed Drug (RLD) 100mg", "Standard Reference Release Curve", "Innovator Drug Characterized", "ICH Standard Compliance"]
            }
        },
        "USA (US FDA - CDER / CBER)": {
            "forms": ["eCTD IND Application", "NDA (505(b)(1) / 505(b)(2))", "ANDA (505(j) Generic)", "Drug Master File (Type II DMF)"],
            "classes": ["NDA (Innovator NCE)", "505(b)(2) Modified Drug", "ANDA (Generic Equivalent)", "Biologic License Application (BLA)"],
            "checklist": [
                {"Statutory Document": "eCTD Module 2 (Summaries & Overviews)", "Regulatory Standard": "21 CFR 314.50", "Compliance Status": "[VERIFIED]"},
                {"Statutory Document": "In-Vitro / In-Vivo Correlation (IVIVC)", "Regulatory Standard": "FDA Bioanalytical Guidance", "Compliance Status": "[READY]"},
                {"Statutory Document": "Current Good Manufacturing Practice (cGMP)", "Regulatory Standard": "21 CFR Part 210/211", "Compliance Status": "[VERIFIED]"},
                {"Statutory Document": "Extractables & Leachables in Container Closure", "Regulatory Standard": "USP <1663> & USP <1664>", "Compliance Status": "[ACTION REQUIRED]"}
            ],
            "sec_queries": [
                {
                    "deficiency": "Complete Response Letter (CRL) Warning: Incomplete Nitrosamine Risk Control Strategy",
                    "risk_level": "Critical",
                    "statutory_reference": "FDA Guidance: Control of Nitrosamine Impurities in Human Drugs",
                    "recommended_defense": "Deploy root-cause synthesis analysis confirming zero secondary amine interactions with active nitrite excipients."
                },
                {
                    "deficiency": "Bioequivalence Narrow Therapeutic Index (NTI) Study Statistical Power Margin",
                    "risk_level": "High",
                    "statutory_reference": "FDA Draft Guidance on Statistical Approaches to BE",
                    "recommended_defense": "Re-calculate 90% Confidence Interval under reference-scaled average bioequivalence (RSABE) method demonstrating 80.00% - 125.00% strict adherence."
                }
            ],
            "predicate_matrix": {
                "Evaluation Parameter": ["Reference Standard", "Bioequivalence Window", "Container Closure System", "Sterility Assurance Level (SAL)"],
                "Target Profile": ["US Innovator Reference Listed Drug", "90% CI strictly 80-125% (AUC & Cmax)", "HDPE Bottle with induction seal", "SAL 10^-6 (Validated Aseptic Processing)"],
                "Benchmark Standard": ["Orange Book Reference Standard", "Equivalence Criteria", "Commercial Standard", "USP <71> Sterility Pass"]
            }
        },
        "EU (EMA - Decentralised / Centralised)": {
            "forms": ["eCTD Marketing Authorisation (MAA)", "Active Substance Master File (ASMF)", "Risk Management Plan (RMP)", "Periodic Benefit-Risk Evaluation (PBRER)"],
            "classes": ["Centralised (Biotech/NCE)", "Decentralised Procedure (DCP)", "Mutual Recognition Procedure (MRP)", "National MAA"],
            "checklist": [
                {"Statutory Document": "Module 1.8.2 (Risk Management Plan - EU RMP)", "Regulatory Standard": "EMA GVP Module V", "Compliance Status": "[READY]"},
                {"Statutory Document": "Module 3 (Quality Overall Summary - ASMF)", "Regulatory Standard": "EU GMP Volume 4", "Compliance Status": "[VERIFIED]"},
                {"Statutory Document": "Environmental Risk Assessment (ERA)", "Regulatory Standard": "EMA/CHMP/SWP/4447/00", "Compliance Status": "[UNDER REVIEW]"},
                {"Statutory Document": "Paediatric Investigation Plan (PIP) Waiver", "Regulatory Standard": "Regulation (EC) No 1901/2006", "Compliance Status": "[ACTION REQUIRED]"}
            ],
            "sec_queries": [
                {
                    "deficiency": "Day 120 List of Questions: Insufficient Phase I ERA (Environmental Fate) Data",
                    "risk_level": "Moderate",
                    "statutory_reference": "EMA Guideline on the Environmental Risk Assessment of Medicinal Products",
                    "recommended_defense": "Provide quantified PEC/PNEC ratios and OECD 301 biodegradation study confirming low environmental persistence threshold."
                },
                {
                    "deficiency": "Validation of Analytical Procedures under Revised ICH Q2(R2) / Q14",
                    "risk_level": "High",
                    "statutory_reference": "ICH Q2(R2) & ICH Q14 Analytical Procedure Development",
                    "recommended_defense": "Submit full analytical Lifecycle documentation including Multivariate Statistical Verification for robustness."
                }
            ],
            "predicate_matrix": {
                "Evaluation Parameter": ["Marketing Route", "Comparator Product", "Pharmacovigilance System", "Environmental Assessment"],
                "Target Profile": ["Centralised / DCP Pathway", "EU Reference Medicinal Product", "EU-QPPV & PSMF Module Validated", "Phase I ERA Action Trigger Cleared"],
                "Benchmark Standard": ["EU Originator MAA", "Reference Standard", "Standard GVP System", "ERA Compliant"]
            }
        }
    }
}

DEMO_DATASETS = {
    "Medical Devices & IVDs": {
        "Select Sample Device...": {"name": "", "use": "", "class": "Class A (Low)"},
        "Orthopedic Titanium Hip Implant": {"name": "Compli-Hip Total Acetabular System", "use": "Total hip arthroplasty for primary and secondary joint degeneration.", "class": "Class C (Mod-High)"},
        "Drug-Eluting Coronary Stent System": {"name": "Compli-DES Bioresorbable Stent", "use": "Percutaneous coronary intervention in symptomatic ischemic artery disease.", "class": "Class D (High)"},
        "AI Diagnostic ECG Monitor": {"name": "CardioSense 300 AI Telemetry", "use": "Continuous automated ambulatory ECG screening and arrhythmia classification.", "class": "Class B (Low-Med)"}
    },
    "Pharmaceuticals, APIs & Biologics": {
        "Select Sample Molecule...": {"name": "", "use": "", "class": "New Chemical Entity (NCE)"},
        "Oncology Kinase Inhibitor Tablet": {"name": "Compli-Kinase (Afatinib Generic)", "use": "First-line treatment of patients with metastatic non-small cell lung cancer (NSCLC) with EGFR mutations.", "class": "Subsequent New Drug (SND)"},
        "Monoclonal Antibody Biosimilar (Trastuzumab)": {"name": "CompliMab (Trastuzumab Biosimilar 440mg)", "use": "Treatment of HER2-overexpressing metastatic breast cancer and gastric adenocarcinoma.", "class": "New Chemical Entity (NCE)"},
        "Cardiovascular Fixed-Dose Combination": {"name": "Compli-Cardio Duo (Telmisartan + Amlodipine)", "use": "Treatment of essential hypertension in adult patients whose blood pressure is not adequately controlled.", "class": "Fixed Dose Combination (FDC)"}
    }
}

# State Management
if 'domain' not in st.session_state:
    st.session_state.domain = "Medical Devices & IVDs"
if 'product_name' not in st.session_state:
    st.session_state.product_name = ""
if 'indication_text' not in st.session_state:
    st.session_state.indication_text = ""
if 'risk_class_choice' not in st.session_state:
    st.session_state.risk_class_choice = ""
if 'compiled' not in st.session_state:
    st.session_state.compiled = False

def on_demo_select():
    domain = st.session_state.domain_picker
    choice = st.session_state.demo_picker
    if choice and not choice.startswith("Select Sample"):
        data = DEMO_DATASETS[domain][choice]
        st.session_state.product_name = data["name"]
        st.session_state.indication_text = data["use"]
        st.session_state.risk_class_choice = data["class"]
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

def generate_styled_docx(domain, name, juris, r_class, use, checklist, sec_items, pred_matrix):
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Inches(0.75)
        sec.bottom_margin = Inches(0.75)
        sec.left_margin = Inches(0.75)
        sec.right_margin = Inches(0.75)
        
    p_hdr = doc.add_paragraph()
    r1 = p_hdr.add_run(f"COMPLIVOX GLOBAL REGULATORY DOSSIER ({domain.upper()})")
    r1.bold = True
    r1.font.size = Pt(16)
    r1.font.color.rgb = RGBColor(16, 44, 87)
    
    p_sub = doc.add_paragraph()
    r2 = p_sub.add_run(f"Statutory Audit, eCTD / DMF Gap Analysis & Subject Expert Committee (SEC) Defense | {juris}")
    r2.font.size = Pt(10)
    r2.font.italic = True
    r2.font.color.rgb = RGBColor(100, 116, 139)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 1. Product Profile
    doc.add_heading("1. Target Product Statutory Profile", level=2)
    meta_tbl = doc.add_table(rows=5, cols=2)
    meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    fields = [
        ("Industry Domain", domain),
        ("Product / Molecule Identification", name if name else "Target Product"),
        ("Statutory Jurisdiction", juris),
        ("Regulatory Classification", r_class),
        ("Intended Purpose / Indications", use[:350] + "..." if len(use) > 350 else use)
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

    # 3. SEC Defense Boxes
    doc.add_heading("3. Regulatory Scrutiny / SEC Defense & Response (RTQ)", level=2)
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
selected_domain = st.sidebar.selectbox(
    "Target Regulatory Domain",
    list(REGULATORY_DATABASE.keys()),
    key="domain_picker"
)

domain_data = REGULATORY_DATABASE[selected_domain]
selected_jurisdiction = st.sidebar.selectbox("Active Jurisdiction", list(domain_data.keys()))
st.sidebar.markdown("---")

demo_options = list(DEMO_DATASETS[selected_domain].keys())
st.sidebar.selectbox("Sample Pre-loader:", demo_options, key="demo_picker", on_change=on_demo_select)
st.sidebar.markdown("---")

curr_config = domain_data[selected_jurisdiction]
is_ready = st.session_state.compiled or bool(st.session_state.product_name)

# Sidebar Action & Status
st.sidebar.subheader("Dossier Status")
if is_ready:
    st.sidebar.success(f"{selected_domain} Ready")
    docx_bytes = generate_styled_docx(
        domain=selected_domain,
        name=st.session_state.product_name,
        juris=selected_jurisdiction,
        r_class=st.session_state.risk_class_choice if st.session_state.risk_class_choice else curr_config["classes"][0],
        use=st.session_state.indication_text,
        checklist=curr_config["checklist"],
        sec_items=curr_config["sec_queries"],
        pred_matrix=curr_config["predicate_matrix"]
    )
    st.sidebar.download_button(
        label="Download Dossier (.DOCX)",
        data=docx_bytes,
        file_name=f"Complivox_{selected_domain[:3].upper()}_Dossier.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
        use_container_width=True
    )
else:
    st.sidebar.info("Awaiting compilation...")

st.sidebar.markdown("---")
st.sidebar.caption("Enterprise Regulatory Intelligence Engine | Multi-Domain Module")

# 4. Main Page Header
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("Complivox Regulatory Intelligence Platform")
    badge_type = "badge-blue" if "Medical" in selected_domain else "badge-green"
    st.markdown(f'<span class="badge {badge_type}">{selected_domain}</span> **Statutory Compliance Framework:** `{selected_jurisdiction}`', unsafe_allow_html=True)
with header_col2:
    if is_ready:
        st.write("")
        st.download_button(
            label="Download Dossier (.DOCX)",
            data=docx_bytes,
            file_name=f"Complivox_{selected_domain[:3].upper()}_Dossier.docx",
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
    st.subheader(f"📁 Document Ingestion ({'DMF/Tech File' if 'Medical' in selected_domain else 'eCTD/Module 3/COA'})")
    uploaded_pdf = st.file_uploader(f"Upload Technical Dossier / Certificate of Analysis (PDF)", type=["pdf"], help="Upload PDF to auto-extract technical specifications and indications.")
    
    if uploaded_pdf is not None:
        extracted = extract_text_from_pdf(uploaded_pdf)
        if extracted and not extracted.startswith("Error"):
            st.success(f"Successfully parsed `{uploaded_pdf.name}` ({len(extracted.split())} words ingested)")
            if not st.session_state.product_name:
                st.session_state.product_name = uploaded_pdf.name.replace(".pdf", "")
            if not st.session_state.indication_text:
                st.session_state.indication_text = extracted[:450].strip() + "..."
            st.session_state.compiled = True
    
    st.markdown("---")
    st.subheader("Target Statutory Parameters")
    col_a, col_b = st.columns(2)
    st.session_state.product_name = col_a.text_input(
        "Product / Molecule Identification",
        value=st.session_state.product_name,
        placeholder="e.g. Compli-DES Stent or Afatinib Tablet 40mg"
    )
    
    class_list = curr_config["classes"]
    current_idx = class_list.index(st.session_state.risk_class_choice) if st.session_state.risk_class_choice in class_list else 0
    st.session_state.risk_class_choice = col_b.selectbox("Regulatory Classification / Drug Category", class_list, index=current_idx)
    
    st.session_state.indication_text = st.text_area(
        "Intended Clinical Purpose / Indications for Use",
        value=st.session_state.indication_text,
        height=95,
        placeholder="Enter indications, therapeutic class, mechanism of action, or clinical scope..."
    )
    
    st.write("**Applicable Statutory Portals & Mandatory Submission Forms:**")
    badges_html = " ".join([f'<span class="badge badge-blue">{f}</span>' for f in curr_config["forms"]])
    st.markdown(badges_html, unsafe_allow_html=True)
    st.write("")
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("Compile Dossier", type="primary", use_container_width=True):
            st.session_state.compiled = True
            st.success(f"{selected_domain} dossier compiled successfully against statutory regulations.")

with tab_audit:
    if is_ready:
        st.subheader("Statutory Compliance & Readiness Scorecard")
        m1, m2, m3 = st.columns(3)
        m1.metric("Audit Readiness Index", "86%", "Passing Grade")
        m2.metric("Pending Statutory Mandates", "2 Items", delta="-High Priority")
        m3.metric("Benchmark Alignment", "94%", "Robust Parity")
        
        st.write("### Mandatory Document Gap Matrix")
        st.dataframe(pd.DataFrame(curr_config["checklist"]), use_container_width=True, hide_index=True)
    else:
        st.info("Fill the parameters (or select a sample / upload PDF) and compile to unlock the gap audit matrix.")

with tab_sec:
    if is_ready:
        st.subheader("Regulatory Scrutiny / SEC Deficiency Forecast")
        st.write("Predicted regulatory objections & recommended response strategies (RTQ):")
        
        for idx, item in enumerate(curr_config["sec_queries"], 1):
            with st.expander(f"Deficiency #{idx}: {item['deficiency']}  [{item['risk_level']}]", expanded=True):
                st.markdown(f"**Statutory Rule / Standard:** `{item['statutory_reference']}`")
                st.info(f"**Recommended Defense Strategy:** {item['recommended_defense']}")
        
        st.markdown("---")
        st.subheader(f"{'Substantial Equivalence (SE) Matrix' if 'Medical' in selected_domain else 'Reference Listed Drug (RLD) Equivalence Matrix'}")
        st.dataframe(pd.DataFrame(curr_config["predicate_matrix"]), use_container_width=True, hide_index=True)
    else:
        st.info("Compile the dossier first to view predicted regulatory deficiencies and export documentation.")
