#!/usr/bin/env python3
"""
Test the new InvestmentReportGenerator
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from evaluating_llm_fin_reports import (
    InvestmentReportGenerator,
    ReportEvaluator,
    MARKDOWN_DIR
)

def test_report_generation():
    """Test the complete report generation"""
    print("🧪 Testing Investment Report Generator")
    print("=" * 60)
    
    # Define persona
    persona_definitions = {
        "Warren Buffett": """Focus on high-quality businesses with durable competitive advantages (economic moats), 
        excellent management, consistent earnings growth, and reasonable valuations. Look for companies that can 
        compound wealth over decades through reinvestment and organic growth."""
    }
    
    # Load a sample financial document
    from evaluating_llm_fin_reports import load_markdown_file, markdown_files
    
    if not markdown_files:
        print("❌ No markdown files found!")
        return
    
    # Use the first available document
    sample_file = markdown_files[0]
    company_name = sample_file.stem
    financial_doc = load_markdown_file(sample_file)
    
    print(f"📄 Using document: {sample_file.name}")
    print(f"📊 Document length: {len(financial_doc)} characters")
    print(f"🏢 Company: {company_name}")
    
    # Initialize report generator
    print("\n⚙️  Initializing report generator...")
    generator = InvestmentReportGenerator(persona_definitions)
    
    # Generate report
    print("📝 Generating investment report...")
    print("   (This may take a minute as it makes multiple LLM calls)")
    
    try:
        report = generator(
            persona_name="Warren Buffett",
            company_name=company_name,
            financial_documents=financial_doc[:15000],  # Limit to first 15k chars for faster testing
            news_data=None
        )
        
        print("\n✅ Report generated successfully!")
        print(f"📏 Report length: {len(report)} characters")
        
        # Save the report
        output_path = Path("test_generated_report.md")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"💾 Report saved to: {output_path}")
        
        # Show preview
        print("\n" + "=" * 60)
        print("REPORT PREVIEW (first 1000 characters):")
        print("=" * 60)
        print(report[:1000])
        print("\n[... rest of report in test_generated_report.md ...]")
        print("=" * 60)
        
        # Now evaluate the report
        print("\n📊 Evaluating the generated report...")
        evaluator = ReportEvaluator(persona_definitions)
        
        evaluation = evaluator(
            persona_name="Warren Buffett",
            company_summary=f"{company_name}: Jamaican company",
            report=report,
            n_questions=10  # Use fewer questions for faster testing
        )
        
        print("\n✅ Evaluation completed!")
        print(f"   Coverage Rate: {evaluation['metrics'].coverage_rate:.2%}")
        print(f"   Quality Score: {evaluation['metrics'].quality_score:.1f}/10")
        print(f"   Alignment Score: {evaluation['alignment'].alignment_score:.1f}/10")
        print(f"   Questions Fully Answered: {evaluation['metrics'].answerable_fully}")
        print(f"   Questions Partially Answered: {evaluation['metrics'].answerable_partial}")
        print(f"   Questions Not Answered: {evaluation['metrics'].not_answerable}")
        
        print("\n🎉 SUCCESS! The InvestmentReportGenerator is working!")
        
        return report, evaluation
        
    except Exception as e:
        print(f"\n❌ Error during report generation: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    test_report_generation()
