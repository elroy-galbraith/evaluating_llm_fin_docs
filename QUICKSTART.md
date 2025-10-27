# 🚀 Quick Start Guide

Get up and running with the LLM Financial Analysis Framework in under 10 minutes!

## 📋 Prerequisites Checklist

- [ ] Python 3.13+ installed (`python --version`)
- [ ] Git installed (`git --version`)
- [ ] At least one LLM API key (see [Getting API Keys](#getting-api-keys))
- [ ] 2GB free disk space
- [ ] Internet connection

---

## ⚡ 5-Minute Setup

### Step 1: Clone and Install (2 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd evaluating_llm_fin_docs

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure API Key (1 minute)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
# Use nano, vim, or any text editor
nano .env
```

Add your API key:
```ini
GEMINI_API_KEY=your_actual_api_key_here
```

Save and exit.

### Step 3: Test Installation (2 minutes)

```bash
# Run basic tests
python test_script.py

# Expected output:
# ✅ Loaded 60 financial documents
# ✅ Generated 5 questions
# ✅ Evaluation completed
# ✅ ALL TESTS PASSED
```

---

## 🎯 Your First Analysis

### Generate a Single Report

```bash
# Run the main pipeline (generates 1 report by default)
python evaluating_llm_fin_reports.py
```

This will:
1. Load financial documents ✅
2. Generate an investment report (2-3 minutes) ⏱️
3. Evaluate the report (1-2 minutes) 📊
4. Save results to `output/` directory 💾

**Output Files:**
- `output/generated_reports/gemini_warren_buffett_*.md` - The investment report
- `output/evaluation_results/results_*.json` - Evaluation data
- `output/SUMMARY_REPORT.md` - Performance summary

### View Your First Report

```bash
# List generated reports
ls output/generated_reports/

# View a report
cat output/generated_reports/gemini_warren_buffett_*.md | head -50
```

---

## 🧪 Interactive Testing

### Test Individual Components

```python
# Start Python REPL
python

# Test document loading
from evaluating_llm_fin_reports import FinancialDocumentLoader, MARKDOWN_DIR
loader = FinancialDocumentLoader(MARKDOWN_DIR)
docs = loader.load_all_documents()
print(f"Loaded {len(docs)} documents")

# Test question generation
from evaluating_llm_fin_reports import QuestionGenerator
gen = QuestionGenerator()
questions = gen(
    persona_name="Warren Buffett",
    persona_philosophy="Focus on quality businesses with moats",
    company_summary="NCB: Jamaica's largest bank",
    n_questions=5
)
print(f"Generated {len(questions.questions)} questions")
for q in questions.questions[:3]:
    print(f"- {q.question}")
```

---

## 🎨 Customization Examples

### Example 1: Analyze a Specific Company

Edit `main()` function in `evaluating_llm_fin_reports.py`:

```python
# Around line 1040
pipeline.run_complete_analysis(
    models=["gemini"],
    personas=["Warren Buffett"],
    companies=["ncb"],  # Just analyze NCB
    company_summaries=company_summaries,
    years=["2022"]  # Just 2022 data
)
```

### Example 2: Compare Multiple Personas

```python
pipeline.run_complete_analysis(
    models=["gemini"],
    personas=["Warren Buffett", "Benjamin Graham", "Peter Lynch"],
    companies=["ncb"],
    company_summaries=company_summaries
)
```

### Example 3: Add Your Own Persona

```python
# Add to persona_definitions dict (around line 1010)
persona_definitions = {
    "Warren Buffett": """...""",
    "Benjamin Graham": """...""",
    
    # Your custom persona
    "Your Name": """
    Your investment philosophy here.
    Focus on: X, Y, Z
    Avoid: A, B, C
    """
}
```

---

## 📊 Understanding the Output

### Report Structure

```markdown
# Investment Analysis: {Company}
**Analyst Perspective:** {Persona}
**Date:** {Date}

## Executive Summary
**Recommendation:** Buy/Sell/Hold
**Confidence:** High/Medium/Low

[Detailed reasoning]

### Key Strengths
- Strength 1
- Strength 2

### Key Concerns
- Concern 1
- Concern 2

### Key Risks
- Risk 1
- Risk 2

## [4-5 Detailed Analysis Sections]
...

## Investment Recommendation
[Final thoughts and valuation]
```

### Evaluation Metrics

```json
{
  "coverage_rate": 0.53,     // 53% of questions answered
  "quality_score": 6.0,      // Average quality: 6.0/10
  "answerable_fully": 8,     // 8 questions fully answered
  "answerable_partial": 7,   // 7 questions partially answered
  "not_answerable": 0,       // 0 questions not answered
  "alignment_score": 9.5     // Persona alignment: 9.5/10
}
```

**What's Good?**
- Coverage: >50% is good, >70% is excellent
- Quality: >6.0 is good, >8.0 is excellent
- Alignment: >8.0 is good, >9.0 is excellent

---

## 🔧 Troubleshooting

### Issue: "API key not found"

```bash
# Check if .env file exists
ls -la | grep .env

# Check if key is set
cat .env | grep GEMINI_API_KEY

# Make sure no extra spaces
# Wrong: GEMINI_API_KEY = your_key
# Right: GEMINI_API_KEY=your_key
```

### Issue: "Module not found"

```bash
# Make sure virtual environment is activated
which python  # Should show path to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Rate limit exceeded"

Gemini free tier limits:
- 60 requests per minute
- 1500 requests per day

**Solution**: Add delays or use paid tier

```python
import time
# Add in pipeline after each report
time.sleep(2)  # Wait 2 seconds between requests
```

### Issue: Reports are too short/low quality

```python
# Increase max_tokens
task_lm = dspy.LM(
    model=f"{PROVIDER}/{TASK_MODEL}",
    max_tokens=8000,  # Increase from 4000
    api_key=api_key
)
```

---

## 🎓 Learning Path

### Day 1: Basics
1. ✅ Setup and installation
2. ✅ Run first analysis
3. ✅ Understand output structure
4. 📚 Read README thoroughly

### Day 2: Exploration
1. 🧪 Test different personas
2. 📊 Analyze multiple companies
3. 🔍 Examine evaluation metrics
4. 📚 Read DSPy documentation

### Week 1: Customization
1. ✨ Add custom persona
2. 🔧 Adjust evaluation parameters
3. 📈 Run batch analyses
4. 📝 Document findings

### Week 2+: Contribution
1. 🐛 Report bugs
2. 💡 Suggest features
3. 🤝 Submit pull requests
4. 📚 Write tutorials

---

## 📚 Next Steps

Ready to dive deeper?

1. **Read the full README** - [README.md](README.md)
2. **Learn DSPy** - [DSPy Documentation](https://dspy-docs.vercel.app/)
3. **Study the code** - `evaluating_llm_fin_reports.py`
4. **Join discussions** - GitHub Discussions
5. **Contribute** - [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🎯 Common Use Cases

### Research Project
```bash
# Run comprehensive analysis
# Edit main() to include all models, personas, companies
python evaluating_llm_fin_reports.py

# Results in output/ directory
# Analyze with pandas, matplotlib, etc.
```

### Testing a Hypothesis
```python
# "Does Gemini better embody value investing than growth investing?"
pipeline.run_complete_analysis(
    models=["gemini"],
    personas=["Benjamin Graham", "Peter Lynch"],
    companies=all_companies
)
# Compare alignment scores in output
```

### Model Comparison
```python
# "Which LLM is best at financial analysis?"
pipeline.run_complete_analysis(
    models=["gemini", "gpt-4", "claude"],
    personas=["Warren Buffett"],
    companies=selected_companies
)
# Compare coverage and quality scores
```

---

## 💡 Pro Tips

1. **Start Small**: Test with 1 company before running full batches
2. **Monitor Costs**: Check API usage regularly
3. **Save Outputs**: Results are valuable - back them up
4. **Document Changes**: Keep notes on experiments
5. **Ask Questions**: Use GitHub Discussions for help

---

## 🆘 Getting Help

**Can't figure something out?**

1. 📖 Check README troubleshooting section
2. 🔍 Search existing issues on GitHub
3. 💬 Ask in GitHub Discussions
4. 🐛 Open a new issue with details

**Include in your question:**
- What you're trying to do
- What you tried
- What happened (error messages, unexpected output)
- Your environment (OS, Python version, provider)

---

## 🎉 You're Ready!

You now have:
- ✅ A working installation
- ✅ Your first generated report
- ✅ Understanding of basic usage
- ✅ Resources for going deeper

**Happy analyzing! 📊🚀**

---

*For more details, see [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md)*
