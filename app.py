import streamlit as st
import requests
import json
import re
from datetime import datetime
from fpdf import FPDF

# ==========================================
# PAGE CONFIGURATION & ENTERPRISE BRANDING
# ==========================================
st.set_page_config(
    page_title="Complivox Global | AI Regulatory Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom SaaS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .brand-container {
        padding: 1.2rem 1.5rem;
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-radius: 12px;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 14px 0 rgba(15, 23, 42, 0.15);
    }
    .brand-title {
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #F8FAFC;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .brand-subtitle {
        font-size: 13px;
        color: #94A3B8;
        margin-top: 4px;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        background-color: #F1F5F9;
        border-radius: 6px 6px 0 0;
        font-weight: 600;
        color: #475569;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284C7 !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# Top Brand Header
st.markdown("""
<div class="brand-container">
    <div class="brand-title">🛡️ Complivox Global Regulatory Intelligence</div>
    <div class="brand-subtitle">Autonomous Regulatory Dossier Synthesis, SEC Deficiency Forecasting & Live PubMed Clinical Trials Engine.</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# SECRETS & ENGINE CONFIGURATION
# ==========================================
sarvam_api_key = st.secrets.get("SARVAM_API_KEY", "")

# Fallback in sidebar if secret is missing
with st.sidebar:
    st.markdown("### 🌐 Global Authority Engine")
    target_framework = st.selectbox(
        "Regulatory Target",
        [
            "CDSCO (India - Medical Device Rules 2017)",
            "US FDA (United States - 510(k) Premarket / PMA)",
            "EU MDR (European Union - Regulation 2017/745)",
            "Pharma CTD / eCTD (ICH Quality, Safety & Efficacy)"
        ]
    )
    
    st.markdown("---")
    st.markdown("**Core Modules Activated:**")
    st.checkbox("Risk Classification & MDR Rule Matrix", value=True, disabled=True)
    st.checkbox("Substantial Equivalence Benchmarking", value=True, disabled=True)
    st.checkbox("Live PubMed Clinical Literature Appraisal", value=True, disabled=True)
    st.checkbox("SEC Deficiency & Query Forecasting", value=True, disabled=True)
    st.checkbox("Statutory Checklist (MD Forms / eCTD)", value=True, disabled=True)
    
    if not sarvam_api_key:
        st.markdown("---")
        sarvam_api_key = st.text_input("Sarvam AI Subscription Key", type="password", placeholder="Enter key for manual session")

    st.markdown("---")
    st.caption("🔒 Complivox Enterprise Architecture v3.0 | Zero Data Retention Standard")

# ==========================================
# PUBMED CLINICAL TRIALS INTEGRATION
# ==========================================
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
                evidence.append(f"• PMID: {pmid} | Title: {data.get('title', 'N/A')} | Source: {data.get('source', 'N/A')} ({data.get('pubdate', 'N/A')})")
        return "\n".join(evidence)
    except Exception as e:
        return f"Clinical Search Status: Literature retrieval completed with non-critical fallback ({str(e)})."

# ==========================================
# ROBUST ENTERPRISE PDF GENERATOR
# ==========================================
class EnterprisePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 8, "COMPLIVOX GLOBAL | REGULATORY INTELLIGENCE DOSSIER", ln=True, align="R")
        self.line(10, 18, 200, 18)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f"Page {self.page_no()} | Confidential Regulatory Assessment", align="C")

def build_pdf_document(product, jurisdiction, content):
    pdf = EnterprisePDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title Banner
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    clean_product = product.encode('latin-1', 'replace').decode('latin-1')
    pdf.cell(0, 8, f"Regulatory Assessment Report: {clean_product}", ln=True)
    
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(71, 85, 105)
    clean_jur = jurisdiction.encode('latin-1', 'replace').decode('latin-1')
    pdf.cell(0, 5, f"Jurisdiction: {clean_jur} | Generated: {datetime.now().strftime('%d %b %Y, %H:%M UTC')}", ln=True)
    pdf.ln(6)
    
    # Body Content
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(30, 41, 59)
    
    # Clean text to prevent Unicode Latin-1 errors
    clean_text = content.replace("–", "-").replace("—", "-").replace("“", '"').replace("”", '"').replace("’", "'").replace("•", "-")
    clean_body = clean_text.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 4.5, clean_body)
    return bytes(pdf.output())

# ==========================================
# MAIN INTERFACE
# ==========================================
col_spec, col_dossier = st.columns([1, 1], gap="large")

with col_spec:
    st.markdown("#### 📋 Technical Submission Dossier")
    
    prod_name = st.text_input("Product / Molecule / Trade Name", placeholder="e.g., Paclitaxel-Eluting Coronary Balloon Catheter")
    
    c1, c2 = st.columns(2)
    with c1:
        prod_cat = st.selectbox("Product Classification Category", [
            "Cardiovascular & Interventional",
            "Orthopedic & Spinal Implants",
            "In-Vitro Diagnostics (IVD)",
            "Software as a Medical Device (SaMD)",
            "Drug-Device Combination",
            "Pharma Small Molecule / Injectable",
            "Ophthalmic & General Surgery"
        ])
    with c2:
        duration_contact = st.selectbox("In-Body Contact Duration", [
            "Transient (< 60 minutes)",
            "Short-term (<= 30 days)",
            "Long-term / Permanent (> 30 days)",
            "Non-invasive / Surface Contact"
        ])
        
    tech_specs = st.text_area(
        "Technical Composition, Materials, Drug Formulation & Intended Indication",
        placeholder="Detail base materials (e.g. Cobalt Chromium, Nitinol), polymer matrix (e.g. PLGA), active pharmaceutical ingredients, deliverability profile, and target clinical endpoints...",
        height=180
    )
    
    exec_btn = st.button("🚀 Synthesize Global Regulatory Dossier", type="primary", use_container_width=True)

with col_dossier:
    st.markdown("#### 📑 Autonomous Regulatory Dossier")
    
    if exec_btn:
        if not sarvam_api_key:
            st.error("⚠️ Authentication Missing: Sarvam AI API Key is required via Streamlit Secrets or manual input.")
        elif not prod_name.strip() or not tech_specs.strip():
            st.warning("⚠️ Input Required: Product Name and Technical Specifications must not be empty.")
        else:
            with st.spinner("Analyzing Medical Device Directives, SEC Query Logs & PubMed Literature..."):
                pubmed_data = fetch_clinical_evidence(prod_name)
                
                system_prompt = f"""
                You are the Principal Regulatory Affairs Officer and Global Compliance Assessor across CDSCO (India MDR 2017), US FDA (21 CFR), and EU MDR (2017/745).
                Target Framework: {target_framework}.

                Generate a definitive, audit-proof Regulatory Strategy Dossier structured strictly as follows:

                1. STATUTORY CLASSIFICATION & REGULATORY PATHWAY
                   - Risk Class (Class A, B, C, or D) with specific Statutory Rule Citations.
                   - Governing Licensing Authority & Statutory Approval Route.

                2. SUBSTANTIAL EQUIVALENCE & PREDICATE BENCHMARKING
                   - Material, mechanical, delivery, and clinical equivalence mapping against benchmark devices.

                3. CLINICAL EVALUATION REPORT (CER) & SAFETY ENDPOINTS
                   - Synthesize PubMed peer-reviewed data into clinical performance and safety endpoints.

                4. CDSCO SEC / AUDIT DEFICIENCY FORECASTING
                   - High-probability technical audit queries, Subject Expert Committee objections, biocompatibility gaps, or clinical trial waiver requirements.

                5. MANDATORY SUBMISSION CHECKLIST & APPLICABLE STANDARDS
                   - Prescribed forms (e.g., MD-14, MD-15, MD-7, 510k, eCTD Modules).
                   - Harmonized Standards (ISO 10993 Biocompatibility, ISO 13485 QMS, ISO 14971 Risk Management, Sterility & Stability testing).

                6. REGULATORY CLEARANCE TIMELINE & MILESTONES
                   - Milestone roadmap to achieve statutory market authorization.
                """
                
                user_prompt = f"""
                DOSSIER SPECIFICATION:
                - Device / Drug Name: {prod_name}
                - Domain: {prod_cat}
                - Contact Profile: {duration_contact}
                - Technical Description: {tech_specs}

                RETRIEVED CLINICAL CITATIONS:
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
                    "temperature": 0.2
                }
                
                try:
                    resp = requests.post("https://api.sarvam.ai/v1/chat/completions", headers=headers, json=payload, timeout=120)
                    if resp.status_code == 200:
                        report_content = str(resp.json()["choices"][0]["message"]["content"])
                        st.session_state["active_dossier"] = report_content
                        st.session_state["prod_name"] = prod_name
                        st.session_state["framework"] = target_framework
                    else:
                        st.error(f"Inference Engine Returned Code {resp.status_code}: {resp.text}")
                except Exception as e:
                    st.error(f"Pipeline Connection Exception: {str(e)}")

    # Display Report & PDF Export
    if "active_dossier" in st.session_state and st.session_state["active_dossier"]:
        st.markdown(st.session_state["active_dossier"])
        
        try:
            pdf_bytes = build_pdf_document(
                st.session_state.get("prod_name", "Product"),
                st.session_state.get("framework", "Regulatory Framework"),
                st.session_state["active_dossier"]
            )
            
            st.download_button(
                label="📥 Export Audit-Ready Regulatory Dossier (PDF)",
                data=pdf_bytes,
                file_name=f"Complivox_Dossier_{st.session_state.get('prod_name', 'Report').replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as pdf_err:
            st.warning(f"PDF compilation notice: Dossier is ready to review on-screen.")
    else:
        st.info("👈 Complete the technical parameters and execute the engine to generate the intelligence dossier.")
