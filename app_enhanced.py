"""
Sophia Prototype - Enhanced Streamlit UI (Stage 3)
==================================================
Production-ready interface with templates, validation, and history.

New Features:
- Template selection and suggestions
- Comprehensive error handling with user-friendly messages
- Workflow history browser
- Input validation with helpful feedback
- Progress persistence
- Export options
- Enhanced status tracking

Usage:
    streamlit run app_enhanced.py
"""

import streamlit as st
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# Import enhanced core functions
from sophia_enhanced import (
    load_env_config,
    initialize_vector_store,
    validate_text_input,
    index_document,
    generate_workflow_from_ai,
    generate_workflow_from_ai_with_goal,
    generate_workflow_from_template,
    execute_task_safe,
    save_output,
    save_workflow_history,
    list_workflow_history,
    ConfigurationError,
    VectorStoreError,
    AIError
)

# Import template functions
from templates import list_templates, suggest_template


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Sophia - AI Project Planner",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# SESSION STATE
# ============================================================================

def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        'config': None,
        'collection': None,
        'user_api_key': '',
        'user_model': '',
        'api_configured': False,
        'document_indexed': False,
        'doc_name': None,
        'doc_content': None,
        'workflow': None,
        'workflow_executed': False,
        'output_files': [],
        'execution_errors': [],
        'template_mode': False,
        'selected_template': None,
        'suggested_template': None,
        'ai_generation_in_progress': False,
        'ai_generation_status': '',
        'workflow_target': '',
        'generation_complete': False,
        'indexed_files': [],  # List of dicts: [{name, chunks, timestamp}, ...]
        'total_chunks_indexed': 0,
        'pending_files': [],  # Files uploaded but not yet indexed
        'failed_tasks': [],  # List of dicts: [{task_index, task, error}, ...]
        'task_outputs': {}  #dict: {taksk_index, output_content}
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================================
# SYSTEM INITIALIZATION
# ============================================================================

def initialize_system():
    """Initialize with user-provided or .env configuration."""
    try:
        with st.spinner("Initializing Sophia..."):
            # Try loading from .env first (for defaults)
            try:
                env_config = load_env_config()
                if not st.session_state.user_api_key:
                    st.session_state.user_api_key = env_config['api_key']
                if not st.session_state.user_model:
                    st.session_state.user_model = env_config['model']
            except ConfigurationError:
                # .env not found or invalid - that's okay, user will input
                pass
            
            # Use user-provided values if available
            if st.session_state.user_api_key and st.session_state.user_model:
                st.session_state.config = {
                    'api_key': st.session_state.user_api_key,
                    'model': st.session_state.user_model,
                    'max_retries': 3,
                    'timeout': 60,
                    'chunk_size': 800,
                    'chunk_overlap': 200
                }
                st.session_state.api_configured = True
            
            if st.session_state.collection is None:
                st.session_state.collection = initialize_vector_store()
        
        return True, None
        
    except VectorStoreError as e:
        error_msg = f"""
        ❌ **Vector Store Error**
        
        {str(e)}
        
        **How to fix:**
        1. Delete the `chroma_db` folder if it exists
        2. Check you have write permissions in this directory
        3. Restart the app
        """
        return False, error_msg
        
    except Exception as e:
        error_msg = f"""
        ❌ **Unexpected Error**
        
        {str(e)}
        
        **How to fix:**
        1. Check all dependencies are installed: `pip install -r requirements.txt`
        2. Verify Python version is 3.11 or higher
        3. Restart the app
        """
        return False, error_msg


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_header():
    """Render application header with version info."""
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        st.title("🤖 Sophia - AI Project Assistant")
        st.markdown("*Non-autonomous prototype: Use AI to design workflows and execute them + self-retrain!*")
    
    with col2:
        if st.session_state.config:
            model_name = st.session_state.config['model'].split('/')[-1]
            st.info(f"🧠 {model_name}")
    
    with col3:
        st.info("📦 v1.0 (Stage 3)")

