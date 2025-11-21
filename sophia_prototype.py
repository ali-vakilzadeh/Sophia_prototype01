"""
Sophia Prototype - Core Engine (Stage 1)
========================================
Minimal prototype for AI-powered project planning workflow automation.

Context Strategy (Main Focus):
- Chunk size: 800 chars (semantic coherence)
- Overlap: 200 chars (context preservation)
- Workflow generation: Top 10 chunks (comprehensive understanding)
- Task execution: Top 5 chunks + all previous outputs (cumulative learning)
- Max context: ~6000 tokens to prevent overflow

Dependencies:
    pip install chromadb openai python-dotenv
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings


# ============================================================================
# CONFIGURATION
# ============================================================================

def load_env_config() -> Dict[str, str]:
    """
    Load configuration from .env file.
    
    Returns:
        Dict with api_key and model name
    """
    load_dotenv()
    
    config = {
        'api_key': os.getenv('OPENROUTER_API_KEY', ''),
        'model': os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')
    }
    
    if not config['api_key']:
        raise ValueError("OPENROUTER_API_KEY not found in .env file")
    
    return config


# ============================================================================
# VECTOR STORE (ChromaDB - Local, Zero Cost)
# ============================================================================

def initialize_vector_store() -> chromadb.Collection:
    """
    Initialize local ChromaDB vector store with persistence.
    
    Returns:
        ChromaDB collection object
    """
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Get or create collection for project documents
    collection = client.get_or_create_collection(
        name="project_docs",
        metadata={"description": "Sophia project specification documents"}
    )
    
    return collection


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks for better context preservation.
    
    Strategy: 800 char chunks with 200 char overlap ensures semantic coherence
    while preventing information loss at boundaries.
    
    Args:
        text: Input document text
        chunk_size: Size of each chunk (default: 800)
        overlap: Overlap between chunks (default: 200)
    
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Don't add empty chunks
        if chunk.strip():
            chunks.append(chunk)
        
        # Move start position (chunk_size - overlap for next iteration)
        start += (chunk_size - overlap)
    
    return chunks


def index_document(collection: chromadb.Collection, text: str, doc_name: str) -> Dict:
    """
    Index document in vector store with chunking.
    
    Args:
        collection: ChromaDB collection
        text: Document text content
        doc_name: Document identifier
    
    Returns:
        Dict with success status and chunk count
    """
    # Clear previous document if exists
    existing_ids = collection.get(where={"source": doc_name})["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)
    
    # Chunk the document
    chunks = chunk_text(text)
    
    # Prepare data for ChromaDB
    ids = [f"{doc_name}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": doc_name, "chunk_index": i} for i in range(len(chunks))]
    
    # Add to vector store
    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    
    return {
        "success": True,
        "chunks_indexed": len(chunks),
        "document": doc_name
    }


def query_vector_store(
    collection: chromadb.Collection, 
    query: str, 
    top_k: int = 5
) -> List[Dict]:
    """
    Retrieve most relevant chunks from vector store.
    
    Context Strategy:
    - Workflow generation: top_k=10 (comprehensive understanding)
    - Task execution: top_k=5 (focused relevant context)
    
    Args:
        collection: ChromaDB collection
        query: Search query
        top_k: Number of results to return
    
    Returns:
        List of dicts with 'text' and 'relevance' keys
    """
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    # Format results
    retrieved = []
    for i, doc in enumerate(results['documents'][0]):
        retrieved.append({
            'text': doc,
            'relevance': 1.0 - (i * 0.1)  # Simple relevance scoring
        })
    
    return retrieved


# ============================================================================
# AI INTERFACE (OpenRouter)
# ============================================================================

def call_openrouter(
    prompt: str, 
    api_key: str, 
    model: str,
    response_format: Optional[str] = None
) -> str:
    """
    Call OpenRouter API with structured prompt.
    
    Args:
        prompt: Input prompt
        api_key: OpenRouter API key
        model: Model identifier
        response_format: Optional "json" for JSON responses
    
    Returns:
        AI response text
    """
    import requests
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    # Add JSON mode if requested
    if response_format == "json":
        payload["response_format"] = {"type": "json_object"}
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )
    
    response.raise_for_status()
    result = response.json()
    
    return result['choices'][0]['message']['content']


# ============================================================================
# WORKFLOW GENERATION
# ============================================================================

def generate_workflow(
    collection: chromadb.Collection, 
    api_key: str, 
    model: str
) -> Dict:
    """
    Generate workflow JSON from indexed document.
    
    Context Strategy: Retrieve top 10 chunks for comprehensive understanding
    of the entire project specification before planning.
    
    Args:
        collection: Vector store with indexed document
        api_key: OpenRouter API key
        model: Model name
    
    Returns:
        Workflow JSON as dict
    """
    # Retrieve comprehensive context (top 10 chunks)
    context_chunks = query_vector_store(
        collection, 
        query="project specification requirements objectives tasks",
        top_k=10
    )
    
    # Assemble context
    context = "\n\n---\n\n".join([chunk['text'] for chunk in context_chunks])
    
    # Craft workflow generation prompt
    prompt = f"""Based on the following project specification, generate a workflow JSON that breaks down project planning into discrete AI tasks.

