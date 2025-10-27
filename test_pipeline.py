#!/usr/bin/env python3
"""
Test the main pipeline functionality
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from evaluating_llm_fin_reports import (
    FinancialDocumentLoader,
    InvestmentReportGenerator,
    ReportEvaluator,
    InvestmentAnalysisPipeline,
    MARKDOWN_DIR
)

def test_main_pipeline():
    """Test the main pipeline components"""
    print("🧪 Testing main pipeline setup...")
    
    # Define personas
    persona_definitions = {
        "Warren Buffett": "Focus on high-quality businesses with durable competitive advantages, strong management, and reasonable valuations.",
        "Benjamin Graham": "Deep value investing with emphasis on margin of safety, asset valuation, and contrarian opportunities."
    }
    
    # Define company summaries
    company_summaries = {
        "ncb": "National Commercial Bank: Largest bank in Jamaica",
        "grace": "GraceKennedy Ltd: Jamaican conglomerate"
    }
    
    try:
        # 1. Load financial documents
        print("   Loading documents...")
        doc_loader = FinancialDocumentLoader(MARKDOWN_DIR)
        docs = doc_loader.load_all_documents()
        
        # 2. Initialize components
        print("   Initializing components...")
        report_generator = InvestmentReportGenerator(persona_definitions)
        report_evaluator = ReportEvaluator(persona_definitions)
        
        # 3. Create pipeline
        output_dir = Path("./test_output")
        pipeline = InvestmentAnalysisPipeline(
            doc_loader=doc_loader,
            report_generator=report_generator,
            report_evaluator=report_evaluator,
            output_dir=output_dir
        )
        
        print("✅ Pipeline created successfully!")
        
        # Test finding company documents
        print("   Testing document lookup...")
        
        # Look for documents that might contain "ncb" or "grace"
        sample_docs = []
        for filename, content in docs.items():
            if any(term in filename.lower() for term in ['ncb', 'grace']):
                sample_docs.append((filename, content[:500]))  # First 500 chars
                if len(sample_docs) >= 3:  # Just get a few examples
                    break
        
        if sample_docs:
            print(f"✅ Found {len(sample_docs)} sample documents:")
            for filename, preview in sample_docs:
                print(f"   - {filename[:60]}{'...' if len(filename) > 60 else ''}")
        else:
            print("⚠️  No documents found matching 'ncb' or 'grace'")
            # Show first few document names instead
            print("   Available documents (first 5):")
            for i, filename in enumerate(list(docs.keys())[:5]):
                print(f"   - {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_metadata_parsing():
    """Test the metadata parsing to see if it can extract company names and years properly"""
    print("\n🧪 Testing metadata parsing...")
    
    loader = FinancialDocumentLoader(MARKDOWN_DIR)
    loader.load_all_documents()
    
    # Test metadata parsing on a few documents
    sample_files = list(loader.documents.keys())[:10]
    
    print("   Sample metadata parsing results:")
    for filename in sample_files:
        metadata = loader.parse_document_metadata(filename)
        print(f"   {filename[:50]}...")
        print(f"     Company: {metadata['company']}")
        print(f"     Year: {metadata['year']}")
        print()

def main():
    """Run pipeline tests"""
    print("🚀 Testing Main Pipeline Functionality")
    print("=" * 60)
    
    # Test 1: Pipeline setup
    pipeline_ok = test_main_pipeline()
    
    # Test 2: Metadata parsing
    test_document_metadata_parsing()
    
    print("=" * 60)
    if pipeline_ok:
        print("✅ PIPELINE TESTS PASSED")
        print("💡 The script is ready to use! You may want to:")
        print("   1. Adjust the metadata parsing logic for better company/year extraction")
        print("   2. Update the main() function paths to match your directory structure")
        print("   3. Define specific personas and company summaries for your analysis")
    else:
        print("❌ PIPELINE TESTS FAILED - Check errors above")
    print("=" * 60)

if __name__ == "__main__":
    main()