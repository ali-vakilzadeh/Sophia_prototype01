"""
Sophia Prototype - Enhanced Core Engine (Stage 3)
=================================================
Production-ready version with error handling, validation, and history.

Enhancements:
- Comprehensive error handling with recovery strategies
- Input validation to prevent bad data
- Workflow history tracking
- Enhanced logging for debugging
- Rate limiting and retry logic
- Template support integration
- File management utilities

This builds on Stage 1 core with production-grade reliability.
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings

# Import templates
from templates import (
    get_template,
    list_templates,
    apply_template_to_context,
    suggest_template
)


# ============================================================================
# CONFIGURATION WITH VALIDATION
# ============================================================================

class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass


def load_env_config() -> Dict[str, str]:
    """
    Load and validate configuration from .env file.
    
    Returns:
        Dict with validated config
    
    Raises:
        ConfigurationError: If config is invalid
    """
    load_dotenv()
    
    api_key = os.getenv('OPENROUTER_API_KEY', '')
    model = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')
    
    # Validation
    if not api_key:
        raise ConfigurationError(
            "OPENROUTER_API_KEY not found in .env file. "
            "Please create a .env file with your API key."
        )
    
    if not api_key.startswith('sk-'):
        raise ConfigurationError(
            "OPENROUTER_API_KEY appears invalid (should start with 'sk-')"
        )
    
    config = {
        'api_key': api_key,
        'model': model,
        'max_retries': int(os.getenv('MAX_RETRIES', '3')),
        'timeout': int(os.getenv('API_TIMEOUT', '60')),
        'chunk_size': int(os.getenv('CHUNK_SIZE', '800')),
        'chunk_overlap': int(os.getenv('CHUNK_OVERLAP', '200'))
    }
    
    return config


# ============================================================================
# VECTOR STORE WITH ERROR HANDLING
# ============================================================================

class VectorStoreError(Exception):
    """Raised when vector store operations fail."""
    pass


def initialize_vector_store() -> chromadb.Collection:
    """
    Initialize ChromaDB with error handling.
    
    Returns:
        ChromaDB collection
    
    Raises:
        VectorStoreError: If initialization fails
    """
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_or_create_collection(
            name="project_docs",
            metadata={"description": "Sophia project specification documents"}
        )
        return collection
    except Exception as e:
        raise VectorStoreError(f"Failed to initialize vector store: {str(e)}")


def validate_text_input(text: str) -> Tuple[bool, Optional[str]]:
    """
    Validate text input before processing.
    
    Args:
        text: Input text to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Text is empty or contains only whitespace"
    
    if len(text) < 100:
        return False, "Text is too short (minimum 100 characters). Please provide more detail."
    
    if len(text) > 100000:
        return False, "Text is too long (maximum 100,000 characters). Please split into smaller documents."
    
    return True, None


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks with validation.
    
    Args:
        text: Input text
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
    
    Returns:
        List of text chunks
    
    Raises:
        ValueError: If parameters are invalid
    """
    if chunk_size <= overlap:
        raise ValueError("Chunk size must be greater than overlap")
    
    if chunk_size < 100:
        raise ValueError("Chunk size too small (minimum 100)")
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        if chunk.strip():
            chunks.append(chunk)
        
        start += (chunk_size - overlap)
    
    return chunks


def index_document(
    collection: chromadb.Collection,
    text: str,
    doc_name: str,
    config: Dict
) -> Dict:
    """
    Index document with validation and error handling.
    
    Args:
        collection: ChromaDB collection
        text: Document text
        doc_name: Document identifier
        config: Configuration dict
    
    Returns:
        Result dict with status and metadata
    
    Raises:
        VectorStoreError: If indexing fails
        ValueError: If input is invalid
    """
    # Validate input
    is_valid, error_msg = validate_text_input(text)
    if not is_valid:
        raise ValueError(f"Invalid input: {error_msg}")
    
    try:
        # Clear previous document if exists
        existing_ids = collection.get(where={"source": doc_name})["ids"]
        if existing_ids:
            collection.delete(ids=existing_ids)
        
        # Chunk the document
        chunks = chunk_text(
            text,
            chunk_size=config.get('chunk_size', 800),
            overlap=config.get('chunk_overlap', 200)
        )
        
        # Prepare data for ChromaDB
        ids = [f"{doc_name}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "source": doc_name,
                "chunk_index": i,
                "timestamp": datetime.now().isoformat()
            }
            for i in range(len(chunks))
        ]
        
        # Add to vector store
        collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        return {
            "success": True,
            "chunks_indexed": len(chunks),
            "document": doc_name,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise VectorStoreError(f"Indexing failed: {str(e)}")


def query_vector_store(
    collection: chromadb.Collection,
    query: str,
    top_k: int = 5
) -> List[Dict]:
    """
    Query vector store with error handling.
    
    Args:
        collection: ChromaDB collection
        query: Search query
        top_k: Number of results
    
    Returns:
        List of result dicts
    
    Raises:
        VectorStoreError: If query fails
    """
    try:
        results = collection.query(
            query_texts=[query],
            n_results=min(top_k, 10)  # Cap at 10 for safety
        )
        
        retrieved = []
        for i, doc in enumerate(results['documents'][0]):
            retrieved.append({
                'text': doc,
                'relevance': 1.0 - (i * 0.1),
                'metadata': results['metadatas'][0][i] if results.get('metadatas') else {}
            })
        
        return retrieved
        
    except Exception as e:
        raise VectorStoreError(f"Query failed: {str(e)}")


# ============================================================================
# AI INTERFACE WITH RETRY LOGIC
# ============================================================================

class AIError(Exception):
    """Raised when AI API calls fail."""
    pass

def clean_json_response(response: str) -> str:
    """
    Clean AI response to extract valid JSON.
    
    Many models wrap JSON in markdown code blocks or add explanatory text.
    This function extracts just the JSON portion.
    
    Args:
        response: Raw AI response
    
    Returns:
        Cleaned JSON string
    """
    import re
    
    # Remove markdown code blocks
    response = re.sub(r'```json\s*', '', response)
    response = re.sub(r'```\s*', '', response)
    
    # Remove any text before the first {
    start = response.find('{')
    if start != -1:
        response = response[start:]
    
    # Remove any text after the last }
    end = response.rfind('}')
    if end != -1:
        response = response[:end + 1]
    
    # Strip whitespace
    response = response.strip()
    
    return response

def call_openrouter_with_retry(
    prompt: str,
    api_key: str,
    model: str,
    config: Dict,
    response_format: Optional[str] = None
) -> str:
    """
    Call OpenRouter with exponential backoff retry logic.
    
    Args:
        prompt: Input prompt
        api_key: API key
        model: Model identifier
        config: Configuration with retry settings
        response_format: Optional "json" for JSON mode (handled via prompt)
    
    Returns:
        AI response text
    
    Raises:
        AIError: If all retries fail
    """
    import requests
    
    max_retries = config.get('max_retries', 3)
    timeout = config.get('timeout', 60)
    
    # If JSON requested, enhance the prompt instead of using API parameter
    if response_format == "json":
        prompt = f"""{prompt}

