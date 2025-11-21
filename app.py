"""
Sophia Prototype - Streamlit UI (Stage 2)
==========================================
User-friendly web interface for AI-powered project planning workflow.

UX Design Principles:
- Progressive disclosure (show next step only when ready)
- Real-time feedback (progress indicators, status messages)
- Clear state management (what's been done, what's next)
- Instant gratification (immediate visual feedback for actions)
- Error resilience (graceful degradation, helpful messages)

Usage:
    streamlit run app.py
"""

import streamlit as st
import json
import os
from datetime import datetime
from typing import List, Dict

# Import core engine functions
from sophia_prototype import (
    load_env_config,
    initialize_vector_store,
    index_document,
    generate_workflow,
    execute_task,
    save_output
)


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
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize all session state variables."""
    if 'config' not in st.session_state:
        st.session_state.config = None
    if 'collection' not in st.session_state:
        st.session_state.collection = None
    if 'document_indexed' not in st.session_state:
        st.session_state.document_indexed = False
    if 'workflow' not in st.session_state:
        st.session_state.workflow = None
    if 'workflow_executed' not in st.session_state:
        st.session_state.workflow_executed = False
    if 'output_files' not in st.session_state:
        st.session_state.output_files = []
    if 'doc_name' not in st.session_state:
        st.session_state.doc_name = None


# ============================================================================
# SYSTEM INITIALIZATION
# ============================================================================

def initialize_system():
    """Initialize configuration and vector store (one-time setup)."""
    try:
        with st.spinner("Initializing Sophia..."):
            # Load config
            if st.session_state.config is None:
                st.session_state.config = load_env_config()
            
            # Initialize vector store
            if st.session_state.collection is None:
                st.session_state.collection = initialize_vector_store()
        
        return True
    except Exception as e:
        st.error(f"❌ Initialization failed: {str(e)}")
        st.info("💡 Make sure your .env file exists with OPENROUTER_API_KEY set")
        return False


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_header():
    """Render application header."""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("🤖 Sophia - AI Project Planning Assistant")
        st.markdown("*Transform your project specifications into structured planning workflows*")
    
    with col2:
        if st.session_state.config:
            model_name = st.session_state.config['model'].split('/')[-1]
            st.info(f"🧠 Model: {model_name}")


def render_sidebar_status():
    """Render workflow status in sidebar."""
    st.sidebar.header("📊 Workflow Status")
    
    # Progress tracking
    steps = [
        ("📄 Document Upload", st.session_state.doc_name is not None),
        ("🔍 Document Indexed", st.session_state.document_indexed),
        ("🗺️ Workflow Generated", st.session_state.workflow is not None),
        ("✅ Workflow Executed", st.session_state.workflow_executed)
    ]
    
    for step_name, completed in steps:
        if completed:
            st.sidebar.success(f"✓ {step_name}")
        else:
            st.sidebar.info(f"○ {step_name}")
    
    # Stats
    if st.session_state.workflow:
        st.sidebar.divider()
        st.sidebar.metric("Tasks in Workflow", len(st.session_state.workflow['tasks']))
    
    if st.session_state.output_files:
        st.sidebar.metric("Output Files", len(st.session_state.output_files))


def render_file_upload():
    """Render file upload section."""
    st.header("📤 Step 1: Upload Project Specification")
    
    uploaded_file = st.file_uploader(
        "Upload your project specification (.txt file)",
        type=['txt'],
        help="Upload a text file containing your project requirements, objectives, and scope"
    )
    
    if uploaded_file is not None:
        # Read file content
        content = uploaded_file.read().decode('utf-8')
        
        # Display preview
        with st.expander("📄 Document Preview", expanded=False):
            st.text_area(
                "Content",
                content,
                height=200,
                disabled=True
            )
        
        # Show file stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Size", f"{len(content)} chars")
        with col2:
            st.metric("Word Count", len(content.split()))
        with col3:
            st.metric("Lines", len(content.split('\n')))
        
        return content, uploaded_file.name
    
    return None, None


def render_indexing_section(content: str, doc_name: str):
    """Render document indexing section."""
    st.header("🔍 Step 2: Index Document")
    
    st.info("📚 This will split your document into chunks and store them in the vector database for intelligent retrieval.")
    
    if st.button("🚀 Index Document", type="primary", use_container_width=True):
        with st.status("Indexing document...", expanded=True) as status:
            try:
                # Index the document
                st.write("🔨 Splitting document into chunks...")
                result = index_document(
                    st.session_state.collection,
                    content,
                    doc_name
                )
                
                st.write(f"✅ Indexed {result['chunks_indexed']} chunks")
                
                # Update state
                st.session_state.document_indexed = True
                st.session_state.doc_name = doc_name
                
                status.update(label="✅ Document indexed successfully!", state="complete")
                st.balloons()
                
            except Exception as e:
                status.update(label="❌ Indexing failed", state="error")
                st.error(f"Error: {str(e)}")


def render_workflow_generation():
    """Render workflow generation section."""
    st.header("🗺️ Step 3: Generate Workflow")
    
    st.info("🤖 AI will analyze your document and create a structured workflow with planning tasks.")
    
    if st.button("✨ Generate Workflow", type="primary", use_container_width=True):
        with st.status("Generating workflow...", expanded=True) as status:
            try:
                st.write("🧠 Retrieving document context...")
                st.write("💭 Analyzing project requirements...")
                
                # Generate workflow
                workflow = generate_workflow(
                    st.session_state.collection,
                    st.session_state.config['api_key'],
                    st.session_state.config['model']
                )
                
                st.write(f"✅ Generated {len(workflow['tasks'])} tasks")
                
                # Update state
                st.session_state.workflow = workflow
                
                status.update(label="✅ Workflow generated successfully!", state="complete")
                st.success(f"🎉 Created workflow: **{workflow['workflow_name']}**")
                
            except Exception as e:
                status.update(label="❌ Generation failed", state="error")
                st.error(f"Error: {str(e)}")


def render_workflow_display():
    """Display generated workflow."""
    if st.session_state.workflow:
        st.header("📋 Generated Workflow")
        
        workflow = st.session_state.workflow
        
        # Workflow name
        st.subheader(workflow['workflow_name'])
        
        # Task list
        st.markdown("### 📝 Tasks:")
        for i, task in enumerate(workflow['tasks'], 1):
            with st.expander(f"Task {i}: {task['name']}", expanded=False):
                st.markdown(f"**Task ID:** {task['task_id']}")
                st.markdown(f"**Output Format:** {task['output_format']}")
                st.markdown("**Prompt:**")
                st.text_area(
                    "Prompt",
                    task['prompt'],
                    height=100,
                    key=f"task_prompt_{i}",
                    disabled=True,
                    label_visibility="collapsed"
                )
        
        # JSON view
        with st.expander("🔧 View Raw JSON", expanded=False):
            st.json(workflow)


def render_workflow_execution():
    """Render workflow execution section."""
    st.header("⚡ Step 4: Execute Workflow")
    
    st.info(f"🎯 This will execute all {len(st.session_state.workflow['tasks'])} tasks sequentially with cumulative context.")
    
    if st.button("🚀 Execute Workflow", type="primary", use_container_width=True):
        workflow = st.session_state.workflow
        output_files = []
        previous_outputs = []
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_tasks = len(workflow['tasks'])
        
        for i, task in enumerate(workflow['tasks'], 1):
            # Update progress
            progress = i / total_tasks
            progress_bar.progress(progress)
            status_text.text(f"Executing task {i}/{total_tasks}: {task['name']}...")
            
            # Create expandable section for task execution
            with st.expander(f"Task {i}: {task['name']}", expanded=True):
                with st.spinner("Processing..."):
                    try:
                        # Execute task
                        result = execute_task(
                            task=task,
                            collection=st.session_state.collection,
                            api_key=st.session_state.config['api_key'],
                            model=st.session_state.config['model'],
                            previous_outputs=previous_outputs
                        )
                        
                        # Save output
                        output_path = save_output(
                            content=result,
                            task_name=task['name'],
                            output_format=task['output_format']
                        )
                        
                        output_files.append(output_path)
                        previous_outputs.append(f"[Task {task['task_id']}: {task['name']}]\n{result}")
                        
                        # Display result preview
                        st.success(f"✅ Completed! Saved to: `{output_path}`")
                        
                        # Show preview
                        preview_length = min(500, len(result))
                        st.text_area(
                            "Preview",
                            result[:preview_length] + ("..." if len(result) > preview_length else ""),
                            height=150,
                            key=f"result_preview_{i}",
                            disabled=True,
                            label_visibility="collapsed"
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Task failed: {str(e)}")
        
        # Update final state
        progress_bar.progress(1.0)
        status_text.text("✅ All tasks completed!")
        
        st.session_state.output_files = output_files
        st.session_state.workflow_executed = True
        
        st.balloons()
        st.success(f"🎉 Workflow complete! Generated {len(output_files)} output files.")


def render_output_downloads():
    """Render download section for output files."""
    if st.session_state.output_files:
        st.header("📥 Download Results")
        
        st.success(f"✅ {len(st.session_state.output_files)} files ready for download")
        
        # Create columns for download buttons
        cols = st.columns(2)
        
        for i, filepath in enumerate(st.session_state.output_files):
            col = cols[i % 2]
            
            with col:
                # Read file content
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract filename
                filename = os.path.basename(filepath)
                
                # Create download button
                st.download_button(
                    label=f"📄 {filename}",
                    data=content,
                    file_name=filename,
                    mime="text/plain",
                    use_container_width=True
                )


def render_reset_button():
    """Render reset workflow button."""
    if st.session_state.workflow_executed:
        st.divider()
        if st.button("🔄 Start New Workflow", type="secondary", use_container_width=True):
            # Reset state
            st.session_state.document_indexed = False
            st.session_state.workflow = None
            st.session_state.workflow_executed = False
            st.session_state.output_files = []
            st.session_state.doc_name = None
            st.rerun()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application flow."""
    # Initialize session state
    init_session_state()
    
    # Initialize system
    if not initialize_system():
        st.stop()
    
    # Render header
    render_header()
    
    # Render sidebar status
    render_sidebar_status()
    
    st.divider()
    
    # Main workflow steps
    
    # Step 1: File Upload
    content, doc_name = render_file_upload()
    
    if content and doc_name:
        st.divider()
        
        # Step 2: Indexing
        if not st.session_state.document_indexed:
            render_indexing_section(content, doc_name)
        else:
            st.success(f"✅ Document '{doc_name}' is indexed and ready")
    
    if st.session_state.document_indexed:
        st.divider()
        
        # Step 3: Workflow Generation
        if not st.session_state.workflow:
            render_workflow_generation()
        else:
            render_workflow_display()
    
    if st.session_state.workflow and not st.session_state.workflow_executed:
        st.divider()
        
        # Step 4: Workflow Execution
        render_workflow_execution()
    
    if st.session_state.workflow_executed:
        st.divider()
        
        # Step 5: Downloads
        render_output_downloads()
        
        # Reset option
        render_reset_button()
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>🤖 Sophia Prototype v1.0 | Powered by AI</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
