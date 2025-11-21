"""
Sophia Prototype - Project Templates (Stage 3)
==============================================
Pre-built workflow templates for common project types.

Design Philosophy:
- Templates reduce AI unpredictability
- Provide consistent structure across similar projects
- Guide users toward best practices
- Reduce workflow generation time and cost

Templates can be used in two modes:
1. Direct application (skip AI workflow generation)
2. As guidance for AI (suggested task structure)
"""

from typing import Dict, List


# ============================================================================
# TEMPLATE DEFINITIONS
# ============================================================================

SOFTWARE_DEVELOPMENT_TEMPLATE = {
    "template_id": "software_dev_v1",
    "template_name": "Software Development Project",
    "description": "Comprehensive planning for software development projects",
    "workflow_name": "Software Development Planning Workflow",
    "tasks": [
        {
            "task_id": "1",
            "name": "requirements_analysis",
            "prompt": """Analyze the project specification and create a comprehensive requirements document.

Include:
- Functional requirements (what the system must do)
- Non-functional requirements (performance, security, scalability)
- User stories or use cases
- Acceptance criteria
- Technical constraints

Format the output as a structured requirements document.""",
            "output_format": "markdown"
        },
        {
            "task_id": "2",
            "name": "architecture_design",
            "prompt": """Based on the requirements and project specification, design the system architecture.

Include:
- High-level system architecture
- Technology stack recommendations
- Data models and database schema
- API design and interfaces
- Security architecture
- Deployment architecture

Format as a technical design document.""",
            "output_format": "markdown"
        },
        {
            "task_id": "3",
            "name": "work_breakdown_structure",
            "prompt": """Create a Work Breakdown Structure (WBS) for the software project.

Break down the project into:
- Major phases/modules
- Features and sub-features
- Development tasks
- Testing and QA tasks
- Deployment tasks
- Documentation tasks

Organize hierarchically with clear parent-child relationships.""",
            "output_format": "markdown"
        },
        {
            "task_id": "4",
            "name": "task_list_with_dependencies",
            "prompt": """Generate a detailed task list with dependencies and estimates.

For each task include:
- Task name and description
- Dependencies (which tasks must complete first)
- Estimated effort (hours or days)
- Assigned role/skill level
- Priority (Critical, High, Medium, Low)

Format as CSV with columns: TaskID, TaskName, Description, Dependencies, Effort, Role, Priority""",
            "output_format": "csv"
        },
        {
            "task_id": "5",
            "name": "sprint_planning",
            "prompt": """Organize tasks into sprint/iteration plan.

Create a sprint plan with:
- Sprint duration (typically 2 weeks)
- Sprint goals
- Tasks allocated to each sprint
- Capacity planning
- Risk mitigation per sprint

Consider team velocity and dependencies.""",
            "output_format": "markdown"
        },
        {
            "task_id": "6",
            "name": "resource_allocation",
            "prompt": """Create a resource allocation plan.

Include:
- Team composition (roles and count)
- Role responsibilities
- Skills required vs. available
- Training needs
- External resources or contractors
- Budget allocation by resource type

Format as CSV with columns: Role, Count, Skills, Responsibilities, Cost""",
            "output_format": "csv"
        },
        {
            "task_id": "7",
            "name": "risk_assessment",
            "prompt": """Conduct a comprehensive risk assessment.

Identify and analyze:
- Technical risks
- Resource risks
- Schedule risks
- Security risks
- Integration risks

For each risk include:
- Description
- Impact (High/Medium/Low)
- Probability (High/Medium/Low)
- Mitigation strategy
- Contingency plan

Format as a risk register.""",
            "output_format": "markdown"
        }
    ]
}