CRITICAL FORMATTING INSTRUCTIONS:
- Return ONLY valid JSON
- Do NOT include any markdown formatting (no ```json or ```)
- Do NOT include any explanatory text before or after the JSON
- Start your response with {{ and end with }}
- Ensure all JSON is properly formatted and parseable"""
    
    for attempt in range(max_retries):
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://sophia-planner.app",  # Optional: for better tracking
                "X-Title": "Sophia Project Planner"  # Optional: for better tracking
            }
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,  # Slight randomness for creativity
                "max_tokens": 4000   # Ensure we get complete responses
            }
            
            # DO NOT add response_format parameter - causes issues with OpenRouter
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract content
            content = result['choices'][0]['message']['content']
            
            # If JSON was requested, clean up the response
            if response_format == "json":
                content = clean_json_response(content)
            
            return content
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
                continue
            raise AIError(f"API request timed out after {max_retries} attempts")
            
        except requests.exceptions.HTTPError as e:
            # Check for specific error codes
            if e.response.status_code == 400:
                raise AIError(f"Bad request to OpenRouter API. Check your model name and parameters. Error: {str(e)}")
            elif e.response.status_code == 401:
                raise AIError("Invalid API key. Please check your OPENROUTER_API_KEY in settings.")
            elif e.response.status_code == 429:
                # Rate limited
                if attempt < max_retries - 1:
                    wait_time = 5 * (2 ** attempt)  # Longer backoff for rate limits
                    time.sleep(wait_time)
                    continue
                raise AIError("Rate limited by OpenRouter. Please wait a moment and try again.")
            else:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                raise AIError(f"API request failed: {str(e)}")
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            raise AIError(f"API request failed: {str(e)}")
        
        except KeyError as e:
            raise AIError(f"Unexpected API response format: {str(e)}")
        
        except Exception as e:
            raise AIError(f"Unexpected error: {str(e)}")
    
    raise AIError("All retry attempts exhausted")


# ============================================================================
# WORKFLOW GENERATION WITH VALIDATION
# ============================================================================

def validate_workflow_json(workflow: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate workflow JSON structure.
    
    Args:
        workflow: Workflow dictionary
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['workflow_name', 'tasks']
    for field in required_fields:
        if field not in workflow:
            return False, f"Missing required field: {field}"
    
    if not isinstance(workflow['tasks'], list):
        return False, "'tasks' must be a list"
    
    if len(workflow['tasks']) == 0:
        return False, "Workflow must have at least one task"
    
    if len(workflow['tasks']) > 15:
        return False, "Too many tasks (maximum 15 for prototype)"
    
    # Validate each task
    required_task_fields = ['task_id', 'name', 'prompt', 'output_format']
    for i, task in enumerate(workflow['tasks']):
        for field in required_task_fields:
            if field not in task:
                return False, f"Task {i+1} missing required field: {field}"
        
        if task['output_format'] not in ['markdown', 'csv']:
            return False, f"Task {i+1} has invalid output_format (must be 'markdown' or 'csv')"
    
    return True, None


def generate_workflow_from_ai(
    collection: chromadb.Collection,
    api_key: str,
    model: str,
    config: Dict
) -> Dict:
    """
    Generate workflow using AI with validation.
    
    Args:
        collection: Vector store
        api_key: API key
        model: Model name
        config: Configuration
    
    Returns:
        Validated workflow dict
    
    Raises:
        AIError: If generation fails
        ValueError: If workflow is invalid
    """
    # Retrieve context
    context_chunks = query_vector_store(collection, 
        "project specification requirements objectives", top_k=10)
    
    context = "\n\n---\n\n".join([chunk['text'] for chunk in context_chunks])
    
    prompt = f"""Based on the following project specification, generate a workflow JSON that breaks down project planning into discrete AI tasks.

