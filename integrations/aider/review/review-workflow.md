# Review Workflow - Detailed Implementation

## Review Pipeline Architecture

The review workflow follows a structured pipeline with multiple stages:

```
Changes Detected → Parse Code → Apply Rules → Generate Findings → Create Report
```

### Pipeline Components

```python
class ReviewPipeline:
    """Orchestrate review pipeline."""
    
    stages = [
        ChangeDetectionStage(),
        CodeParsingStage(),
        RuleApplicationStage(),
        FindingAggregationStage(),
        ReportGenerationStage(),
    ]
    
    def execute(self, input: ReviewInput) -> ReviewOutput:
        """Run through all pipeline stages."""
        data = input
        for stage in self.stages:
            data = stage.process(data)
        return data
```

## Stage Details

### 1. Change Detection

```python
class ChangeDetectionStage:
    """Detect and collect changes for review."""
    
    def process(self, input: ReviewInput) -> ChangeData:
        """
        Detect changes based on scope.
        
        Scopes:
        - 'changed': All uncommitted changes
        - 'staged': Only staged changes
        - 'all': Entire codebase
        - 'branch': Compare branch to base
        """
        
    def get_changed_files(self, scope: str) -> List[ChangedFile]:
        """Get list of changed files."""
        if scope == "changed":
            return self.git.status().unstaged + self.git.status().staged
        elif scope == "staged":
            return self.git.status().staged
        elif scope == "all":
            return self.git.list_files()
        elif scope.startswith("branch:"):
            _, branch = scope.split(":", 1)
            return self.git.diff(branch, "HEAD").files
            
    def read_file_content(self, file: str) -> str:
        """Read file content for analysis."""
```

### 2. Code Parsing

```python
class CodeParsingStage:
    """Parse code into structured format."""
    
    def process(self, data: ChangeData) -> ParsedData:
        """Parse code files."""
        parsed_files = []
        
        for file in data.changed_files:
            content = file.content
            language = self.detect_language(file.path)
            
            if language == "python":
                ast = self.parse_python(content)
            elif language == "javascript":
                ast = self.parse_javascript(content)
            # ... other languages
            
            parsed_files.append(ParsedFile(
                path=file.path,
                language=language,
                ast=ast,
                content=content
            ))
        
        return ParsedData(files=parsed_files)
    
    def detect_language(self, path: str) -> str:
        """Detect language from file extension."""
        ext = Path(path).suffix.lower()
        return {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
        }.get(ext, 'unknown')
    
    def parse_python(self, content: str) -> ast.AST:
        """Parse Python code."""
        import ast
        return ast.parse(content)
    
    def parse_javascript(self, content: str) -> dict:
        """Parse JavaScript using tree-sitter or similar."""
        # Use appropriate parser
        pass
```

### 3. Rule Application

```python
class RuleApplicationStage:
    """Apply review rules to parsed code."""
    
    def __init__(self):
        self.rules = self.load_rules()
        
    def process(self, data: ParsedData) -> FindingData:
        """Apply all rules to parsed files."""
        all_findings = []
        
        for file in data.files:
            file_findings = []
            
            for rule in self.rules:
                if rule.applies_to(file.language):
                    findings = rule.check(file)
                    file_findings.extend(findings)
            
            all_findings.extend(file_findings)
        
        return FindingData(findings=all_findings)
    
    def load_rules(self) -> List[ReviewRule]:
        """Load enabled rules."""
        rules = []
        
        # Load built-in rules
        rules.extend(self.load_builtin_rules())
        
        # Load custom rules
        rules.extend(self.load_custom_rules())
        
        return rules
```

### 4. Finding Aggregation

```python
class FindingAggregationStage:
    """Aggregate and prioritize findings."""
    
    def process(self, data: FindingData) -> AggregatedData:
        """Aggregate findings."""
        # Group by severity
        by_severity = self.group_by_severity(data.findings)
        
        # Group by file
        by_file = self.group_by_file(data.findings)
        
        # Calculate statistics
        stats = self.calculate_stats(data.findings)
        
        # Deduplicate findings
        unique_findings = self.deduplicate(data.findings)
        
        # Sort by priority
        sorted_findings = self.sort_by_priority(unique_findings)
        
        return AggregatedData(
            findings=sorted_findings,
            by_severity=by_severity,
            by_file=by_file,
            stats=stats
        )
    
    def sort_by_priority(
        self,
        findings: List[Finding]
    ) -> List[Finding]:
        """Sort findings by priority."""
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.WARNING: 1,
            Severity.INFO: 2,
        }
        
        return sorted(
            findings,
            key=lambda f: (
                severity_order[f.severity],
                f.file,
                f.line
            )
        )
```

### 5. Report Generation

```python
class ReportGenerationStage:
    """Generate review report."""
    
    def process(self, data: AggregatedData) -> ReviewOutput:
        """Generate final report."""
        return ReviewOutput(
            findings=data.findings,
            stats=data.stats,
            report=self.generate_text_report(data),
            json=self.generate_json_report(data),
            html=self.generate_html_report(data)
        )
    
    def generate_text_report(self, data: AggregatedData) -> str:
        """Generate text report."""
        lines = []
        lines.append("=== Code Review Report ===\n")
        
        # Summary
        lines.append(f"Files Reviewed: {data.stats.files_reviewed}")
        lines.append(f"Total Findings: {len(data.findings)}\n")
        
        # By severity
        for severity in [Severity.CRITICAL, Severity.WARNING, Severity.INFO]:
            count = len(data.by_severity.get(severity, []))
            lines.append(f"{severity.value}: {count}")
        
        lines.append("")
        
        # Findings by severity
        for severity in [Severity.CRITICAL, Severity.WARNING, Severity.INFO]:
            findings = data.by_severity.get(severity, [])
            if findings:
                lines.append(f"\n{severity.value} Issues:")
                for finding in findings:
                    lines.append(f"  {finding.file}:{finding.line}")
                    lines.append(f"    {finding.message}")
                    if finding.suggestion:
                        lines.append(f"    Suggestion: {finding.suggestion}")
        
        return "\n".join(lines)
```

## Rule Implementation

### Base Rule Class

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

class ReviewRule(ABC):
    """Base class for review rules."""
    
    name: str
    description: str
    severity: Severity
    languages: List[str] = ['*']  # Apply to all languages by default
    auto_fixable: bool = False
    
    @abstractmethod
    def check(self, file: ParsedFile) -> List[Finding]:
        """Check file for issues."""
        pass
    
    def applies_to(self, language: str) -> bool:
        """Check if rule applies to language."""
        return '*' in self.languages or language in self.languages
    
