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

# Custom CSS for modern, user-friendly styling
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Card styling */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .card-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease;
        font-size: 1rem;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
    }
    
    /* Info boxes */
    .info-box {
        padding: 1.25rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-left: 4px solid #0ea5e9;
        margin: 1rem 0;
    }
    
    .success-box {
        padding: 1.25rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-left: 4px solid #22c55e;
        margin: 1rem 0;
    }
    
    .result-box {
        padding: 2rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #fafafa 0%, #ffffff 100%);
        border: 2px solid #667eea;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Section dividers */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #e2e8f0 50%, transparent 100%);
        margin: 2rem 0;
    }
    
    /* Better spacing */
    .element-container {
        margin-bottom: 1.5rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<p class="main-header">🧬 SynthaTrial</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">In Silico Pharmacogenomics Platform</p>', unsafe_allow_html=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# Sidebar for patient profile - Better organized with expanders
with st.sidebar:
    st.markdown("## 👤 Patient Profile")
    st.markdown("---")
    
    # Basic Information Section
    with st.expander("📋 Basic Information", expanded=True):
        patient_id = st.text_input(
            "Patient ID", 
            value="SP-01", 
            help="Unique identifier for the patient",
            key="patient_id"
        )
        age = st.number_input(
            "Age", 
            min_value=0, 
            max_value=120, 
            value=45, 
            step=1,
            help="Patient age in years"
        )
    
    # Genetic Markers Section
    with st.expander("🧬 Genetic Markers", expanded=True):
        st.caption("Cytochrome P450 enzyme activity levels")
        
        cyp2d6 = st.selectbox(
            "CYP2D6 Status",
            ["extensive_metabolizer", "intermediate_metabolizer", "poor_metabolizer", "ultra_rapid_metabolizer"],
            index=2,
            help="Cytochrome P450 2D6 enzyme activity",
            key="cyp2d6"
        )
        
        cyp2c19 = st.selectbox(
            "CYP2C19 Status",
            ["extensive_metabolizer", "intermediate_metabolizer", "poor_metabolizer", "ultra_rapid_metabolizer"],
            index=0,
            help="Cytochrome P450 2C19 enzyme activity",
            key="cyp2c19"
        )
        
        cyp3a4 = st.selectbox(
            "CYP3A4 Status",
            ["extensive_metabolizer", "intermediate_metabolizer", "poor_metabolizer", "ultra_rapid_metabolizer"],
            index=1,
            help="Cytochrome P450 3A4 enzyme activity",
            key="cyp3a4"
        )
    
    # Medical Conditions Section
    with st.expander("🏥 Medical Conditions", expanded=False):
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
            default=["Chronic Liver Disease"],
            help="Select all relevant medical conditions",
            key="conditions"
        )
    
    # Lifestyle Factors Section
    with st.expander("🍷 Lifestyle Factors", expanded=False):
        alcohol = st.selectbox(
            "Alcohol Consumption",
            ["None", "Light", "Moderate", "Heavy"],
            index=2,
            help="Alcohol consumption level",
            key="alcohol"
        )
        
        smoking = st.selectbox(
            "Smoking Status",
            ["Non-smoker", "Former smoker", "Current smoker"],
            index=0,
            help="Smoking status",
            key="smoking"
        )
    
    # Quick Summary
    st.markdown("---")
    with st.expander("📊 Profile Summary", expanded=False):
        st.caption("**Patient ID:** " + patient_id)
        st.caption(f"**Age:** {age} years")
        st.caption(f"**Conditions:** {len(conditions)} selected")
        st.caption(f"**CYP2D6:** {cyp2d6.replace('_', ' ').title()}")

# Main content area with better tabs
tab1, tab2, tab3 = st.tabs(["🔬 Drug Simulation", "📊 About", "📖 Examples"])