PROJECT SPECIFICATION:
{context}

Generate a JSON workflow with tasks for:
1. Creating Work Breakdown Structure (WBS)
2. Generating detailed task list with dependencies
3. Prioritizing tasks
4. Identifying required resources
5. Any other planning tasks you deem necessary

Return ONLY valid JSON in this exact format:
{{
  "workflow_name": "Project Planning Workflow",
  "tasks": [
    {{
      "task_id": "1",
      "name": "create_wbs",
      "prompt": "Based on the project specification, create a comprehensive Work Breakdown Structure...",
      "output_format": "markdown"
    }},
    {{
      "task_id": "2",
      "name": "create_task_list",
      "prompt": "Generate a detailed task list with dependencies...",
      "output_format": "csv"
    }}
  ]
}}

Ensure each task prompt is self-contained and references the project specification context."""
    
    # Call AI
    response = call_openrouter(prompt, api_key, model, response_format="json")
    
    # Parse JSON
    workflow = json.loads(response)
    
    return workflow


# ============================================================================
# TASK EXECUTION
# ============================================================================

def execute_task(
    task: Dict,
    collection: chromadb.Collection,
    api_key: str,
    model: str,
    previous_outputs: List[str]
) -> str:
    """
    Execute a single workflow task with cumulative context.
    
    Context Assembly Strategy (CRITICAL):
    1. Retrieve top 5 most relevant chunks from vector store
    2. Include ALL previous task outputs (cumulative learning)
    3. Order: Most relevant chunks first, then previous outputs
    4. Monitor token count (~6000 token limit = ~24,000 chars)
    
    Args:
        task: Task dict with prompt and metadata
        collection: Vector store
        api_key: API key
        model: Model name
        previous_outputs: List of previous task results
    
    Returns:
        Task output text
    """
    # Extract task prompt
    task_prompt = task['prompt']
    
    # Retrieve relevant context (top 5 chunks)
    context_chunks = query_vector_store(
        collection,
        query=task_prompt,
        top_k=5
    )
    
    # Assemble context components
    context_parts = []
    
    # 1. Most relevant chunks from project spec
    spec_context = "\n\n".join([chunk['text'] for chunk in context_chunks])
    context_parts.append(f"PROJECT SPECIFICATION CONTEXT:\n{spec_context}")
    
    # 2. Previous task outputs (cumulative learning)
    if previous_outputs:
        prev_context = "\n\n---\n\n".join(previous_outputs)
        context_parts.append(f"PREVIOUS TASK OUTPUTS:\n{prev_context}")
    
    # Combine all context
    full_context = "\n\n" + "="*50 + "\n\n".join(context_parts)
    
    # Token safety: Truncate if too long (rough estimate: 4 chars = 1 token)
    MAX_CONTEXT_CHARS = 20000  # ~5000 tokens for context, leaves room for response
    if len(full_context) > MAX_CONTEXT_CHARS:
        full_context = full_context[:MAX_CONTEXT_CHARS] + "\n\n[Context truncated for token limit]"
    
    # Build final prompt
    final_prompt = f"""{task_prompt}

{full_context}

