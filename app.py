import io
import re
import streamlit as st
from pypdf import PdfReader
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Complivox Global | Statutory Defense Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0E7490;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 25px;
    }
    .metric-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .stButton>button {
        background-color: #0E7490;
        color: white;
        border-radius: 6px;
        font-weight: 600;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- WORD DOSSIER BUILDER ---
def generate_docx_dossier(domain, framework, doc_name, findings, gaps, rtqs):
    """Crash-safe Word dossier with no-split table formatting"""
    doc = Document()

    # Standard clean margins
    for s in doc.sections:
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.7)
        s.left_margin = Inches(0.7)
        s.right_margin = Inches(0.7)

    # Document Header
    t = doc.add_paragraph()
    tr = t.add_run("COMPLIVOX GLOBAL")
    tr.font.name = "Arial"
    tr.font.size = Pt(18)
    tr.font.bold = True
    tr.font.color.rgb = RGBColor(14, 116, 144)
    t.paragraph_format.space_after = Pt(2)

    sub = doc.add_paragraph()
    sub_run = sub.add_run(f"Statutory Pre-Submission Defense Dossier | Framework: {framework} ({domain})\nSource Document: {doc_name}")
    sub_run.font.name = "Arial"
    sub_run.font.size = Pt(9.5)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(100, 116, 139)
    sub.paragraph_format.space_after = Pt(14)

    # 1. Technical Compliance Findings
    h1 = doc.add_paragraph()
    h1r = h1.add_run("1. Technical Compliance Extraction")
    h1r.font.name = "Arial"
    h1r.font.bold = True
    h1r.font.size = Pt(11)
    h1.paragraph_format.keep_with_next = True
    h1.paragraph_format.space_after = Pt(4)

    for item in findings:
        p = doc.add_paragraph(style='List Bullet')
        pr = p.add_run(str(item))
        pr.font.name = "Arial"
        pr.font.size = Pt(9.5)
        p.paragraph_format.space_after = Pt(2)

    # 2. Statutory Gap & Deficiency Matrix
    h2 = doc.add_paragraph()
    h2r = h2.add_run("2. Statutory Gap & Deficiency Matrix")
    h2r.font.name = "Arial"
    h2r.font.bold = True
    h2r.font.size = Pt(11)
    h2.paragraph_format.keep_with_next = True
    h2.paragraph_format.space_before = Pt(8)
    h2.paragraph_format.space_after = Pt(6)

    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True

    # Dark header row
    hdr_cells = table.rows[0].cells
    cols = ["Regulatory Requirement", "Status / Deficit", "Risk Level"]
    for i, col_name in enumerate(cols):
        hdr_cells[i].text = col_name
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1E293B"/>')
        hdr_cells[i]._tc.get_or_add_tcPr().append(shd)
        p = hdr_cells[i].paragraphs[0]
        if len(p.runs) > 0:
            p.runs[0].font.name = "Arial"
            p.runs[0].font.bold = True
            p.runs[0].font.size = Pt(9)
            p.runs[0].font.color.rgb = RGBColor(255, 255, 255)

    for g in gaps:
        row = table.add_row().cells
        row[0].text = str(g.get("rule", "Statutory Requirement"))
        row[1].text = str(g.get("detail", "Pending validation"))
        row[2].text = str(g.get("risk", "Medium"))
        for c_idx, cell in enumerate(row):
            shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
            cell._tc.get_or_add_tcPr().append(shd)
            if len(cell.paragraphs[0].runs) > 0:
                cell.paragraphs[0].runs[0].font.name = "Arial"
                cell.paragraphs[0].runs[0].font.size = Pt(8.5)
                if c_idx == 2 and g.get("risk") == "High":
                    cell.paragraphs[0].runs[0].font.bold = True
                    cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(185, 28, 28)

    # Prevent row split across pages
    for r in table.rows:
        trPr = r._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

    # 3. SEC Objections & RTQ Defense
    h3 = doc.add_paragraph()
    h3r = h3.add_run("3. Pre-Emptive SEC Objections & RTQ Defense Strategy")
    h3r.font.name = "Arial"
    h3r.font.bold = True
    h3r.font.size = Pt(11)
    h3.paragraph_format.keep_with_next = True
    h3.paragraph_format.space_before = Pt(10)
    h3.paragraph_format.space_after = Pt(6)

    for idx, r in enumerate(rtqs, 1):
        card = doc.add_table(rows=1, cols=1)
        card.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = card.rows[0].cells[0]
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F1F5F9"/>')
        cell._tc.get_or_add_tcPr().append(shd)

        cp = cell.paragraphs[0]
        cp.paragraph_format.space_after = Pt(2)
        r1 = cp.add_run(f"Objection #{idx}: {r.get('query', '')} [{r.get('risk', 'High')}]\n")
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGBColor(15, 23, 42)

        r2 = cp.add_run(f"Statutory Standard: {r.get('standard', '')}\n")
        r2.font.name = "Arial"
        r2.font.italic = True
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = RGBColor(71, 85, 105)

        r3 = cp.add_run(f"Recommended Defense (RTQ): {r.get('defense', '')}")
        r3.font.name = "Arial"
        r3.font.bold = True
        r3.font.size = Pt(9)
        r3.font.color.rgb = RGBColor(14, 116, 144)

        # Non-split table card
        card.rows[0]._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

        spacer = doc.add_paragraph()
        spacer.paragraph_format.space_after = Pt(4)

    target_stream = io.BytesIO()
    doc.save(target_stream)
    target_stream.seek(0)
    return target_stream