PROJECT SPECIFICATION:
{context}

Generate a JSON workflow with 4-7 tasks covering:
- Requirements analysis or WBS
- Task breakdown and dependencies
- Resource planning
- Risk assessment or timeline planning

CRITICAL: Return ONLY valid JSON, no other text. Use this exact structure:
{{
  "workflow_name": "Descriptive workflow name",
  "tasks": [
    {{
      "task_id": "1",
      "name": "task_identifier_lowercase",
      "prompt": "Detailed task instructions...",
      "output_format": "markdown"
    }}
  ]
}}

IMPORTANT:
- Output_format must be either "markdown" or "csv"
- Each task prompt should clearly reference project context
- Start your response with {{ and end with }}
- Do NOT wrap in markdown code blocks"""
    
    # Call AI
    response = call_openrouter_with_retry(prompt, api_key, model, config, response_format="json")
    
    # Parse and validate
    try:
        workflow = json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {str(e)}")
    
    is_valid, error_msg = validate_workflow_json(workflow)
    if not is_valid:
        raise ValueError(f"Invalid workflow structure: {error_msg}")
    
    return workflow

def generate_workflow_from_ai_with_goal(
    collection: chromadb.Collection,
    api_key: str,
    model: str,
    config: Dict,
    workflow_goal: str
) -> Dict:
    """
    Generate workflow using AI with specific user goal.
    
    Args:
        collection: Vector store with indexed document
        api_key: API key
        model: Model name
        config: Configuration
        workflow_goal: User-specified workflow goal/objective
    
    Returns:
        Validated workflow dict
    
    Raises:
        AIError: If generation fails
        ValueError: If workflow is invalid
    """
    #debug: check inquiry is launched:
    print("Function called:", config, workflow_goal)
    # Retrieve context
    context_chunks = query_vector_store(collection, 
        "project specification requirements objectives", top_k=10)
    
    context = "\n\n---\n\n".join([chunk['text'] for chunk in context_chunks])
    print("context generated, length:", len(context))
    # Enhanced prompt with user goal
    prompt = f"""Based on the following project specification, generate a workflow JSON that breaks down into discrete AI tasks.

