# Commit Workflow - Detailed Implementation

## Commit Pipeline Architecture

The commit workflow follows a structured pipeline:

```
Analyze Changes → Categorize → Generate Message → Validate → Commit → Post-process
```

### Pipeline Components

```python
class CommitPipeline:
    """Orchestrate commit pipeline."""
    
    stages = [
        ChangeAnalysisStage(),
        CategorizationStage(),
        MessageGenerationStage(),
        ValidationStage(),
        CommitExecutionStage(),
        PostCommitStage(),
    ]
    
    def execute(self, input: CommitInput) -> CommitOutput:
        """Execute pipeline stages."""
        data = input
        for stage in self.stages:
            data = stage.process(data)
        return data
```

## Stage Details

### 1. Change Analysis

```python
class ChangeAnalysisStage:
    """Analyze staged changes."""
    
    def process(self, input: CommitInput) -> AnalysisData:
        """Analyze changes."""
        # Get staged files
        staged = self.git.diff("--staged", "--name-only")
        
        # Analyze each file
        file_analyses = []
        for file in staged:
            analysis = self.analyze_file(file)
            file_analyses.append(analysis)
        
        # Aggregate analysis
        return AnalysisData(
            files=file_analyses,
            stats=self.calculate_stats(file_analyses),
            changes=self.extract_changes(file_analyses)
        )
    
    def analyze_file(self, file: str) -> FileAnalysis:
        """Analyze single file changes."""
        # Get diff
        diff = self.git.diff("--staged", file)
        
        # Parse hunks
        hunks = self.parse_hunks(diff)
        
        # Detect change types
        types = self.detect_change_types(hunks)
        
        # Extract metadata
        metadata = self.extract_metadata(file, hunks)
        
        return FileAnalysis(
            path=file,
            hunks=hunks,
            types=types,
            metadata=metadata
        )
    
    def detect_change_types(
        self,
        hunks: List[Hunk]
    ) -> List[ChangeType]:
        """Detect types of changes."""
        types = []
        
        for hunk in hunks:
            # New code addition
            if hunk.added > 0 and hunk.removed == 0:
                types.append(ChangeType.ADDITION)
            
            # Code deletion
            elif hunk.added == 0 and hunk.removed > 0:
                types.append(ChangeType.DELETION)
            
            # Code modification
            else:
                types.append(ChangeType.MODIFICATION)
        
        return types
```

### 2. Categorization

```python
class CategorizationStage:
    """Categorize changes."""
    
    def __init__(self):
        self.rules = self.load_rules()
        
    def process(self, data: AnalysisData) -> CategorizedData:
        """Categorize changes."""
        # Determine primary type
        commit_type = self.determine_type(data)
        
        # Determine scope
        scope = self.determine_scope(data)
        
        # Check for breaking changes
        breaking = self.check_breaking(data)
        
        # Find related issues
        issues = self.find_issues(data)
        
        return CategorizedData(
            type=commit_type,
            scope=scope,
            breaking=breaking,
            issues=issues,
            analysis=data
        )
    
    def determine_type(self, data: AnalysisData) -> str:
        """Determine commit type."""
        # Apply type detection rules
        for rule in self.rules:
            if rule.matches(data):
                return rule.type
        
        # Default categorization
        if self.is_new_feature(data):
            return "feat"
        elif self.is_bug_fix(data):
            return "fix"
        elif self.is_refactor(data):
            return "refactor"
        elif self.is_documentation(data):
            return "docs"
        elif self.is_test(data):
            return "test"
        else:
            return "chore"
    
    def determine_scope(self, data: AnalysisData) -> str:
        """Determine commit scope."""
        # Extract common path component
        paths = [f.path for f in data.files]
        
        # Find common directory
        common = self.find_common_path(paths)
        
        # Extract module name
        scope = self.extract_module(common)
        
        return scope
    
    def check_breaking(self, data: AnalysisData) -> bool:
        """Check for breaking changes."""
        # Look for breaking change indicators
        indicators = [
            "BREAKING CHANGE:",
            "!",
            "deprecated",
            "removed",
        ]
        
        for file in data.files:
            for hunk in file.hunks:
                for indicator in indicators:
                    if indicator in hunk.content:
                        return True
        
        # Check for API signature changes
        if self.has_signature_change(data):
            return True
        
        return False
```

### 3. Message Generation

```python
class MessageGenerationStage:
    """Generate commit message."""
    
    def process(self, data: CategorizedData) -> MessageData:
        """Generate message."""
        # Generate subject
        subject = self.generate_subject(data)
        
        # Generate body
        body = self.generate_body(data)
        
        # Generate footer
        footer = self.generate_footer(data)
        
        # Combine
        message = self.format_message(subject, body, footer)
        
        return MessageData(
            subject=subject,
            body=body,
            footer=footer,
            message=message
        )
    
    def generate_subject(self, data: CategorizedData) -> str:
        """Generate commit subject."""
        # Format: type(scope): description
        
        parts = []
        
        # Type
        parts.append(data.type)
        
        # Scope
        if data.scope:
            parts.append(f"({data.scope})")
        
        # Breaking indicator
        if data.breaking:
            parts.append("!")
        
        # Separator
        parts.append(": ")
        
        # Description
        description = self.generate_description(data)
        parts.append(description)
        
        return "".join(parts)
    
    def generate_description(
        self,
        data: CategorizedData
    ) -> str:
        """Generate short description."""
        # Use AI to summarize
        prompt = self.build_summary_prompt(data)
        summary = self.ai.generate(prompt)
        
        # Make imperative
        summary = self.to_imperative(summary)
        
        # Lowercase first letter
        summary = summary[0].lower() + summary[1:]
        
        # Remove trailing period
        summary = summary.rstrip(".")
        
        # Limit length
        if len(summary) > 72:
            summary = summary[:71] + "…"
        
        return summary
    
    def generate_body(self, data: CategorizedData) -> str:
        """Generate commit body."""
        lines = []
        
        # Add details
        for file in data.analysis.files:
            details = self.get_file_details(file)
            lines.append(f"- {file.path}: {details}")
        
        # Add breaking change notice
