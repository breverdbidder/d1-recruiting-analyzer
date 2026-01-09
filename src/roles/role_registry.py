"""
Role Registry for BidDeed.AI Agents
Implements framework Layer 4: Modular Roles Architecture
Version: 1.0.0
Date: January 9, 2026
"""

from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class AgentRole(str, Enum):
    """Agent roles in BidDeed.AI ecosystem."""
    DISCOVERY = "discovery"
    ENRICHMENT = "enrichment"
    TITLE_ANALYSIS = "title_analysis"
    RISK_SCORING = "risk_scoring"
    BID_CALCULATION = "bid_calculation"
    REPORT_GENERATION = "report_generation"
    DISPOSITION = "disposition"
    ORCHESTRATION = "orchestration"

class RoleCapability(BaseModel):
    """Capability that a role provides."""
    name: str
    description: str
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    tools_required: List[str] = Field(default_factory=list)
    estimated_tokens: int = 0
    estimated_cost: float = 0.0

class AgentRoleDefinition(BaseModel):
    """Complete definition of an agent role."""
    role: AgentRole
    display_name: str
    description: str
    capabilities: List[RoleCapability] = Field(default_factory=list)
    dependencies: List[AgentRole] = Field(default_factory=list)
    llm_tier: str = "BALANCED"  # FREE, ULTRA_CHEAP, CHEAP, BALANCED, SMART, QUALITY
    context_window: int = 16384
    temperature: float = 0.3
    system_prompt_template: str = ""
    forecast_engines: List[str] = Field(default_factory=list)

