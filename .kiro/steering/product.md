# Product Overview

SynthaTrial is an **In Silico Pharmacogenomics Platform** (Version 0.3 Beta) that simulates drug effects on synthetic patient cohorts using Agentic AI. The system predicts how patients will respond to medications based on their genetic profile, medical history, and lifestyle factors with comprehensive multi-enzyme coverage and CPIC guideline compliance.

## Core Functionality

- **Molecular Analysis**: Converts drug SMILES strings to 2048-bit Morgan fingerprints using RDKit with structural analysis capabilities and enhanced validation
- **Similarity Search**: Finds similar drugs using vector similarity search in Pinecone database with enhanced metadata and mock mode fallback
- **Genetic Profiling**: Processes VCF files to extract CYP enzyme variants - supports "Big 3" enzymes (CYP2D6, CYP2C19, CYP2C9) covering ~60-70% of clinically used drugs with comprehensive star allele mapping
- **Multi-Chromosome Support**: Analyzes chromosome 22 (CYP2D6) and chromosome 10 (CYP2C19, CYP2C9) for comprehensive pharmacogenomic profiling with integrity validation
- **AI Simulation**: Uses Google Gemini LLM (gemini-2.5-flash default) with enhanced RAG to predict drug responses based on patient genetics and CPIC guidelines with structured output parsing
- **Activity Score Method**: CPIC/PharmVar guideline-based metabolizer status inference with star allele mapping and comprehensive phenotype prediction
- **Performance Benchmarking**: Built-in tools for measuring vector retrieval latency, LLM simulation time, and end-to-end workflows with detailed analytics
- **Data Integrity Validation**: Comprehensive VCF file validation, corruption detection, and download verification with detailed reporting
- **CPIC Compliance Testing**: Automated validation against Clinical Pharmacogenetics Implementation Consortium guidelines with accuracy metrics
- **Modern Web Interface**: Enhanced Streamlit UI with gradient styling, example use cases, real-time validation, and improved user experience

## Key Use Cases

- Drug development and patient response prediction with comprehensive enzyme coverage and validation tools
- Personalized medicine and dosing optimization for major drug classes:
  - **CYP2D6**: Codeine, Tramadol, Metoprolol, Antidepressants (~25% of drugs)
  - **CYP2C19**: Clopidogrel (Plavix), Omeprazole, PPIs (antiplatelet, GI drugs)
  - **CYP2C9**: Warfarin, Ibuprofen, Phenytoin, NSAIDs (anticoagulation, pain management)
- Risk assessment for adverse drug reactions across multiple metabolic pathways with comprehensive reporting
- Research and development prototype with clinical-grade enzyme coverage and CPIC compliance
- Performance benchmarking for pharmacogenomics platforms with detailed analytics and timing measurements
- CPIC guideline validation and compliance testing with automated accuracy metrics
- Educational tool for pharmacogenomics concepts and drug-gene interactions with interactive examples and comprehensive documentation
- Documentation and knowledge management with streamlined, well-organized guides for setup, usage, and troubleshooting
- Data integrity validation for VCF files and genomic datasets with comprehensive error reporting
- Platform validation and testing with comprehensive test suites and validation frameworks

## Target Users

- Researchers in pharmacogenomics and personalized medicine
- Drug developers and pharmaceutical companies
- Healthcare professionals (research context only)
- Bioinformatics researchers working with VCF data and genomic analysis
- Students and educators in pharmacogenomics and personalized medicine
- Platform developers building pharmacogenomics tools and validation frameworks
- Quality assurance teams validating genomic data integrity and platform performance

## Important Notes

- This is an MVP prototype (Version 0.3 Beta) for research purposes only
- **Not intended for clinical decision-making**
- Follows CPIC (Clinical Pharmacogenetics Implementation Consortium) guidelines with comprehensive validation testing and accuracy metrics
- Integrates with 1000 Genomes Project VCF data (chromosomes 10 and 22) and ChEMBL drug database with integrity validation
- **Major Platform Capability**: Big 3 enzymes provide 2.4x-2.8x increase in drug coverage compared to CYP2D6 alone
- **Full backward compatibility**: Single-chromosome mode maintained for existing workflows
- **Comprehensive testing**: Includes integrity checking, performance benchmarking, CPIC validation, and automated accuracy assessment
- **Comprehensive documentation**: Streamlined structure with single-file guides for setup, usage, implementation, troubleshooting, and research validation
- **Modern web interface**: Enhanced UI with gradient styling, example use cases, real-time validation, and improved user experience
- **Data quality assurance**: Built-in VCF validation, corruption detection, and comprehensive error reporting
- **Performance monitoring**: Detailed benchmarking tools for vector retrieval, LLM processing, and end-to-end workflow analysis