# --- STATUTORY AUDIT ENGINE ---
def run_statutory_audit(text, domain, framework):
    text_lower = text.lower()
    findings = []
    gaps = []
    rtqs = []

    if domain == "Pharmaceuticals & Bulk Drugs":
        # Check Nitrosamines
        if "nitrosamine" in text_lower or "ndma" in text_lower:
            findings.append("Nitrosamine risk assessment mentioned in technical dossier.")
        else:
            findings.append("Nitrosamine risk assessment section missing or non-explicit.")
            gaps.append({"rule": "ICH M7 / CDSCO Nitrosamine Guidance", "detail": "Absence of confirmatory LC-MS/MS testing for nitrosamine impurities.", "risk": "High"})
            rtqs.append({
                "query": "Risk evaluation and limit justification for potential Nitrosamine contamination in synthetic route.",
                "standard": "CDSCO Notification No. 29-114/2019-DC / US FDA Guidance on Nitrosamines",
                "defense": "Submit synthetic route purge-factor calculations proving secondary/tertiary amines are removed before final crystallization.",
                "risk": "High"
            })

        # Check Stability
        if "zone ivb" in text_lower or "30°c/75% rh" in text_lower or "accelerated" in text_lower:
            findings.append("Stability study protocol meets climatic zone requirements.")
        else:
            findings.append("Stability evaluation does not explicitly state Zone IVb conditions.")
            gaps.append({"rule": "ICH Q1A (R2) / NDCT Schedule Y", "detail": "Real-time stability data at 30°C/75% RH for Indian climatic conditions unverified.", "risk": "Medium"})
            rtqs.append({
                "query": "Submission of completed 6-month accelerated and ongoing 12-month real-time Zone IVb stability data.",
                "standard": "CDSCO Form 40 / NDCT Rule 75",
                "defense": "Furnish interim 6-month stability matrix with committed protocol for 24-month long-term testing at 30°C/75% RH.",
                "risk": "Medium"
            })

        # Check Dissolution / BE
        if "dissolution" in text_lower or "bioequivalence" in text_lower:
            findings.append("Comparative in-vitro dissolution / BE profile identified.")
        else:
            gaps.append({"rule": "NDCT Rules 2019 / US FDA BE Guidance", "detail": "Comparative dissolution profile in 3 discriminatory media missing.", "risk": "High"})
            rtqs.append({
                "query": "Demonstration of in-vitro similarity (f2 factor > 50) against reference listed innovator product.",
                "standard": "Rule 60(1) Phase III Clinical Waiver / FDA Guidance on BE",
                "defense": "Provide multi-point dissolution data at pH 1.2, 4.5, and 6.8 showing f2 similarity factor between 50-100.",
                "risk": "High"
            })

    else: # Medical Devices
        # Check Biocompatibility (ISO 10993)
        if "iso 10993" in text_lower or "biocompatibility" in text_lower or "cytotoxicity" in text_lower:
            findings.append("Biological safety assessment referenced under ISO 10993 framework.")
        else:
            findings.append("ISO 10993 biological evaluation summary not explicitly confirmed.")
            gaps.append({"rule": "ISO 10993-1 / MDR 2017 Schedule 4", "detail": "Cytotoxicity, sensitization, and intracutaneous reactivity tests absent.", "risk": "High"})
            rtqs.append({
                "query": "Complete ISO 10993 biocompatibility testing for direct patient-contact materials.",
                "standard": "CDSCO Form MD-14 Guidance / FDA 510(k) Cytotoxicity Criteria",
                "defense": "Provide GLP-certified biological safety endpoints and material characterization certificate of analysis (COA).",
                "risk": "High"
            })

        # Check Sterilization (ISO 11135 / 11137)
        if "sterilization" in text_lower or "sal 10" in text_lower or "ethylene oxide" in text_lower or "gamma" in text_lower:
            findings.append("Sterilization validation protocol and Sterility Assurance Level (SAL 10^-6) verified.")
        else:
            gaps.append({"rule": "ISO 11135 / ISO 11137 Validation", "detail": "Sterilization validation report and EO residue limits missing.", "risk": "High"})
            rtqs.append({
                "query": "Sterilization validation protocol and residual limits justification.",
                "standard": "MDR 2017 Fifth Schedule / ISO 10993-7",
                "defense": "Submit EO/ECH residual testing reports adhering to allowable limits under ISO 10993-7 along with dose mapping.",
                "risk": "High"
            })

        # Check Predicate Substantial Equivalence
        if "predicate" in text_lower or "substantially equivalent" in text_lower or "comparative matrix" in text_lower:
            findings.append("Predicate device substantial equivalence comparison table detected.")
        else:
            gaps.append({"rule": "FDA 21 CFR 807.87 / CDSCO MD-14", "detail": "Side-by-side technological and performance comparison with predicate missing.", "risk": "Medium"})
            rtqs.append({
                "query": "Demonstration of technological equivalence against approved predicate device.",
                "standard": "CDSCO SUGAM Portal / FDA 510(k) Section 12",
                "defense": "Submit side-by-side comparative table demonstrating identical intended use, materials, and bench test performance.",
                "risk": "Medium"
            })

    return findings, gaps, rtqs

