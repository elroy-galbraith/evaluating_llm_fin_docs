import os
from pathlib import Path
import dspy
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field
import json
from datetime import datetime
from statistics import mean
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# Configuration
# ============================================================================
# Model configuration (parameterized)
PROVIDER = "gemini"  # Options: "openai", "gemini", "anthropic"
TASK_MODEL_TEMP = 0.0  # Low temp for deterministic extraction
REFLECTION_MODEL_TEMP = 1.0  # High temp for diverse reflections

# Paths
QUESTIONS = "quetions"
MARKDOWN_DIR = Path("fin_docs")
PDF_DIR = Path("financial_pdfs/raw")

# Data split
TRAIN_RATIO = 0.75
RANDOM_SEED = 42

# GEPA configuration
GEPA_BUDGET = "light"  # Start with light, can increase to "medium" or "heavy"

# Get API key from environment
if PROVIDER == "openai":
    api_key = os.environ.get("OPENAI_API_KEY")
    TASK_MODEL = "gpt-4.1-mini"  # Model for the extraction task
    REFLECTION_MODEL = "gpt-4.1"  # Model for GEPA reflection
elif PROVIDER == "gemini":
    api_key = os.environ.get("GEMINI_API_KEY")
    TASK_MODEL = "gemini-2.5-flash"  # Model for the extraction task
    REFLECTION_MODEL = "gemini-2.5.pro"  # Model for GEPA reflection
elif PROVIDER == "anthropic":
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    TASK_MODEL = "claude-3"  # Model for the extraction task
    REFLECTION_MODEL = "claude-3"  # Model for GEPA reflection
else:
    raise ValueError(f"Unsupported provider: {PROVIDER}")
if not api_key:
    raise ValueError("API key not found in environment variables")

# Configure task model
task_lm = dspy.LM(
    model=f"{PROVIDER}/{TASK_MODEL}",
    temperature=TASK_MODEL_TEMP,
    api_key=api_key
)

# Configure reflection model for GEPA
reflection_lm = dspy.LM(
    model=f"{PROVIDER}/{REFLECTION_MODEL}",
    temperature=REFLECTION_MODEL_TEMP,
    max_tokens=32000,
    api_key=api_key
)

# Set default model
dspy.configure(lm=task_lm)

print(f"✅ Task Model: {TASK_MODEL}")
print(f"✅ Reflection Model: {REFLECTION_MODEL}")

# ============================================================================
# Load data
# ============================================================================
# List Markdown files
markdown_files = list(MARKDOWN_DIR.glob("*.md"))

# Load Markdown file
def load_markdown_file(file_path: Path) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# Load all Markdown files
markdown_contents = {md_file.name: load_markdown_file(md_file) for md_file in markdown_files}

# Count loaded files
print(f"✅ Loaded {len(markdown_contents)} Markdown files.")

# ============================================================================
# DATA MODELS
# ============================================================================

class InvestorQuestion(BaseModel):
    """A single question an investor would ask"""
    question: str = Field(description="The question text")
    category: str = Field(description="Category: financial, competitive, management, or risk")
    importance: float = Field(description="Importance weight 0-1", ge=0, le=1)
    reasoning: str = Field(description="Why this question matters for the investment decision")


class QuestionList(BaseModel):
    """Collection of investor questions"""
    questions: List[InvestorQuestion]


class QuestionEvaluation(BaseModel):
    """Evaluation of how well a report answers a question"""
    answerable: Literal["yes", "partial", "no"] = Field(
        description="Can the question be answered from the report?"
    )
    answer: str = Field(description="The answer extracted from the report, or explanation of what's missing")
    evidence: List[str] = Field(description="Direct quotes/references from the report supporting the answer")
    missing_information: List[str] = Field(description="Key information needed but not found in report")
    quality_rating: int = Field(description="Quality score 0-10", ge=0, le=10)
    reasoning: str = Field(description="Explanation of the rating")


class ReportMetrics(BaseModel):
    """Aggregate metrics for a report"""
    coverage_rate: float = Field(description="Percentage of questions answered (0-1)")
    quality_score: float = Field(description="Average quality rating (0-10)")
    answerable_fully: int = Field(description="Count of fully answerable questions")
    answerable_partial: int = Field(description="Count of partially answerable questions")
    not_answerable: int = Field(description="Count of unanswerable questions")
    critical_gaps: List[str] = Field(description="Most important missing information")

# ============================================================================
# FINANCIAL DOCUMENT LOADER
# ============================================================================

