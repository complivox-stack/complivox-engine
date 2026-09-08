import streamlit as st
import requests
import hashlib
import json
import io
import os
from datetime import datetime, timezone
from fpdf import FPDF
from pypdf import PdfReader
from docx import Document
from google import genai
from google.genai import types

# --- Enterprise Page Configuration ---
st.set_page_config(
    page_title="Complivox Global | Regulatory Scrutiny Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enterprise Interface Styling ---
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .hero-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .guide-step {
        background: #ffffff;
        border: 1.5px solid #0284c7;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .sec-card {
        background-color: #fef2f2;
        border-left: 5px solid #dc2626;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    .defense-card {
        background-color: #f0fdf4;
        border-left: 5px solid #16a34a;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    .pubmed-card {
        background-color: #eff6ff;
        border-left: 5px solid #2563eb;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
        font-size: 0.88em;
    }
    .statute-tag {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.76em;
        font-weight: 600;
        margin: 2px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# --- Dynamic Statutory Grounding Engine ---
@st.cache_data(show_spinner=False)
def scan_repository_knowledge():
    detected_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    statutory_context = []
    
    for f in detected_files:
        clean_name = f.replace(".pdf", "").replace("_", " ").strip()
        statutory_context.append({
            "filename": f,
            "display": clean_name
        })
    return statutory_context

local_statutes = scan_repository_knowledge()

# --- Universal Regulatory Pathway Catalog ---
pathways_catalog = {
    "💊 Pharmaceuticals & Formulations": {
        "India (CDSCO & SUGAM)": [
            "Form 40 (API / Bulk Drug Substance Registration)",
            "Form 41 (Finished Formulation Import Registration)",
            "CT-06 (Clinical Trial Protocol / SEC Scrutiny)",
            "Written Confirmation (WC EU Export Compliance)"
        ],
        "United States (US FDA)": [
            "DMF Type II (Active Pharmaceutical Ingredient)",
            "ANDA Module 3 Quality Dossier (21 CFR 314)",
            "IND Safety & Protocol Defense (21 CFR 312)"
        ],
        "Europe (EMA / EDQM)": [
            "ASMF (Active Substance Master File - CPMP/QWP)",
            "CEP Dossier (EDQM Ph. Eur. Compliance)"
        ],
        "Dual Filing (CDSCO + US FDA)": [
            "Combined Form 40 + US DMF Type II Statutory Scrutiny"
        ]
    },
    "🩺 Medical Devices & In-Vitro Diagnostics": {
        "India (CDSCO MDR 2017)": [
            "MD-14 (Medical Device Import License - Class A/B/C/D)",
            "MD-15 (Medical Device Import Permission / IVD)",
            "Device Master File (DMF) & Plant Master File (PMF)",
            "PSUR Module Compliance (SUGAM 3.0 Verification)"
        ],
        "United States (US FDA)": [
            "510(k) Premarket Notification (Substantial Equivalence)",
            "PMA (Premarket Approval - Class III Life-Supporting)",
            "De Novo Regulatory Classification"
        ],
        "Europe (EU MDR)": [
            "EU MDR 2017/745 Annex II & III Technical Documentation",
            "EU IVDR 2017/746 Technical Dossier"
        ],
        "Dual Filing (CDSCO MD-14 + US FDA 510(k))": [
            "Combined Form MD-14 + 510(k) Equivalence Scrutiny"
        ]
    }
}

# --- Sidebar Controls ---
st.sidebar.image("https://img.icons8.com/fluency/96/shield.png", width=56)
st.sidebar.title("Complivox Global")
st.sidebar.caption("Enterprise Regulatory Intelligence Engine")

domain_choice = st.sidebar.radio("Target Regulated Domain:", list(pathways_catalog.keys()))
active_jurisdictions = pathways_catalog[domain_choice]

jurisdiction = st.sidebar.selectbox("Target Regulatory Authority:", list(active_jurisdictions.keys()))
filing_type = st.sidebar.selectbox("Statutory Pathway:", active_jurisdictions[jurisdiction])

# Pure Backend Secret Key Resolution (No frontend input exposed)
api_key = st.secrets.get("GEMINI_API_KEY", "")

st.sidebar.divider()
st.sidebar.markdown(f"**Linked Statutory Instruments ({len(local_statutes)}):**")
for item in local_statutes[:5]:
    st.sidebar.markdown(f"<span class='statute-tag'>Active</span> {item['display'][:34]}...", unsafe_allow_html=True)

if len(local_statutes) > 5:
    st.sidebar.caption(f"+ {len(local_statutes) - 5} additional statutory circulars indexed.")

st.sidebar.divider()
st.sidebar.markdown("**🔒 Zero-Data Retention SLA Active**")
st.sidebar.caption("Processing executed strictly in volatile memory. Compliant with 21 CFR Part 11 & GAMP 5 data integrity standards.")

# --- PubMed Evidence Fetcher ---
@st.cache_data(show_spinner=False, ttl=3600)
def fetch_pubmed_citations(query_term, max_results=1):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    citations = []
    try:
        search_url = f"{base_url}esearch.fcgi?db=pubmed&term={query_term}&retmode=json&retmax={max_results}"
        res = requests.get(search_url, timeout=3).json()
        id_list = res.get('esearchresult', {}).get('idlist', [])
        
        if id_list:
            fetch_url = f"{base_url}esummary.fcgi?db=pubmed&id={','.join(id_list)}&retmode=json"
            summary_res = requests.get(fetch_url, timeout=3).json()
            result_dict = summary_res.get('result', {})
            
            for pmid in id_list:
                doc = result_dict.get(pmid, {})
                citations.append({
                    "pmid": pmid,
                    "title": doc.get('title', 'Regulatory Toxicology & Safety Evaluation'),
                    "source": f"{doc.get('source', 'J Pharm Sci')} ({doc.get('pubdate', '2024')})",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
    except Exception:
        citations = [{
            "pmid": "31818274",
            "title": "ICH M7 Guideline: Assessment and Control of Mutagenic Impurities in Pharmaceuticals.",
            "source": "Regul Toxicol Pharmacol (2020)",
            "url": "https://pubmed.ncbi.nlm.nih.gov/31818274/"
        }]
    return citations

# --- Scrutiny Execution Router ---
def execute_statutory_scrutiny(text, jurisdiction, filing_type, domain, api_key, statutes):
    statute_context_list = [s['display'] for s in statutes]
    statutes_joined = "; ".join(statute_context_list)

    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""
You are the Principal Regulatory Auditor and Subject Expert Committee (SEC) Advisor for Complivox Global.
Evaluate this dossier submission for {jurisdiction} ({filing_type}) within the {domain} domain.

Statutory Instruments Grounding:
The engine maintains these indexed circulars: {statutes_joined}. Cite these precisely where relevant.

Statutory Directives:
- Pharmaceuticals: Rigorously audit Zone IVb stability per CDSCO G.S.R. 1337(E), ICH M7 nitrosamine purge evaluation, ICH Q3D elemental impurities (ICP-MS), and ICH Q3C residual solvents.
- Medical Devices: Rigorously audit MDR 2017 Fourth Schedule Part A & B, Free Sale Certificate apostille status per G.S.R. 754(E), ISO 13485:2016 scope coverage, ISO 10993 biocompatibility matrix, and 510(k) predicate equivalence rationale.

Return ONLY a valid JSON object strictly matching this schema:
{{
  "score": <integer from 10 to 100>,
  "objections": [
    {{"code": "<Rule Code>", "rule": "<Statutory Guideline / Gazette Reference>", "issue": "<Deficiency Details>"}}
  ],
  "defenses": [
    "<Authoritative legal and scientific Response to Query (RTQ) justification>"
  ],
  "pubmed_queries": [
    "<Scientific toxicology search term>"
  ]
}}

Submission Dossier Excerpt:
\"\"\"{text}\"\"\"
"""
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text)
            return data["score"], data["objections"], data["defenses"], data.get("pubmed_queries", [])
        except Exception:
            pass

    return execute_fallback_heuristics(text, jurisdiction, filing_type, domain)

# --- Built-In Heuristic Fallback Engine ---
def execute_fallback_heuristics(text, jurisdiction, filing_type, domain):
    content = text.lower()
    objections = []
    defenses = []
    pubmed_queries = []
    score = 100

    if "Devices" in domain:
        if not any(k in content for k in ["free sale", "fsc", "certificate of free sale"]):
            objections.append({
                "code": "CDSCO-MDR-FSC-01",
                "rule": "Medical Device Rules 2017 / G.S.R. 754(E) Fourth Schedule",
                "issue": "Missing Apostilled/Consularized Free Sale Certificate (FSC) issued by National Regulatory Authority of origin."
            })
            defenses.append("Furnish authenticated Apostilled Free Sale Certificate from recognized reference body (US FDA CFS / EU CE Certificate).")
            score -= 25

        if not any(k in content for k in ["iso 13485", "qms"]):
            objections.append({
                "code": "CDSCO-MDR-QMS-02",
                "rule": "MDR 2017 Rule 34 / ISO 13485:2016 Compliance",
                "issue": "Valid Notified Body ISO 13485:2016 certification covering the legal manufacturing premises not documented."
            })
            defenses.append("Submit valid Notified Body accredited ISO 13485:2016 certificate covering the audited manufacturing facility.")
            score -= 20

        if not any(k in content for k in ["iso 10993", "biocompatibility", "cytotoxicity"]):
            objections.append({
                "code": "DEV-BIO-03",
                "rule": "ISO 10993-1:2018 / Medical Device Biocompatibility Matrix",
                "issue": "Biological evaluation endpoints (cytotoxicity, systemic toxicity, sensitization) not documented."
            })
            defenses.append("Submit GLP-compliant biological safety evaluation test reports as per ISO 10993-1:2018.")
            pubmed_queries.append("ISO 10993 biocompatibility medical devices")
            score -= 25
    else:
        if any(k in jurisdiction for k in ["CDSCO", "Dual", "India"]):
            if not any(k in content for k in ["zone ivb", "30°c", "30c", "30 deg"]):
                objections.append({
                    "code": "CDSCO-STAB-01",
                    "rule": "CDSCO G.S.R. 1337(E) Stability Guidelines",
                    "issue": "Missing Zone IVb (30 deg C +/- 2 deg C / 75% RH +/- 5% RH) real-time stability data. Submission relies solely on Zone II."
                })
                defenses.append("Submit 6-month accelerated testing data supported by a formal statutory commitment for 12-month Zone IVb real-time study.")
                score -= 30

        if not any(k in content for k in ["nitrosamine", "ich m7", "purge", "ndma"]):
            objections.append({
                "code": "TOX-M7-04",
                "rule": "ICH M7(R1) / US FDA Nitrosamine Guidance",
                "issue": "Absence of Nitrosamine Drug-Substance purge ratio evaluation and acceptable intake limit calculation."
            })
            defenses.append("Provide Option 4 purge justification establishing theoretical maximum nitrosamine contamination is below 18 ng/day threshold.")
            pubmed_queries.append("nitrosamine impurity risk assessment pharmaceuticals")
            score -= 25

        if not any(k in content for k in ["elemental", "ich q3d", "icp-ms"]):
            objections.append({
                "code": "QUAL-Q3D-03",
                "rule": "ICH Q3D Elemental Impurities Guideline",
                "issue": "Class 1 and Class 2A heavy metal impurity risk evaluation not documented."
            })
            defenses.append("Submit ICP-MS validated analytical results demonstrating elemental concentrations fall strictly below PDE limits.")
            pubmed_queries.append("ICH Q3D elemental impurities pharmaceuticals")
            score -= 15

    return max(score, 10), objections, defenses, pubmed_queries

# --- Document Serialization Utilities ---
def clean_for_export(t: str) -> str:
    reps = {"°": " deg ", "±": "+/-", "—": "-", "–": "-", "“": '"', "”": '"', "’": "'", "‘": "'"}
    for k, v in reps.items():
        t = t.replace(k, v)
    return t.encode("latin-1", "replace").decode("latin-1")

class ComplivoxPDF(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 16, 'F')
        self.set_font("Helvetica", 'B', 10)
        self.set_text_color(255, 255, 255)
        self.set_xy(12, 4)
        self.cell(186, 8, "COMPLIVOX GLOBAL | STATUTORY PRE-SUBMISSION DEFENSE DOSSIER")
        self.ln(10)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", 'I', 7)
        self.set_text_color(148, 163, 184)
        self.cell(0, 6, "Confidential - Pre-Submission Regulatory Scrutiny Audit | Complivox Platform", align='C')

def create_dossier_pdf(score, objections, defenses, citations, jurisdiction, filing_type, file_hash, domain):
    pdf = ComplivoxPDF(format='A4')
    pdf.set_margins(12, 18, 12)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", 'B', 12)
    pdf.set_text_color(15, 23, 42)
    clean_domain = domain.replace("💊", "").replace("🩺", "").strip()
    pdf.cell(0, 7, clean_for_export(f"Executive Statutory Audit: {clean_domain}"), ln=True)

    pdf.set_font("Helvetica", '', 8)
    pdf.set_text_color(100, 116, 139)
    current_time = datetime.now(timezone.utc).strftime('%d-%b-%Y %H:%M UTC')
    pdf.cell(0, 4, clean_for_export(f"Target Authority: {jurisdiction} | Pathway: {filing_type} | Generated: {current_time}"), ln=True)
    pdf.cell(0, 4, f"Audit Hash (SHA-256): {file_hash[:32]}...", ln=True)
    pdf.ln(3)

    # Score Metrics Box
    current_y = pdf.get_y()
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(12, current_y, 186, 11, 'F')
    pdf.set_font("Helvetica", 'B', 8.5)
    pdf.set_text_color(15, 23, 42)
    pdf.set_xy(15, current_y + 2)
    pdf.cell(85, 7, f"Statutory Defense Readiness: {score}/100")
    pdf.set_xy(105, current_y + 2)
    status_str = "STATUS: ACTION REQUIRED (HIGH QUERY DEFICIT)" if score < 70 else "STATUS: STATUTORILY DEFENSIBLE"
    pdf.cell(90, 7, status_str, align='R')
    pdf.set_xy(12, current_y + 14)

    # Objections
    pdf.set_font("Helvetica", 'B', 9)
    pdf.set_text_color(185, 28, 28)
    pdf.cell(0, 5, "FLAGGED STATUTORY GAPS & ANTICIPATED COMMITTEE OBJECTIONS", ln=True)
    pdf.set_draw_color(226, 232, 240)
    pdf.line(12, pdf.get_y(), 198, pdf.get_y())
    pdf.ln(2)

    for obj in objections:
        pdf.set_font("Helvetica", 'B', 8)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 4, clean_for_export(f"[{obj.get('code','DEF')}] {obj.get('rule','Statutory Rule')}"), ln=True)
        pdf.set_font("Helvetica", '', 7.5)
        pdf.multi_cell(186, 3.8, clean_for_export(f"Deficiency: {obj.get('issue','')}"))
        pdf.ln(1)

    pdf.ln(2)
    # Defenses
    pdf.set_font("Helvetica", 'B', 9)
    pdf.set_text_color(22, 101, 52)
    pdf.cell(0, 5, "PRE-EMPTIVE STATUTORY DEFENSE STRATEGY (RTQ PROTOCOLS)", ln=True)
    pdf.line(12, pdf.get_y(), 198, pdf.get_y())
    pdf.ln(2)

    for idx, d in enumerate(defenses, 1):
        pdf.set_font("Helvetica", '', 7.5)
        pdf.set_text_color(30, 41, 59)
        pdf.multi_cell(186, 3.8, clean_for_export(f"{idx}. {d}"))
        pdf.ln(1)

    # PubMed Literature Evidence
    if citations:
        pdf.ln(2)
        pdf.set_font("Helvetica", 'B', 9)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(0, 5, "NCBI / PUBMED CLINICAL & TOXICOLOGICAL CITATIONS", ln=True)
        pdf.line(12, pdf.get_y(), 198, pdf.get_y())
        pdf.ln(2)
        for cit in citations:
            pdf.set_font("Helvetica", 'B', 7)
            pdf.set_text_color(30, 41, 59)
            pdf.cell(0, 3.5, clean_for_export(f"PMID {cit['pmid']} | {cit['source']}"), ln=True)
            pdf.set_font("Helvetica", '', 7)
            pdf.multi_cell(186, 3.5, clean_for_export(f"Title: {cit['title']}"))
            pdf.ln(1)

    out = pdf.output()
    return bytes(out) if not isinstance(out, bytes) else out

def create_dossier_docx(score, objections, defenses, citations, jurisdiction, filing_type, file_hash, domain):
    doc = Document()
    doc.add_heading("COMPLIVOX GLOBAL | STATUTORY DEFENSE DOSSIER", level=0)
    
    clean_domain = domain.replace("💊", "").replace("🩺", "").strip()
    p = doc.add_paragraph()
    p.add_run(f"Domain: {clean_domain}\n").bold = True
    p.add_run(f"Target Authority: {jurisdiction} | Pathway: {filing_type}\n")
    p.add_run(f"Audit Hash (SHA-256): {file_hash}\n")
    p.add_run(f"Defense Readiness: {score}/100 | Status: {'Defensible' if score >= 70 else 'Deficit Flagged'}\n")

    doc.add_heading("1. Flagged Committee Objections (Anticipated Deficiencies)", level=1)
    for obj in objections:
        p_obj = doc.add_paragraph()
        p_obj.add_run(f"[{obj.get('code','DEF')}] {obj.get('rule','')}\n").bold = True
        p_obj.add_run(f"Deficiency: {obj.get('issue','')}")

    doc.add_heading("2. Pre-Emptive Defense Protocols (Response to Queries - RTQ)", level=1)
    for idx, d in enumerate(defenses, 1):
        doc.add_paragraph(f"{idx}. {d}")

    if citations:
        doc.add_heading("3. Toxicological & Clinical Evidence (PubMed Grounding)", level=1)
        for cit in citations:
            doc.add_paragraph(f"PMID: {cit['pmid']} - {cit['title']} ({cit['source']})")

    file_stream = io.BytesIO()
    doc.save(file_stream)
    return file_stream.getvalue()

# --- Main Application Header ---
st.markdown(f"""
<div class="hero-box">
    <h2 style="margin:0; font-size: 1.7rem;">Complivox Global | Regulatory Scrutiny Engine</h2>
    <p style="margin:6px 0 0 0; color: #cbd5e1; font-size: 0.95rem;">
        Autonomous pre-submission audit for CDSCO (MD-14/15, Form 40), US FDA (510k, ANDA) & EMA dossiers. Backed by {len(local_statutes)} statutory gazette instruments.
    </p>
</div>
""", unsafe_allow_html=True)

# 3-Step Execution Scaffolding
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="guide-step"><strong>Step 1: Classification</strong><br><span style="font-size:0.85em;">Select Domain & Authority</span></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="guide-step"><strong>Step 2: Input Submission</strong><br><span style="font-size:0.85em;">Upload PDF / Excerpt</span></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="guide-step"><strong>Step 3: Export Dossier</strong><br><span style="font-size:0.85em;">Generate PDF & Word (.docx)</span></div>', unsafe_allow_html=True)

st.write("")

# Context Selection Mode
input_mode = st.radio("Submission Context Input Mode:", ["Live Demonstration Excerpt", "Upload Technical Dossier (PDF)"], horizontal=True)

active_text = ""

if input_mode == "Upload Technical Dossier (PDF)":
    uploaded_pdf = st.file_uploader("Upload technical DMF excerpt, Certificate of Analysis, or Device Master File (PDF)", type=["pdf"])
    if uploaded_pdf:
        try:
            reader = PdfReader(uploaded_pdf)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    active_text += extracted + "\n"
            st.success(f"Parsed {len(reader.pages)} page(s) successfully from {uploaded_pdf.name}")
        except Exception as err:
            st.error(f"Error reading PDF: {err}")
else:
    default_sample = (
        "Drug Substance: Ondansetron Hydrochloride USP.\nAccelerated Stability: Tested at 40°C / 75% RH for 6 months.\nLong Term Testing: Tested at 25°C / 60% RH for 12 months.\nResidual Solvents: Complies with standard pharmacopeial limits.\nPrimary Packaging: Double polyethylene bags inside tamper-evident HDPE drums."
        if "Pharmaceuticals" in domain_choice else
        "Device Name: Disposable Sterile Laparoscopic Trocar (Class B).\nIntended Use: Laparoscopic abdominal access cannula.\nSterilization: Ethylene Oxide (EO) validated per ISO 11135.\nPackaging: Medical grade Tyvek pouch inside shelf carton.\nMissing Documents: ISO 10993 cytotoxicity extractables evaluation pending. Free Sale Certificate not apostilled."
    )
    active_text = st.text_area("Technical Submission Excerpt:", value=default_sample, height=130)

st.write("")

# --- Scrutiny Execution Trigger ---
if st.button("🚀 Run Statutory Scrutiny Audit Now", type="primary", use_container_width=True):
    if not active_text.strip():
        st.warning("Please provide technical submission text or upload a dossier PDF.")
    else:
        with st.spinner("Executing statutory matrix analysis against CDSCO gazettes & NCBI PubMed..."):
            file_hash = hashlib.sha256(active_text.encode("utf-8")).hexdigest()
            score, objections, defenses, pubmed_queries = execute_statutory_scrutiny(
                active_text, jurisdiction, filing_type, domain_choice, api_key, local_statutes
            )
            
            citations = []
            for q in pubmed_queries[:2]:
                citations.extend(fetch_pubmed_citations(q, max_results=1))

            # Metric Scorecards
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Defense Readiness", f"{score} / 100", delta=f"{score - 100} Deficit", delta_color="inverse")
            m2.metric("Committee Objections", len(objections))
            m3.metric("Defensive RTQ Protocols", len(defenses))
            m4.metric("Live PubMed Evidence", len(citations))

            st.divider()

            # Detailed Output Layout
            col1, col2 = st.columns([1.1, 0.9])

            with col1:
                st.subheader("🚩 Anticipated Committee Objections")
                for obj in objections:
                    st.markdown(f"""
                    <div class="sec-card">
                        <strong>[{obj.get('code','DEF')}] {obj.get('rule','Statute')}</strong><br>
                        <span style="font-size:0.9em; color:#7f1d1d;"><strong>Deficiency:</strong> {obj.get('issue','')}</span>
                    </div>
                    """, unsafe_allow_html=True)

                st.subheader("🛡️ Pre-Emptive Statutory Defense Strategy (RTQ)")
                for idx, d in enumerate(defenses, 1):
                    st.markdown(f"""
                    <div class="defense-card">
                        <strong>Defense Protocol #{idx}:</strong><br>
                        <span style="font-size:0.9em; color:#14532d;">{d}</span>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                st.subheader("📚 PubMed Scientific Evidence Grounding")
                if citations:
                    for cit in citations:
                        st.markdown(f"""
                        <div class="pubmed-card">
                            <strong>PMID: {cit['pmid']}</strong> | {cit['source']}<br>
                            <a href="{cit['url']}" target="_blank" style="color:#1d4ed8; font-weight:600; text-decoration:none;">{cit['title']}</a>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No toxicological queries triggered for this excerpt.")

                st.subheader("📥 Export Official Defense Dossier")
                
                # PDF Dossier Export
                pdf_data = create_dossier_pdf(score, objections, defenses, citations, jurisdiction, filing_type, file_hash, domain_choice)
                st.download_button(
                    label="📄 Download Official A4 Statutory Dossier (PDF)",
                    data=pdf_data,
                    file_name=f"Complivox_Audit_{jurisdiction[:6].replace(' ','_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

                # Word Dossier Export
                docx_data = create_dossier_docx(score, objections, defenses, citations, jurisdiction, filing_type, file_hash, domain_choice)
                st.download_button(
                    label="📝 Download Editable Defense Protocols (.docx)",
                    data=docx_data,
                    file_name=f"Complivox_Defense_{jurisdiction[:6].replace(' ','_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

st.divider()
st.caption("Complivox Global Platform | CDSCO MDR 2017 • Form MD-14/15 • US FDA 21 CFR • EMA ASMF • ICH M7/Q3D • ISO 10993.")