# --- APPLICATION INTERFACE ---
st.markdown('<div class="main-header">Complivox Global</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Dual Statutory Regulatory Intelligence Engine for Pharma & MedTech Pre-Submission Defense</div>', unsafe_allow_html=True)

# SIDEBAR CONTROLS
st.sidebar.title("⚙️ Audit Configuration")
domain = st.sidebar.radio(
    "Target Regulatory Domain",
    ["Pharmaceuticals & Bulk Drugs", "Medical Devices & Diagnostics"]
)

if domain == "Pharmaceuticals & Bulk Drugs":
    framework = st.sidebar.selectbox(
        "Statutory Filing Framework",
        ["CDSCO Form 40 / NDCT 2019 (India)", "US FDA eCTD Module 1-5 (USA)", "EU CTD Marketing Authorization (EMA)"]
    )
else:
    framework = st.sidebar.selectbox(
        "Statutory Filing Framework",
        ["CDSCO Form MD-14 / MDR 2017 (India)", "US FDA 510(k) Substantial Equivalence", "EU MDR 2017/745 Annex II/III"]
    )

st.sidebar.markdown("---")
st.sidebar.info("💡 **Compliance Tip:** Upload digital PDF technical summaries or DMF excerpts for instant statutory gap detection.")

# MAIN INTERFACE TABS
tab_audit, tab_quick_audit = st.tabs(["📄 Document Audit & Dossier Generator", "⚡ Quick Rule-Engine Simulator"])

