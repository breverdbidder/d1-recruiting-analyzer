"""
Evaluation System for ForecastEngines
Implements framework Layer 6: System Evaluation Model
Version: 1.0.0
Date: January 9, 2026
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import json
import hashlib

class ForecastEngineMetric(BaseModel):
    """Metrics for a single ForecastEngine execution."""
    engine_name: str
    property_id: Optional[str] = None
    case_number: Optional[str] = None
    score: float  # 0-100
    confidence: float  # 0-1
    execution_time: float  # seconds
    tokens_used: int = 0
    cost: float = 0.0  # USD
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    inputs_hash: str = ""
    outputs: Dict[str, Any] = Field(default_factory=dict)
    llm_tier: Optional[str] = None

class AggregateMetrics(BaseModel):
    """Aggregate metrics across executions."""
    engine_name: str
    total_executions: int
    avg_score: float
    avg_confidence: float
    avg_execution_time: float
    total_cost: float
    success_rate: float  # score >= 75
    period_start: datetime
    period_end: datetime

class PerformanceIssue(BaseModel):
    """Identified performance issue."""
    engine_name: str
    issue_type: str  # "low_score", "low_confidence", "slow_execution", "high_cost"
    current_value: float
    target_value: float
    severity: str  # "low", "medium", "high", "critical"
    recommendation: str

class ForecastEngineEvaluator:
    """Evaluates ForecastEngine performance and generates recommendations."""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self._metrics_cache: List[ForecastEngineMetric] = []
        self._cache_max_size = 1000
    
    async def record_metric(self, metric: ForecastEngineMetric):
        """Record a ForecastEngine execution metric."""
        # Generate inputs hash if not provided
        if not metric.inputs_hash and metric.outputs:
            metric.inputs_hash = self._hash_data(metric.outputs.get("inputs", {}))
        
        # Insert to Supabase
        try:
            self.supabase.table("forecast_engine_metrics").insert({
                "engine_name": metric.engine_name,
                "property_id": metric.property_id,
                "case_number": metric.case_number,
                "score": metric.score,
                "confidence": metric.confidence,
                "execution_time": metric.execution_time,
                "tokens_used": metric.tokens_used,
                "cost": metric.cost,
                "timestamp": metric.timestamp.isoformat(),
                "inputs_hash": metric.inputs_hash,
                "outputs": json.dumps(metric.outputs),
                "llm_tier": metric.llm_tier
            }).execute()
        except Exception as e:
            print(f"Warning: Failed to record metric to Supabase: {e}")
        
        # Add to cache
        self._metrics_cache.append(metric)
        
        # Trim cache if too large
        if len(self._metrics_cache) > self._cache_max_size:
            self._metrics_cache = self._metrics_cache[-self._cache_max_size:]
    
    async def get_aggregate_metrics(
        self,
        engine_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_executions: int = 5
    ) -> Dict[str, AggregateMetrics]:
        """Get aggregate metrics for engines."""
        
        query = self.supabase.table("forecast_engine_metrics").select("*")
        
        if engine_name:
            query = query.eq("engine_name", engine_name)
        
        if start_date:
            query = query.gte("timestamp", start_date.isoformat())
        
        if end_date:
            query = query.lte("timestamp", end_date.isoformat())
        
        try:
            response = query.execute()
        except Exception as e:
            print(f"Error querying metrics: {e}")
            return {}
        
        # Aggregate by engine
        engines: Dict[str, List[Dict]] = {}
        for row in response.data:
            name = row["engine_name"]
            if name not in engines:
                engines[name] = []
            engines[name].append(row)
        
        # Compute aggregates
        aggregates = {}
        for name, metrics in engines.items():
            if len(metrics) < min_executions:
                continue  # Skip engines with too few executions
            
            aggregates[name] = AggregateMetrics(
                engine_name=name,
                total_executions=len(metrics),
                avg_score=sum(m["score"] for m in metrics) / len(metrics),
                avg_confidence=sum(m["confidence"] for m in metrics) / len(metrics),
                avg_execution_time=sum(m["execution_time"] for m in metrics) / len(metrics),
                total_cost=sum(m["cost"] for m in metrics),
                success_rate=len([m for m in metrics if m["score"] >= 75]) / len(metrics),
                period_start=min(self._parse_datetime(m["timestamp"]) for m in metrics),
                period_end=max(self._parse_datetime(m["timestamp"]) for m in metrics)
            )
        
        return aggregates
    
    async def identify_issues(
        self,
        score_threshold: float = 70.0,
        confidence_threshold: float = 0.75,
        execution_time_threshold: float = 5.0,
        cost_threshold: float = 0.01
    ) -> List[PerformanceIssue]:
        """Identify performance issues across all engines."""
        aggregates = await self.get_aggregate_metrics()
        issues = []
        
        for name, metrics in aggregates.items():
            # Low score
            if metrics.avg_score < score_threshold:
                severity = self._calculate_severity(
                    metrics.avg_score, score_threshold, lower_is_worse=True
                )
                issues.append(PerformanceIssue(
                    engine_name=name,
                    issue_type="low_score",
                    current_value=metrics.avg_score,
                    target_value=85.0,
                    severity=severity,
                    recommendation="Review prompt engineering and input quality. Consider using higher LLM tier."
                ))
            
            # Low confidence
            if metrics.avg_confidence < confidence_threshold:
                severity = self._calculate_severity(
                    metrics.avg_confidence, confidence_threshold, lower_is_worse=True
                )
                issues.append(PerformanceIssue(
                    engine_name=name,
                    issue_type="low_confidence",
                    current_value=metrics.avg_confidence,
                    target_value=0.85,
                    severity=severity,
                    recommendation="Add more training data, adjust model temperature, or provide clearer instructions."
                ))
            
            # Slow execution
            if metrics.avg_execution_time > execution_time_threshold:
                severity = self._calculate_severity(
                    metrics.avg_execution_time, execution_time_threshold, lower_is_worse=False
                )
                issues.append(PerformanceIssue(
                    engine_name=name,
                    issue_type="slow_execution",
                    current_value=metrics.avg_execution_time,
                    target_value=3.0,
                    severity=severity,
                    recommendation="Optimize prompt length, reduce input size, or switch to faster LLM tier."
                ))
            
            # High cost
            if metrics.total_cost / metrics.total_executions > cost_threshold:
                avg_cost = metrics.total_cost / metrics.total_executions
                severity = self._calculate_severity(
                    avg_cost, cost_threshold, lower_is_worse=False
                )
                issues.append(PerformanceIssue(
                    engine_name=name,
                    issue_type="high_cost",
                    current_value=avg_cost,
                    target_value=cost_threshold * 0.5,
                    severity=severity,
                    recommendation="Switch to cheaper LLM tier or optimize token usage."
                ))
        
        return sorted(issues, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}[x.severity])
    
    async def generate_optimization_report(
        self,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive optimization report."""
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        aggregates = await self.get_aggregate_metrics(start_date=start_date)
        issues = await self.identify_issues()
        
        # Calculate overall statistics
        if aggregates:
            total_executions = sum(m.total_executions for m in aggregates.values())
            total_cost = sum(m.total_cost for m in aggregates.values())
            avg_success_rate = sum(m.success_rate for m in aggregates.values()) / len(aggregates)
            avg_score = sum(m.avg_score for m in aggregates.values()) / len(aggregates)
        else:
            total_executions = total_cost = avg_success_rate = avg_score = 0
        
        # Top performers
        top_performers = sorted(
            aggregates.values(),
            key=lambda m: (m.avg_score, m.avg_confidence),
            reverse=True
        )[:3]
        
        # Bottom performers
        bottom_performers = sorted(
            aggregates.values(),
            key=lambda m: (m.avg_score, m.avg_confidence)
        )[:3]
        
        return {
            "report_date": datetime.utcnow().isoformat(),
            "period_days": period_days,
            "summary": {
                "total_engines": len(aggregates),
                "total_executions": total_executions,
                "total_cost": round(total_cost, 4),
                "avg_success_rate": round(avg_success_rate, 3),
                "avg_score": round(avg_score, 2),
                "issues_found": len(issues)
            },
            "top_performers": [
                {
                    "engine": m.engine_name,
                    "avg_score": round(m.avg_score, 2),
                    "avg_confidence": round(m.avg_confidence, 3),
                    "executions": m.total_executions
                }
                for m in top_performers
            ],
            "bottom_performers": [
                {
                    "engine": m.engine_name,
                    "avg_score": round(m.avg_score, 2),
                    "avg_confidence": round(m.avg_confidence, 3),
                    "executions": m.total_executions
                }
                for m in bottom_performers
            ],
            "issues": [
                {
                    "engine": issue.engine_name,
                    "type": issue.issue_type,
                    "severity": issue.severity,
                    "current": round(issue.current_value, 3),
                    "target": round(issue.target_value, 3),
                    "recommendation": issue.recommendation
                }
                for issue in issues
            ],
            "recommendations": self._generate_system_recommendations(aggregates, issues)
        }
    
    def _generate_system_recommendations(
        self,
        aggregates: Dict[str, AggregateMetrics],
        issues: List[PerformanceIssue]
    ) -> List[str]:
        """Generate system-level recommendations."""
        recommendations = []
        
        if not aggregates:
            return ["No data available yet. Start recording metrics."]
        
        # Cost optimization
        total_cost = sum(m.total_cost for m in aggregates.values())
        if total_cost > 5.0:
            recommendations.append(
                f"High monthly cost (${total_cost:.2f}). Review LLM tier usage in Smart Router."
            )
        
        # Performance issues
        critical_issues = [i for i in issues if i.severity == "critical"]
        if critical_issues:
            recommendations.append(
                f"Found {len(critical_issues)} critical issues. Address these immediately."
            )
        
        # Success rate
        avg_success = sum(m.success_rate for m in aggregates.values()) / len(aggregates)
        if avg_success < 0.8:
            recommendations.append(
                f"Overall success rate ({avg_success:.1%}) below target. Review prompt quality."
            )
        
        # Execution time
        slow_engines = [
            m.engine_name for m in aggregates.values()
            if m.avg_execution_time > 5.0
        ]
        if slow_engines:
            recommendations.append(
                f"Slow execution detected: {', '.join(slow_engines)}. Optimize prompts."
            )
        
        return recommendations if recommendations else ["System performing well. Continue monitoring."]
    
    def _calculate_severity(
        self,
        current: float,
        threshold: float,
        lower_is_worse: bool
    ) -> str:
        """Calculate severity based on deviation from threshold."""
        if lower_is_worse:
            deviation = (threshold - current) / threshold
        else:
            deviation = (current - threshold) / threshold
        
        if deviation < 0:
            return "low"
        elif deviation < 0.2:
            return "medium"
        elif deviation < 0.4:
            return "high"
        else:
            return "critical"
    
    def _hash_data(self, data: Dict[str, Any]) -> str:
        """Generate hash of data for deduplication."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _parse_datetime(self, timestamp_str: str) -> datetime:
        """Parse datetime from ISO format string."""
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    
    async def get_engine_trend(
        self,
        engine_name: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get performance trend for a specific engine."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.supabase.table("forecast_engine_metrics").select("*").eq(
            "engine_name", engine_name
        ).gte("timestamp", start_date.isoformat()).order("timestamp")
        
        try:
            response = query.execute()
            data = response.data
        except Exception as e:
            print(f"Error getting engine trend: {e}")
            return {}
        
        if not data:
            return {"error": "No data found for this engine"}
        
        # Calculate daily averages
        daily_data = {}
        for row in data:
            date = row["timestamp"][:10]  # Get date part
            if date not in daily_data:
                daily_data[date] = {"scores": [], "confidences": [], "times": []}
            
            daily_data[date]["scores"].append(row["score"])
            daily_data[date]["confidences"].append(row["confidence"])
            daily_data[date]["times"].append(row["execution_time"])
        
        trend = {
            "engine_name": engine_name,
            "period_days": days,
            "daily_averages": [
                {
                    "date": date,
                    "avg_score": round(sum(d["scores"]) / len(d["scores"]), 2),
                    "avg_confidence": round(sum(d["confidences"]) / len(d["confidences"]), 3),
                    "avg_time": round(sum(d["times"]) / len(d["times"]), 3),
                    "executions": len(d["scores"])
                }
                for date, d in sorted(daily_data.items())
            ]
        }
        
        return trend