MARKETING_CAMPAIGN_TEMPLATE = {
    "template_id": "marketing_campaign_v1",
    "template_name": "Marketing Campaign",
    "description": "Strategic planning for marketing campaigns",
    "workflow_name": "Marketing Campaign Planning Workflow",
    "tasks": [
        {
            "task_id": "1",
            "name": "campaign_strategy",
            "prompt": """Develop a comprehensive marketing campaign strategy.

Include:
- Campaign objectives and KPIs
- Target audience definition
- Value proposition
- Key messaging
- Brand positioning
- Campaign timeline

Format as a strategic brief.""",
            "output_format": "markdown"
        },
        {
            "task_id": "2",
            "name": "channel_mix",
            "prompt": """Define the marketing channel mix and tactics.

For each channel include:
- Channel selection rationale
- Specific tactics (ads, content, events, etc.)
- Budget allocation
- Expected reach and engagement
- Success metrics

Channels to consider: Digital ads, Social media, Email, Content marketing, Events, PR, Partnerships

Format as CSV: Channel, Tactics, Budget, Reach, Metrics""",
            "output_format": "csv"
        },
        {
            "task_id": "3",
            "name": "content_calendar",
            "prompt": """Create a detailed content calendar.

Include:
- Content pieces (blogs, videos, social posts, emails)
- Publishing schedule
- Content themes/topics
- Distribution channels
- Content owner/creator
- Status tracking

Format as CSV: Date, ContentType, Topic, Channel, Owner, Status""",
            "output_format": "csv"
        },
        {
            "task_id": "4",
            "name": "budget_breakdown",
            "prompt": """Break down the campaign budget.

Include:
- Channel-specific budgets
- Creative production costs
- Technology/tools costs
- Personnel costs
- Contingency buffer

Calculate ROI projections based on expected outcomes.

Format as CSV: Category, SubCategory, Cost, Percentage""",
            "output_format": "csv"
        },
        {
            "task_id": "5",
            "name": "measurement_plan",
            "prompt": """Create a comprehensive measurement and analytics plan.

Define:
- KPIs for each channel and overall campaign
- Tracking mechanisms
- Reporting frequency
- Dashboard requirements
- A/B testing plan
- Attribution model

Include both leading and lagging indicators.""",
            "output_format": "markdown"
        }
    ]
}


RESEARCH_PROJECT_TEMPLATE = {
    "template_id": "research_project_v1",
    "template_name": "Research Project",
    "description": "Academic or business research project planning",
    "workflow_name": "Research Project Planning Workflow",
    "tasks": [
        {
            "task_id": "1",
            "name": "research_design",
            "prompt": """Design the research methodology and approach.

Include:
- Research questions and hypotheses
- Research methodology (qualitative, quantitative, mixed)
- Data collection methods
- Sampling strategy
- Data analysis approach
- Validity and reliability considerations

Format as a research design document.""",
            "output_format": "markdown"
        },
        {
            "task_id": "2",
            "name": "literature_review_plan",
            "prompt": """Create a literature review plan.

Define:
- Key topics and themes
- Search strategy and databases
- Inclusion/exclusion criteria
- Analysis framework
- Expected number of sources
- Timeline for completion

Organize by research themes.""",
            "output_format": "markdown"
        },
        {
            "task_id": "3",
            "name": "research_phases",
            "prompt": """Break down research into phases with deliverables.

Typical phases:
- Planning and design
- Literature review
- Data collection
- Data analysis
- Results interpretation
- Report writing
- Peer review and revision

For each phase include timeline, activities, and deliverables.

Format as CSV: Phase, StartDate, EndDate, Activities, Deliverables""",
            "output_format": "csv"
        },
        {
            "task_id": "4",
            "name": "resource_requirements",
            "prompt": """Identify resource requirements for the research.

Include:
- Personnel (researchers, assistants, statisticians)
- Equipment and facilities
- Software/tools
- Data sources and access
- Budget by category

Format as CSV: ResourceType, Description, Quantity, Cost""",
            "output_format": "csv"
        },
        {
            "task_id": "5",
            "name": "ethical_considerations",
            "prompt": """Document ethical considerations and compliance requirements.

Address:
- Human subjects protection (if applicable)
- Data privacy and confidentiality
- Informed consent procedures
- IRB/ethics committee requirements
- Data management and retention
- Conflict of interest disclosures

Format as an ethics checklist.""",
            "output_format": "markdown"
        }
    ]
}