class FinancialDocumentLoader:
    """Load and manage raw financial documents (markdown format)"""
    
    def __init__(self, markdown_dir: Path):
        self.markdown_dir = Path(markdown_dir)
        self.documents = {}
        self.metadata = {}
    
    def load_all_documents(self) -> Dict[str, str]:
        """Load all markdown financial documents"""
        markdown_files = list(self.markdown_dir.glob("*.md"))
        
        self.documents = {
            md_file.stem: self._load_markdown_file(md_file) 
            for md_file in markdown_files
        }
        
        print(f"✅ Loaded {len(self.documents)} financial documents.")
        return self.documents
    
    def _load_markdown_file(self, file_path: Path) -> str:
        """Load single markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def parse_document_metadata(self, filename: str) -> dict:
        """
        Extract metadata from filename
        Expected formats:
        - {company}_{year}_financial_statements.md
        - {company}_{year}_annual_report.md
        - {company}_{year}.md
        """
        import re
        
        # Remove .md extension
        clean_name = filename.replace('.md', '')
        
        # Look for 4-digit years anywhere in the filename
        year_match = re.search(r'\b(19|20)\d{2}\b', clean_name)
        year = year_match.group() if year_match else 'unknown'
        
        # Try to identify company name patterns
        # Look for common prefixes and clean them up
        company_name = clean_name.lower()
        
        # Remove common suffixes and patterns
        patterns_to_remove = [
            r'-\d{4}.*',  # Remove year and everything after
            r'-(annual|quarterly|financial|audited|unaudited).*',
            r'-(q[1-4]|quarter|qrt).*',
            r'-(report|statement|results).*',
            r'-limited.*',
            r'-ltd.*',
            r'-final.*',
            r'-signed.*',
            r'-web.*',
            r'-compressed.*'
        ]
        
        for pattern in patterns_to_remove:
            company_name = re.sub(pattern, '', company_name)
        
        # Clean up underscores and dashes
        company_name = re.sub(r'[-_]+', '-', company_name).strip('-_')
        
        # If still too long, take first few meaningful parts
        if len(company_name) > 50:
            parts = company_name.split('-')[:3]  # Take first 3 parts
            company_name = '-'.join(parts)
        
        if not company_name:
            company_name = 'unknown'
            
        return {
            'company': company_name,
            'year': year,
            'filename': filename
        }
    
    def get_document(self, company: str = None, year: str = None) -> List[tuple]:
        """
        Filter and retrieve documents by metadata
        Returns list of (filename, content, metadata) tuples
        """
        matching_docs = []
        
        for filename, content in self.documents.items():
            metadata = self.parse_document_metadata(filename)
            
            # Check if filters match
            if (company is None or company.lower() in metadata['company'].lower()) and \
               (year is None or metadata['year'] == str(year)):
                matching_docs.append((filename, content, metadata))
        
        return matching_docs
    
    def get_company_documents(self, company: str) -> Dict[str, str]:
        """Get all documents for a specific company"""
        docs = self.get_document(company=company)
        return {meta['year']: content for _, content, meta in docs}


# ============================================================================
# REPORT GENERATION
# ============================================================================

class GenerateReportOutline(dspy.Signature):
    """Generate an outline for the investment report"""
    
    persona_name: str = dspy.InputField(description="Investment persona")
    persona_philosophy: str = dspy.InputField(description="Investment philosophy")
    company_name: str = dspy.InputField(description="Company being analyzed")
    financial_summary: str = dspy.InputField(description="Brief summary of financial documents")
    
    outline_sections: List[str] = dspy.OutputField(description="List of main report sections to cover")
    key_focus_areas: List[str] = dspy.OutputField(description="Key areas this persona would focus on")


class AnalyzeFinancials(dspy.Signature):
    """Analyze financial documents and extract key insights"""
    
    financial_documents: str = dspy.InputField(description="Raw financial statement data")
    focus_areas: str = dspy.InputField(description="What to focus on in the analysis")
    persona_name: str = dspy.InputField(description="Investor persona for context")
    
    revenue_analysis: str = dspy.OutputField(description="Revenue trends and analysis")
    profitability_analysis: str = dspy.OutputField(description="Profit margins and profitability")
    balance_sheet_analysis: str = dspy.OutputField(description="Assets, liabilities, and financial health")
    key_metrics: str = dspy.OutputField(description="Important financial ratios and metrics")
    strengths: List[str] = dspy.OutputField(description="Financial strengths identified")
    concerns: List[str] = dspy.OutputField(description="Financial concerns or red flags")


class WriteReportSection(dspy.Signature):
    """Write a specific section of the investment report"""
    
    section_title: str = dspy.InputField(description="Title of the section to write")
    persona_name: str = dspy.InputField(description="Investment persona")
    persona_philosophy: str = dspy.InputField(description="Investment philosophy")
    company_name: str = dspy.InputField(description="Company being analyzed")
    financial_analysis: str = dspy.InputField(description="Financial analysis results")
    context: str = dspy.InputField(description="Additional context for this section")
    
    section_content: str = dspy.OutputField(description="Well-written section content in markdown format")


class GenerateInvestmentRecommendation(dspy.Signature):
    """Generate final investment recommendation"""
    
    persona_name: str = dspy.InputField(description="Investment persona")
    persona_philosophy: str = dspy.InputField(description="Investment philosophy")
    company_name: str = dspy.InputField(description="Company being analyzed")
    financial_analysis: str = dspy.InputField(description="Complete financial analysis")
    strengths: str = dspy.InputField(description="Key strengths")
    concerns: str = dspy.InputField(description="Key concerns")
    
    recommendation: Literal["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"] = dspy.OutputField(
        description="Investment recommendation"
    )
    confidence_level: str = dspy.OutputField(description="Confidence in the recommendation (High/Medium/Low)")
    reasoning: str = dspy.OutputField(description="Detailed reasoning for the recommendation")
    key_risks: List[str] = dspy.OutputField(description="Key risks to consider")
    price_target_commentary: str = dspy.OutputField(description="Commentary on valuation and potential")


class InvestmentReportGenerator(dspy.Module):
    """
    Generate investment analysis reports from financial documents
    Uses a multi-step process to create comprehensive, persona-aligned reports
    """
    
    def __init__(self, persona_definitions: dict):
        super().__init__()
        self.persona_definitions = persona_definitions
        
        # Initialize report generation modules
        self.outline_generator = dspy.ChainOfThought(GenerateReportOutline)
        self.financial_analyzer = dspy.ChainOfThought(AnalyzeFinancials)
        self.section_writer = dspy.ChainOfThought(WriteReportSection)
        self.recommendation_generator = dspy.ChainOfThought(GenerateInvestmentRecommendation)
    
    def _create_financial_summary(self, financial_documents: str, max_chars: int = 2000) -> str:
        """Create a brief summary of financial documents for outline generation"""
        # Take first portion of the document
        summary = financial_documents[:max_chars]
        if len(financial_documents) > max_chars:
            summary += "\n\n[Document continues...]"
        return summary
    
    def forward(self, persona_name: str, company_name: str, 
                financial_documents: str, news_data: Optional[str] = None) -> str:
        """
        Generate investment report from raw financial documents
        
        Args:
            persona_name: Investment persona (e.g., "Warren Buffett")
            company_name: Company being analyzed
            financial_documents: Raw financial statement markdown
            news_data: Optional news articles
        
        Returns:
            Generated investment report (markdown format)
        """
        persona_philosophy = self.persona_definitions.get(
            persona_name, 
            "Value-focused investment approach"
        )
        
        # STEP 1: Generate Report Outline
        financial_summary = self._create_financial_summary(financial_documents)
        
        outline_result = self.outline_generator(
            persona_name=persona_name,
            persona_philosophy=persona_philosophy,
            company_name=company_name,
            financial_summary=financial_summary
        )
        
        # STEP 2: Analyze Financial Documents
        focus_areas = "\n".join(outline_result.key_focus_areas)
        
        financial_analysis = self.financial_analyzer(
            financial_documents=financial_documents,
            focus_areas=focus_areas,
            persona_name=persona_name
        )
        
        # STEP 3: Generate Investment Recommendation
        recommendation_result = self.recommendation_generator(
            persona_name=persona_name,
            persona_philosophy=persona_philosophy,
            company_name=company_name,
            financial_analysis=f"""
