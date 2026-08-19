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

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .brand-container {
        padding: 1.2rem 1.5rem;
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-radius: 12px;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
    }
    .brand-title { font-size: 24px; font-weight: 800; color: #F8FAFC; }
    .brand-subtitle { font-size: 13px; color: #94A3B8; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand-container">
    <div class="brand-title">🛡️ Complivox Global Regulatory Intelligence</div>
    <div class="brand-subtitle">Autonomous Regulatory Dossier Synthesis, SEC Deficiency Forecasting & Live PubMed Clinical Evidence Engine.</div>
</div>
""", unsafe_allow_html=True)

sarvam_api_key = st.secrets.get("SARVAM_API_KEY", "")

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
    if not sarvam_api_key:
        sarvam_api_key = st.text_input("🔑 Sarvam AI API Key", type="password", placeholder="Enter your key here")
    else:
        st.success("✅ Backend API Secret Loaded")
        
    st.markdown("---")
    st.markdown("**Core Modules Activated:**")
    st.checkbox("Risk Classification & Rule Matrix", value=True, disabled=True)
    st.checkbox("Substantial Equivalence Benchmarking", value=True, disabled=True)
    st.checkbox("Live PubMed Clinical Literature Appraisal", value=True, disabled=True)
    st.checkbox("SEC Deficiency & Query Forecasting", value=True, disabled=True)
    st.checkbox("Statutory Checklist (MD Forms / eCTD)", value=True, disabled=True)

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
    except Exception as e:
        return "Literature synthesis fallback mode active."

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
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | Confidential Regulatory Assessment", align="C")

def build_pdf_document(product, jurisdiction, content):
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
    clean_jur = jurisdiction.encode('latin-1', 'replace').decode('latin-1')
    pdf.cell(0, 5, f"Framework: {clean_jur} | Date: {datetime.now().strftime('%d %b %Y')}", ln=True)
    pdf.ln(5)
    
    # Clean text: remove markdown artifacts for polished PDF printing
    clean_text = content.replace("###", "").replace("##", "").replace("**", "").replace("–", "-").replace("—", "-").replace("“", '"').replace("”", '"').replace("’", "'").replace("•", "-")
    clean_body = clean_text.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(0, 5, clean_body)
    return bytes(pdf.output())

# Main Interface
col_spec, col_dossier = st.columns([1, 1], gap="large")

with col_spec:
    st.markdown("#### 📋 Technical Submission Dossier")
    
    prod_name = st.text_input("Product / Molecule / Trade Name", value="Sirolimus-Eluting Coronary Stent")
    
    c1, c2 = st.columns(2)
    with c1:
        prod_cat = st.selectbox("Classification Category", [
            "Cardiovascular & Interventional",
            "Orthopedic & Spinal Implants",
            "In-Vitro Diagnostics (IVD)",
            "Software as a Medical Device (SaMD)",
            "Drug-Device Combination",
            "Pharma Small Molecule / Injectable",
            "Ophthalmic & General Surgery"
        ])
    with c2:
        duration_contact = st.selectbox("In-Body Duration", [
            "Long-term / Permanent (> 30 days)",
            "Short-term (<= 30 days)",
            "Transient (< 60 minutes)",
            "Non-invasive / Surface Contact"
        ])
        
    tech_specs = st.text_area(
        "Technical Composition & Clinical Indication",
        value="Cobalt-Chromium L605 platform, strut thickness 65 microns, coated with biodegradable PLGA polymer and Sirolimus (1.4 mcg/mm2) for treatment of de novo native coronary artery lesions.",
        height=180
    )
    
    exec_btn = st.button("🚀 Synthesize Global Regulatory Dossier", type="primary", use_container_width=True)

with col_dossier:
    st.markdown("#### 📑 Autonomous Regulatory Dossier")
    
    if exec_btn:
        if not sarvam_api_key:
            st.error("⚠️ API Key Missing: Enter key in sidebar or save in Secrets.")
        elif not prod_name.strip() or not tech_specs.strip():
            st.warning("⚠️ Please fill in all required fields.")
        else:
            with st.spinner("Executing Full Clinical Synthesis & AI Regulatory Engine..."):
                pubmed_data = fetch_clinical_evidence(prod_name)
                
                system_prompt = f"""
                You are the Principal Regulatory Affairs Officer across CDSCO (India MDR 2017), US FDA (21 CFR), and EU MDR (2017/745).
                Target Framework: {target_framework}.

                Generate a complete, exhaustive Regulatory Strategy Dossier covering all 6 sections thoroughly:
                1. STATUTORY CLASSIFICATION & REGULATORY PATHWAY (Class A-D, Exact MDR Rules, Statutory Approval route).
                2. SUBSTANTIAL EQUIVALENCE & PREDICATE BENCHMARKING (Material, mechanical and delivery parameters).
                3. CLINICAL EVALUATION REPORT (CER) SYNTHESIS (Safety and clinical efficacy endpoints).
                4. CDSCO SEC / AUDIT DEFICIENCY FORECASTING (Anticipated committee objections & testing gaps).
                5. MANDATORY SUBMISSION CHECKLIST (Prescribed Forms like MD-14/MD-15, ISO 10993, ISO 13485, ISO 14971).
                6. REGULATORY CLEARANCE ROADMAP & TIMELINE.
                """
                
                user_prompt = f"""
                Device / Molecule: {prod_name}
                Category: {prod_cat}
                Duration: {duration_contact}
                Technical Specifications: {tech_specs}

                PubMed Clinical Findings:
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
                    else:
                        st.error(f"❌ API Error ({resp.status_code}): {resp.text}")
                except Exception as e:
                    st.error(f"❌ Connection Error: {str(e)}")

    if st.session_state.get("dossier_text"):
        st.markdown(st.session_state["dossier_text"])
        
        try:
            pdf_bytes = build_pdf_document(
                st.session_state.get("prod_name", "Product"),
                st.session_state.get("framework", "Regulatory Framework"),
                st.session_state["dossier_text"]
            )
            
            st.download_button(
                label="📥 Export Audit-Ready Regulatory Dossier (PDF)",
                data=pdf_bytes,
                file_name=f"Complivox_Dossier_{st.session_state.get('prod_name', 'Report').replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as pdf_err:
            st.warning("PDF ready for viewing on screen.")
    else:
        st.info("👈 Click **'Synthesize Global Regulatory Dossier'** to generate your technical report.")