# PRODUCTION ROLE DEFINITIONS
BIDDEED_ROLES: Dict[AgentRole, AgentRoleDefinition] = {
    AgentRole.DISCOVERY: AgentRoleDefinition(
        role=AgentRole.DISCOVERY,
        display_name="Discovery Agent",
        description="Scrapes foreclosure auction listings from RealForeclose",
        capabilities=[
            RoleCapability(
                name="scrape_realforeclose",
                description="Extract auction data from RealForeclose portal",
                inputs=["date_range", "county"],
                outputs=["case_numbers", "addresses", "opening_bids"],
                tools_required=["playwright", "beca_scraper_v2"],
                estimated_tokens=500,
                estimated_cost=0.0
            )
        ],
        dependencies=[],
        llm_tier="FREE",
        context_window=8192,
        temperature=0.1,
        system_prompt_template="You are a foreclosure auction discovery agent. Extract auction data accurately from RealForeclose.",
        forecast_engines=[]
    ),
    
    AgentRole.ENRICHMENT: AgentRoleDefinition(
        role=AgentRole.ENRICHMENT,
        display_name="Data Enrichment Agent",
        description="Enriches property data from BCPAO, Census, and other sources",
        capabilities=[
            RoleCapability(
                name="enrich_property_data",
                description="Gather ARV, repairs, demographics, comparables",
                inputs=["parcel_id", "address"],
                outputs=["arv", "repairs", "demographics", "comparables"],
                tools_required=["bcpao_api", "census_api", "zillow_api"],
                estimated_tokens=1200,
                estimated_cost=0.0003
            )
        ],
        dependencies=[AgentRole.DISCOVERY],
        llm_tier="ULTRA_CHEAP",
        context_window=16384,
        temperature=0.2,
        system_prompt_template="You are a data enrichment specialist. Gather comprehensive property data from multiple sources.",
        forecast_engines=["DemographicEngine", "ComparableEngine", "RepairEstimateEngine"]
    ),
    
    AgentRole.TITLE_ANALYSIS: AgentRoleDefinition(
        role=AgentRole.TITLE_ANALYSIS,
        display_name="Title Intelligence Agent",
        description="Analyzes lien priority and title risks",
        capabilities=[
            RoleCapability(
                name="analyze_lien_priority",
                description="Determine lien priority order and survival risks",
                inputs=["case_number", "liens_list"],
                outputs=["priority_order", "risk_score", "red_flags"],
                tools_required=["acclaimweb_api", "realtdm_api"],
                estimated_tokens=2500,
                estimated_cost=0.0007
            )
        ],
        dependencies=[AgentRole.DISCOVERY, AgentRole.ENRICHMENT],
        llm_tier="ULTRA_CHEAP",
        context_window=32768,
        temperature=0.2,
        system_prompt_template="You are a title analysis expert specializing in foreclosure liens. Detect HOA risks and lien survival scenarios.",
        forecast_engines=["LienPriorityEngine", "TitleRiskEngine"]
    ),
    
    AgentRole.RISK_SCORING: AgentRoleDefinition(
        role=AgentRole.RISK_SCORING,
        display_name="Risk Scoring Agent",
        description="Evaluates overall investment risk using ForecastEngines",
        capabilities=[
            RoleCapability(
                name="score_property_risk",
                description="Calculate comprehensive risk score (0-100)",
                inputs=["property_data", "liens", "market_data"],
                outputs=["risk_score", "confidence", "risk_factors"],
                tools_required=["forecast_engines"],
                estimated_tokens=2000,
                estimated_cost=0.0006
            )
        ],
        dependencies=[AgentRole.ENRICHMENT, AgentRole.TITLE_ANALYSIS],
        llm_tier="ULTRA_CHEAP",
        context_window=32768,
        temperature=0.3,
        system_prompt_template="You are a risk assessment expert. Evaluate all risk factors and provide actionable scores.",
        forecast_engines=["TitleRiskEngine", "MarketTimingEngine", "ExitStrategyEngine"]
    ),
    
    AgentRole.BID_CALCULATION: AgentRoleDefinition(
        role=AgentRole.BID_CALCULATION,
        display_name="Bid Strategy Agent",
        description="Calculates maximum bid using formula and market data",
        capabilities=[
            RoleCapability(
                name="calculate_max_bid",
                description="Compute max bid: (ARV×70%)-Repairs-$10K-MIN($25K,15%ARV)",
                inputs=["arv", "repairs", "liens", "market_data"],
                outputs=["max_bid", "confidence", "bid_recommendation"],
                tools_required=["bcpao_api", "zillow_api"],
                estimated_tokens=1500,
                estimated_cost=0.0004
            )
        ],
        dependencies=[AgentRole.ENRICHMENT, AgentRole.TITLE_ANALYSIS, AgentRole.RISK_SCORING],
        llm_tier="ULTRA_CHEAP",
        context_window=16384,
        temperature=0.3,
        system_prompt_template="You are a bid calculation expert. Apply the max bid formula and provide clear recommendations.",
        forecast_engines=["BidStrategyEngine", "CashFlowEngine"]
    ),
    
    AgentRole.REPORT_GENERATION: AgentRoleDefinition(
        role=AgentRole.REPORT_GENERATION,
        display_name="Report Generation Agent",
        description="Generates comprehensive DOCX reports with recommendations",
        capabilities=[
            RoleCapability(
                name="generate_property_report",
                description="Create one-page DOCX report with BidDeed.AI branding",
                inputs=["property_data", "analysis_results", "recommendation"],
                outputs=["docx_file", "report_url"],
                tools_required=["docx_skill", "bcpao_photos"],
                estimated_tokens=1000,
                estimated_cost=0.0003
            )
        ],
        dependencies=[AgentRole.BID_CALCULATION, AgentRole.RISK_SCORING],
        llm_tier="ULTRA_CHEAP",
        context_window=16384,
        temperature=0.4,
        system_prompt_template="You are a report generation specialist. Create clear, actionable reports for investors.",
        forecast_engines=[]
    ),
    
    AgentRole.DISPOSITION: AgentRoleDefinition(
        role=AgentRole.DISPOSITION,
        display_name="Disposition Tracking Agent",
        description="Tracks post-auction outcomes and updates database",
        capabilities=[
            RoleCapability(
                name="track_disposition",
                description="Record auction results and update metrics",
                inputs=["case_number", "auction_result", "final_bid"],
                outputs=["disposition_status", "roi_actual"],
                tools_required=["supabase_mcp"],
                estimated_tokens=800,
                estimated_cost=0.0002
            )
        ],
        dependencies=[AgentRole.BID_CALCULATION],
        llm_tier="ULTRA_CHEAP",
        context_window=8192,
        temperature=0.2,
        system_prompt_template="You are a disposition tracking specialist. Accurately record outcomes for learning.",
        forecast_engines=["DispositionEngine"]
    ),
    
    AgentRole.ORCHESTRATION: AgentRoleDefinition(
        role=AgentRole.ORCHESTRATION,
        display_name="Workflow Orchestrator",
        description="Coordinates all agents and manages state transitions",
        capabilities=[
            RoleCapability(
                name="orchestrate_pipeline",
                description="Execute 12-stage pipeline with error recovery",
                inputs=["auction_date", "properties"],
                outputs=["pipeline_results", "metrics", "recommendations"],
                tools_required=["langgraph", "supabase_mcp", "smart_router"],
                estimated_tokens=5000,
                estimated_cost=0.0021
            )
        ],
        dependencies=[],  # No dependencies, orchestrates others
        llm_tier="BALANCED",
        context_window=1000000,
        temperature=0.4,
        system_prompt_template="You are the BidDeed.AI orchestrator. Coordinate all agents efficiently and handle failures gracefully.",
        forecast_engines=["WorkflowOptimizationEngine"]
    )
}