EVENT_PLANNING_TEMPLATE = {
    "template_id": "event_planning_v1",
    "template_name": "Event Planning",
    "description": "Planning for conferences, meetings, or events",
    "workflow_name": "Event Planning Workflow",
    "tasks": [
        {
            "task_id": "1",
            "name": "event_concept",
            "prompt": """Define the event concept and objectives.

Include:
- Event purpose and goals
- Target audience
- Event format (in-person, virtual, hybrid)
- Theme and branding
- Success metrics
- High-level timeline

Format as an event brief.""",
            "output_format": "markdown"
        },
        {
            "task_id": "2",
            "name": "venue_logistics",
            "prompt": """Plan venue and logistics requirements.

Detail:
- Venue specifications (size, layout, AV equipment)
- Catering requirements
- Transportation and parking
- Accommodation for attendees
- Technology needs (WiFi, streaming, registration)
- Accessibility requirements

Format as a logistics checklist.""",
            "output_format": "markdown"
        },
        {
            "task_id": "3",
            "name": "task_timeline",
            "prompt": """Create a detailed task timeline leading up to the event.

Break down by time period (6 months out, 3 months, 1 month, 1 week, day-of):
- Key milestones
- Tasks with owners
- Deadlines
- Dependencies

Format as CSV: Deadline, Task, Owner, Status, Dependencies""",
            "output_format": "csv"
        },
        {
            "task_id": "4",
            "name": "budget_planning",
            "prompt": """Create comprehensive event budget.

Include:
- Venue and facility costs
- Catering and beverage
- Audio/visual and technology
- Marketing and promotion
- Speaker fees and travel
- Staff and contractors
- Contingency (10-15%)

Calculate per-attendee costs and break-even point.

Format as CSV: Category, Item, Quantity, UnitCost, TotalCost""",
            "output_format": "csv"
        },
        {
            "task_id": "5",
            "name": "marketing_promotion",
            "prompt": """Develop event marketing and promotion plan.

Include:
- Registration page and process
- Email campaigns timeline
- Social media strategy
- Partnership and sponsorship outreach
- PR and media relations
- Post-event follow-up

Define promotional phases: Save-the-date, Early bird, Regular, Last call.""",
            "output_format": "markdown"
        }
    ]
}


BUSINESS_STRATEGY_TEMPLATE = {
    "template_id": "business_strategy_v1",
    "template_name": "Business Strategy",
    "description": "Strategic business planning and analysis",
    "workflow_name": "Business Strategy Planning Workflow",
    "tasks": [
        {
            "task_id": "1",
            "name": "situation_analysis",
            "prompt": """Conduct comprehensive situation analysis.

Perform:
- SWOT analysis (Strengths, Weaknesses, Opportunities, Threats)
- Market analysis (size, growth, trends)
- Competitive landscape
- Customer analysis
- Internal capabilities assessment

Format as a structured analysis document.""",
            "output_format": "markdown"
        },
        {
            "task_id": "2",
            "name": "strategic_objectives",
            "prompt": """Define strategic objectives and goals.

Create:
- Vision and mission alignment
- 3-5 year strategic objectives
- SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)
- Key results and KPIs
- Success criteria

Prioritize objectives by impact and feasibility.""",
            "output_format": "markdown"
        },
        {
            "task_id": "3",
            "name": "strategic_initiatives",
            "prompt": """Identify strategic initiatives to achieve objectives.

For each initiative detail:
- Description and rationale
- Expected outcomes
- Resource requirements
- Timeline
- Risks and dependencies
- Success metrics

Format as CSV: Initiative, Description, Owner, Timeline, Budget, KPIs""",
            "output_format": "csv"
        },
        {
            "task_id": "4",
            "name": "implementation_roadmap",
            "prompt": """Create implementation roadmap.

Organize initiatives into phases:
- Quick wins (0-3 months)
- Short-term (3-12 months)
- Medium-term (1-2 years)
- Long-term (2-5 years)

Show dependencies and sequencing.
Identify resource allocation across phases.""",
            "output_format": "markdown"
        },
        {
            "task_id": "5",
            "name": "financial_projections",
            "prompt": """Develop financial projections and business case.

Include:
- Revenue projections
- Cost structure
- Investment requirements
- Cash flow analysis
- Break-even analysis
- ROI calculations
- Sensitivity analysis

Format as CSV: Year, Revenue, Costs, Profit, CumulativeCashFlow""",
            "output_format": "csv"
        }
    ]
}


