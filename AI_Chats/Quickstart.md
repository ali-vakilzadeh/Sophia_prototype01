# 🚀 Sophia Prototype - Quick Start Guide

Get up and running in 5 minutes!

---

## One-Time Setup (5 minutes)

### 1. Install Python 3.11+

Check if you have it:
```bash
python --version
```

If not, download from [python.org](https://python.org)

### 2. Create Project Folder

```bash
mkdir sophia_prototype
cd sophia_prototype
```

### 3. Save All Files

Save these files from the artifacts:
- `sophia_prototype.py` - Core engine
- `app.py` - Streamlit UI
- `requirements.txt` - Dependencies
- `.env.example` - Config template
- `sample_project.txt` - Example project (optional)

### 4. Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- ChromaDB (vector store)
- Streamlit (UI framework)
- OpenRouter client libraries
- Other utilities

### 6. Configure API Key

```bash
# Copy template
cp .env.example .env

# Edit .env file and add your OpenRouter API key
# Get one free at: https://openrouter.ai/keys
```

Your `.env` should look like:
```
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxx
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

### 7. Create Outputs Folder

```bash
mkdir outputs
```

---

## Usage (2 minutes per project)

### Option A: Web UI (Recommended)

1. **Start the UI:**
   ```bash
   streamlit run app.py
   ```

2. **Browser opens automatically** to `http://localhost:8501`

3. **Follow the steps:**
   - Upload project specification (.txt file)
   - Click "Index Document"
   - Click "Generate Workflow"
   - Click "Execute Workflow"
   - Download your results!

### Option B: Command Line

1. **Edit sample document** in `sophia_prototype.py`:
   ```python
   # Line ~330, replace sample_doc with your project
   sample_doc = """
   Your project specification here...
   """
   ```

2. **Run the script:**
   ```bash
   python sophia_prototype.py
   ```

3. **Results** saved to `./outputs/` folder

---

## Your First Run (End-to-End Example)

### Using the provided sample:

```bash
# 1. Start the UI
streamlit run app.py

# 2. In the browser:
#    - Upload: sample_project.txt
#    - Click: "Index Document" (3 seconds)
#    - Click: "Generate Workflow" (15 seconds)
#    - Click: "Execute Workflow" (2 minutes)

# 3. Check outputs folder:
ls outputs/

# You'll see files like:
# 2025-01-15-create_wbs-rev0.md
# 2025-01-15-task_list-rev0.csv
# 2025-01-15-priorities-rev0.md
# ...
```

**Expected time**: 3-4 minutes total

---

## Troubleshooting

### "OPENROUTER_API_KEY not found"
- Make sure you created `.env` (not `.env.example`)
- Check the API key is valid at openrouter.ai
- Restart the app after editing `.env`

### "Module not found" errors
```bash
# Make sure virtual environment is activated
# Then reinstall:
pip install -r requirements.txt
```

### "Port 8501 already in use"
```bash
# Stop other Streamlit apps or use different port:
streamlit run app.py --server.port 8502
```

### Outputs are empty
- Check your project specification has enough detail
- Try the provided `sample_project.txt` first
- Verify API key has credits at openrouter.ai

---

## What You Get

### Input:
A text file with your project specification (requirements, objectives, constraints)

### Output:
Multiple planning documents:
- **Work Breakdown Structure** (WBS) - markdown
- **Task List with Dependencies** - CSV
- **Priority Matrix** - markdown or CSV
- **Resource Allocation Plan** - CSV
- **Risk Assessment** - markdown
- *(Actual tasks depend on AI's analysis)*

### Technology:
- ✅ Local vector database (no cloud costs)
- ✅ Smart context retrieval (cumulative learning)
- ✅ Real-time progress tracking
- ✅ One-click downloads

---

## File Structure After Setup

```
sophia_prototype/
├── venv/                          # Virtual environment (don't commit)
├── chroma_db/                     # Vector database (auto-created)
├── outputs/                       # Generated files
│   ├── 2025-01-15-wbs-rev0.md
│   ├── 2025-01-15-tasks-rev0.csv
│   └── ...
├── sophia_prototype.py            # Core engine
├── app.py                         # Streamlit UI
├── requirements.txt               # Dependencies
├── .env                           # Your config (gitignore!)
├── .env.example                   # Config template
└── sample_project.txt             # Example input
```

---

## Next Steps

### For Testing:
1. Try `sample_project.txt` first to verify everything works
2. Create your own project specification
3. Experiment with different project types

### For Customization:
1. Adjust chunk size in `sophia_prototype.py` (line ~70)
2. Change retrieval counts (lines ~200, ~300)
3. Modify workflow generation prompt (line ~220)
4. Customize UI colors in `app.py`

### For Production:
*Wait for Stage 3 which adds:*
- Error handling and validation
- Workflow templates
- History and comparison
- Export options (PDF, ZIP)

---

## Common Workflows

### Software Project:
Input: Requirements, tech stack, timeline, team
Output: Sprint planning, task breakdown, milestones

### Marketing Campaign:
Input: Goals, audience, channels, budget
Output: Campaign timeline, content plan, KPIs

### Research Project:
Input: Objectives, methodology, resources
Output: Research phases, task distribution, milestones

### Event Planning:
Input: Event details, budget, venue, attendees
Output: Timeline, task checklist, vendor list

---

## Performance Tips

### Faster Execution:
- Use Claude Sonnet (faster) instead of Opus
- Keep project specs concise (under 10,000 words)
- Close other AI applications

### Better Results:
- Include specific requirements and constraints
- Mention team size, timeline, budget
- Be clear about deliverables and success criteria

### Cost Optimization:
- OpenRouter charges per token
- Shorter specs = lower costs
- Typical project costs: $0.10-0.50

---

## Support

### Get Help:
- Check `SETUP_GUIDE.md` for detailed documentation
- Read `STAGE2_USAGE.md` for UI walkthroughs
- Review the code comments in both Python files

### Extend the System:
- Add custom task types in workflow generation
- Create project templates for common use cases
- Integrate with other tools via API

### Report Issues:
- Check API key is valid and has credits
- Verify all dependencies are installed
- Test with `sample_project.txt` first

---

## Credits

Built with:
- **ChromaDB** - Local vector database
- **OpenRouter** - AI model access
- **Streamlit** - Web framework
- **Python 3.11** - Core language

---

**You're ready to go!** 🎉

Run `streamlit run app.py` and start planning your first project!

---

*Sophia Prototype v1.0*  
*Stages Completed: 1 (Core Engine) ✓ | 2 (UI) ✓ | 3 (Polish) - Coming Next*