class RoleRegistry:
    """Manages agent roles and execution order."""
    
    def __init__(self):
        self.roles = BIDDEED_ROLES
        self._execution_order: Optional[List[AgentRole]] = None
    
    def get_role(self, role: AgentRole) -> AgentRoleDefinition:
        """Get role definition."""
        return self.roles[role]
    
    def get_execution_order(self) -> List[AgentRole]:
        """Get topologically sorted execution order based on dependencies."""
        if self._execution_order:
            return self._execution_order
        
        visited = set()
        order = []
        
        def visit(role: AgentRole):
            if role in visited:
                return
            visited.add(role)
            
            role_def = self.roles[role]
            for dep in role_def.dependencies:
                visit(dep)
            
            order.append(role)
        
        for role in self.roles:
            visit(role)
        
        self._execution_order = order
        return order
    
    def estimate_pipeline_cost(self) -> Dict[str, float]:
        """Estimate cost for full pipeline execution."""
        total_tokens = sum(
            sum(cap.estimated_tokens for cap in role_def.capabilities)
            for role_def in self.roles.values()
        )
        total_cost = sum(
            sum(cap.estimated_cost for cap in role_def.capabilities)
            for role_def in self.roles.values()
        )
        
        return {
            "total_tokens": total_tokens,
            "total_cost_per_property": total_cost,
            "execution_order": [r.value for r in self.get_execution_order()]
        }
    
    def get_role_by_forecast_engine(self, engine_name: str) -> List[AgentRole]:
        """Find roles that use a specific ForecastEngine."""
        return [
            role for role, role_def in self.roles.items()
            if engine_name in role_def.forecast_engines
        ]
    
    def get_dependencies_for_role(self, role: AgentRole) -> List[AgentRole]:
        """Get all dependencies for a role."""
        role_def = self.get_role(role)
        return role_def.dependencies
    
    def list_all_roles(self) -> List[AgentRoleDefinition]:
        """List all role definitions."""
        return list(self.roles.values())
    
    def get_role_by_name(self, name: str) -> Optional[AgentRoleDefinition]:
        """Get role by display name or role value."""
        for role_def in self.roles.values():
            if role_def.display_name == name or role_def.role.value == name:
                return role_def
        return None

# Global registry instance
_registry = RoleRegistry()

def get_registry() -> RoleRegistry:
    """Get the global role registry instance."""
    return _registry
