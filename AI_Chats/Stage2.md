# Stage 2: Streamlit UI - Usage Guide

## 🎉 What's New in Stage 2

Stage 2 wraps the powerful Stage 1 core engine with an intuitive, beautiful web interface. No more editing Python files - just upload, click, and download!

### Key Features

✨ **Progressive Workflow UI**
- Step-by-step guided process
- Clear visual feedback at each stage
- Status tracking in sidebar

🎯 **Real-Time Execution**
- Live progress indicators
- Expandable task results
- Instant file previews

📥 **Easy Downloads**
- One-click download buttons
- All outputs accessible immediately
- Clean file organization

🔄 **Session Management**
- State persistence during workflow
- Easy reset to start fresh
- No data loss during execution

---

## Quick Start

### 1. Install Dependencies (if not done for Stage 1)

```bash
pip install -r requirements.txt
```

### 2. Launch the UI

```bash
streamlit run app.py
```

This will:
- Start a local web server
- Open your browser automatically to `http://localhost:8501`
- Display the Sophia interface

---

## Using the Interface

### Step-by-Step Workflow

#### **Step 1: Upload Project Specification** 📤

1. Click **"Browse files"** or drag-and-drop a `.txt` file
2. Preview your document content in the expandable section
3. View file statistics (size, word count, lines)

**Example file format:**
```text
Project: Mobile App Development

Objective: Create a fitness tracking app

Requirements:
- User registration and profiles
- Activity tracking (steps, calories)
- Social features (friends, challenges)
- Integration with wearable devices

Timeline: 4 months
Budget: $80,000
Team: 3 developers, 1 designer
```

#### **Step 2: Index Document** 🔍

1. Click **"🚀 Index Document"** button
2. Watch the status indicator as your document is:
   - Split into 800-character chunks
   - Embedded as vectors
   - Stored in ChromaDB
3. See confirmation: "✅ Indexed X chunks"

*This usually takes 2-5 seconds*

#### **Step 3: Generate Workflow** 🗺️

1. Click **"✨ Generate Workflow"** button
2. AI analyzes your project specification
3. Creates a structured workflow with tasks like:
   - Work Breakdown Structure (WBS)
   - Task lists with dependencies
   - Resource allocation
   - Priority matrices
4. View the generated workflow with expandable task details

*This usually takes 10-20 seconds*

#### **Step 4: Execute Workflow** ⚡

1. Click **"🚀 Execute Workflow"** button
2. Watch real-time progress:
   - Progress bar shows overall completion
   - Each task expands as it executes
   - Preview results immediately after each task
3. Tasks execute sequentially with cumulative context

*This takes 15-30 seconds per task*

#### **Step 5: Download Results** 📥

1. Scroll to the **"Download Results"** section
2. Click any download button to save files locally
3. Files are organized with date-stamped names:
   - `2025-01-15-create_wbs-rev0.md`
   - `2025-01-15-task_list-rev0.csv`

---

## Interface Features

### Sidebar Status Panel 📊

The sidebar shows your progress through the workflow:
- ✓ Green checkmarks = completed steps
- ○ Grey circles = pending steps
- Live metrics (task count, output files)

### Expandable Sections

Click any section header to expand/collapse:
- **Document Preview**: See uploaded file content
- **Task Details**: View full prompts and parameters
- **Task Results**: Preview output before downloading
- **Raw JSON**: Inspect workflow structure

### Status Indicators

Watch for these visual cues:
- 🔵 **Blue "info" boxes**: Instructions and guidance
- 🟢 **Green "success" boxes**: Completed actions
- 🟡 **Yellow "warning" boxes**: Attention needed
- 🔴 **Red "error" boxes**: Something went wrong
- 🔄 **Spinners**: Processing in progress
- 🎈 **Balloons**: Major milestone achieved!

---

## Example Workflow Run

Here's what a typical session looks like:

