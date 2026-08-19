import streamlit as st
import requests
import json
from fpdf import FPDF
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Complivox Global | AI Regulatory Intelligence & Compliance Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom UI Styling
st.markdown("""
    <style>
    .main-header { font-size: 30px; font-weight: 800; color: #0F172A; margin-bottom: 2px; }
    .sub-header { font-size: 15px; color: #475569; margin-bottom: 20px; }
    .status-badge { background-color: #EEF2FF; color: #3730A3; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 12px; }
    .metric-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🛡️ Complivox Global Regulatory Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Regulatory Dossier Generation, SEC Query Prediction, Predicate Benchmarking & Clinical Evaluation for Medical Devices & Pharmaceuticals.</div>', unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=60)
    st.header("⚙️ Configuration")
    sarvam_api_key = st.text_input("Sarvam AI API Key", type="password", placeholder="Enter API Key")
    
    target_jurisdiction = st.selectbox(
        "Target Regulatory Authority",
        [
            "CDSCO (India - Medical Device Rules 2017)",
            "US FDA (United States - 510(k) Premarket / PMA)",
            "EU MDR (European Union - Regulation 2017/745)",
            "Pharma CTD / eCTD (ICH Modules 1-5)"
        ]
    )
    
    st.markdown("---")
    st.markdown("**Active Regulatory Modules**")
    m1 = st.checkbox("Risk Classification & Rule Citation", value=True)
    m2 = st.checkbox("Substantial Equivalence & Predicate Finder", value=True)
    m3 = st.checkbox("Clinical Evidence Synthesis (Live PubMed)", value=True)
    m4 = st.checkbox("SEC / Audit Deficiency Risk Predictor", value=True)
    m5 = st.checkbox("Mandatory Dossier Checklist (MD Forms/eCTD)", value=True)
    
    st.markdown("---")
    st.caption("Complivox Enterprise v2.4 | Zero Data Loss Architecture")

# Main Interface
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.markdown("### 📋 Product Profile & Technical Specs")
    
    product_name = st.text_input("Product / Molecule / Device Trade Name", placeholder="e.g., Paclitaxel-Eluting Peripheral Balloon Catheter")
    
    c1, c2 = st.columns(2)
    with c1:
        product_type = st.selectbox("Product Category", [
            "Cardiovascular & Interventional",
            "Orthopedic & Spinal Implants",
            "In-Vitro Diagnostics (IVD)",
            "Software as a Medical Device (SaMD)",
            "Drug-Device Combination",
            "Pharma Small Molecule / Formulation",
            "Ophthalmic & General Surgery"
        ])
    with c2:
        intended_use_duration = st.selectbox("Intended In-Body Duration", [
            "Transient (< 60 minutes)",
            "Short-term (<= 30 days)",
            "Long-term / Permanent Implantation (> 30 days)",
            "Non-invasive / External"
        ])
        
    specs_payload = st.text_area(
        "Technical Composition, Materials, Drug Load, & Clinical Indication",
        placeholder="Provide materials (e.g., Nitinol, PTFE), coating formulation, delivery mechanism, intended anatomical site, and primary clinical objective...",
        height=180
    )
    
    run_btn = st.button("🚀 Execute Global Regulatory Analysis", type="primary", use_container_width=True)

# PubMed Clinical Search Function
def retrieve_pubmed_clinical_trials(query_term):
    try:
        search_endpoint = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={requests.utils.quote(query_term)}&retmode=json&retmax=3"
        res = requests.get(search_endpoint, timeout=10).json()
        uids = res.get("esearchresult", {}).get("idlist", [])
        if not uids:
            return "No indexed PubMed peer-reviewed literature found for immediate citation."
        
        sum_endpoint = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={','.join(uids)}&retmode=json"
        summary_res = requests.get(sum_endpoint, timeout=10).json().get("result", {})
        
        citations = []
        for uid in uids:
            if uid in summary_res:
                data = summary_res[uid]
                citations.append(f"• Title: {data.get('title', '')} | Source: {data.get('source', '')} ({data.get('pubdate', '')})")
        return "\n".join(citations)
    except Exception as err:
        return f"Clinical Search Pipeline Warning: {str(err)}"

# Output Column
with col_output:
    st.markdown("### 📑 Regulatory Assessment Report")
    
    if run_btn:
        if not sarvam_api_key:
            st.error("⚠️ Authentication Key Missing: Enter your Sarvam AI API key in the sidebar.")
        elif not product_name or not specs_payload:
            st.warning("⚠️ Input Required: Enter both Product Name and Technical Specifications.")
        else:
            with st.spinner("Analyzing Global Databases, PubMed Literature & Regulatory Guidelines..."):
                clinical_data = retrieve_pubmed_clinical_trials(product_name)
                
                system_instructions = f"""
                You are an authoritative Global Regulatory Affairs Director and Subject Matter Expert across CDSCO (India MDR 2017), US FDA (21 CFR), and EU MDR (2017/745).
                Target Regulatory Framework: {target_jurisdiction}.

                Generate a publication-grade, professional Regulatory Assessment Dossier. You MUST structure the report under these exact standardized headings:
                
                1. EXECUTIVE REGULATORY CLASSIFICATION & STATUTORY PATHWAY
                   - Statutory Risk Classification (Class A, B, C, or D) with exact Rule citations.
                   - Statutory Pathway and Primary Licensing Authority.
                
                2. SUBSTANTIAL EQUIVALENCE & PREDICATE BENCHMARKING
                   - Benchmark technical, material, and clinical parameters against approved predicates.
                
                3. CLINICAL EVALUATION REPORT (CER) SYNTHESIS
                   - Clinical safety, performance endpoints, and literature appraisal synthesizing the retrieved PubMed studies.
                
                4. CDSCO SEC / AUDIT DEFICIENCY & OBJECTION PREDICTOR
                   - High-probability technical queries, Subject Expert Committee (SEC) objections, biocompatibility gaps, or clinical trial waiver risks.
                
                5. MANDATORY SUBMISSION CHECKLIST & TESTING STANDARDS
                   - Exact statutory forms required (e.g., MD-14, MD-15, MD-7, 510(k), eCTD Modules).
                   - Mandatory testing standards (ISO 10993 biocompatibility, ISO 13485 QMS, ISO 14971 Risk Management, accelerated stability).
                
                6. ACTIONABLE TIMELINE & REGULATORY ROADMAP
                   - Step-by-step roadmap to achieve formal market clearance.
                """
                
                user_instructions = f"""
                PRODUCT SPECIFICATION DOSSIER:
                - Device / Drug Name: {product_name}
                - Classification Category: {product_type}
                - Duration of Contact: {intended_use_duration}
                - Technical Composition & Purpose: {specs_payload}
                
                LIVE NCBI PUBMED CLINICAL TRIALS EXTRACTED:
                {clinical_data}
                """
                
                headers = {
                    "api-subscription-key": sarvam_api_key.strip(),
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "sarvam-105b",
                    "messages": [
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": user_instructions}
                    ],
                    "temperature": 0.2
                }
                
                try:
                    resp = requests.post("https://api.sarvam.ai/v1/chat/completions", headers=headers, json=payload, timeout=100)
                    if resp.status_code == 200:
                        report_body = resp.json()["choices"][0]["message"]["content"]
                        st.session_state["report_body"] = report_body
                        st.session_state["active_prod"] = product_name
                        st.session_state["active_jur"] = target_jurisdiction
                    else:
                        st.error(f"Sarvam AI Service Response ({resp.status_code}): {resp.text}")
                except Exception as ex:
                    st.error(f"Execution Error: {str(ex)}")

    if "report_body" in st.session_state:
        st.markdown(st.session_state["report_body"])
        
        # PDF Dossier Generator
        class PDFReport(FPDF):
            def header(self):
                self.set_font('Helvetica', 'B', 12)
                self.cell(0, 10, 'COMPLIVOX GLOBAL REGULATORY INTELLIGENCE DOSSIER', border=False, ln=True, align='L')
                self.set_draw_color(200, 200, 200)
                self.line(10, 18, 200, 18)
                self.ln(5)
            
            def footer(self):
                self.set_y(-15)
                self.set_font('Helvetica', 'I', 8)
                self.cell(0, 10, f'Confidential | Generated via Complivox Engine | Page {self.page_no()}', align='C')

        pdf = PDFReport()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, f"Product Assessment: {st.session_state['active_prod']}", ln=True)
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 6, f"Jurisdiction: {st.session_state['active_jur']} | Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
        pdf.ln(6)
        
        pdf.set_font("Helvetica", "", 9)
        sanitized_text = st.session_state["report_body"].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5.5, sanitized_text)
        
        pdf_bytes = bytes(pdf.output())
        st.download_button(
            label="📥 Export Regulatory Dossier (PDF)",
            data=pdf_bytes,
            file_name=f"{st.session_state['active_prod'].replace(' ', '_')}_Complivox_Dossier.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info("👈 Complete the product specification profile on the left and click 'Execute Global Regulatory Analysis' to generate the technical dossier.")