def render_api_configuration():
    """Render API configuration section."""
    st.header("🔑 Configure AI Model")
    
    if st.session_state.api_configured:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.success(f"Model: {st.session_state.user_model}")
        with col2:
            api_key_masked = st.session_state.user_api_key[:8] + "..." + st.session_state.user_api_key[-4:]
            st.success(f"API Key: {api_key_masked}")
        with col3:
            if st.button("Change", use_container_width=True):
                st.session_state.api_configured = False
                st.rerun()
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info("Configure your AI model to start. You can use OpenRouter, OpenAI, or compatible APIs.")
        
        with col2:
            with st.expander("Where to get API keys", expanded=False):
                st.markdown("""
                **OpenRouter** (Recommended)
                - Sign up at [openrouter.ai](https://openrouter.ai)
                - Get key at [openrouter.ai/keys](https://openrouter.ai/keys)
                - Access to Claude, GPT-4, and more
                
                **OpenAI**
                - Sign up at [platform.openai.com](https://platform.openai.com)
                - Use model: `gpt-4` or `gpt-3.5-turbo`
                """)
        
        # Input fields
        col1, col2 = st.columns(2)
        
        with col1:
            api_key_input = st.text_input(
                "API Key",
                value=st.session_state.user_api_key,
                type="password",
                placeholder="sk-or-v1-... or sk-...",
                help="Your OpenRouter or OpenAI API key"
            )
        
        with col2:
            model_input = st.text_input(
                "Model Name",
                value=st.session_state.user_model,
                placeholder="anthropic/claude-3.5-sonnet or gpt-4",
                help="Full model identifier (e.g., anthropic/claude-3.5-sonnet for OpenRouter)"
            )
        
        # Validate and save
        if api_key_input and model_input:
            if len(api_key_input) < 10:
                st.warning("API key seems too short")
            elif not model_input.strip():
                st.warning("Please enter a model name")
            else:
                if st.button("Save Configuration", type="primary", use_container_width=True):
                    st.session_state.user_api_key = api_key_input
                    st.session_state.user_model = model_input
                    st.session_state.config = {
                        'api_key': api_key_input,
                        'model': model_input,
                        'max_retries': 3,
                        'timeout': 60,
                        'chunk_size': 800,
                        'chunk_overlap': 200
                    }
                    st.session_state.api_configured = True
                    st.success("✅ Configuration saved!")
                    st.rerun()
        else:
            st.warning("Please provide both API key and model name to continue")

def render_sidebar():
    """Enhanced sidebar with history and templates."""
    with st.sidebar.expander("Debug Info", expanded=False):
        st.write("Pending files:", len(st.session_state.pending_files))
        st.write("Indexed files:", len(st.session_state.indexed_files))
        st.write("AI in progress:", st.session_state.ai_generation_in_progress)
        st.write("Generation complete:", st.session_state.generation_complete)
        st.write("Workflow exists:", st.session_state.workflow is not None)
        st.sidebar.header("Progress")
    
    # Progress tracking
    steps = [
        ("📄 Files Uploaded", len(st.session_state.indexed_files) > 0),
        ("🔍 Files Indexed", st.session_state.document_indexed),
        ("🗺️ Workflow Generated", st.session_state.workflow is not None),
        ("✅ Workflow Executed", st.session_state.workflow_executed)
    ]

    for step_name, completed in steps:
        if completed:
            st.sidebar.success(f"✓ {step_name}")
        else:
            st.sidebar.info(f"○ {step_name}")
    
    # Stats
    if st.session_state.indexed_files:
        st.sidebar.divider()
        st.sidebar.metric("Files Indexed", len(st.session_state.indexed_files))
        st.sidebar.metric("Total Chunks", st.session_state.total_chunks_indexed)
    
    if st.session_state.workflow:
        st.sidebar.metric("Workflow Tasks", len(st.session_state.workflow['tasks']))
    
    if st.session_state.output_files:
        st.sidebar.metric("Output Files", len(st.session_state.output_files))
    
    if st.session_state.execution_errors:
        st.sidebar.metric("Errors", len(st.session_state.execution_errors))
    
    # Indexed Files List
    if st.session_state.indexed_files:
        st.sidebar.divider()
        st.sidebar.header("📚 Indexed Files")
        
        for idx, file_info in enumerate(st.session_state.indexed_files, 1):
            with st.sidebar.expander(f"📄 {file_info['name']}", expanded=False):
                st.caption(f"🧩 Chunks: {file_info['chunks']}")
                st.caption(f"⏰ Indexed: {file_info['timestamp']}")
    
    # Workflow History
    if 'SPACE_ID' not in os.environ:
        st.sidebar.divider()
        st.sidebar.header("📚 History")
        
        history = list_workflow_history()
        if history:
            st.sidebar.caption(f"Found {len(history)} previous workflows")
            
            with st.sidebar.expander("View History", expanded=False):
                for item in history[:5]:
                    st.caption(f"**{item['workflow_name']}**")
                    st.caption(f"⏰ {item['timestamp']}")
                    st.caption(f"📝 {item['num_tasks']} tasks")
                    st.divider()
        else:
            st.sidebar.caption("No history yet")
    else:
        st.sidebar.divider()
        st.sidebar.info("💡 History disabled on Spaces")