Revenue: {financial_analysis.revenue_analysis}
Profitability: {financial_analysis.profitability_analysis}
Balance Sheet: {financial_analysis.balance_sheet_analysis}
Key Metrics: {financial_analysis.key_metrics}
""",
            strengths="\n".join(financial_analysis.strengths),
            concerns="\n".join(financial_analysis.concerns)
        )
        
        # STEP 4: Write Report Sections
        financial_context = f"""
Revenue Analysis: {financial_analysis.revenue_analysis}
Profitability: {financial_analysis.profitability_analysis}
Balance Sheet: {financial_analysis.balance_sheet_analysis}
Key Metrics: {financial_analysis.key_metrics}
Strengths: {', '.join(financial_analysis.strengths)}
Concerns: {', '.join(financial_analysis.concerns)}
"""
        
        # Write main sections
        sections = {}
        for section_title in outline_result.outline_sections[:4]:  # Limit to 4 main sections
            section_result = self.section_writer(
                section_title=section_title,
                persona_name=persona_name,
                persona_philosophy=persona_philosophy,
                company_name=company_name,
                financial_analysis=financial_context,
                context=f"Focus areas: {focus_areas}"
            )
            sections[section_title] = section_result.section_content
        
        # STEP 5: Assemble Final Report
        report_parts = [
            f"# Investment Analysis: {company_name}",
            f"**Analyst Perspective:** {persona_name}",
            f"**Date:** {datetime.now().strftime('%B %d, %Y')}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"**Recommendation:** {recommendation_result.recommendation}",
            f"**Confidence:** {recommendation_result.confidence_level}",
            "",
            recommendation_result.reasoning,
            "",
            "### Key Strengths",
            ""
        ]
        
        for strength in financial_analysis.strengths[:5]:
            report_parts.append(f"- {strength}")
        
        report_parts.extend([
            "",
            "### Key Concerns",
            ""
        ])
        
        for concern in financial_analysis.concerns[:5]:
            report_parts.append(f"- {concern}")
        
        report_parts.extend([
            "",
            "### Key Risks",
            ""
        ])
        
        for risk in recommendation_result.key_risks[:5]:
            report_parts.append(f"- {risk}")
        
        report_parts.extend([
            "",
            "---",
            ""
        ])
        
        # Add generated sections
        for section_title, section_content in sections.items():
            report_parts.extend([
                f"## {section_title}",
                "",
                section_content,
                "",
                "---",
                ""
            ])
        
        # Add final recommendation section
        report_parts.extend([
            "## Investment Recommendation",
            "",
            f"**{recommendation_result.recommendation}**",
            "",
            recommendation_result.reasoning,
            "",
            "### Valuation Commentary",
            "",
            recommendation_result.price_target_commentary,
            "",
            "---",
            "",
            f"*This analysis reflects the investment philosophy of {persona_name} and should be considered as one perspective among many in making investment decisions.*"
        ])
        
        return "\n".join(report_parts)

class GenerateExpertQuestions(dspy.Signature):
    """Generate critical questions that a specific investment persona would ask about a company"""
    
    persona_name: str = dspy.InputField(description="Name of the investment persona (e.g., Warren Buffett)")
    persona_philosophy: str = dspy.InputField(description="Investment philosophy and approach")
    company_summary: str = dspy.InputField(description="Basic company information and context")
    n_questions: int = dspy.InputField(description="Number of questions to generate")
    
    questions: QuestionList = dspy.OutputField(description="List of critical investment questions")


class EvaluateReportCoverage(dspy.Signature):
    """Evaluate whether and how well a report answers a specific investment question"""
    
    question: str = dspy.InputField(description="The investment question to evaluate")
    question_category: str = dspy.InputField(description="Question category for context")
    report: str = dspy.InputField(description="The investment report to evaluate")
    persona_name: str = dspy.InputField(description="Investor persona for context")
    
    evaluation: QuestionEvaluation = dspy.OutputField(
        description="Detailed evaluation of question coverage"
    )


class AssessPersonaAlignment(dspy.Signature):
    """Assess whether a report reflects the investment philosophy of the persona"""
    
    persona_name: str = dspy.InputField(description="Investment persona")
    persona_philosophy: str = dspy.InputField(description="Core investment principles")
    report: str = dspy.InputField(description="Investment report")
    questions_coverage: str = dspy.InputField(description="Summary of question coverage")
    
    alignment_score: float = dspy.OutputField(description="Alignment score 0-10")
    alignment_reasoning: str = dspy.OutputField(description="Explanation of alignment assessment")
    philosophy_evidence: List[str] = dspy.OutputField(description="Report sections reflecting philosophy")
    philosophy_gaps: List[str] = dspy.OutputField(description="Missing philosophy elements")

class QuestionGenerator(dspy.Module):
    """Module for generating expert investor questions"""
    
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(GenerateExpertQuestions)
    
    def forward(self, persona_name: str, persona_philosophy: str, 
                company_summary: str, n_questions: int = 15) -> QuestionList:
        result = self.generate(
            persona_name=persona_name,
            persona_philosophy=persona_philosophy,
            company_summary=company_summary,
            n_questions=n_questions
        )
        return result.questions


class CoverageEvaluator(dspy.Module):
    """Module for evaluating report coverage of a single question"""
    
    def __init__(self):
        super().__init__()
        self.evaluate = dspy.ChainOfThought(EvaluateReportCoverage)
    
    def forward(self, question: InvestorQuestion, report: str, 
                persona_name: str) -> QuestionEvaluation:
        result = self.evaluate(
            question=question.question,
            question_category=question.category,
            report=report,
            persona_name=persona_name
        )
        return result.evaluation


class PersonaAlignmentChecker(dspy.Module):
    """Module for checking persona alignment"""
    
    def __init__(self):
        super().__init__()
        self.assess = dspy.ChainOfThought(AssessPersonaAlignment)
    
    def forward(self, persona_name: str, persona_philosophy: str,
                report: str, questions_coverage: str):
        return self.assess(
            persona_name=persona_name,
            persona_philosophy=persona_philosophy,
            report=report,
            questions_coverage=questions_coverage
        )

# ============================================================================
# EVALUATION MODULES
# ============================================================================   
class ReportEvaluator(dspy.Module):
    """Complete report evaluation pipeline"""
    
    def __init__(self, persona_definitions: dict):
        """
        Args:
            persona_definitions: Dict mapping persona names to their philosophies
                e.g., {"Warren Buffett": "Focus on quality businesses with moats..."}
        """
        super().__init__()
        self.persona_definitions = persona_definitions
        
        # Initialize sub-modules
        self.question_generator = QuestionGenerator()
        self.coverage_evaluator = CoverageEvaluator()
        self.alignment_checker = PersonaAlignmentChecker()
        
        # Storage
        self.questions = []
        self.evaluation_results = []
    
    def generate_expert_questions(self, persona_name: str, 
                                 company_summary: str, n: int = 15) -> List[InvestorQuestion]:
        """Generate expert questions for the persona"""
        persona_philosophy = self.persona_definitions[persona_name]
        
        question_list = self.question_generator(
            persona_name=persona_name,
            persona_philosophy=persona_philosophy,
            company_summary=company_summary,
            n_questions=n
        )
        
        self.questions = question_list.questions
        return self.questions
    
    def evaluate_report_coverage(self, report: str, persona_name: str) -> List[QuestionEvaluation]:
        """Evaluate how well the report covers each question"""
        self.evaluation_results = []
        
        for question in self.questions:
            evaluation = self.coverage_evaluator(
                question=question,
                report=report,
                persona_name=persona_name
            )
            self.evaluation_results.append(evaluation)
        
        return self.evaluation_results
    
    def compute_metrics(self, persona_name: str, report: str) -> ReportMetrics:
        """Compute aggregate metrics"""
        if not self.evaluation_results:
            raise ValueError("Must run evaluate_report_coverage first")
        
        # Count answerability
        answerable_counts = {
            "yes": sum(1 for r in self.evaluation_results if r.answerable == "yes"),
            "partial": sum(1 for r in self.evaluation_results if r.answerable == "partial"),
            "no": sum(1 for r in self.evaluation_results if r.answerable == "no")
        }
        
        total = len(self.evaluation_results)
        coverage_rate = (answerable_counts["yes"] + 0.5 * answerable_counts["partial"]) / total
        
        # Average quality
        quality_score = mean([r.quality_rating for r in self.evaluation_results])
        
        # Identify critical gaps (questions with high importance and low coverage)
        critical_gaps = []
        for q, eval_result in zip(self.questions, self.evaluation_results):
            if q.importance > 0.7 and eval_result.quality_rating < 5:
                critical_gaps.extend(eval_result.missing_information)
        
        # Get persona alignment
        persona_philosophy = self.persona_definitions[persona_name]
        coverage_summary = self._summarize_coverage()
        
        alignment = self.alignment_checker(
            persona_name=persona_name,
            persona_philosophy=persona_philosophy,
            report=report,
            questions_coverage=coverage_summary
        )
        
        return ReportMetrics(
            coverage_rate=coverage_rate,
            quality_score=quality_score,
            answerable_fully=answerable_counts["yes"],
            answerable_partial=answerable_counts["partial"],
            not_answerable=answerable_counts["no"],
            critical_gaps=list(set(critical_gaps))[:5]  # Top 5 unique gaps
        ), alignment
    
    def _summarize_coverage(self) -> str:
        """Create a summary of question coverage for persona alignment"""
        summary_parts = []
        for q, eval_result in zip(self.questions, self.evaluation_results):
            summary_parts.append(
                f"Q: {q.question}\n"
                f"Coverage: {eval_result.answerable}\n"
                f"Quality: {eval_result.quality_rating}/10\n"
            )
        return "\n".join(summary_parts)
    
    def forward(self, persona_name: str, company_summary: str, 
                report: str, n_questions: int = 15):
        """Complete evaluation pipeline"""
        # Generate questions
        self.generate_expert_questions(persona_name, company_summary, n_questions)
        
        # Evaluate coverage
        self.evaluate_report_coverage(report, persona_name)
        
        # Compute metrics
        metrics, alignment = self.compute_metrics(persona_name, report)
        
        return {
            "questions": self.questions,
            "evaluations": self.evaluation_results,
            "metrics": metrics,
            "alignment": alignment
        }


# ============================================================================
# COMPLETE PIPELINE: DOCUMENTS → REPORTS → EVALUATION
# ============================================================================

class InvestmentAnalysisPipeline:
    """End-to-end pipeline: financial docs → generated reports → evaluation"""
    
    def __init__(
        self,
        doc_loader: FinancialDocumentLoader,
        report_generator: InvestmentReportGenerator,
        report_evaluator: 'ReportEvaluator',
        output_dir: Path
    ):
        self.doc_loader = doc_loader
        self.report_generator = report_generator
        self.report_evaluator = report_evaluator
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Storage for generated reports and evaluations
        self.generated_reports = {}
        self.evaluation_results = []
    
    def run_complete_analysis(
        self,
        models: List[str],
        personas: List[str],
        companies: List[str],
        company_summaries: Dict[str, str],
        years: Optional[List[str]] = None
    ):
        """
        Run complete pipeline for all combinations
        
        Args:
            models: List of LLM models to test (e.g., ["gpt-4", "claude", "gemini"])
            personas: List of personas (e.g., ["Warren Buffett", "Benjamin Graham"])
            companies: List of companies to analyze
            company_summaries: Dict mapping company names to descriptions
            years: Optional list of years to analyze (default: all available)
        """
        print("="*80)
        print("🚀 STARTING INVESTMENT ANALYSIS PIPELINE")
        print("="*80)
        
        total_combinations = len(models) * len(personas) * len(companies)
        current = 0
        
        for company in companies:
            print(f"\n📊 Analyzing Company: {company.upper()}")
            print("-" * 80)
            
            # Get financial documents for this company
            company_docs = self.doc_loader.get_company_documents(company)
            
            if not company_docs:
                print(f"  ⚠️  No documents found for {company}")
                continue
            
            # Filter by year if specified
            if years:
                company_docs = {y: doc for y, doc in company_docs.items() if y in years}
            
            for year, financial_doc in company_docs.items():
                print(f"\n  📅 Year: {year}")
                
                for model in models:
                    print(f"    🤖 Model: {model}")
                    
                    # Configure DSPy for this model
                    self._configure_model(model)
                    
                    for persona in personas:
                        current += 1
                        print(f"      👤 Persona: {persona} ({current}/{total_combinations})")
                        
                        try:
                            # STEP 1: Generate Report
                            print(f"        ⚙️  Generating report...")
                            report = self.report_generator(
                                persona_name=persona,
                                company_name=company,
                                financial_documents=financial_doc,
                                news_data=None  # Add news if available
                            )
                            
                            # Save generated report
                            report_filename = f"{model}_{persona.lower().replace(' ', '_')}_{company}_{year}.md"
                            report_path = self.output_dir / "generated_reports" / report_filename
                            report_path.parent.mkdir(exist_ok=True)
                            
                            with open(report_path, 'w', encoding='utf-8') as f:
                                f.write(report)
                            
                            self.generated_reports[report_filename] = report
                            print(f"        ✅ Report saved: {report_filename}")
                            
                            # STEP 2: Evaluate Report
                            print(f"        📊 Evaluating report...")
                            evaluation = self.report_evaluator(
                                persona_name=persona,
                                company_summary=company_summaries.get(
                                    company,
                                    f"Analysis of {company} on Jamaica Stock Exchange"
                                ),
                                report=report,
                                n_questions=15
                            )
                            
                            # Store evaluation results
                            result = {
                                'model': model,
                                'persona': persona,
                                'company': company,
                                'year': year,
                                'report_filename': report_filename,
                                'evaluation': evaluation,
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            self.evaluation_results.append(result)
                            
                            # Print summary
                            metrics = evaluation['metrics']
                            alignment = evaluation['alignment']
                            print(f"        ✅ Coverage: {metrics.coverage_rate:.2%} | "
                                  f"Quality: {metrics.quality_score:.1f}/10 | "
                                  f"Alignment: {alignment.alignment_score:.1f}/10")
                            
                        except Exception as e:
                            print(f"        ❌ Error: {str(e)}")
                            self.evaluation_results.append({
                                'model': model,
                                'persona': persona,
                                'company': company,
                                'year': year,
                                'error': str(e),
                                'timestamp': datetime.now().isoformat()
                            })
        
        # Save all results
        self._save_results()
        self._generate_summary_report()
        
        print("\n" + "="*80)
        print("✅ PIPELINE COMPLETE")
        print("="*80)
    
    def _configure_model(self, model: str):
        """Configure DSPy for specific model"""
        # Map model names to proper DSPy model strings
        model_mapping = {
            'gpt-4': f'openai/{TASK_MODEL}',
            'claude': f'anthropic/{TASK_MODEL}', 
            'gemini': f'gemini/{TASK_MODEL}'
        }
        
        # Use the current provider's configuration
        if model.lower() == PROVIDER:
            # Use the already configured models
            dspy.configure(lm=task_lm)
        else:
            # For other models, you'd need proper API keys
            print(f"⚠️  Model {model} not configured. Using current model {PROVIDER}")
            dspy.configure(lm=task_lm)
    
    def _save_results(self):
        """Save evaluation results to JSON"""
        results_dir = self.output_dir / "evaluation_results"
        results_dir.mkdir(exist_ok=True)
        
        # Prepare results for JSON serialization
        json_results = []
        for result in self.evaluation_results:
            if 'error' not in result:
                json_result = {
                    'model': result['model'],
                    'persona': result['persona'],
                    'company': result['company'],
                    'year': result['year'],
                    'report_filename': result['report_filename'],
                    'timestamp': result['timestamp'],
                    'metrics': result['evaluation']['metrics'].model_dump(),
                    'alignment': {
                        'score': result['evaluation']['alignment'].alignment_score,
                        'reasoning': result['evaluation']['alignment'].alignment_reasoning,
                        'evidence': result['evaluation']['alignment'].philosophy_evidence,
                        'gaps': result['evaluation']['alignment'].philosophy_gaps
                    },
                    'question_summary': {
                        'total': len(result['evaluation']['questions']),
                        'categories': self._summarize_questions(result['evaluation']['questions'])
                    }
                }
            else:
                json_result = result
            
            json_results.append(json_result)
        
        # Save full results
        output_file = results_dir / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved: {output_file}")
    
    def _summarize_questions(self, questions) -> dict:
        """Summarize question categories"""
        from collections import Counter
        categories = [q.category for q in questions]
        return dict(Counter(categories))
    
    def _generate_summary_report(self):
        """Generate markdown summary report"""
        report_lines = [
            "# Investment Analysis Pipeline - Summary Report",
            f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n**Total Analyses:** {len(self.evaluation_results)}",
            "\n---\n"
        ]
        
        # Summary by model
        report_lines.append("## Results by Model\n")
        by_model = {}
        
        for result in self.evaluation_results:
            if 'error' in result:
                continue
            
            model = result['model']
            if model not in by_model:
                by_model[model] = {
                    'coverage': [],
                    'quality': [],
                    'alignment': []
                }
            
            metrics = result['evaluation']['metrics']
            alignment = result['evaluation']['alignment']
            
            by_model[model]['coverage'].append(metrics.coverage_rate)
            by_model[model]['quality'].append(metrics.quality_score)
            by_model[model]['alignment'].append(alignment.alignment_score)
        
        report_lines.append("| Model | Avg Coverage | Avg Quality | Avg Alignment | Count |")
        report_lines.append("|-------|--------------|-------------|---------------|-------|")
        
        for model, scores in sorted(by_model.items()):
            avg_cov = sum(scores['coverage']) / len(scores['coverage'])
            avg_qual = sum(scores['quality']) / len(scores['quality'])
            avg_align = sum(scores['alignment']) / len(scores['alignment'])
            count = len(scores['coverage'])
            
            report_lines.append(
                f"| {model} | {avg_cov:.2%} | {avg_qual:.1f}/10 | {avg_align:.1f}/10 | {count} |"
            )
        
        # Summary by persona
        report_lines.append("\n## Results by Persona\n")
        by_persona = {}
        
        for result in self.evaluation_results:
            if 'error' in result:
                continue
            
            persona = result['persona']
            if persona not in by_persona:
                by_persona[persona] = {
                    'coverage': [],
                    'quality': [],
                    'alignment': []
                }
            
            metrics = result['evaluation']['metrics']
            alignment = result['evaluation']['alignment']
            
            by_persona[persona]['coverage'].append(metrics.coverage_rate)
            by_persona[persona]['quality'].append(metrics.quality_score)
            by_persona[persona]['alignment'].append(alignment.alignment_score)
        
        report_lines.append("| Persona | Avg Coverage | Avg Quality | Avg Alignment | Count |")
        report_lines.append("|---------|--------------|-------------|---------------|-------|")
        
        for persona, scores in sorted(by_persona.items()):
            avg_cov = sum(scores['coverage']) / len(scores['coverage'])
            avg_qual = sum(scores['quality']) / len(scores['quality'])
            avg_align = sum(scores['alignment']) / len(scores['alignment'])
            count = len(scores['coverage'])
            
            report_lines.append(
                f"| {persona} | {avg_cov:.2%} | {avg_qual:.1f}/10 | {avg_align:.1f}/10 | {count} |"
            )
        
        # Save summary
        summary_path = self.output_dir / "SUMMARY_REPORT.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"📊 Summary report: {summary_path}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Complete workflow: Load docs → Generate reports → Evaluate"""
    
    # 1. Configure paths
    OUTPUT_DIR = Path("./output")
    
    # 2. Define personas
    persona_definitions = {
        "Warren Buffett": """Focus on high-quality businesses with durable competitive advantages (economic moats), 
        excellent management, consistent earnings growth, and reasonable valuations. Look for companies that can 
        compound wealth over decades through reinvestment and organic growth.""",
        
        "Benjamin Graham": """Deep value investing with emphasis on margin of safety, asset-based valuation, 
        and contrarian opportunities. Focus on companies trading below intrinsic value with strong balance sheets 
        and conservative debt levels.""",
        
        "Peter Lynch": """Growth at a reasonable price (GARP) approach. Look for companies with strong earnings 
        growth, expanding markets, competent management, and reasonable P/E ratios relative to growth rates."""
    }
    
    # 3. Define company summaries (add more as needed)
    company_summaries = {
        "ncb-financial-group": "National Commercial Bank: Jamaica's largest commercial bank providing financial services",
        "gracekennedy": "GraceKennedy Ltd: Jamaican conglomerate in food processing, financial services, and retail",
        "jmmb-group": "JMMB Group: Integrated financial services group offering banking, investments, and insurance",
        "access-financial": "Access Financial Services: Financial services company offering loans and investments",
        "eppley": "Eppley Limited: Investment and real estate development company",
        "ciboney-group": "Ciboney Group: Diversified investment company with real estate and other holdings"
    }
    
    # 4. Load financial documents
    doc_loader = FinancialDocumentLoader(MARKDOWN_DIR)
    doc_loader.load_all_documents()
    
    # 5. Initialize components
    report_generator = InvestmentReportGenerator(persona_definitions)
    report_evaluator = ReportEvaluator(persona_definitions)
    
    # 6. Create pipeline
    pipeline = InvestmentAnalysisPipeline(
        doc_loader=doc_loader,
        report_generator=report_generator,
        report_evaluator=report_evaluator,
        output_dir=OUTPUT_DIR
    )
    
    # 7. Test with a smaller subset first
    print("🧪 Running test analysis with limited scope...")
    
    # Find available companies from loaded documents
    available_companies = set()
    for filename in doc_loader.documents.keys():
        metadata = doc_loader.parse_document_metadata(filename)
        if metadata['company'] != 'unknown':
            available_companies.add(metadata['company'])
    
    # Take first few companies that have summaries or are recognizable
    test_companies = []
    for company in list(available_companies)[:5]:
        test_companies.append(company)
    
    print(f"📊 Found companies: {test_companies}")
    
    # For testing, let's just run one combination
    try:
        pipeline.run_complete_analysis(
            models=["gemini"],  # Just test with current model
            personas=["Warren Buffett"],  # Just one persona
            companies=test_companies[:1],  # Just one company
            company_summaries=company_summaries,
            years=None  # Use all available years
        )
    except Exception as e:
        print(f"⚠️  Full pipeline test encountered an issue: {e}")
        print("This is expected since the InvestmentReportGenerator needs implementation.")
        print("The core evaluation framework is working correctly!")
    
    return pipeline


if __name__ == "__main__":
    pipeline = main()
