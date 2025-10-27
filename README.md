# 📊 Evaluating LLM Performance on Financial Document Analysis

> A comprehensive framework for evaluating Large Language Models (LLMs) on their ability to generate investment analysis reports that align with specific investment philosophies.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DSPy](https://img.shields.io/badge/DSPy-3.0.3-green.svg)](https://github.com/stanfordnlp/dspy)

## 🎯 Project Overview

This research project evaluates how well different LLMs can generate investment analysis reports that authentically embody the investment philosophies of legendary investors like Warren Buffett, Benjamin Graham, and Peter Lynch. 

The framework provides:
- **Automated report generation** from financial documents using different LLM models
- **Multi-dimensional evaluation** measuring coverage, quality, and persona alignment
- **Systematic benchmarking** across models, personas, companies, and time periods
- **Research-grade datasets** for studying LLM capabilities in specialized financial domains

### Key Research Questions

1. **Persona Fidelity**: Can LLMs authentically embody specific investment philosophies?
2. **Model Comparison**: Which LLM (GPT-4, Claude, Gemini) performs best at financial analysis?
3. **Coverage & Quality**: How comprehensive and accurate are LLM-generated investment reports?
4. **Consistency**: Do LLMs maintain quality across different companies and time periods?

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Investment Analysis Pipeline                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────┐
        │   1. Load Financial Documents         │
        │   - 60+ Jamaican Stock Exchange       │
        │   - Markdown formatted statements     │
        └───────────────┬───────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │   2. Generate Investment Reports      │
        │   - Multi-step DSPy pipeline         │
        │   - Persona-aligned analysis         │
        │   - 5 LLM calls per report           │
        └───────────────┬───────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │   3. Evaluate Report Quality          │
        │   - Generate expert questions        │
        │   - Assess coverage & quality        │
        │   - Measure persona alignment        │
        └───────────────┬───────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │   4. Save Results & Analytics         │
        │   - JSON evaluation results          │
        │   - Markdown summary reports         │
        │   - Aggregated statistics            │
        └───────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+ (recommended)
- API key for at least one LLM provider (Gemini, OpenAI, or Anthropic)
- ~2GB disk space for documents and outputs

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd evaluating_llm_fin_docs
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your API key(s)
```

Example `.env` file:
```ini
# Add at least one API key
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

5. **Run the pipeline**
```bash
# Test with default settings (1 company, 1 persona, current model)
python evaluating_llm_fin_reports.py

# Or run comprehensive tests
python test_script.py
python test_pipeline.py
python test_report_generator.py
```

---

## 📁 Project Structure

```
evaluating_llm_fin_docs/
│
├── evaluating_llm_fin_reports.py    # Main pipeline implementation
├── evaluating_llm_fin_reports.ipynb # Jupyter notebook version
├── requirements.txt                  # Python dependencies
├── .env                             # Environment variables (create from .env.example)
│
├── fin_docs/                        # Financial documents (60+ markdown files)
│   ├── NCB-Financial-Group-*.md
│   ├── Access-Financial-*.md
│   └── ...
│
├── output/                          # Generated outputs
│   ├── generated_reports/           # Investment analysis reports
│   ├── evaluation_results/          # JSON evaluation data
│   └── SUMMARY_REPORT.md           # Aggregated statistics
│
├── test_script.py                   # Core component tests
├── test_pipeline.py                 # Pipeline integration tests
├── test_report_generator.py         # Report generation tests
│
└── docs/                            # Documentation
    ├── TEST_RESULTS.md
    └── IMPLEMENTATION_COMPLETE.md
```

---

## 🧩 Core Components

### 1. **FinancialDocumentLoader**
Loads and manages financial documents with intelligent metadata parsing.

```python
from evaluating_llm_fin_reports import FinancialDocumentLoader

loader = FinancialDocumentLoader("fin_docs")
documents = loader.load_all_documents()

# Get documents for specific company
ncb_docs = loader.get_company_documents("ncb")
```

### 2. **InvestmentReportGenerator**
Multi-step DSPy pipeline that generates comprehensive investment reports.

**Process:**
1. Generate report outline based on persona
2. Analyze financial documents
3. Create investment recommendation
4. Write detailed report sections
5. Assemble final markdown report

```python
from evaluating_llm_fin_reports import InvestmentReportGenerator

personas = {
    "Warren Buffett": "Focus on quality businesses with moats..."
}

generator = InvestmentReportGenerator(personas)
report = generator(
    persona_name="Warren Buffett",
    company_name="NCB Financial Group",
    financial_documents=financial_doc
)
```

### 3. **ReportEvaluator**
Evaluates generated reports across multiple dimensions.

**Metrics:**
- **Coverage Rate**: % of expert questions answered (0-100%)
- **Quality Score**: Average answer quality (0-10)
- **Alignment Score**: Persona philosophy alignment (0-10)

```python
from evaluating_llm_fin_reports import ReportEvaluator

evaluator = ReportEvaluator(personas)
evaluation = evaluator(
    persona_name="Warren Buffett",
    company_summary="Jamaica's largest commercial bank",
    report=generated_report,
    n_questions=15
)

print(f"Coverage: {evaluation['metrics'].coverage_rate:.2%}")
print(f"Quality: {evaluation['metrics'].quality_score:.1f}/10")
print(f"Alignment: {evaluation['alignment'].alignment_score:.1f}/10")
```

### 4. **InvestmentAnalysisPipeline**
End-to-end orchestrator for batch processing.

```python
from evaluating_llm_fin_reports import InvestmentAnalysisPipeline

pipeline = InvestmentAnalysisPipeline(
    doc_loader=loader,
    report_generator=generator,
    report_evaluator=evaluator,
    output_dir=Path("./output")
)

pipeline.run_complete_analysis(
    models=["gemini", "gpt-4", "claude"],
    personas=["Warren Buffett", "Benjamin Graham"],
    companies=["ncb", "gracekennedy"],
    company_summaries=company_summaries,
    years=["2022", "2023"]
)
```

---

## 🎭 Investment Personas

The framework supports multiple investment philosophies:

### Warren Buffett - Quality & Moats
- Focus on durable competitive advantages (economic moats)
- Excellent management and corporate governance
- Consistent earnings growth and capital allocation
- Long-term wealth compounding

### Benjamin Graham - Deep Value
- Emphasis on margin of safety
- Asset-based valuation
- Contrarian opportunities
- Strong balance sheets with conservative debt

### Peter Lynch - Growth at Reasonable Price (GARP)
- Strong earnings growth potential
- Expanding markets and opportunities
- Reasonable P/E ratios relative to growth
- Competent management execution

**Adding New Personas:**
Edit the `persona_definitions` dict in `main()`:
```python
persona_definitions = {
    "Your Persona": """Your investment philosophy here..."""
}
```

---

## 📊 Output Examples

### Generated Investment Report
```markdown
# Investment Analysis: NCB Financial Group
**Analyst Perspective:** Warren Buffett
**Date:** October 27, 2025

## Executive Summary
**Recommendation:** Buy
**Confidence:** Medium

NCB Financial Group presents a compelling case for a value investor...

### Key Strengths
- Exceptional net profit growth (88% YoY)
- Improved ROE to 16.14%
- Strong operational efficiency (71.87% cost-to-income ratio)
...
```

### Evaluation Results (JSON)
```json
{
  "model": "gemini",
  "persona": "Warren Buffett",
  "company": "ncb",
  "year": "2022",
  "metrics": {
    "coverage_rate": 0.53,
    "quality_score": 6.0,
    "answerable_fully": 8,
    "answerable_partial": 7,
    "not_answerable": 0
  },
  "alignment": {
    "score": 9.5,
    "reasoning": "Report strongly reflects Buffett's philosophy..."
  }
}
```

### Summary Report
```markdown
## Results by Model

| Model  | Avg Coverage | Avg Quality | Avg Alignment | Count |
|--------|--------------|-------------|---------------|-------|
| gemini | 53.33%      | 6.0/10      | 9.5/10       | 12    |
| gpt-4  | 61.25%      | 7.2/10      | 8.8/10       | 12    |
| claude | 58.10%      | 6.8/10      | 9.1/10       | 12    |
```

---

## ⚙️ Configuration

### Model Configuration

Edit the configuration section in `evaluating_llm_fin_reports.py`:

```python
# Model configuration
PROVIDER = "gemini"  # Options: "openai", "gemini", "anthropic"
TASK_MODEL_TEMP = 0.0  # Low for deterministic extraction
REFLECTION_MODEL_TEMP = 1.0  # High for diverse reflections

# For Gemini:
TASK_MODEL = "gemini-2.5-flash"
REFLECTION_MODEL = "gemini-2.5.pro"

# For OpenAI:
TASK_MODEL = "gpt-4-turbo"
REFLECTION_MODEL = "gpt-4"

# For Anthropic:
TASK_MODEL = "claude-3-opus"
REFLECTION_MODEL = "claude-3-sonnet"
```

### Pipeline Parameters

```python
# In main() function:
pipeline.run_complete_analysis(
    models=["gemini"],  # Which models to test
    personas=["Warren Buffett", "Benjamin Graham"],
    companies=["ncb", "gracekennedy"],
    company_summaries=company_summaries,
    years=["2022", "2023"],  # Optional: filter by year
)
```

---

## 🧪 Testing

The project includes comprehensive tests:

```bash
# Test core components (document loading, question generation, evaluation)
python test_script.py

# Test pipeline setup and integration
python test_pipeline.py

# Test report generation end-to-end
python test_report_generator.py
```

**Expected Test Results:**
- ✅ All 60 financial documents loaded
- ✅ Question generation produces 5-15 questions per persona
- ✅ Report generation creates ~20-30k character reports
- ✅ Evaluation produces coverage (40-60%), quality (5-7/10), alignment (7-10/10)

---

## 🔬 Research Use Cases

### 1. **Model Comparison Study**
Compare GPT-4, Claude, and Gemini on financial analysis tasks:
```python
pipeline.run_complete_analysis(
    models=["gpt-4", "claude", "gemini"],
    personas=["Warren Buffett"],
    companies=all_companies,
    years=["2023"]
)
```

### 2. **Persona Fidelity Analysis**
Measure how well models embody different investment styles:
```python
pipeline.run_complete_analysis(
    models=["gpt-4"],
    personas=["Warren Buffett", "Benjamin Graham", "Peter Lynch"],
    companies=selected_companies
)
```

### 3. **Temporal Consistency**
Evaluate consistency across different time periods:
```python
pipeline.run_complete_analysis(
    models=["gemini"],
    personas=["Warren Buffett"],
    companies=["ncb"],
    years=["2020", "2021", "2022", "2023"]
)
```

### 4. **Industry-Specific Analysis**
Focus on specific sectors:
```python
financial_companies = ["ncb", "jmmb-group", "access-financial"]
manufacturing_companies = ["berger-paints", "caribbean-flavours"]
```

---

## 📈 Performance Characteristics

**Report Generation:**
- Time: ~2-3 minutes per report (5 LLM calls)
- Cost: ~$0.01-0.05 per report (depends on model)
- Token usage: 10k-20k tokens per report

**Evaluation:**
- Time: ~1-2 minutes per evaluation (15 LLM calls)
- Generates 15 expert questions
- Evaluates each question individually

**Full Pipeline:**
- 1 model × 1 persona × 1 company = ~5 minutes
- 3 models × 3 personas × 10 companies = ~7.5 hours
- Results cached and can be analyzed later

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### For Collaborators

1. **Fork and clone** the repository
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make your changes** and test thoroughly
4. **Commit with clear messages**: `git commit -m "Add: New persona for Cathie Wood"`
5. **Push and create PR**: `git push origin feature/your-feature`

### Areas for Contribution

- 🎭 **New Personas**: Add investment styles (Ray Dalio, Cathie Wood, etc.)
- 📊 **New Metrics**: Additional evaluation dimensions
- 🔧 **Optimizations**: Improve speed, reduce token usage
- 📈 **Analysis Tools**: Visualization and statistical analysis
- 📚 **Documentation**: Tutorials, examples, research papers
- 🧪 **Testing**: More comprehensive test coverage

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings to all classes and functions
- Keep functions focused and modular

---

## 📚 Documentation

- [Test Results](TEST_RESULTS.md) - Latest test outcomes
- [Implementation Details](IMPLEMENTATION_COMPLETE.md) - Technical deep dive
- [DSPy Documentation](https://dspy-docs.vercel.app/) - Framework reference

---

## 🐛 Troubleshooting

### Common Issues

**"API key not found"**
```bash
# Make sure .env file exists and has correct key
cat .env
# Should show: GEMINI_API_KEY=your_key_here
```

**"LLM response truncated"**
```python
# Increase max_tokens in configuration
task_lm = dspy.LM(
    model=f"{PROVIDER}/{TASK_MODEL}",
    max_tokens=8000,  # Increase from default 4000
    api_key=api_key
)
```

**"No documents found for company"**
```python
# Check available companies
loader = FinancialDocumentLoader("fin_docs")
loader.load_all_documents()
available = set(loader.parse_document_metadata(f)['company'] 
                for f in loader.documents.keys())
print(available)
```

**Performance Issues**
```python
# Reduce scope for testing
pipeline.run_complete_analysis(
    models=["gemini"],  # Just one model
    personas=["Warren Buffett"],  # Just one persona
    companies=["ncb"],  # Just one company
    years=["2023"]  # Just one year
)
```

---

## 📊 Data

### Financial Documents
- **Source**: Jamaica Stock Exchange quarterly and annual reports
- **Format**: Markdown converted from PDFs
- **Companies**: 30+ Jamaican public companies
- **Time Period**: 2018-2023
- **Count**: 60+ documents

### Document Naming Convention
```
{Company}-{Type}-{Period}-{Year}.md

Examples:
NCB-Financial-Group-Unaudited-Results-Q3-2022.md
Access-Financial-Audited-Statements-2021.md
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **DSPy Framework** by Stanford NLP for structured LLM programming
- **Jamaica Stock Exchange** for public financial disclosures
- **OpenAI, Anthropic, Google** for LLM APIs

---

## 📧 Contact

For questions, suggestions, or collaboration opportunities:
- **Issues**: Open a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Email**: [Your contact email]

---

## 🔮 Future Roadmap

- [ ] Support for more LLM providers (Cohere, LLaMA, etc.)
- [ ] Web interface for interactive analysis
- [ ] Automated financial ratio calculations
- [ ] Integration with real-time market data
- [ ] Multi-language support for international markets
- [ ] Fine-tuning dataset generation
- [ ] Comparative analysis visualizations
- [ ] GEPA optimization for report quality
- [ ] News sentiment integration
- [ ] Portfolio-level analysis

---

**Built with ❤️ for financial AI research**

*Last Updated: October 27, 2025*
