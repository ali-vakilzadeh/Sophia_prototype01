# Sophia Prototype - Setup & Usage Guide

## Stage 1: Core Engine (Complete ✓)

### Prerequisites
- Python 3.11+ installed
- OpenRouter API key ([Get one here](https://openrouter.ai/keys))

### Installation Steps

1. **Create project directory**
   ```bash
   mkdir sophia_prototype
   cd sophia_prototype
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Activate (Windows)
   venv\Scripts\activate
   
   # Activate (Mac/Linux)
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy example config
   cp .env.example .env
   
   # Edit .env and add your OpenRouter API key
   # OPENROUTER_API_KEY=your_actual_key_here
   ```

5. **Create outputs folder**
   ```bash
   mkdir outputs
   ```

### Project Structure
```
sophia_prototype/
├── sophia_prototype.py    # Core engine (Stage 1)
├── app.py                 # Streamlit UI (Stage 2 - coming next)
├── requirements.txt       # Python dependencies
├── .env.example          # Configuration template
├── .env                  # Your actual config (gitignore this!)
├── chroma_db/            # Vector store data (auto-created)
└── outputs/              # Generated workflow outputs
```

### Testing Stage 1

Run the example workflow:
```bash
python sophia_prototype.py
```

**Expected output:**
```
[1/5] Loading configuration...
✓ Using model: anthropic/claude-3.5-sonnet

[2/5] Initializing vector store...
✓ ChromaDB ready

[3/5] Indexing project specification...
✓ Indexed 2 chunks

[4/5] Generating workflow from project spec...
✓ Generated workflow: Project Planning Workflow
  Tasks: 4

[5/5] Executing workflow tasks...

[Task 1] Executing: create_wbs...
[Task 1] ✓ Complete. Saved to: outputs/2025-01-15-create_wbs-rev0.md

[Task 2] Executing: create_task_list...
[Task 2] ✓ Complete. Saved to: outputs/2025-01-15-create_task_list-rev0.csv

...

✓ All tasks complete!
  Output files: 4
```

### Using Your Own Project Specification

Edit `sophia_prototype.py` and replace the `sample_doc` variable in the `main()` function with your project specification text.

Or, wait for Stage 2 (Streamlit UI) to upload files via web interface!

---

## Key Features Implemented (Stage 1)

### ✓ Context Retrieval Strategy
- **Chunk size**: 800 characters (optimal semantic coherence)
- **Overlap**: 200 characters (preserves context at boundaries)
- **Workflow generation**: Top 10 chunks (comprehensive understanding)
- **Task execution**: Top 5 chunks + all previous outputs
- **Token management**: Auto-truncation at ~20,000 characters

### ✓ Vector Store
- **Engine**: ChromaDB (local, zero cost, persistent)
- **Storage**: `./chroma_db/` directory
- **Indexing**: Automatic chunking and embedding

### ✓ AI Integration
- **Provider**: OpenRouter API
- **JSON mode**: Structured workflow generation
- **Context assembly**: Smart ordering (relevant chunks → previous outputs)

### ✓ Workflow Execution
- **Sequential processing**: Tasks run in order
- **Cumulative learning**: Each task sees all previous outputs
- **Auto-saving**: Outputs saved with date-stamped filenames

---

## Context Strategy Deep Dive

### Why This Approach?

1. **800-char chunks with 200 overlap**
   - Preserves semantic meaning across boundaries
   - Prevents mid-sentence/mid-concept cuts
   - Optimal for embedding models

2. **Top 10 for workflow, Top 5 for tasks**
   - Workflow needs "big picture" understanding
   - Individual tasks need focused context
   - Balances comprehensiveness vs. noise

3. **Include all previous outputs**
   - Tasks build on each other (WBS → Task List → Priorities)
   - Maintains consistency across outputs
   - Simulates "working memory"

4. **Token limit safety**
   - Monitors total context size
   - Truncates at 20,000 chars (~5,000 tokens)
   - Leaves room for AI response generation

### Example Context Flow

**Task 1 (WBS creation):**
```
Context:
- Top 5 chunks from project spec
- Previous outputs: (none)
Total: ~4,000 chars
```

**Task 2 (Task list):**
```
Context:
- Top 5 chunks from project spec
- Previous outputs: [WBS output]
Total: ~8,000 chars
```

**Task 3 (Priorities):**
```
Context:
- Top 5 chunks from project spec
- Previous outputs: [WBS output, Task list output]
Total: ~12,000 chars
```

Each task has progressively more context but stays under token limits.

---

## Troubleshooting

### "OPENROUTER_API_KEY not found"
- Make sure `.env` file exists (not `.env.example`)
- Check that API key is correctly set in `.env`
- Verify no spaces around the `=` sign

### "ChromaDB initialization error"
- Delete `chroma_db/` folder and retry
- Check write permissions in project directory

### "API request failed"
- Verify API key is valid at openrouter.ai
- Check internet connection
- Ensure model name is correct in `.env`

### Output files are empty
- Check API response in console
- Verify model supports JSON mode (Claude/GPT-4 recommended)
- Try with a more detailed project specification

---

## Next Steps

**Stage 2** (Coming next with Extended Thinking):
- Streamlit UI for file upload
- Real-time workflow visualization
- Progress tracking
- Download buttons for outputs

**Stage 3** (Final polish with Extended Thinking):
- Error handling refinements
- Workflow JSON validation
- Progress indicators
- Example project templates

---

## Performance Notes

- **Cold start**: ~10-15 seconds (vector store initialization)
- **Document indexing**: ~2-3 seconds per 10,000 chars
- **Workflow generation**: ~10-20 seconds (depends on model)
- **Per-task execution**: ~15-30 seconds (includes context retrieval + AI call)
- **Total for 5-task workflow**: ~2-3 minutes

---

## Contributing

This is a prototype! Feel free to:
- Modify chunk sizes in `chunk_text()`
- Adjust retrieval counts in `generate_workflow()` and `execute_task()`
- Change the workflow generation prompt
- Add new output formats

---

**Status**: Stage 1 Complete ✓  
**Next**: Stage 2 (Streamlit UI) with Extended Thinking