**WORKFLOW GOAL:**
{workflow_goal}

**PROJECT SPECIFICATION:**
{context}

Create a JSON workflow with 4-7 tasks that will accomplish the stated goal. The tasks should:
1. Be specific to the project specification
2. Build logically toward the workflow goal
3. Include appropriate analysis, planning, and documentation tasks
4. Produce actionable deliverables

CRITICAL: Return ONLY valid JSON, no other text. Use this exact format:
{{
  "workflow_name": "Descriptive name matching the goal",
  "tasks": [
    {{
      "task_id": "1",
      "name": "task_identifier_lowercase",
      "prompt": "Detailed instructions that reference the project spec and contribute to the goal...",
      "output_format": "markdown"
    }},
    {{
      "task_id": "2",
      "name": "another_task_name",
      "prompt": "More detailed instructions...",
      "output_format": "csv"
    }}
  ]
}}

IMPORTANT:
- Output_format must be either "markdown" or "csv"
- Each task prompt should clearly reference project context
- Start your response with {{ and end with }}
- Do NOT wrap in markdown code blocks"""
    
    print ("prompt generated - len: ", len(prompt)," chars")
    # Call AI with the enhanced prompt
    response = call_openrouter_with_retry(prompt, api_key, model, config, response_format="json")
    print("responce received ", len(response), " chars")
    # Parse and validate
    try:
        workflow = json.loads(response)
        print("json parsed")
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {str(e)}")
    
    is_valid, error_msg = validate_workflow_json(workflow)
    print("workflow validated")
    if not is_valid:
        raise ValueError(f"Invalid workflow structure: {error_msg}")
    
    return workflow

def generate_workflow_from_template(
    template_id: str,
    collection: chromadb.Collection
) -> Dict:
    """
    Generate workflow from template with context enhancement.
    
    Args:
        template_id: Template identifier
        collection: Vector store with indexed project
    
    Returns:
        Enhanced template workflow
    
    Raises:
        ValueError: If template not found
    """
    template = get_template(template_id)
    if not template:
        raise ValueError(f"Template not found: {template_id}")
    
    # Get project context
    context_chunks = query_vector_store(collection,
        "project specification", top_k=10)
    project_context = "\n\n".join([chunk['text'] for chunk in context_chunks])
    
    # Enhance template with context
    workflow = apply_template_to_context(template, project_context)
    
    return workflow


# ============================================================================
# TASK EXECUTION WITH ERROR HANDLING
# ============================================================================

def execute_task_safe(
    task: Dict,
    collection: chromadb.Collection,
    api_key: str,
    model: str,
    config: Dict,
    previous_outputs: List[str]
) -> Tuple[bool, str, Optional[str]]:
    """
    Execute task with comprehensive error handling.
    
    Args:
        task: Task dict
        collection: Vector store
        api_key: API key
        model: Model name
        config: Configuration
        previous_outputs: Previous task outputs
    
    Returns:
        Tuple of (success, result_or_error, error_type)
    """
    try:
        # Retrieve context
        context_chunks = query_vector_store(collection, task['prompt'], top_k=5)
        
        # Assemble context
        spec_context = "\n\n".join([chunk['text'] for chunk in context_chunks])
        context_parts = [f"PROJECT SPECIFICATION:\n{spec_context}"]
        
        if previous_outputs:
            prev_context = "\n\n---\n\n".join(previous_outputs)
            context_parts.append(f"PREVIOUS OUTPUTS:\n{prev_context}")
        
        full_context = "\n\n" + "="*50 + "\n\n".join(context_parts)
        
        # Token safety
        if len(full_context) > 20000:
            full_context = full_context[:20000] + "\n\n[Context truncated]"
        
        # Build prompt
        final_prompt = f"""{task['prompt']}

