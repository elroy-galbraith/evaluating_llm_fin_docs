#!/usr/bin/env python3
"""
Test script for evaluating_llm_fin_reports.py
"""

import sys
from pathlib import Path

# Add the current directory to path so we can import the main script
sys.path.append(str(Path(__file__).parent))

from evaluating_llm_fin_reports import (
    FinancialDocumentLoader,
    ReportEvaluator,
    QuestionGenerator,
    MARKDOWN_DIR
)

def test_document_loading():
    """Test if financial documents are loaded correctly"""
    print("🧪 Testing document loading...")
    
    loader = FinancialDocumentLoader(MARKDOWN_DIR)
    documents = loader.load_all_documents()
    
    print(f"✅ Loaded {len(documents)} documents")
    
    # Test a specific document lookup
    if documents:
        first_doc_name = list(documents.keys())[0]
        content = documents[first_doc_name]
        print(f"✅ Sample document '{first_doc_name}' has {len(content)} characters")
        
        # Test metadata parsing
        metadata = loader.parse_document_metadata(first_doc_name)
        print(f"✅ Parsed metadata: {metadata}")
    
    return loader

def test_question_generation():
    """Test the question generation module"""
    print("\n🧪 Testing question generation...")
    
    # Define a simple persona
    persona_definitions = {
        "Warren Buffett": "Focus on high-quality businesses with durable competitive advantages, strong management, and reasonable valuations. Look for companies with economic moats and consistent earnings."
    }
    
    # Create question generator
    question_gen = QuestionGenerator()
    
    try:
        # Generate questions for a test company
        questions = question_gen(
            persona_name="Warren Buffett",
            persona_philosophy=persona_definitions["Warren Buffett"],
            company_summary="GraceKennedy Ltd: A Jamaican conglomerate operating in food processing, financial services, and retail.",
            n_questions=5
        )
        
        print(f"✅ Generated {len(questions.questions)} questions")
        for i, q in enumerate(questions.questions[:3], 1):  # Show first 3
            print(f"   {i}. [{q.category}] {q.question}")
            print(f"      Importance: {q.importance:.2f}")
        
        return questions
        
    except Exception as e:
        print(f"❌ Question generation failed: {e}")
        return None

def test_report_evaluator():
    """Test the report evaluation functionality"""
    print("\n🧪 Testing report evaluator...")
    
    # Define persona
    persona_definitions = {
        "Warren Buffett": "Focus on high-quality businesses with durable competitive advantages."
    }
    
    # Create evaluator
    evaluator = ReportEvaluator(persona_definitions)
    
    # Sample report for testing
    sample_report = """
# Investment Analysis: GraceKennedy Ltd
## Analyst: Warren Buffett

## Financial Performance
GraceKennedy showed strong revenue growth of 15% year-over-year, reaching $85 billion JMD. 
The company maintains healthy profit margins with net profit margin of 8.5%.

## Competitive Position
The company has established market leadership in food processing with brands like Grace products.
Their distribution network across the Caribbean provides a competitive moat.

## Management Quality
The management team has demonstrated consistent execution over the past decade.
CEO Don Wehby has led strategic acquisitions that enhanced shareholder value.

## Valuation
Trading at P/E ratio of 12x, below historical average of 15x, suggesting potential undervaluation.
"""
    
    try:
        # Test evaluation
        result = evaluator(
            persona_name="Warren Buffett",
            company_summary="GraceKennedy Ltd: Jamaican conglomerate",
            report=sample_report,
            n_questions=5
        )
        
        print(f"✅ Evaluation completed")
        print(f"   Coverage Rate: {result['metrics'].coverage_rate:.2%}")
        print(f"   Quality Score: {result['metrics'].quality_score:.1f}/10")
        print(f"   Alignment Score: {result['alignment'].alignment_score:.1f}/10")
        
        return result
        
    except Exception as e:
        print(f"❌ Report evaluation failed: {e}")
        return None

def main():
    """Run all tests"""
    print("🚀 Starting LLM Financial Reports Script Tests")
    print("=" * 60)
    
    # Test 1: Document loading
    loader = test_document_loading()
    
    # Test 2: Question generation
    questions = test_question_generation()
    
    # Test 3: Report evaluation
    evaluation = test_report_evaluator()
    
    print("\n" + "=" * 60)
    if loader and questions and evaluation:
        print("✅ ALL TESTS PASSED - Script is working correctly!")
    else:
        print("❌ Some tests failed - Check the errors above")
    print("=" * 60)

if __name__ == "__main__":
    main()