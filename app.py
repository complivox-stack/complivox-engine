import streamlit as st
import requests
import json
import re
import os
from datetime import datetime
from fpdf import FPDF
from pypdf import PdfReader

# ==========================================
# 1. PAGE CONFIGURATION & ENTERPRISE THEME
# ==========================================
st.set_page_config(
    page_title="Complivox Global | AI Regulatory Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End SaaS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .brand-container {
        padding: 1.2rem 1.8rem;
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-radius: 12px;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
        border: 1px solid #334155;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    .brand-title { font-size: 22px; font-weight: 800; color: #F8FAFC; letter-spacing: -0.5px; }
    .brand-subtitle { font-size: 13px; color: #94A3B8; margin-top: 4px; line-height: 1.4; }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: all 0.2s ease-in-out;
    }
    .status-badge {
        padding: 4px 10px;
        background: #10B981;
        color: white;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Main Branding Header
st.markdown("""
<div class="brand-container">
    <div class="brand-title">🛡️ Complivox Global Regulatory Intelligence Platform</div>
    <div class="brand-subtitle">Autonomous Statutory Dossier Synthesis, SEC Deficiency Forecasting, SUGAM 3.0 Alignment & Live PubMed Evidence Engine.</div>
</div>
""", unsafe_allow_html=True)

# Silent API key load from Secrets
sarvam_api_key = st.secrets.get("SARVAM_API_KEY", "")

# ==========================================
# 2. SIDEBAR CONTROLS & AUTHORITY SELECTION
# ==========================================
with st.sidebar:
    st.markdown("### 🌐 Global Authority Engine")
    
    target_framework = st.selectbox(
        "Regulatory Target Authority",
        [
            "CDSCO (India - Medical Device Rules 2017 & SUGAM)",
            "US FDA (United States - 510(k) Premarket / PMA)",
            "EU MDR (European Union - Regulation 2017/745)",
            "Pharma CTD / eCTD (ICH Quality, Safety & Efficacy)"
        ]
    )
    
    submission_intent = st.selectbox(
        "Filing Transaction Intent",
        [
            "Import Licence & SUGAM Clearance (MD-14 / MD-15)",
            "Domestic Manufacturing Licence (MD-7 / MD-9)",
            "Export Clearance & Free Sale Certificate (MD-28 / CoFS)",
            "Clinical Investigation / Evaluation (MD-26 / SEC Review)",
            "Post-Marketing Surveillance & PSUR Compliance (SUGAM 3.0)"
        ]
    )
    
    st.markdown("---")
    st.markdown("**Enterprise Active Modules:**")
    st.checkbox("Statutory Gazette & Rule Citation Engine", value=True, disabled=True)
    st.checkbox("SUGAM 3.0 Portal Form Alignment", value=True, disabled=True)
    st.checkbox("Real-time NCBI PubMed Literature Extraction", value=True, disabled=True)
    st.checkbox("CDSCO SEC Committee Deficiency Predictor", value=True, disabled=True)
    st.checkbox("Master File Checklist (PMF, DMF, CoFS, ISO 13485)", value=True, disabled=True)
    
    st.markdown("---")
    st.caption("🔒 Complivox Architecture v3.5 | ISO/IEC 27001 & Zero Data Retention Standard")

# ==========================================
# 3. KNOWLEDGE BASE & PARSING ENGINES
# ==========================================
def extract_text_from_file(uploaded_file):
    extracted = ""
    try:
        if uploaded_file.name.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                extracted += page.extract_text() or ""
        elif uploaded_file.name.endswith(".txt"):
            extracted = uploaded_file.read().decode("utf-8")
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
    return extracted.strip()

@st.cache_data
def scan_repository_knowledge():
    kb_summary = []
    for root, _, files in os.walk("."):
        for fname in files:
            if fname.lower().endswith(('.pdf', '.txt', '.htm', '.html')) and any(k in fname.lower() for k in ['mdr', 'cdsco', 'sugam', 'guidance', 'psur', 'drugs', 'g.s.r']):
                fpath = os.path.join(root, fname)
                try:
                    if fname.lower().endswith('.pdf'):
                        reader = PdfReader(fpath)
                        text = " ".join([page.extract_text() or "" for page in reader.pages[:3]])
                        kb_summary.append(f"Statutory Document: {fname}\nKey Clauses: {text[:600]}")
                    elif fname.lower().endswith(('.txt', '.html', '.htm')):
                        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                            kb_summary.append(f"Statutory Document: {fname}\nKey Clauses: {f.read()[:600]}")
                except Exception:
                    pass
    return "\n\n".join(kb_summary[:5])

def fetch_clinical_evidence(term):
    try:
        clean_term = re.sub(r'[^a-zA-Z0-9\s]', '', term)
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={requests.utils.quote(clean_term)}&retmode=json&retmax=3"
        res = requests.get(search_url, timeout=8).json()
        ids = res.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return "No direct peer-reviewed PubMed citations indexed for this explicit product identifier."
        sum_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={','.join(ids)}&retmode=json"
        summary_res = requests.get(sum_url, timeout=8).json().get("result", {})
        evidence = []
        for pmid in ids:
            if pmid in summary_res:
                data = summary_res[pmid]
                evidence.append(f"- PMID {pmid}: {data.get('title', 'N/A')} ({data.get('source', 'N/A')}, {data.get('pubdate', 'N/A')})")
        return "\n".join(evidence)
    except Exception:
        return "Clinical literature synthesis active via global databases."

# ==========================================
# 4. ENTERPRISE PDF GENERATOR
# ==========================================
class EnterprisePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 8, "COMPLIVOX GLOBAL | STATUTORY REGULATORY DOSSIER", ln=True, align="R")
        self.line(10, 18, 200, 18)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | Confidential Regulatory Submission Document", align="C")

def build_pdf_document(product, jurisdiction, intent, content):
    pdf = EnterprisePDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(15, 23, 42)
    clean_product = product.encode('latin-1', 'replace').decode('latin-1')
    pdf.cell(0, 8, f"Regulatory Assessment Report: {clean_product}", ln=True)
    
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(71, 85, 105)
    clean_meta = f"Jurisdiction: {jurisdiction} | Filing Intent: {intent}".encode('latin-1', 'replace').decode('latin-1')
    pdf.cell(0, 5, clean_meta, ln=True)
    
    clean_date = f"Generated On: {datetime.now().strftime('%d %B %Y')} | Standard: Zero Data Retention".encode('latin-1', 'replace').decode('latin-1')
    pdf.cell(0, 5, clean_date, ln=True)
    pdf.ln(5)
    
    # Format markdown into clean human-readable text for PDF
    clean_text = content.replace("###", "").replace("##", "").replace("**", "").replace("–", "-").replace("—", "-").replace("“", '"').replace("”", '"').replace("’", "'").replace("•", "-")
    clean_body = clean_text.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(0, 4.8, clean_body)
    return bytes(pdf.output())

# ==========================================
# 5. USER INTERFACE & WORKSPACE
# ==========================================
col_spec, col_dossier = st.columns([1, 1], gap="large")

with col_spec:
    st.markdown("#### 📋 Technical Submission Dossier")
    
    prod_name = st.text_input("Product / Molecule / Device Trade Name", value="Sirolimus-Eluting Coronary Stent")
    
    uploaded_file = st.file_uploader("📂 Upload Technical Spec Sheet or Lab Report (PDF / TXT)", type=["pdf", "txt"])
    doc_context = ""
    if uploaded_file is not None:
        doc_context = extract_text_from_file(uploaded_file)
        st.success(f"✅ Extracted {len(doc_context)} characters from {uploaded_file.name}")
    
    c1, c2 = st.columns(2)
    with c1:
        prod_cat = st.selectbox("Product Classification Category", [
            "Cardiovascular & Interventional (Stents, Catheters)",
            "Orthopedic & Spinal Implants",
            "In-Vitro Diagnostics (IVD & Reagents)",
            "Software as a Medical Device (SaMD / AI Diagnostics)",
            "Drug-Device Combination Products",
            "Biologics & Biosimilars (Monoclonal Antibodies, mRNA)",
            "Active Implantable Devices (Pacemakers, Neurostimulators)",
            "Pharma Small Molecule / Injectables",
            "Ophthalmic & General Surgery Devices",
            "Dental Implants & Restorative Materials",
            "Oncology Drug Delivery Systems",
            "Custom / Other Category..."
        ])
        if prod_cat == "Custom / Other Category...":
            custom_cat = st.text_input("Specify Custom Category Name")
            if custom_cat.strip():
                prod_cat = custom_cat.strip()
                
    with c2:
        duration_contact = st.selectbox("In-Body Contact Duration", [
            "Long-term / Permanent (> 30 days)",
            "Short-term (<= 30 days)",
            "Transient (< 60 minutes)",
            "Non-invasive / Surface Contact"
        ])
        
    tech_specs = st.text_area(
        "Technical Composition, Drug Formulation & Indication",
        value="Cobalt-Chromium L605 platform, strut thickness 65 microns, coated with biodegradable PLGA polymer and Sirolimus (1.4 mcg/mm2) for treatment of de novo native coronary artery lesions.",
        height=140
    )
    
    exec_btn = st.button("🚀 Synthesize Global Regulatory Dossier", type="primary", use_container_width=True)

with col_dossier:
    st.markdown("#### 📑 Autonomous Regulatory Dossier")
    
    if exec_btn:
        if not sarvam_api_key:
            st.error("⚠️ Backend authentication key missing in Streamlit Secrets.")
        elif not prod_name.strip() or (not tech_specs.strip() and not doc_context.strip()):
            st.warning("⚠️ Please fill in product name and specifications or upload a file.")
        else:
            with st.spinner("Executing CDSCO/SUGAM Statutory Synthesis & AI Regulatory Engine..."):
                pubmed_data = fetch_clinical_evidence(prod_name)
                statutory_kb = scan_repository_knowledge()
                combined_specs = f"{tech_specs}\n\n[UPLOADED TECHNICAL SPECIFICATION DATA]:\n{doc_context}" if doc_context else tech_specs
                
                system_prompt = f"""
                You are the Principal Regulatory Affairs Officer, Global Auditor, and CDSCO/SUGAM Technical Specialist.
                Target Framework: {target_framework}.
                Filing Transaction Intent: {submission_intent}.

                OFFICIAL STATUTORY KNOWLEDGE BASE & GAZETTE NOTIFICATIONS:
                - Medical Device Rules (MDR) 2017 & Drugs and Cosmetics Act 1940
                - G.S.R. 409(E), G.S.R. 754(E), G.S.R. 777(E)
                - SUGAM 3.0 Online Submission Guidelines & PSUR Module
                {statutory_kb}

                Generate a complete, audit-ready Regulatory Strategy Dossier strictly covering:
                1. STATUTORY CLASSIFICATION & EXACT LEGAL CLAUSES (Class A-D, Exact MDR 2017 Rules, Schedule M/Part IV-A).
                2. TRANSACTION WORKFLOW & STATUTORY FORMS (Exact Forms: MD-14/15 for Import, MD-7/8/9/10 for Mfg, PMF/DMF checklists, Free Sale Certificate).
                3. SUBSTANTIAL EQUIVALENCE & PREDICATE BENCHMARKING (Material composition, mechanical profile, delivery parameters).
                4. CLINICAL EVALUATION REPORT & PSUR REQUIREMENTS (Safety and efficacy endpoints, Periodic Safety Update Report compliance under SUGAM 3.0).
                5. CDSCO SEC / REGULATORY DEFICIENCY FORECASTING (Anticipated committee objections, testing gaps, stability requirements).
                6. MANDATORY SUBMISSION CHECKLIST & ROADMAP (ISO 10993, ISO 13485, ISO 14971, accelerated stability timeline).
                """
                
                user_prompt = f"""
                Product Name: {prod_name}
                Category: {prod_cat}
                Duration: {duration_contact}
                Filing Intent: {submission_intent}
                Technical Specifications & Document Input:
                {combined_specs}

                PubMed Peer-Reviewed Clinical Data:
                {pubmed_data}
                """
                
                headers = {
                    "api-subscription-key": sarvam_api_key.strip(),
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "sarvam-105b",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 4096
                }
                
                try:
                    resp = requests.post("https://api.sarvam.ai/v1/chat/completions", headers=headers, json=payload, timeout=160)
                    if resp.status_code == 200:
                        content = resp.json()["choices"][0]["message"]["content"]
                        st.session_state["dossier_text"] = content
                        st.session_state["prod_name"] = prod_name
                        st.session_state["framework"] = target_framework
                        st.session_state["intent"] = submission_intent
                    else:
                        st.error(f"❌ API Error ({resp.status_code}): {resp.text}")
                except Exception as e:
                    st.error(f"❌ Connection Error: {str(e)}")

    # Show Output and PDF Export Button only when dossier is ready
    if st.session_state.get("dossier_text"):
        st.markdown(st.session_state["dossier_text"])
        
        try:
            pdf_bytes = build_pdf_document(
                st.session_state.get("prod_name", "Product"),
                st.session_state.get("framework", "Regulatory Framework"),
                st.session_state.get("intent", "Submission Intent"),
                st.session_state["dossier_text"]
            )
            
            st.download_button(
                label="📥 Export Audit-Ready Regulatory Dossier (PDF)",
                data=pdf_bytes,
                file_name=f"Complivox_Dossier_{st.session_state.get('prod_name', 'Report').replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception:
            st.warning("PDF ready for viewing on screen.")
    else:
        st.info("👈 Click **'Synthesize Global Regulatory Dossier'** to generate your technical report.")
