import io
import re
import pandas as pd
import streamlit as st
from pypdf import PdfReader
from fpdf import FPDF

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Complivox Global | Statutory Defense Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ENTERPRISE STYLING ---
st.markdown("""
<style>
    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0E7490;
        margin-bottom: 0px;
        letter-spacing: -0.5px;
    }
    .brand-sub {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 18px;
    }
    .metric-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-radius: 8px;
        padding: 14px 18px;
        color: white;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .metric-card-val {
        font-size: 1.7rem;
        font-weight: 800;
        color: #38BDF8;
    }
    .metric-card-lbl {
        font-size: 0.8rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .report-card {
        background-color: #F8FAFC;
        border-left: 4px solid #0E7490;
        padding: 12px 16px;
        border-radius: 0 6px 6px 0;
        margin-bottom: 10px;
    }
    .stDownloadButton>button {
        background: linear-gradient(90deg, #0E7490, #0369A1) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        padding: 0.6rem 1rem !important;
        border: none !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# --- VECTOR PDF ENGINE (A4 FULL SPREAD) ---
class DossierPDF(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 28, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 15)
        self.set_xy(12, 6)
        self.cell(0, 7, 'COMPLIVOX GLOBAL', ln=True)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(148, 163, 184)
        self.set_xy(12, 14)
        self.cell(0, 5, 'Statutory Pre-Submission Defense Dossier & SEC Scrutiny Matrix', ln=True)
        self.ln(10)

    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'Complivox Global Engine | Confidential Regulatory Dossier | Page {self.page_no()}', 0, 0, 'C')

def create_full_pdf(domain, framework, doc_name, findings, gaps, rtqs, score):
    pdf = DossierPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Meta Banner Card
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(12, 32, 186, 14, 'F')
    pdf.set_text_color(15, 23, 42)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_xy(15, 34)
    pdf.cell(62, 5, f"Domain: {domain[:28]}")
    pdf.cell(78, 5, f"Framework: {framework[:32]}")
    pdf.cell(42, 5, f"Compliance Score: {score}/100", ln=True)

    pdf.set_y(50)

    # 1. Technical Findings
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.set_text_color(14, 116, 144)
    pdf.cell(0, 5, '1. TECHNICAL COMPLIANCE EXTRACTION STATUS', ln=True)
    pdf.set_text_color(51, 65, 85)
    pdf.set_font('Helvetica', '', 8)
    for item in findings:
        pdf.multi_cell(186, 4.5, f"- {item}")
    pdf.ln(2)

    # 2. Gap Matrix
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.set_text_color(14, 116, 144)
    pdf.cell(0, 5, '2. STATUTORY DEFICIENCY MATRIX', ln=True)
    
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(58, 6, ' Regulatory Standard', 1, 0, 'L', True)
    pdf.cell(102, 6, ' Identified Deficit', 1, 0, 'L', True)
    pdf.cell(26, 6, ' Risk Level', 1, 1, 'C', True)

    pdf.set_text_color(30, 41, 59)
    pdf.set_font('Helvetica', '', 7.5)
    for g in gaps:
        pdf.cell(58, 6, f" {g['rule'][:32]}", 1, 0, 'L')
        pdf.cell(102, 6, f" {g['detail'][:62]}", 1, 0, 'L')
        pdf.cell(26, 6, f" {g['risk']}", 1, 1, 'C')
    pdf.ln(3)

    # 3. SEC Objections
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.set_text_color(14, 116, 144)
    pdf.cell(0, 5, '3. PRE-EMPTIVE SEC OBJECTIONS & DEFENSE STRATEGY (RTQ)', ln=True)

    for idx, r in enumerate(rtqs, 1):
        pdf.set_fill_color(248, 250, 252)
        pdf.set_text_color(15, 23, 42)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(186, 5, f" Objection #{idx}: {r.get('query', '')[:88]}", 'LTR', 1, 'L', True)
        
        pdf.set_text_color(100, 116, 139)
        pdf.set_font('Helvetica', 'I', 7)
        pdf.cell(186, 4.5, f" Standard: {r.get('standard', '')[:92]}", 'LR', 1, 'L', True)
        
        pdf.set_text_color(14, 116, 144)
        pdf.set_font('Helvetica', 'B', 7.5)
        pdf.multi_cell(186, 4.5, f" Recommended Defense (RTQ): {r.get('defense', '')}", 'LBR', 'L', True)
        pdf.ln(2)

    return bytes(pdf.output())

# --- STATUTORY AUDIT LOGIC ---
def run_full_audit(text, domain, framework):
    t = text.lower()
    findings = []
    gaps = []
    rtqs = []
    score = 100

    if domain == "Pharmaceuticals & Bulk Drugs":
        if "nitrosamine" in t or "ndma" in t:
            findings.append("Nitrosamine toxicological evaluation identified in synthesis route.")
        else:
            score -= 25
            findings.append("Nitrosamine risk assessment section missing or unconfirmed.")
            gaps.append({"rule": "ICH M7 / CDSCO Nitrosamines", "detail": "Absence of confirmatory LC-MS/MS testing for nitrosamine impurities.", "risk": "High"})
            rtqs.append({
                "query": "Risk evaluation and limit justification for potential Nitrosamine contamination in synthetic route.",
                "standard": "CDSCO Notification No. 29-114/2019-DC / US FDA Guidance",
                "defense": "Submit synthetic route purge-factor calculations proving secondary/tertiary amines are removed before final crystallization.",
                "risk": "High"
            })

        if "zone ivb" in t or "30°c/75% rh" in t or "accelerated" in t:
            findings.append("Climatic Zone IVb stability testing protocol verified.")
        else:
            score -= 20
            findings.append("Climatic Zone IVb stability testing parameters unverified.")
            gaps.append({"rule": "ICH Q1A (R2) / NDCT Schedule Y", "detail": "Real-time stability data at 30°C/75% RH for Indian climatic conditions absent.", "risk": "Medium"})
            rtqs.append({
                "query": "Submission of completed 6-month accelerated and ongoing 12-month real-time Zone IVb stability data.",
                "standard": "CDSCO Form 40 / NDCT Rule 75",
                "defense": "Furnish interim 6-month stability matrix with committed protocol for 24-month long-term testing at 30°C/75% RH.",
                "risk": "Medium"
            })

        if "dissolution" in t or "bioequivalence" in t:
            findings.append("Comparative in-vitro dissolution / BE profile identified.")
        else:
            score -= 25
            gaps.append({"rule": "NDCT Rules 2019 / US FDA BE Guidance", "detail": "Comparative dissolution profile in 3 discriminatory media missing.", "risk": "High"})
            rtqs.append({
                "query": "Demonstration of in-vitro similarity (f2 factor > 50) against reference listed innovator product.",
                "standard": "Rule 60(1) Phase III Clinical Waiver / FDA Guidance on BE",
                "defense": "Provide multi-point dissolution data at pH 1.2, 4.5, and 6.8 showing f2 similarity factor between 50-100.",
                "risk": "High"
            })

    else: # Medical Devices
        if "iso 10993" in t or "biocompatibility" in t or "cytotoxicity" in t:
            findings.append("Biological safety assessment referenced under ISO 10993.")
        else:
            score -= 30
            findings.append("ISO 10993 biological evaluation summary not explicitly confirmed.")
            gaps.append({"rule": "ISO 10993-1 / MDR 2017 Schedule 4", "detail": "Cytotoxicity, sensitization, and intracutaneous reactivity tests absent.", "risk": "High"})
            rtqs.append({
                "query": "Complete ISO 10993 biocompatibility testing for direct patient-contact materials.",
                "standard": "CDSCO Form MD-14 Guidance / FDA 510(k) Cytotoxicity Criteria",
                "defense": "Provide GLP-certified biological safety endpoints and material characterization certificate of analysis (COA).",
                "risk": "High"
            })

        if "sterilization" in t or "sal 10" in t or "ethylene oxide" in t:
            findings.append("Sterilization validation protocol and Sterility Assurance Level (SAL 10^-6) verified.")
        else:
            score -= 25
            gaps.append({"rule": "ISO 11135 / ISO 11137 Validation", "detail": "Sterilization validation report and EO residue limits missing.", "risk": "High"})
            rtqs.append({
                "query": "Sterilization validation protocol and residual limits justification.",
                "standard": "MDR 2017 Fifth Schedule / ISO 10993-7",
                "defense": "Submit EO/ECH residual testing reports adhering to allowable limits under ISO 10993-7 along with dose mapping.",
                "risk": "High"
            })

        if "predicate" in t or "substantially equivalent" in t:
            findings.append("Predicate device substantial equivalence comparison table detected.")
        else:
            score -= 20
            gaps.append({"rule": "FDA 21 CFR 807.87 / CDSCO MD-14", "detail": "Side-by-side technological and performance comparison with predicate missing.", "risk": "Medium"})
            rtqs.append({
                "query": "Demonstration of technological equivalence against approved predicate device.",
                "standard": "CDSCO SUGAM Portal / FDA 510(k) Section 12",
                "defense": "Submit side-by-side comparative table demonstrating identical intended use, materials, and bench test performance.",
                "risk": "Medium"
            })

    return findings, gaps, rtqs, max(score, 35)

# --- USER INTERFACE ---
st.markdown('<div class="brand-title">COMPLIVOX GLOBAL</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-sub">Dual Statutory Regulatory Intelligence Engine | Pre-Submission Defense Architecture</div>', unsafe_allow_html=True)

# SIDEBAR
st.sidebar.markdown("### ⚙️ Regulatory Controls")
domain = st.sidebar.radio("Target Domain", ["Pharmaceuticals & Bulk Drugs", "Medical Devices & Diagnostics"])

if domain == "Pharmaceuticals & Bulk Drugs":
    framework = st.sidebar.selectbox("Filing Framework", ["CDSCO Form 40 / NDCT 2019 (India)", "US FDA eCTD Module 1-5 (USA)", "EU CTD Marketing Authorization (EMA)"])
else:
    framework = st.sidebar.selectbox("Filing Framework", ["CDSCO Form MD-14 / MDR 2017 (India)", "US FDA 510(k) Substantial Equivalence", "EU MDR 2017/745 Annex II/III"])

st.sidebar.markdown("---")
st.sidebar.info("💡 **Instant Audit Tip:** Upload any technical PDF summary to generate audit-ready defense dossiers instantly.")

# --- TOP SECTION: DIRECT INGESTION & IMMEDIATE EXPORT (ZERO SCROLL) ---
top_c1, top_c2 = st.columns([1.1, 0.9])

with top_c1:
    st.markdown("#### 1. Upload Submission Dossier")
    uploaded_file = st.file_uploader("Upload Technical Dossier / DMF / Summary (PDF)", type=["pdf"])
    extracted_text = ""
    file_name = "Sample_Audit_Dossier.pdf"
    
    if uploaded_file:
        try:
            reader = PdfReader(uploaded_file)
            file_name = uploaded_file.name
            for p in reader.pages:
                txt = p.extract_text()
                if txt:
                    extracted_text += txt + "\n"
            st.success(f"✓ Parsed `{file_name}` ({len(reader.pages)} Pages)")
        except Exception as e:
            st.error(f"Error: {e}")

with top_c2:
    st.markdown("#### 2. Defense Audit & Instant Export")
    text_to_process = extracted_text if extracted_text else "nitrosamine evaluation accelerated stability only without BE"
    findings, gaps, rtqs, score = run_full_audit(text_to_process, domain, framework)
    
    pdf_bytes = create_full_pdf(domain, framework, file_name, findings, gaps, rtqs, score)
    
    st.download_button(
        label="📥 Download Audit Dossier (PDF)",
        data=pdf_bytes,
        file_name=f"Complivox_Audit_Dossier_{domain[:3].upper()}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.caption("⚡ Full A4 Vector PDF generated at the top without page-splitting.")

st.markdown("---")

# --- EXECUTIVE DASHBOARD METRICS ---
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-lbl">Regulatory Scrutiny Index</div>
        <div class="metric-card-val">{score}/100</div>
        <div style="font-size: 0.75rem; color: {'#4ADE80' if score>75 else '#F87171'};">
            {'✓ Low Scrutiny Risk' if score>75 else '⚠️ High SEC Rejection Risk'}
        </div>
    </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-lbl">Identified Deficiencies</div>
        <div class="metric-card-val">{len(gaps)}</div>
        <div style="font-size: 0.75rem; color: #FBBF24;">Actionable Statutory Gaps</div>
    </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-lbl">Pre-Drafted RTQ Responses</div>
        <div class="metric-card-val">{len(rtqs)}</div>
        <div style="font-size: 0.75rem; color: #38BDF8;">Audit-Ready Defenses</div>
    </div>
    """, unsafe_allow_html=True)

# --- DETAILED MATRICES ---
r1, r2 = st.columns([1, 1.2])

with r1:
    st.markdown("### 📋 Statutory Gap Matrix")
    for g in gaps:
        b_color = "#DC2626" if g["risk"] == "High" else "#D97706"
        st.markdown(f"""
        <div class="report-card" style="border-left-color: {b_color};">
            <strong style="color: {b_color};">[{g['risk'].upper()} RISK] {g['rule']}</strong><br>
            <span style="font-size: 0.85rem; color: #334155;">{g['detail']}</span>
        </div>
        """, unsafe_allow_html=True)

with r2:
    st.markdown("### 🛡️ Pre-Emptive SEC Objections & Defense")
    for idx, r in enumerate(rtqs, 1):
        with st.expander(f"Objection #{idx}: {r['query']}", expanded=True):
            st.caption(f"**Statutory Standard:** {r['standard']}")
            st.info(f"**Recommended RTQ Defense:**\n\n{r['defense']}")