{full_context}

Provide detailed output in {task['output_format']} format."""
        
        # Execute
        result = call_openrouter_with_retry(final_prompt, api_key, model, config)
        
        return True, result, None
        
    except AIError as e:
        return False, str(e), "AI_ERROR"
    except VectorStoreError as e:
        return False, str(e), "VECTOR_ERROR"
    except Exception as e:
        return False, str(e), "UNKNOWN_ERROR"


# ============================================================================
# WORKFLOW HISTORY
# ============================================================================

def save_workflow_history(workflow: Dict, output_files: List[str]) -> str:
    """
    Save workflow execution history.
    
    Args:
        workflow: Executed workflow
        output_files: List of generated files
    
    Returns:
        History file path
    """
    os.makedirs("history", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    history_file = f"history/workflow_{timestamp}.json"
    
    history = {
        "workflow_name": workflow.get("workflow_name", "Unknown"),
        "timestamp": timestamp,
        "num_tasks": len(workflow.get("tasks", [])),
        "output_files": output_files,
        "workflow": workflow
    }
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)
    
    return history_file


def list_workflow_history() -> List[Dict]:
    """
    List all workflow execution history.
    
    Returns:
        List of history metadata
    """
    if not os.path.exists("history"):
        return []
    
    history_files = [f for f in os.listdir("history") if f.endswith('.json')]
    history_list = []
    
    for filename in sorted(history_files, reverse=True):
        try:
            with open(f"history/{filename}", 'r', encoding='utf-8') as f:
                data = json.load(f)
                history_list.append({
                    "filename": filename,
                    "workflow_name": data.get("workflow_name"),
                    "timestamp": data.get("timestamp"),
                    "num_tasks": data.get("num_tasks")
                })
        except:
            continue
    
    return history_list


# ============================================================================
# FILE OUTPUT WITH VERSIONING
# ============================================================================

def save_output(content: str, task_name: str, output_format: str) -> str:
    """
    Save output with automatic versioning if file exists.
    
    Args:
        content: Output content
        task_name: Task identifier
        output_format: File format
    
    Returns:
        File path
    """
    os.makedirs("outputs", exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    ext = "md" if output_format == "markdown" else "csv"
    
    # Check for existing files and increment version
    version = 0
    while True:
        filename = f"{date_str}-{task_name}-rev{version}.{ext}"
        filepath = os.path.join("outputs", filename)
        if not os.path.exists(filepath):
            break
        version += 1
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath


# Export all public functions
__all__ = [
    'ConfigurationError',
    'VectorStoreError',
    'AIError',
    'load_env_config',
    'initialize_vector_store',
    'validate_text_input',
    'index_document',
    'query_vector_store',
    'validate_workflow_json',
    'generate_workflow_from_ai',
    'generate_workflow_from_ai_with_goal',
    'generate_workflow_from_template',
    'execute_task_safe',
    'save_workflow_history',
    'list_workflow_history',
    'save_output'
]