```
1. Upload "ecommerce_project.txt" (5 KB)
   ✅ Indexed 8 chunks

2. Generate Workflow
   ✅ Created "E-Commerce Platform Planning"
   📝 5 tasks generated

3. Execute Workflow
   [Task 1/5] Creating WBS... ✅ (18 seconds)
   [Task 2/5] Generating task list... ✅ (22 seconds)
   [Task 3/5] Prioritizing tasks... ✅ (15 seconds)
   [Task 4/5] Resource allocation... ✅ (19 seconds)
   [Task 5/5] Risk assessment... ✅ (17 seconds)

4. Download Results
   📄 2025-01-15-wbs-rev0.md
   📄 2025-01-15-task_list-rev0.csv
   📄 2025-01-15-priorities-rev0.md
   📄 2025-01-15-resources-rev0.csv
   📄 2025-01-15-risks-rev0.md

Total time: ~2 minutes
```

---

## Tips & Tricks

### 💡 Best Practices

**For Better Results:**
- Write detailed project specs (more context = better output)
- Include specific requirements, constraints, and goals
- Mention team size, timeline, and budget if relevant

**File Organization:**
- Outputs are saved to `./outputs/` folder
- Files include date stamps for version tracking
- Use the naming pattern to organize multiple runs

**Performance:**
- First run takes longer (model initialization)
- Subsequent runs are faster (cached models)
- Close other AI apps to free up resources

### 🔄 Starting Fresh

To run a new project:
1. Scroll to bottom and click **"🔄 Start New Workflow"**
2. Upload your new project specification
3. Repeat the workflow

*Note: Previous outputs remain in `./outputs/` folder*

### 🐛 Troubleshooting

**"Initialization failed" error:**
- Check that `.env` file exists
- Verify `OPENROUTER_API_KEY` is set
- Ensure API key is valid at openrouter.ai

**"Connection error" during execution:**
- Check internet connection
- Verify OpenRouter service status
- Try again (temporary API issues)

**Tasks producing empty results:**
- Check the task prompt in expanded view
- Ensure your project spec has enough detail
- Try with a more comprehensive specification

**UI not updating:**
- Click "Always rerun" if prompted
- Refresh browser page (Ctrl+R / Cmd+R)
- Restart Streamlit server

---

## Advanced Usage

### Customizing the Experience

**Change AI Model:**
Edit `.env` file:
```
OPENROUTER_MODEL=openai/gpt-4-turbo
```

**Adjust Chunk Parameters:**
Edit `sophia_prototype.py`:
```python
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 250):
```

**Modify Retrieval Count:**
Edit `execute_task()` in `sophia_prototype.py`:
```python
context_chunks = query_vector_store(
    collection,
    query=task_prompt,
    top_k=8  # Increase for more context
)
```

### Running on a Server

Deploy to cloud:
```bash
# Using Streamlit Cloud (free)
1. Push code to GitHub
2. Go to share.streamlit.io
3. Connect repository
4. Add secrets (API key) in dashboard

# Using Docker
docker build -t sophia .
docker run -p 8501:8501 sophia
```

---

## Performance Benchmarks

### Typical Execution Times

| Operation | Time | Notes |
|-----------|------|-------|
| UI Load | 1-2s | First page load |
| System Init | 2-3s | ChromaDB connection |
| Document Index | 2-5s | Depends on file size |
| Workflow Gen | 10-20s | AI processing time |
| Task Execution | 15-30s | Per task, varies by complexity |
| File Download | Instant | Local file access |

### Resource Usage

- **Memory**: ~500 MB (ChromaDB + Streamlit)
- **Disk**: ~50 MB (vector database)
- **Network**: Minimal (only AI API calls)

---

## What's Next?

**Stage 3** (Coming with final Extended Thinking session):
- Enhanced error handling
- Workflow validation
- Pre-built project templates
- Export options (PDF, ZIP)
- Advanced progress indicators
- Workflow history and comparison

---

## Keyboard Shortcuts

- `R` - Refresh UI
- `Ctrl+K` - Clear cache (dev mode)
- `Ctrl+C` (terminal) - Stop server

---

## Feedback & Iteration

The prototype is designed for rapid testing. Feel free to:
- Modify prompts in the workflow generation section
- Adjust UI layout in `app.py`
- Add custom task types
- Experiment with different models

---

**Status**: Stage 2 Complete ✓  
**Interface**: Streamlit Web UI @ http://localhost:8501  
**Next**: Stage 3 (Final polish) with Extended Thinking
