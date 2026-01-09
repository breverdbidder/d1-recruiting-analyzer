"""
Command System for Skill Mill
Implements framework Layer 3: Command as Everything
Version: 1.0.0
Date: January 9, 2026
"""

from typing import Optional, Dict, Any, List, Callable
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import json
import re

class CommandType(str, Enum):
    """Type of skill command."""
    SCRAPE = "scrape"
    ANALYZE = "analyze"
    GENERATE = "generate"
    VALIDATE = "validate"
    TRANSFORM = "transform"
    QUERY = "query"

class CommandStatus(str, Enum):
    """Execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class CommandParameter(BaseModel):
    """Parameter definition with validation rules."""
    name: str
    type: str  # "str", "int", "float", "bool", "dict", "list"
    required: bool = True
    description: str = ""
    default: Optional[Any] = None
    choices: Optional[List[Any]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None  # Regex for string validation
    min_length: Optional[int] = None
    max_length: Optional[int] = None

class SkillCommand(BaseModel):
    """Command definition for a skill."""
    name: str
    type: CommandType
    description: str
    parameters: List[CommandParameter] = Field(default_factory=list)
    cost_estimate: float = 0.0  # USD
    estimated_duration: int = 0  # seconds
    requires_mcp: bool = False
    mcp_servers: List[str] = Field(default_factory=list)
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    
    def validate_parameters(self, params: Dict[str, Any]) -> Dict[str, str]:
        """Validate parameters against rules, return errors."""
        errors = {}
        
        for param_def in self.parameters:
            value = params.get(param_def.name)
            
            # Check required
            if param_def.required and value is None:
                errors[param_def.name] = "Required parameter missing"
                continue
            
            if value is None:
                continue
            
            # Type validation
            expected_type = {
                "str": str, 
                "int": int, 
                "float": float,
                "bool": bool, 
                "dict": dict, 
                "list": list
            }.get(param_def.type)
            
            if expected_type and not isinstance(value, expected_type):
                errors[param_def.name] = f"Expected {param_def.type}, got {type(value).__name__}"
                continue
            
            # Choices validation
            if param_def.choices and value not in param_def.choices:
                errors[param_def.name] = f"Must be one of {param_def.choices}"
            
            # Numeric range validation
            if param_def.type in ["int", "float"]:
                if param_def.min_value is not None and value < param_def.min_value:
                    errors[param_def.name] = f"Must be >= {param_def.min_value}"
                
                if param_def.max_value is not None and value > param_def.max_value:
                    errors[param_def.name] = f"Must be <= {param_def.max_value}"
            
            # String length validation
            if param_def.type == "str":
                if param_def.min_length is not None and len(value) < param_def.min_length:
                    errors[param_def.name] = f"Must be at least {param_def.min_length} characters"
                
                if param_def.max_length is not None and len(value) > param_def.max_length:
                    errors[param_def.name] = f"Must be at most {param_def.max_length} characters"
                
                # Pattern validation
                if param_def.pattern:
                    if not re.match(param_def.pattern, value):
                        errors[param_def.name] = f"Must match pattern: {param_def.pattern}"
        
        return errors

class CommandResult(BaseModel):
    """Result of command execution."""
    command_name: str
    status: CommandStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CommandRegistry:
    """Registry for skill commands."""
    
    def __init__(self):
        self._commands: Dict[str, SkillCommand] = {}
        self._handlers: Dict[str, Callable] = {}
        self._execution_log: List[CommandResult] = []
    
    def register(self, command: SkillCommand, handler: Callable):
        """Register command with handler function."""
        if command.name in self._commands:
            raise ValueError(f"Command already registered: {command.name}")
        
        self._commands[command.name] = command
        self._handlers[command.name] = handler
    
    def get_command(self, name: str) -> Optional[SkillCommand]:
        """Get command definition by name."""
        return self._commands.get(name)
    
    def execute(
        self, 
        command_name: str, 
        parameters: Dict[str, Any],
        log_execution: bool = True
    ) -> CommandResult:
        """Execute command with parameters."""
        start_time = datetime.utcnow()
        
        try:
            command = self.get_command(command_name)
            if not command:
                raise ValueError(f"Unknown command: {command_name}")
            
            # Validate parameters
            errors = command.validate_parameters(parameters)
            if errors:
                raise ValueError(f"Parameter validation failed: {errors}")
            
            # Execute handler
            handler = self._handlers[command_name]
            result = handler(**parameters)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            cmd_result = CommandResult(
                command_name=command_name,
                status=CommandStatus.COMPLETED,
                result=result,
                execution_time=execution_time,
                metadata={"parameters": parameters}
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            cmd_result = CommandResult(
                command_name=command_name,
                status=CommandStatus.FAILED,
                error=str(e),
                execution_time=execution_time,
                metadata={"parameters": parameters}
            )
        
        if log_execution:
            self._execution_log.append(cmd_result)
        
        return cmd_result
    
    def list_commands(self, command_type: Optional[CommandType] = None) -> List[SkillCommand]:
        """List all registered commands, optionally filtered by type."""
        commands = list(self._commands.values())
        
        if command_type:
            commands = [cmd for cmd in commands if cmd.type == command_type]
        
        return sorted(commands, key=lambda c: c.name)
    
    def get_execution_log(
        self, 
        command_name: Optional[str] = None,
        limit: int = 100
    ) -> List[CommandResult]:
        """Get execution log, optionally filtered by command name."""
        log = self._execution_log[-limit:]
        
        if command_name:
            log = [r for r in log if r.command_name == command_name]
        
        return log
    
    def get_command_stats(self, command_name: str) -> Dict[str, Any]:
        """Get execution statistics for a command."""
        executions = [r for r in self._execution_log if r.command_name == command_name]
        
        if not executions:
            return {"error": "No executions found"}
        
        successes = [e for e in executions if e.status == CommandStatus.COMPLETED]
        failures = [e for e in executions if e.status == CommandStatus.FAILED]
        
        return {
            "total_executions": len(executions),
            "successes": len(successes),
            "failures": len(failures),
            "success_rate": len(successes) / len(executions) if executions else 0,
            "avg_execution_time": sum(e.execution_time for e in executions) / len(executions),
            "last_execution": executions[-1].timestamp.isoformat()
        }
    
    def generate_documentation(self, format: str = "markdown") -> str:
        """Generate command documentation."""
        if format == "markdown":
            return self._generate_markdown_docs()
        elif format == "json":
            return json.dumps(
                [cmd.dict() for cmd in self.list_commands()],
                indent=2
            )
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_markdown_docs(self) -> str:
        """Generate markdown documentation."""
        docs = "# Skill Commands\n\n"
        docs += f"**Total Commands**: {len(self._commands)}  \n"
        docs += f"**Generated**: {datetime.utcnow().isoformat()}  \n\n"
        
        # Group by type
        by_type = {}
        for cmd in self.list_commands():
            if cmd.type not in by_type:
                by_type[cmd.type] = []
            by_type[cmd.type].append(cmd)
        
        for cmd_type, commands in sorted(by_type.items()):
            docs += f"## {cmd_type.value.upper()} Commands\n\n"
            
            for cmd in sorted(commands, key=lambda c: c.name):
                docs += f"### {cmd.name}\n\n"
                docs += f"**Description**: {cmd.description}  \n"
                docs += f"**Cost Estimate**: ${cmd.cost_estimate:.4f}  \n"
                docs += f"**Duration**: ~{cmd.estimated_duration}s  \n"
                
                if cmd.requires_mcp:
                    docs += f"**Requires MCP**: {', '.join(cmd.mcp_servers)}  \n"
                
                if cmd.parameters:
                    docs += "\n**Parameters**:\n\n"
                    for param in cmd.parameters:
                        req = "**required**" if param.required else "optional"
                        docs += f"- `{param.name}` ({param.type}, {req}): {param.description}\n"
                        
                        if param.default is not None:
                            docs += f"  - Default: `{param.default}`\n"
                        if param.choices:
                            docs += f"  - Choices: {param.choices}\n"
                        if param.pattern:
                            docs += f"  - Pattern: `{param.pattern}`\n"
                
                if cmd.examples:
                    docs += "\n**Examples**:\n\n"
                    for i, example in enumerate(cmd.examples, 1):
                        docs += f"{i}. {example.get('description', 'Example')}:\n"
                        docs += f"   ```python\n"
                        docs += f"   registry.execute(\"{cmd.name}\", {json.dumps(example.get('parameters', {}), indent=4)})\n"
                        docs += f"   ```\n\n"
                
                docs += "\n---\n\n"
        
        return docs

# Global registry instance
_registry = CommandRegistry()

def get_registry() -> CommandRegistry:
    """Get the global command registry instance."""
    return _registry

def register_command(command: SkillCommand, handler: Callable):
    """Convenience function to register a command."""
    _registry.register(command, handler)

def execute_command(command_name: str, **parameters) -> CommandResult:
    """Convenience function to execute a command."""
    return _registry.execute(command_name, parameters)