def render_file_upload():
    """Enhanced file upload with multi-file support."""
    st.header("📤 Step 1: Upload Project Documents")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Upload project specification files (.txt, .md)",
            type=['txt', 'md'],  # CHANGED: Added 'md'
            help="Upload one or multiple text or markdown files with your project requirements",
            accept_multiple_files=True,  # ENABLE MULTI-FILE
            key="file_uploader"
        )
    
    with col2:
        st.info("""
        **What to include:**
        - Project objectives
        - Requirements
        - Constraints
        - Timeline & budget
        - Team structure
        
        **Accepted formats:**
        - Plain text (.txt)
        - Markdown (.md)
        
        **Multi-file support:**
        Upload multiple documents!
        """)
    
    # Show currently indexed files
    if st.session_state.indexed_files:
        st.success(f"✅ **{len(st.session_state.indexed_files)} file(s) indexed** | "
                   f"**{st.session_state.total_chunks_indexed} total chunks**")
        
        with st.expander("📚 View Indexed Files", expanded=True):
            for idx, file_info in enumerate(st.session_state.indexed_files, 1):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.text(f"{idx}. {file_info['name']}")
                with col2:
                    st.caption(f"🧩 {file_info['chunks']} chunks")
                with col3:
                    st.caption(f"⏰ {file_info['timestamp']}")
    
    # Process uploaded files
    if uploaded_files:
        # Check for new files not yet indexed
        existing_names = {f['name'] for f in st.session_state.indexed_files}
        new_files = [f for f in uploaded_files if f.name not in existing_names]
        
        if new_files:
            # Clear pending files before rebuilding (prevent duplicates)
            st.session_state.pending_files = []
            st.divider()
            st.info(f"📥 **{len(new_files)} new file(s) ready to index**")
            
            # Show preview of new files
            for uploaded_file in new_files:
                with st.expander(f"📄 Preview: {uploaded_file.name}", expanded=False):
                    content = uploaded_file.read().decode('utf-8')
                    
                    # Validate
                    is_valid, error_msg = validate_text_input(content)
                    
                    if not is_valid:
                        st.error(f"❌ Invalid file: {error_msg}")
                        continue
                    
                    # Show stats
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Characters", f"{len(content):,}")
                    with col2:
                        st.metric("Words", f"{len(content.split()):,}")
                    with col3:
                        st.metric("Lines", f"{len(content.split(chr(10))):,}")
                    with col4:
                        estimated_chunks = max(1, len(content) // 600)
                        st.metric("Est. Chunks", estimated_chunks)
                    
                    # Preview text
                    st.text_area(
                        "Content Preview",
                        content[:500] + ("..." if len(content) > 500 else ""),
                        height=150,
                        disabled=True,
                        label_visibility="collapsed"
                    )
                    
                    # Store for indexing (check if not already in pending)
                    if not any(f['name'] == uploaded_file.name for f in st.session_state.pending_files):
                        st.session_state.pending_files.append({
                            'name': uploaded_file.name,
                            'content': content
                        })
            
            return True  # Signal that new files are ready
        else:
            st.info("ℹ️ All uploaded files are already indexed")
            return False
    
    return False


def render_indexing_section():
    """Enhanced indexing with multi-file batch processing."""
    st.header("🔍 Step 2: Index Documents")
    
    if not st.session_state.pending_files:
        st.warning("⚠️ No new files to index. Upload files first!")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(f"📚 Ready to index **{len(st.session_state.pending_files)} file(s)**")
    
    with col2:
        # Show suggested template based on first file
        if not st.session_state.suggested_template and st.session_state.pending_files:
            first_content = st.session_state.pending_files[0]['content']
            st.session_state.suggested_template = suggest_template(first_content)
        
        templates = {tid: t for tid, t in ((t['id'], t) for t in list_templates())}
        suggested = templates.get(st.session_state.suggested_template, {})
        
        if suggested:
            st.success(f"💡 Suggested: **{suggested['name']}**")
    
    if st.button("🚀 Index All Files", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_files = len(st.session_state.pending_files)
        total_chunks = 0
        
        for idx, file_data in enumerate(st.session_state.pending_files, 1):
            try:
                # Update progress
                progress = (idx - 1) / total_files
                progress_bar.progress(progress)
                status_text.text(f"📄 Indexing {idx}/{total_files}: {file_data['name']}...")
                
                # Index the file
                result = index_document(
                    st.session_state.collection,
                    file_data['content'],
                    file_data['name'],
                    st.session_state.config
                )
                
                # Store indexed file info
                st.session_state.indexed_files.append({
                    'name': file_data['name'],
                    'chunks': result['chunks_indexed'],
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                
                total_chunks += result['chunks_indexed']
                
                status_text.success(f"✅ {file_data['name']}: {result['chunks_indexed']} chunks")
                
            except VectorStoreError as e:
                status_text.error(f"❌ {file_data['name']}: Vector store error - {str(e)}")
                st.info("💡 Try deleting the `chroma_db` folder and restarting")
                
            except ValueError as e:
                status_text.error(f"❌ {file_data['name']}: Validation error - {str(e)}")
                
            except Exception as e:
                status_text.error(f"❌ {file_data['name']}: {str(e)}")
        
        # Final progress
        progress_bar.progress(1.0)
        
        # Update state
        st.session_state.total_chunks_indexed = sum(f['chunks'] for f in st.session_state.indexed_files)
        st.session_state.document_indexed = True
        st.session_state.pending_files = []  # Clear pending files
        
        # Success message
        #st.balloons()
        st.success(f"🎉 **Indexed {len(st.session_state.indexed_files)} file(s) successfully!** "
                   f"Total: {st.session_state.total_chunks_indexed} chunks")


def render_template_or_ai_choice():
    """Let user choose between template and AI workflow generation."""
    st.header("🗺️ Step 3: Generate Workflow")
    
    st.info("Choose how to generate your workflow:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Use Template")
        st.caption("Faster, structured, consistent results")
        
        templates = list_templates()
        template_options = {t['name']: t['id'] for t in templates}
        
        # Highlight suggested template
        default_idx = 0
        if st.session_state.suggested_template:
            suggested_name = next((t['name'] for t in templates 
                                 if t['id'] == st.session_state.suggested_template), None)
            if suggested_name and suggested_name in template_options:
                default_idx = list(template_options.keys()).index(suggested_name)
        
        selected_template_name = st.selectbox(
            "Select template",
            options=list(template_options.keys()),
            index=default_idx,
            disabled=st.session_state.ai_generation_in_progress  # Disable during AI generation
        )
        
        selected_template_id = template_options[selected_template_name]
        
        # Show template details
        template_info = next(t for t in templates if t['id'] == selected_template_id)
        st.caption(f"📝 {template_info['description']}")
        st.caption(f"✅ {template_info['num_tasks']} predefined tasks")
        
        if st.button(
            "📋 Use This Template", 
            use_container_width=True,
            disabled=st.session_state.ai_generation_in_progress  # Disable during AI generation
        ):
            st.session_state.template_mode = True
            st.session_state.selected_template = selected_template_id
            st.rerun()
    
    with col2:
        st.subheader("🤖 AI Generated")
        st.caption("Custom, adaptive, project-specific")
        
        # ADD: User input for workflow target
        st.markdown("**What should the workflow achieve?**")
        workflow_target = st.text_area(
            "Workflow Goal",
            placeholder="Example: Create a comprehensive project plan for launching a mobile app, including timeline, resources, and risk management",
            height=100,
            key="workflow_target_input",
            disabled=st.session_state.ai_generation_in_progress,
            label_visibility="collapsed"
        )
        
        st.caption("💡 Be specific about deliverables you need")
        
        # Button with validation
        button_disabled = (
            not workflow_target or 
            len(workflow_target.strip()) < 20 or 
            st.session_state.ai_generation_in_progress
        )
        
        if st.button(
            "✨ Generate with AI", 
            type="primary", 
            use_container_width=True,
            disabled=button_disabled
            ):
            
            if len(workflow_target.strip()) < 20:
                st.error("❌ Please provide a more detailed workflow goal (minimum 20 characters)")
            else:
                # Store the target and trigger generation
                
                st.session_state.workflow_target = workflow_target
                st.session_state.template_mode = False
                st.session_state.ai_generation_in_progress = True
                st.session_state.generation_complete = False
                # st.rerun()
        
        # Show character count hint
        if workflow_target:
            char_count = len(workflow_target.strip())
            if char_count < 20:
                st.caption(f"⚠️ {char_count}/20 characters (minimum)")
            else:
                st.caption(f"✅ {char_count} characters")
        
        # Help text
        with st.expander("💡 Tips for Better AI Workflows", expanded=False):
            st.markdown("""
            **Good workflow goals:**
            - ✅ "Create a comprehensive launch plan with timeline, marketing strategy, and risk assessment"
            - ✅ "Generate technical documentation including architecture, API specs, and deployment guide"
            - ✅ "Develop a research methodology with literature review, data collection plan, and analysis framework"
            
            **Too vague:**
            - ❌ "Make a plan"
            - ❌ "Do the project"
            
            **Pro tip:** Mention specific deliverables you need (WBS, timeline, budget, etc.)
            """)

def render_workflow_generation_ai():
    """Generate workflow using AI with detailed progress indicators."""
    st.header("✨ Generating AI Workflow")
    
    # Show workflow goal
    st.info(f"🎯 **Goal:** {st.session_state.workflow_target}")
    
    # Progress indicator
    progress_bar = st.progress(0)
    status_container = st.empty()
    
    # Status messages
    statuses = [
        ("🔍 Analyzing project specification...", 0.2),
        ("🧠 Sending AI request...", 0.3),
        ("⏳ Awaiting AI response...", 0.5),
        ("📥 Response received...", 0.7),
        ("🔧 Parsing workflow JSON...", 0.85),
        ("✅ Workflow generated...", 0.95),
        ("🎉 Workflow ready!", 1.0)
    ]
    
    try:
        import time
        
        for idx, (status_text, progress_value) in enumerate(statuses):
            status_container.info(status_text)
            progress_bar.progress(progress_value)
            
            # Actual AI generation happens at "Sending AI request"
            if idx == 1:  # Index 1 is "Sending AI request"
                # Call the actual AI generation with the workflow target
                workflow = generate_workflow_from_ai_with_goal(
                    st.session_state.collection,
                    st.session_state.config['api_key'],
                    st.session_state.config['model'],
                    st.session_state.config,
                    st.session_state.workflow_target
                )
                st.session_state.workflow = workflow
            
            # Small delay for UX (let users see each step)
            time.sleep(0.3)
        
        # Success
        progress_bar.progress(1.0)
        status_container.success(f"🎉 Created: **{st.session_state.workflow['workflow_name']}**")
        
        # Update state - IMPORTANT: Set these BEFORE showing success
        st.session_state.ai_generation_in_progress = False
        st.session_state.generation_complete = True
        
        # Show success message
        #st.balloons()
        st.success(f"✅ Generated {len(st.session_state.workflow['tasks'])} custom tasks!")
        
        # Force rerun to show workflow
        time.sleep(1)
        st.rerun()
        
    except AIError as e:
        progress_bar.empty()
        status_container.error("❌ AI generation failed")
        st.error(f"**AI Error:** {str(e)}")
        st.info("💡 **How to fix:**\n- Check your API key and internet connection\n- Try again (AI can be temporarily unavailable)\n- Or use a template instead")
        
        # Reset state
        st.session_state.ai_generation_in_progress = False
        st.session_state.generation_complete = False
        
    except ValueError as e:
        progress_bar.empty()
        status_container.error("❌ Invalid workflow")
        st.error(f"**Validation Error:** {str(e)}")
        st.info("💡 **How to fix:**\n- The AI generated invalid JSON\n- Try again with a clearer goal\n- Or use a template instead")
        
        # Reset state
        st.session_state.ai_generation_in_progress = False
        st.session_state.generation_complete = False
        
    except Exception as e:
        progress_bar.empty()
        status_container.error("❌ Unexpected error")
        st.error(f"**Error:** {str(e)}")
        
        # Reset state
        st.session_state.ai_generation_in_progress = False
        st.session_state.generation_complete = False


def render_workflow_generation_template():
    """Generate workflow from template."""
    st.header("📋 Applying Template")
    
    with st.status("Applying template...", expanded=True) as status:
        try:
            st.write("📋 Loading template...")
            st.write("🔧 Enhancing with project context...")
            
            workflow = generate_workflow_from_template(
                st.session_state.selected_template,
                st.session_state.collection
            )
            
            st.write(f"✅ Prepared {len(workflow['tasks'])} tasks")
            
            st.session_state.workflow = workflow
            
            status.update(label="✅ Template applied!", state="complete")
            st.success(f"🎉 Ready: **{workflow['workflow_name']}**")
            # Force rerun to show workflow
            import time
            time.sleep(0.5)
            st.rerun()
        except ValueError as e:
            status.update(label="❌ Template error", state="error")
            st.error(f"Error: {str(e)}")
            
        except Exception as e:
            status.update(label="❌ Unexpected error", state="error")
            st.error(f"Error: {str(e)}")


def render_workflow_display():
    """Display workflow with enhanced visualization."""
    if st.session_state.workflow:
        st.header("📋 Workflow Details")
        
        workflow = st.session_state.workflow
        
        # Workflow summary
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader(workflow['workflow_name'])
        with col2:
            st.metric("Total Tasks", len(workflow['tasks']))
        with col3:
            source = "Template" if st.session_state.template_mode else "AI Generated"
            st.info(f"📦 {source}")
        
        # Task list
        st.markdown("### 📝 Task Breakdown:")
        
        for i, task in enumerate(workflow['tasks'], 1):
            with st.expander(f"Task {i}: {task['name']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**ID:** `{task['task_id']}`")
                    st.markdown(f"**Output:** {task['output_format']}")
                
                with col2:
                    # Estimate complexity
                    prompt_length = len(task['prompt'])
                    if prompt_length < 200:
                        complexity = "🟢 Simple"
                    elif prompt_length < 500:
                        complexity = "🟡 Medium"
                    else:
                        complexity = "🔴 Complex"
                    st.info(complexity)
                
                st.markdown("**Instructions:**")
                st.text_area(
                    "prompt",
                    task['prompt'],
                    height=150,
                    key=f"task_{i}_prompt",
                    disabled=True,
                    label_visibility="collapsed"
                )
        
        # Export workflow
        with st.expander("💾 Export Workflow JSON", expanded=False):
            st.download_button(
                "Download Workflow JSON",
                data=json.dumps(workflow, indent=2),
                file_name=f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )


def render_workflow_execution():
    """Execute workflow with enhanced error handling."""
    st.header("⚡ Step 4: Execute Workflow")
    
    workflow = st.session_state.workflow
    estimated_time = len(workflow['tasks']) * 20
    
    st.info(f"🎯 Will execute {len(workflow['tasks'])} tasks | ⏱️ Est. {estimated_time}s")
    
    if st.button("🚀 Execute Workflow", type="primary", use_container_width=True):
        output_files = []
        previous_outputs = []
        errors = []
        st.session_state.failed_tasks = []  # Reset failed tasks
        st.session_state.task_outputs = {}  # Reset task outputs
        
        # Progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_tasks = len(workflow['tasks'])
        
        for i, task in enumerate(workflow['tasks'], 1):
            progress = i / total_tasks
            progress_bar.progress(progress)
            status_text.text(f"Executing {i}/{total_tasks}: {task['name']}...")
            
            with st.expander(f"Task {i}: {task['name']}", expanded=True):
                with st.spinner("Processing..."):
                    # Execute task
                    success, result, error_type = execute_task_safe(
                        task=task,
                        collection=st.session_state.collection,
                        api_key=st.session_state.config['api_key'],
                        model=st.session_state.config['model'],
                        config=st.session_state.config,
                        previous_outputs=previous_outputs
                    )
                    
                    if success:
                        # Save output
                        output_path = save_output(
                            content=result,
                            task_name=task['name'],
                            output_format=task['output_format']
                        )
                        
                        output_files.append(output_path)
                        previous_outputs.append(f"[Task {task['task_id']}]\n{result}")
                        st.session_state.task_outputs[i-1] = result
                        
                        st.success(f"✅ Complete! → `{output_path}`")
                        
                        # Preview
                        preview_len = min(300, len(result))
                        st.text_area(
                            "Preview",
                            result[:preview_len] + ("..." if len(result) > preview_len else ""),
                            height=120,
                            key=f"result_{i}",
                            disabled=True,
                            label_visibility="collapsed"
                        )
                    else:
                        # Handle error
                        st.error(f"❌ Task failed: {result}")
                        errors.append({
                            "task": task['name'],
                            "error": result,
                            "type": error_type
                        })
                        
                        # Store failed task for retry
                        st.session_state.failed_tasks.append({  
                            'task_index': i - 1,
                            'task': task,
                            'error': result,
                            'error_type': error_type,
                            'previous_outputs': previous_outputs.copy()
                        })

                        # Provide recovery options
                        if error_type == "AI_ERROR":
                            st.warning("💡 Try: Check API key, wait a moment, retry")
                        elif error_type == "VECTOR_ERROR":
                            st.warning("💡 Try: Reindex document, restart app")
        
        # Final update
        progress_bar.progress(1.0)
        status_text.text("✅ Workflow execution complete!")
        
        # Update state
        st.session_state.output_files = output_files
        st.session_state.execution_errors = errors
        st.session_state.workflow_executed = True
        
        # Save history
        history_file = save_workflow_history(workflow, output_files)
        
        # Final status
        if not errors:
            #st.balloons()
            st.success(f"🎉 Perfect! Generated {len(output_files)} files")
        else:
            st.warning(f"⚠️ Completed with {len(errors)} errors. {len(output_files)} files generated.")
        
        st.info(f"💾 History saved: `{history_file}`")

# ADD this new function after render_workflow_execution():

def render_retry_failed_tasks():
    """Allow user to retry failed tasks."""
    if st.session_state.failed_tasks:
        st.divider()
        st.header("🔄 Retry Failed Tasks (check you AI API connection before retry)")
        
        st.warning(f"⚠️ {len(st.session_state.failed_tasks)} task(s) failed during execution")
        
        for failed_info in st.session_state.failed_tasks:
            task_idx = failed_info['task_index']
            task = failed_info['task']
            error = failed_info['error']
            error_type = failed_info['error_type']
            
            with st.expander(f"❌ Task {task_idx + 1}: {task['name']}", expanded=True):
                st.error(f"**Error:** {error}")
                
                if error_type == "AI_ERROR":
                    st.info("💡 **Likely cause:** API rate limiting or temporary service issue")
                    st.caption("**Suggestion:** Wait a moment and retry")
                elif error_type == "VECTOR_ERROR":
                    st.info("💡 **Likely cause:** Database access issue")
                    st.caption("**Suggestion:** Try restarting the app")
                else:
                    st.info("💡 **Likely cause:** Unexpected error")
                
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if st.button(f"🔄 Retry Task {task_idx + 1}", 
                               key=f"retry_task_{task_idx}",
                               type="primary",
                               use_container_width=True):
                        
                        with st.spinner(f"Retrying Task {task_idx + 1}..."):
                            # Retry the task
                            success, result, new_error_type = execute_task_safe(
                                task=task,
                                collection=st.session_state.collection,
                                api_key=st.session_state.config['api_key'],
                                model=st.session_state.config['model'],
                                config=st.session_state.config,
                                previous_outputs=failed_info['previous_outputs']
                            )
                            
                            if success:
                                # Save output
                                output_path = save_output(
                                    content=result,
                                    task_name=task['name'],
                                    output_format=task['output_format']
                                )
                                
                                # Update state
                                st.session_state.output_files.append(output_path)
                                st.session_state.task_outputs[task_idx] = result
                                
                                # Remove from failed tasks
                                st.session_state.failed_tasks = [
                                    f for f in st.session_state.failed_tasks 
                                    if f['task_index'] != task_idx
                                ]
                                
                                # Remove from errors
                                st.session_state.execution_errors = [
                                    e for e in st.session_state.execution_errors
                                    if e.get('task') != task['name']
                                ]
                                
                                st.success(f"✅ Task {task_idx + 1} completed successfully!")
                                st.info(f"📁 Saved to: `{output_path}`")
                                
                                import time
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ Retry failed: {result}")
                                st.warning("💡 You can try again after waiting a bit longer")
                
                with col2:
                    st.caption(f"**Original error type:** {error_type}")
                    st.caption("Retrying will use the same context and previous outputs")

def render_outputs_section():
    """Enhanced output download section."""
    if st.session_state.output_files:
        st.header("📥 Download Results")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.success(f"✅ {len(st.session_state.output_files)} files ready")
        
        with col2:
            if st.button("📦 Export All as ZIP", use_container_width=True):
                st.info("💡 ZIP export coming soon!")
        
        # File list
        cols = st.columns(2)
        
        for i, filepath in enumerate(st.session_state.output_files):
            col = cols[i % 2]
            
            with col:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                filename = os.path.basename(filepath)
                file_size = len(content)
                
                # File card
                with st.container():
                    st.markdown(f"**{filename}**")
                    st.caption(f"📊 {file_size:,} chars")
                    
                    st.download_button(
                        label="⬇️ Download",
                        data=content,
                        file_name=filename,
                        mime="text/plain",
                        key=f"download_{i}",
                        use_container_width=True
                    )

# New feature: add generated data to training for next workflow

def render_add_to_training_section():
    """Allow user to add generated outputs to ChromaDB for next workflow."""
    if st.session_state.output_files and st.session_state.workflow_executed:
        st.divider()
        st.header("🔄 Continue with Generated Files")
        
        st.info("""
        💡 **Pro tip:** Add generated files to training to create follow-up workflows 
        based on what you just created!
        
        For example:
        - Generate a project plan, then create implementation details
        - Create WBS, then develop detailed task breakdowns
        - Make requirements doc, then generate test plans
        """)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📚 Add Generated Files to Training & Start New Workflow", 
                        type="primary", 
                        use_container_width=True):
                with st.spinner("Adding generated files to training..."):
                    progress_bar = st.progress(0)
                    total_files = len(st.session_state.output_files)
                    
                    newly_indexed = []
                    
                    for idx, filepath in enumerate(st.session_state.output_files, 1):
                        try:
                            # Read the file
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Get filename
                            filename = os.path.basename(filepath)
                            
                            # Index it
                            result = index_document(
                                st.session_state.collection,
                                content,
                                filename,
                                st.session_state.config
                            )
                            
                            newly_indexed.append({
                                'name': filename,
                                'chunks': result['chunks_indexed'],
                                'timestamp': datetime.now().strftime("%H:%M:%S")
                            })
                            
                            progress_bar.progress(idx / total_files)
                            
                        except Exception as e:
                            st.error(f"❌ Failed to index {filename}: {str(e)}")
                    
                    # Add to indexed files
                    st.session_state.indexed_files.extend(newly_indexed)
                    st.session_state.total_chunks_indexed = sum(
                        f['chunks'] for f in st.session_state.indexed_files
                    )
                    
                    # Reset workflow state but keep files indexed
                    st.session_state.workflow = None
                    st.session_state.workflow_executed = False
                    st.session_state.output_files = []
                    st.session_state.execution_errors = []
                    st.session_state.template_mode = False
                    st.session_state.selected_template = None
                    st.session_state.ai_generation_in_progress = False
                    st.session_state.generation_complete = False
                    
                    progress_bar.progress(1.0)
                    st.success(f"✅ Added {len(newly_indexed)} files to training!")
                    st.balloons()
                    
                    import time
                    time.sleep(1)
                    st.rerun()
        
        with col2:
            st.caption("This will:")
            st.caption("✅ Index all generated files")
            st.caption("✅ Keep them with original files")
            st.caption("✅ Reset workflow for new generation")
            st.caption("✅ Preserve all indexed content")

def render_reset_section():
    """Reset workflow with confirmation."""
    if st.session_state.workflow_executed:
        st.divider()
        
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("🔄 New Workflow (Keep Files)", type="secondary", use_container_width=True):
                # Reset workflow but keep indexed files
                st.session_state.workflow = None
                st.session_state.workflow_executed = False
                st.session_state.output_files = []
                st.session_state.execution_errors = []
                st.session_state.template_mode = False
                st.session_state.selected_template = None
                st.session_state.ai_generation_in_progress = False
                st.session_state.generation_complete = False
                st.rerun()
        with col2:
            if st.button("🗑️ Clear All & Start Over", type="secondary", use_container_width=True):
                # Reset everything including files
                st.session_state.document_indexed = False
                st.session_state.workflow = None
                st.session_state.workflow_executed = False
                st.session_state.output_files = []
                st.session_state.execution_errors = []
                st.session_state.doc_name = None
                st.session_state.template_mode = False
                st.session_state.selected_template = None
                st.session_state.suggested_template = None
                st.session_state.ai_generation_in_progress = False
                st.session_state.generation_complete = False
                st.session_state.indexed_files = []
                st.session_state.total_chunks_indexed = 0
                st.session_state.pending_files = []
                
                # Clear ChromaDB
                try:
                    st.session_state.collection = initialize_vector_store()
                except:
                    pass
                
                st.rerun()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application with enhanced flow control."""
    init_session_state()
    
    # System initialization
    success, error_msg = initialize_system()
    if not success:
        st.error(error_msg)
        st.stop()
    
    # Header
    render_header()
    
    # Sidebar
    render_sidebar()
    
    st.divider()
    
    # Main workflow
    
    # Step 0: API Configuration (MUST be configured first)
    render_api_configuration()
    
    if not st.session_state.api_configured:
        st.info("👆 Please configure your API key and model above to continue")
        st.stop()
    
    st.divider()

    # Step 1: Upload
    has_new_files = render_file_upload()
    
    # Step 2: Index
    if has_new_files or (st.session_state.pending_files and not st.session_state.document_indexed):
        st.divider()
        render_indexing_section()
    
    if st.session_state.document_indexed and not has_new_files:
        st.divider()
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.success(f"✅ **{len(st.session_state.indexed_files)} file(s) indexed and ready**")
        with col2:
            st.info(f"🧩 {st.session_state.total_chunks_indexed} chunks")
        with col3:
            # Option to add more files
            if st.button("➕ Add More Files", key="add_more_btn"):
                st.info("👆 Scroll up to upload additional files")
    
    if st.session_state.document_indexed:
        st.divider()
        
        # Step 3: Generate workflow
        if not st.session_state.workflow:
            if st.session_state.template_mode is False and st.session_state.selected_template is None and st.session_state.ai_generation_in_progress is False:
                
                render_template_or_ai_choice()
            elif st.session_state.template_mode:
                if not st.session_state.generation_complete:
                    render_workflow_generation_template()
            elif st.session_state.ai_generation_in_progress:
                render_workflow_generation_ai()
            else:
                
                render_template_or_ai_choice()
        else:
            render_workflow_display()
    
    if st.session_state.workflow and not st.session_state.workflow_executed:
        st.divider()
        
        # Step 4: Execute
        render_workflow_execution()
    
    if st.session_state.failed_tasks and st.session_state.workflow_executed:
        render_retry_failed_tasks()

    if st.session_state.workflow_executed:
        st.divider()
        
        # Step 5: Download
        render_outputs_section()

        # Step 6: Add to training for next workflow
        render_add_to_training_section()
        
        # Reset
        render_reset_section()
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>🤖 Sophia Prototype v1.0 (Stage 3: Production Ready)</p>
            <p>With Templates • Error Handling • History • Validation</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