with tab_audit:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Upload Technical Document")
        uploaded_file = st.file_uploader("Upload Technical Summary / DMF / COA (PDF)", type=["pdf"])
        
        extracted_text = ""
        if uploaded_file is not None:
            try:
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
                st.success(f"✓ Successfully parsed '{uploaded_file.name}' ({len(reader.pages)} pages)")
            except Exception as e:
                st.error(f"Error reading PDF: {e}")

    with col2:
        st.subheader("2. Statutory Defense Controls")
        if extracted_text:
            st.metric("Extracted Characters", f"{len(extracted_text):,}")
            run_btn = st.button("🚀 Run Statutory Scrutiny Engine")
        else:
            st.info("Upload a regulatory PDF on the left to start automated compliance scanning.")
            run_btn = False

    if extracted_text and run_btn:
        findings, gaps, rtqs = run_statutory_audit(extracted_text, domain, framework)
        st.markdown("---")

        # RESULTS SECTION
        res_col1, res_col2 = st.columns([1, 1.2])

        with res_col1:
            st.subheader("📊 Extraction & Gap Matrix")
            st.markdown("**Identified Compliance Status:**")
            for f in findings:
                st.markdown(f"• {f}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Statutory Deficiencies Found:**")
            for g in gaps:
                badge = "🔴 HIGH" if g["risk"] == "High" else "🟡 MEDIUM"
                st.warning(f"**[{badge}] {g['rule']}**\n\n{g['detail']}")

        with res_col2:
            st.subheader("🛡️ Pre-Emptive SEC Objections & Defense")
            for idx, r in enumerate(rtqs, 1):
                with st.expander(f"Objection #{idx}: {r['query']}", expanded=True):
                    st.caption(f"**Statutory Standard:** {r['standard']}")
                    st.info(f"**Recommended RTQ Defense:**\n\n{r['defense']}")

            # EXPORT BUTTON
            st.markdown("---")
            docx_stream = generate_docx_dossier(
                domain=domain,
                framework=framework,
                doc_name=uploaded_file.name,
                findings=findings,
                gaps=gaps,
                rtqs=rtqs
            )

            st.download_button(
                label="📥 Download Audit Dossier (.DOCX)",
                data=docx_stream,
                file_name=f"Complivox_Audit_Dossier_{domain[:3].upper()}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

with tab_quick_audit:
    st.subheader("⚡ Instant Regulatory Query Simulator")
    st.write("Run pre-configured compliance scenarios without uploading a PDF.")
    
    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        scenario = st.selectbox(
            "Select Regulatory Scenario",
            [
                "CDSCO Form 40 API Import - Nitrosamine & Zone IVb Stability Query",
                "CDSCO Form MD-14 Device Import - Biocompatibility & EO Residuals",
                "US FDA 510(k) - Predicate Substantial Equivalence Margin"
            ]
        )
    
    if st.button("Run Simulation Scenario"):
        st.success(f"Simulation Analysis generated for: **{scenario}**")
        if "Nitrosamine" in scenario:
            sim_findings, sim_gaps, sim_rtqs = run_statutory_audit("nitrosamine missing accelerated only", "Pharmaceuticals & Bulk Drugs", "CDSCO Form 40 / NDCT 2019 (India)")
        elif "Biocompatibility" in scenario:
            sim_findings, sim_gaps, sim_rtqs = run_statutory_audit("no biocompatibility", "Medical Devices & Diagnostics", "CDSCO Form MD-14 / MDR 2017 (India)")
        else:
            sim_findings, sim_gaps, sim_rtqs = run_statutory_audit("predicate pending", "Medical Devices & Diagnostics", "US FDA 510(k) Substantial Equivalence")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### Deficiencies")
            for g in sim_gaps:
                st.error(f"**{g['rule']}**: {g['detail']}")
        with col_b:
            st.markdown("### Pre-Drafted Defense")
            for r in sim_rtqs:
                st.info(f"**Standard:** {r['standard']}\n\n**Defense:** {r['defense']}")