# ============================================================================
# TEMPLATE REGISTRY
# ============================================================================

TEMPLATE_REGISTRY = {
    "software_development": SOFTWARE_DEVELOPMENT_TEMPLATE,
    "marketing_campaign": MARKETING_CAMPAIGN_TEMPLATE,
    "research_project": RESEARCH_PROJECT_TEMPLATE,
    "event_planning": EVENT_PLANNING_TEMPLATE,
    "business_strategy": BUSINESS_STRATEGY_TEMPLATE
}


def get_template(template_id: str) -> Dict:
    """
    Retrieve a template by ID.
    
    Args:
        template_id: Template identifier
    
    Returns:
        Template dictionary or None if not found
    """
    return TEMPLATE_REGISTRY.get(template_id)


def list_templates() -> List[Dict]:
    """
    List all available templates with metadata.
    
    Returns:
        List of template metadata dicts
    """
    return [
        {
            "id": key,
            "name": template["template_name"],
            "description": template["description"],
            "num_tasks": len(template["tasks"])
        }
        for key, template in TEMPLATE_REGISTRY.items()
    ]


def apply_template_to_context(template: Dict, project_context: str) -> Dict:
    """
    Enhance template prompts with project-specific context.
    
    This function takes a template and enriches each task prompt
    with the actual project specification context.
    
    Args:
        template: Template dictionary
        project_context: Project specification text
    
    Returns:
        Enhanced template ready for execution
    """
    enhanced_template = template.copy()
    enhanced_template["tasks"] = []
    
    for task in template["tasks"]:
        enhanced_task = task.copy()
        
        # Add context to prompt
        enhanced_task["prompt"] = f"""{task['prompt']}

PROJECT CONTEXT:
{project_context}

Base your analysis and recommendations specifically on the project context provided above."""
        
        enhanced_template["tasks"].append(enhanced_task)
    
    return enhanced_template


def suggest_template(project_text: str) -> str:
    """
    Suggest most appropriate template based on project text analysis.
    
    Uses simple keyword matching. In production, this could use
    semantic similarity or classification.
    
    Args:
        project_text: Project specification text
    
    Returns:
        Suggested template ID
    """
    text_lower = project_text.lower()
    
    # Simple keyword-based suggestion
    if any(word in text_lower for word in ['software', 'application', 'system', 'development', 'api', 'database']):
        return "software_development"
    
    elif any(word in text_lower for word in ['marketing', 'campaign', 'advertising', 'promotion', 'brand']):
        return "marketing_campaign"
    
    elif any(word in text_lower for word in ['research', 'study', 'analysis', 'hypothesis', 'methodology']):
        return "research_project"
    
    elif any(word in text_lower for word in ['event', 'conference', 'meeting', 'venue', 'attendee']):
        return "event_planning"
    
    elif any(word in text_lower for word in ['strategy', 'business', 'growth', 'market', 'competitive']):
        return "business_strategy"
    
    # Default to software development (most versatile)
    return "software_development"
