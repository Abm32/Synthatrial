#!/usr/bin/env python3
"""
SynthaTrial - Streamlit Web UI
In Silico Pharmacogenomics Platform
"""

import streamlit as st
import os
from src.input_processor import get_drug_fingerprint
from src.vector_search import find_similar_drugs
from src.agent_engine import run_simulation

# Page configuration
st.set_page_config(
    page_title="SynthaTrial - Pharmacogenomics Simulator",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #1565a0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f0f2f6;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .result-box {
        padding: 1.5rem;
        border-radius: 5px;
        background-color: #f8f9fa;
        border: 2px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🧬 SynthaTrial</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">In Silico Pharmacogenomics Platform</p>', unsafe_allow_html=True)

# Sidebar for patient profile
with st.sidebar:
    st.header("👤 Patient Profile")
    
    patient_id = st.text_input("Patient ID", value="SP-01", help="Unique identifier for the patient")
    age = st.number_input("Age", min_value=0, max_value=120, value=45, step=1)
    
    st.subheader("🧬 Genetic Markers")
    
    cyp2d6 = st.selectbox(
        "CYP2D6 Status",
        ["extensive_metabolizer", "intermediate_metabolizer", "poor_metabolizer", "ultra_rapid_metabolizer"],
        index=2,
        help="Cytochrome P450 2D6 enzyme activity"
    )
    
    cyp2c19 = st.selectbox(
        "CYP2C19 Status",
        ["extensive_metabolizer", "intermediate_metabolizer", "poor_metabolizer", "ultra_rapid_metabolizer"],
        index=0,
        help="Cytochrome P450 2C19 enzyme activity"
    )
    
    cyp3a4 = st.selectbox(
        "CYP3A4 Status",
        ["extensive_metabolizer", "intermediate_metabolizer", "poor_metabolizer", "ultra_rapid_metabolizer"],
        index=1,
        help="Cytochrome P450 3A4 enzyme activity"
    )
    
    st.subheader("🏥 Medical Conditions")
    conditions = st.multiselect(
        "Select Conditions",
        [
            "Hypertension",
            "Type 2 Diabetes",
            "Chronic Liver Disease",
            "Chronic Kidney Disease",
            "Heart Disease",
            "Asthma",
            "COPD",
            "Depression",
            "Anxiety",
            "Chronic Pain"
        ],
        # Default must be one of the options above
        default=["Chronic Liver Disease"],
        help="Select all relevant medical conditions"
    )
    
    st.subheader("🍷 Lifestyle Factors")
    alcohol = st.selectbox(
        "Alcohol Consumption",
        ["None", "Light", "Moderate", "Heavy"],
        index=2,
        help="Alcohol consumption level"
    )
    
    smoking = st.selectbox(
        "Smoking Status",
        ["Non-smoker", "Former smoker", "Current smoker"],
        index=0,
        help="Smoking status"
    )

# Main content area
tab1, tab2, tab3 = st.tabs(["🔬 Drug Simulation", "📊 About", "📖 Examples"])

with tab1:
    st.header("Drug Input")
    
    # Drug input method selection
    input_method = st.radio(
        "Select Input Method",
        ["SMILES String", "Drug Name (with SMILES)"],
        horizontal=True
    )
    
    if input_method == "SMILES String":
        smiles_input = st.text_input(
            "Enter SMILES String",
            value="CC(=O)Nc1ccc(O)cc1",
            help="Enter the SMILES notation for the drug molecule (e.g., CC(=O)Nc1ccc(O)cc1 for Paracetamol)"
        )
        drug_name = st.text_input(
            "Drug Name (Optional)",
            value="Synthetic-Para-101",
            help="A name or identifier for this drug"
        )
    else:
        drug_name = st.text_input(
            "Drug Name",
            value="Paracetamol",
            help="Name of the drug"
        )
        smiles_input = st.text_input(
            "SMILES String",
            value="CC(=O)Nc1ccc(O)cc1",
            help="SMILES notation for the drug"
        )
    
    # Example SMILES
    with st.expander("💡 Common Drug SMILES Examples"):
        examples = {
            "Paracetamol (Acetaminophen)": "CC(=O)Nc1ccc(O)cc1",
            "Ibuprofen": "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
            "Aspirin": "CC(=O)Oc1ccccc1C(=O)O",
            "Caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            "Morphine": "CN1CC[C@]23C4=C5C=CC(=C4O)Oc4c5c(C[C@@H]1[C@@H]2C=C[C@@H]3O)cc(c4)O"
        }
        for name, smiles in examples.items():
            st.code(f"{name}: {smiles}")
            if st.button(f"Use {name}", key=f"example_{name}"):
                smiles_input = smiles
                drug_name = name
                st.rerun()
    
    # Run simulation button
    run_button = st.button("🚀 Run Simulation", type="primary", use_container_width=True)
    
    if run_button:
        if not smiles_input.strip():
            st.error("❌ Please enter a SMILES string")
        else:
            # Build patient profile string
            genetics_text = f"CYP2D6 {cyp2d6.replace('_', ' ').title()}"
            if cyp2c19 != "extensive_metabolizer":
                genetics_text += f", CYP2C19 {cyp2c19.replace('_', ' ').title()}"
            if cyp3a4 != "extensive_metabolizer":
                genetics_text += f", CYP3A4 {cyp3a4.replace('_', ' ').title()}"
            
            conditions_text = ", ".join(conditions) if conditions else "None"
            lifestyle_text = f"Alcohol: {alcohol}, Smoking: {smoking}"
            
            patient_profile = f"""
ID: {patient_id}
Age: {age}
Genetics: {genetics_text}
Conditions: {conditions_text}
Lifestyle: {lifestyle_text}
"""
            
            # Progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Process SMILES
                status_text.text("🔄 Step 1/3: Processing SMILES and generating molecular fingerprint...")
                progress_bar.progress(20)
                fingerprint = get_drug_fingerprint(smiles_input)
                st.success(f"✅ Fingerprint generated: {len(fingerprint)} bits")
                
                # Step 2: Find similar drugs
                status_text.text("🔄 Step 2/3: Searching for similar drugs...")
                progress_bar.progress(50)
                similar_drugs = find_similar_drugs(fingerprint, top_k=3)
                
                with st.expander("🔍 Similar Drugs Found", expanded=False):
                    for i, drug in enumerate(similar_drugs, 1):
                        st.write(f"**{i}. {drug}**")
                
                # Step 3: Run AI simulation
                status_text.text("🔄 Step 3/3: Running pharmacogenomics simulation with AI...")
                progress_bar.progress(80)
                
                # Check for API key
                api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
                if not api_key:
                    st.warning("⚠️ GOOGLE_API_KEY not found. Showing expected input instead.")
                    st.info(f"""
**Expected Input for LLM:**
- Drug: {drug_name}
- Similar Drugs: {', '.join(similar_drugs)}
- Patient Profile: {patient_profile}
                    """)
                else:
                    result = run_simulation(drug_name, similar_drugs, patient_profile)
                    progress_bar.progress(100)
                    status_text.text("✅ Simulation complete!")
                    
                    # Display results
                    st.markdown("---")
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown("## 📋 Simulation Results")
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
            except ValueError as e:
                st.error(f"❌ Error: {str(e)}")
                progress_bar.progress(0)
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                st.exception(e)
                progress_bar.progress(0)

with tab2:
    st.header("About SynthaTrial")
    
    st.markdown("""
    ### 🧬 What is SynthaTrial?
    
    SynthaTrial is an **In Silico Pharmacogenomics Platform** that simulates drug effects on synthetic patient cohorts using Agentic AI.
    
    ### 🔬 How It Works
    
    1. **Molecular Fingerprinting**: Converts SMILES strings to 2048-bit molecular fingerprints using Morgan Fingerprints
    2. **Similarity Search**: Finds similar drugs using vector similarity search (Pinecone)
    3. **AI Simulation**: Uses advanced LLMs (Gemini) to predict physiological reactions based on:
       - Patient genetic markers (CYP2D6, CYP2C19, CYP3A4)
       - Medical conditions
       - Lifestyle factors
       - Similar drug profiles
    
    ### 🎯 Use Cases
    
    - **Drug Development**: Predict patient responses before clinical trials
    - **Personalized Medicine**: Tailor drug selection based on genetics
    - **Risk Assessment**: Identify patients at high risk for adverse reactions
    - **Dosing Optimization**: Adjust dosages based on metabolic profiles
    
    ### ⚠️ Disclaimer
    
    This is an MVP prototype for research and development purposes. 
    **Not intended for clinical decision-making.**
    
    ### 🔧 Technical Stack
    
    - **Chemistry**: RDKit (molecular fingerprinting)
    - **Vector Search**: Pinecone (similarity search)
    - **AI**: Google Gemini (pharmacogenomics analysis)
    - **UI**: Streamlit (web interface)
    """)

with tab3:
    st.header("Example Use Cases")
    
    st.subheader("Example 1: Paracetamol for CYP2D6 Poor Metabolizer")
    st.code("""
SMILES: CC(=O)Nc1ccc(O)cc1
Patient: CYP2D6 Poor Metabolizer, Chronic Liver Disease
Expected: High risk due to reduced metabolism and liver impairment
    """)
    
    st.subheader("Example 2: Ibuprofen for Patient with GI Issues")
    st.code("""
SMILES: CC(C)Cc1ccc(C(C)C(=O)O)cc1
Patient: History of GI bleeding, CYP2C19 Intermediate Metabolizer
Expected: Increased risk of gastrointestinal side effects
    """)
    
    st.subheader("Example 3: Codeine for CYP2D6 Ultra-Rapid Metabolizer")
    st.code("""
SMILES: CN1CC[C@]23C4=C5C=CC(=C4O)Oc4c5c(C[C@@H]1[C@@H]2C=C[C@@H]3O)cc(c4)O
Patient: CYP2D6 Ultra-Rapid Metabolizer
Expected: Increased conversion to morphine, higher risk of overdose
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "SynthaTrial v0.2 (Beta) | Built with ❤️ for Pharmacogenomics Research"
    "</div>",
    unsafe_allow_html=True
)