with tab1:
    # Step 1: Drug Input Section
    st.markdown("### Step 1: Enter Drug Information")
    st.caption("Provide the drug's SMILES notation or select from examples")

    # Determine default values for this run (can be set by example selectors)
    default_smiles = "CC(=O)Nc1ccc(O)cc1"
    default_drug = "Synthetic-Para-101"

    if "example_smiles" in st.session_state:
        default_smiles = st.session_state.example_smiles
    if "example_drug" in st.session_state:
        default_drug = st.session_state.example_drug

    # Drug input in a card-like container
    col1, col2 = st.columns([2, 1])

    with col1:
        # Drug input method selection
        input_method = st.radio(
            "**Input Method**",
            ["SMILES String", "Drug Name (with SMILES)"],
            horizontal=True,
            key="input_method"
        )

        if input_method == "SMILES String":
            smiles_input = st.text_input(
                "Enter SMILES String",
                value=default_smiles,
                help="Enter the SMILES notation for the drug molecule",
                key="smiles_input"
            )
            drug_name = st.text_input(
                "Drug Name (Optional)",
                value=default_drug,
                help="A name or identifier for this drug",
                key="drug_name_optional"
            )
        else:
            drug_name = st.text_input(
                "Drug Name",
                value=default_drug,
                help="Name of the drug",
                key="drug_name"
            )
            smiles_input = st.text_input(
                "SMILES String",
                value=default_smiles,
                help="SMILES notation for the drug",
                key="smiles_input_alt"
            )

    with col2:
        st.markdown("#### 💡 Quick Examples")
        examples = {
            "Paracetamol": "CC(=O)Nc1ccc(O)cc1",
            "Ibuprofen": "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
            "Aspirin": "CC(=O)Oc1ccccc1C(=O)O",
            "Caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"
        }

        selected_example = st.selectbox(
            "Select example:",
            ["None"] + list(examples.keys()),
            key="example_selector"
        )

        if selected_example != "None":
            # Store chosen example for the next rerun; widget keys remain untouched
            st.session_state.example_smiles = examples[selected_example]
            st.session_state.example_drug = selected_example
            st.info(f"✅ Selected: **{selected_example}**")
            st.code(examples[selected_example])
            st.rerun()
    
    st.markdown("---")
    
    # Step 2: Review and Run
    st.markdown("### Step 2: Review & Run Simulation")
    
    # Review section
    review_col1, review_col2 = st.columns(2)
    
    with review_col1:
        st.markdown("**📋 Drug Information:**")
        st.info(f"""
        **Drug Name:** {drug_name if drug_name else 'Not specified'}
        **SMILES:** `{smiles_input[:50]}{'...' if len(smiles_input) > 50 else ''}`
        """)
    
    with review_col2:
        st.markdown("**👤 Patient Profile:**")
        st.info(f"""
        **ID:** {patient_id} | **Age:** {age}
        **CYP2D6:** {cyp2d6.replace('_', ' ').title()}
        **Conditions:** {len(conditions)} selected
        """)
    
    # Run simulation button - prominent and centered
    st.markdown("")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        run_button = st.button(
            "🚀 Run Simulation", 
            type="primary", 
            use_container_width=True,
            key="run_sim"
        )
    
    if run_button:
        if not smiles_input.strip():
            st.error("❌ **Error:** Please enter a SMILES string to proceed.")
        else:
            st.markdown("---")
            st.markdown("### Step 3: Simulation Progress")
            
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
            
            # Progress indicators with better visual feedback
            progress_container = st.container()
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            try:
                # Step 1: Process SMILES
                with st.status("🔄 **Step 1/3:** Processing SMILES and generating molecular fingerprint...", expanded=True) as status:
                    progress_bar.progress(20)
                    fingerprint = get_drug_fingerprint(smiles_input)
                    status.update(label=f"✅ **Step 1 Complete:** Fingerprint generated ({len(fingerprint)} bits)", state="complete")
                
                # Step 2: Find similar drugs
                with st.status("🔄 **Step 2/3:** Searching for similar drugs in database...", expanded=True) as status:
                    progress_bar.progress(50)
                    similar_drugs = find_similar_drugs(fingerprint, top_k=3)
                    
                    # Display similar drugs in a nice format
                    status.update(label=f"✅ **Step 2 Complete:** Found {len(similar_drugs)} similar drugs", state="complete")
                    
                    # Show similar drugs in columns
                    st.markdown("**🔍 Similar Drugs Found:**")
                    sim_cols = st.columns(len(similar_drugs))
                    for i, (col, drug) in enumerate(zip(sim_cols, similar_drugs)):
                        with col:
                            st.markdown(f"""
                            <div style='padding: 1rem; background: #f8fafc; border-radius: 8px; text-align: center; border: 1px solid #e2e8f0;'>
                                <strong>{i+1}. {drug}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Step 3: Run AI simulation
                with st.status("🔄 **Step 3/3:** Running pharmacogenomics simulation with AI...", expanded=True) as status:
                    progress_bar.progress(80)
                    
                    # Check for API key
                    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
                    if not api_key:
                        status.update(label="⚠️ **Warning:** API key not found", state="error")
                        st.warning("⚠️ **GOOGLE_API_KEY** not found. Showing expected input instead.")
                        
                        st.markdown("---")
                        st.markdown("### 📋 Expected Simulation Input")
                        info_col1, info_col2 = st.columns(2)
                        
                        with info_col1:
                            st.markdown("**Drug Information:**")
                            st.info(f"""
                            - **Drug Name:** {drug_name}
                            - **SMILES:** `{smiles_input}`
                            - **Similar Drugs:** {', '.join(similar_drugs)}
                            """)
                        
                        with info_col2:
                            st.markdown("**Patient Profile:**")
                            st.info(patient_profile)
                    else:
                        result = run_simulation(drug_name, similar_drugs, patient_profile)
                        progress_bar.progress(100)
                        status.update(label="✅ **Step 3 Complete:** Simulation finished successfully!", state="complete")
                        
                        # Display results in a beautiful container
                        st.markdown("---")
                        st.markdown("### 📊 Simulation Results")
                        
                        # Results container with better styling
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        st.markdown(result)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Additional metrics or actions could go here
                        st.markdown("")
                        col_export1, col_export2, col_export3 = st.columns([1, 1, 1])
                        with col_export2:
                            st.download_button(
                                label="📥 Download Results",
                                data=result,
                                file_name=f"simulation_{patient_id}_{drug_name.replace(' ', '_')}.txt",
                                mime="text/plain"
                            )
                    
            except ValueError as e:
                st.error(f"❌ **Validation Error:** {str(e)}")
                progress_bar.progress(0)
            except Exception as e:
                st.error(f"❌ **Unexpected Error:** {str(e)}")
                with st.expander("🔍 Error Details"):
                    st.exception(e)
                progress_bar.progress(0)

with tab2:
    st.markdown("## 📊 About SynthaTrial")
    st.markdown("---")
    
    # What is SynthaTrial
    st.markdown("### 🧬 What is SynthaTrial?")
    st.info("""
    SynthaTrial is an **In Silico Pharmacogenomics Platform** that simulates drug effects on synthetic patient cohorts using Agentic AI. 
    It helps predict how different patients will respond to medications based on their genetic profile, medical history, and lifestyle factors.
    """)
    
    st.markdown("---")
    
    # How It Works - in columns
    st.markdown("### 🔬 How It Works")
    
    col_work1, col_work2, col_work3 = st.columns(3)
    
    with col_work1:
        st.markdown("""
        <div style='padding: 1.5rem; background: #f8fafc; border-radius: 10px; border-left: 4px solid #667eea;'>
            <h4>1️⃣ Molecular Fingerprinting</h4>
            <p>Converts SMILES strings to 2048-bit molecular fingerprints using Morgan Fingerprints</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_work2:
        st.markdown("""
        <div style='padding: 1.5rem; background: #f8fafc; border-radius: 10px; border-left: 4px solid #764ba2;'>
            <h4>2️⃣ Similarity Search</h4>
            <p>Finds similar drugs using vector similarity search (Pinecone)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_work3:
        st.markdown("""
        <div style='padding: 1.5rem; background: #f8fafc; border-radius: 10px; border-left: 4px solid #f093fb;'>
            <h4>3️⃣ AI Simulation</h4>
            <p>Uses advanced LLMs (Gemini) to predict physiological reactions</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("**Factors Considered:**")
    factor_cols = st.columns(4)
    with factor_cols[0]:
        st.markdown("🧬 **Genetic Markers**\n- CYP2D6\n- CYP2C19\n- CYP3A4")
    with factor_cols[1]:
        st.markdown("🏥 **Medical Conditions**\n- Chronic diseases\n- Comorbidities")
    with factor_cols[2]:
        st.markdown("🍷 **Lifestyle Factors**\n- Alcohol\n- Smoking")
    with factor_cols[3]:
        st.markdown("💊 **Drug Profiles**\n- Similar drugs\n- Known interactions")
    
    st.markdown("---")
    
    # Use Cases
    st.markdown("### 🎯 Use Cases")
    use_case_cols = st.columns(2)
    
    with use_case_cols[0]:
        st.markdown("""
        - **💊 Drug Development**: Predict patient responses before clinical trials
        - **👤 Personalized Medicine**: Tailor drug selection based on genetics
        """)
    
    with use_case_cols[1]:
        st.markdown("""
        - **⚠️ Risk Assessment**: Identify patients at high risk for adverse reactions
        - **📏 Dosing Optimization**: Adjust dosages based on metabolic profiles
        """)
    
    st.markdown("---")
    
    # Technical Stack
    st.markdown("### 🔧 Technical Stack")
    tech_cols = st.columns(4)
    
    tech_stack = [
        ("🧪 RDKit", "Molecular fingerprinting"),
        ("🔍 Pinecone", "Vector similarity search"),
        ("🤖 Google Gemini", "Pharmacogenomics analysis"),
        ("🌐 Streamlit", "Web interface")
    ]
    
    for col, (name, desc) in zip(tech_cols, tech_stack):
        with col:
            st.markdown(f"""
            <div style='padding: 1rem; background: white; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center;'>
                <strong>{name}</strong><br>
                <small>{desc}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Disclaimer
    st.warning("""
    ⚠️ **Disclaimer:** This is an MVP prototype for research and development purposes. 
    **Not intended for clinical decision-making.**
    """)

with tab3:
    st.markdown("## 📖 Example Use Cases")
    st.caption("Click on any example to see how SynthaTrial analyzes different scenarios")
    st.markdown("---")
    
    # Example 1
    with st.expander("💊 Example 1: Paracetamol for CYP2D6 Poor Metabolizer", expanded=True):
        col_ex1_1, col_ex1_2 = st.columns([1, 2])
        
        with col_ex1_1:
            st.markdown("**Drug Information:**")
            st.code("SMILES:\nCC(=O)Nc1ccc(O)cc1\n\nDrug: Paracetamol", language="text")
        
        with col_ex1_2:
            st.markdown("**Patient Profile:**")
            st.info("""
            - **CYP2D6:** Poor Metabolizer
            - **Medical Condition:** Chronic Liver Disease
            - **Expected Outcome:** High risk due to reduced metabolism and liver impairment
            """)
        
        if st.button("🚀 Try This Example", key="ex1_btn"):
            st.session_state.example_smiles = "CC(=O)Nc1ccc(O)cc1"
            st.session_state.example_drug = "Paracetamol"
            st.session_state.cyp2d6 = "poor_metabolizer"
            st.session_state.conditions = ["Chronic Liver Disease"]
            st.rerun()
    
    st.markdown("---")
    
    # Example 2
    with st.expander("💊 Example 2: Ibuprofen for Patient with GI Issues", expanded=False):
        col_ex2_1, col_ex2_2 = st.columns([1, 2])
        
        with col_ex2_1:
            st.markdown("**Drug Information:**")
            st.code("SMILES:\nCC(C)Cc1ccc(C(C)C(=O)O)cc1\n\nDrug: Ibuprofen", language="text")
        
        with col_ex2_2:
            st.markdown("**Patient Profile:**")
            st.info("""
            - **CYP2C19:** Intermediate Metabolizer
            - **Medical Condition:** History of GI bleeding
            - **Expected Outcome:** Increased risk of gastrointestinal side effects
            """)
        
        if st.button("🚀 Try This Example", key="ex2_btn"):
            st.session_state.example_smiles = "CC(C)Cc1ccc(C(C)C(=O)O)cc1"
            st.session_state.example_drug = "Ibuprofen"
            st.session_state.cyp2c19 = "intermediate_metabolizer"
            st.session_state.conditions = ["Heart Disease"]  # Approximate for GI issues
            st.rerun()
    
    st.markdown("---")
    
    # Example 3
    with st.expander("💊 Example 3: Codeine for CYP2D6 Ultra-Rapid Metabolizer", expanded=False):
        col_ex3_1, col_ex3_2 = st.columns([1, 2])
        
        with col_ex3_1:
            st.markdown("**Drug Information:**")
            st.code("SMILES:\nCN1CC[C@]23C4=C5C=CC(=C4O)Oc4c5c(C[C@@H]1[C@@H]2C=C[C@@H]3O)cc(c4)O\n\nDrug: Codeine", language="text")
        
        with col_ex3_2:
            st.markdown("**Patient Profile:**")
            st.info("""
            - **CYP2D6:** Ultra-Rapid Metabolizer
            - **Expected Outcome:** Increased conversion to morphine, higher risk of overdose
            """)
        
        if st.button("🚀 Try This Example", key="ex3_btn"):
            st.session_state.example_smiles = "CN1CC[C@]23C4=C5C=CC(=C4O)Oc4c5c(C[C@@H]1[C@@H]2C=C[C@@H]3O)cc(c4)O"
            st.session_state.example_drug = "Codeine"
            st.session_state.cyp2d6 = "ultra_rapid_metabolizer"
            st.rerun()
    
    st.markdown("---")
    
    # Quick reference
    st.markdown("### 📚 Quick Reference: Common Drug SMILES")
    
    common_drugs = {
        "Paracetamol (Acetaminophen)": "CC(=O)Nc1ccc(O)cc1",
        "Ibuprofen": "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
        "Aspirin": "CC(=O)Oc1ccccc1C(=O)O",
        "Caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        "Morphine": "CN1CC[C@]23C4=C5C=CC(=C4O)Oc4c5c(C[C@@H]1[C@@H]2C=C[C@@H]3O)cc(c4)O"
    }
    
    for drug_name, smiles in common_drugs.items():
        st.markdown(f"**{drug_name}:** `{smiles}`")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; padding: 2rem 0; font-size: 0.9rem;'>"
    "🧬 <strong>SynthaTrial</strong> v0.2 (Beta) | Built with ❤️ for Pharmacogenomics Research"
    "</div>",
    unsafe_allow_html=True
)