Provide a detailed, well-structured response in {task['output_format']} format."""
    
    # Execute task
    result = call_openrouter(final_prompt, api_key, model)
    
    return result


def execute_workflow(
    workflow: Dict,
    collection: chromadb.Collection,
    api_key: str,
    model: str
) -> List[str]:
    """
    Execute entire workflow with cumulative context building.
    
    Each task sees:
    - Relevant chunks from original document
    - ALL outputs from previous tasks (builds on previous work)
    
    Args:
        workflow: Workflow JSON dict
        collection: Vector store
        api_key: API key
        model: Model name
    
    Returns:
        List of output file paths
    """
    output_files = []
    previous_outputs = []
    
    print(f"\n{'='*60}")
    print(f"Executing Workflow: {workflow['workflow_name']}")
    print(f"{'='*60}\n")
    
    for task in workflow['tasks']:
        task_id = task['task_id']
        task_name = task['name']
        
        print(f"[Task {task_id}] Executing: {task_name}...")
        
        # Execute task with cumulative context
        result = execute_task(
            task=task,
            collection=collection,
            api_key=api_key,
            model=model,
            previous_outputs=previous_outputs
        )
        
        # Save output
        output_path = save_output(
            content=result,
            task_name=task_name,
            output_format=task['output_format']
        )
        
        output_files.append(output_path)
        previous_outputs.append(f"[Task {task_id}: {task_name}]\n{result}")
        
        print(f"[Task {task_id}] ✓ Complete. Saved to: {output_path}\n")
    
    print(f"{'='*60}")
    print(f"Workflow Complete! Generated {len(output_files)} outputs.")
    print(f"{'='*60}\n")
    
    return output_files


# ============================================================================
# FILE OUTPUT
# ============================================================================

def save_output(content: str, task_name: str, output_format: str) -> str:
    """
    Save task output to file with date-stamped naming.
    
    Naming convention: YYYY-MM-DD-{task_name}-rev0.{ext}
    
    Args:
        content: Output content
        task_name: Task identifier
        output_format: 'markdown' or 'csv'
    
    Returns:
        File path
    """
    # Create outputs directory if needed
    os.makedirs("outputs", exist_ok=True)
    
    # Generate filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    ext = "md" if output_format == "markdown" else "csv"
    filename = f"{date_str}-{task_name}-rev0.{ext}"
    filepath = os.path.join("outputs", filename)
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath


# ============================================================================
# MAIN EXECUTION EXAMPLE
# ============================================================================

def main():
    """
    Example usage of the Sophia prototype core engine.
    """
    print("\n" + "="*60)
    print("SOPHIA PROTOTYPE - STAGE 1: CORE ENGINE")
    print("="*60 + "\n")
    
    # 1. Load configuration
    print("[1/5] Loading configuration...")
    config = load_env_config()
    print(f"✓ Using model: {config['model']}\n")
    
    # 2. Initialize vector store
    print("[2/5] Initializing vector store...")
    collection = initialize_vector_store()
    print("✓ ChromaDB ready\n")
    
    # 3. Index sample document
    print("[3/5] Indexing project specification...")
    sample_doc = """
    Project: E-Commerce Platform Development
    
    Objective: Build a modern e-commerce platform for selling artisan crafts online.
    
    Requirements:
    - User authentication and profile management
    - Product catalog with search and filtering
    - Shopping cart and checkout system
    - Payment gateway integration (Stripe)
    - Order management for sellers
    - Review and rating system
    - Mobile-responsive design
    
    Timeline: 6 months
    Budget: $150,000
    Team: 5 developers, 1 designer, 1 project manager
    
    Technical Stack: React, Node.js, PostgreSQL, AWS
    """
    
    result = index_document(collection, sample_doc, "project_spec_v1")
    print(f"✓ Indexed {result['chunks_indexed']} chunks\n")
    
    # 4. Generate workflow
    print("[4/5] Generating workflow from project spec...")
    workflow = generate_workflow(collection, config['api_key'], config['model'])
    print(f"✓ Generated workflow: {workflow['workflow_name']}")
    print(f"  Tasks: {len(workflow['tasks'])}\n")
    
    # 5. Execute workflow
    print("[5/5] Executing workflow tasks...\n")
    output_files = execute_workflow(workflow, collection, config['api_key'], config['model'])
    
    print("\n✓ All tasks complete!")
    print(f"  Output files: {len(output_files)}")
    for filepath in output_files:
        print(f"    - {filepath}")


if __name__ == "__main__":
    main()
