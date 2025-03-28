from typing import List, Dict, Set, Tuple
import spacy
from dataclasses import dataclass
from ..config.settings import settings

@dataclass
class QuestionDependency:
    """Represents a question and its dependencies."""
    question: str
    index: int
    dependencies: Set[int]
    ordinal_refs: List[int]

class QuestionOptimizer:
    """Analyzes and optimizes question order based on dependencies."""
    
    def __init__(self):
        # Load English language model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
    
    def analyze_dependencies(self, questions: List[str]) -> List[QuestionDependency]:
        """Analyze questions for dependencies and ordinal references."""
        dependencies = []
        
        for idx, question in enumerate(questions):
            doc = self.nlp(question)
            deps = set()
            ordinals = []
            
            # Analyze ordinal references
            for token in doc:
                if token.pos_ == "NUM" and token.like_num:
                    try:
                        num = int(token.text)
                        if num > 0 and num <= len(questions):
                            ordinals.append(num - 1)  # Convert to 0-based index
                    except ValueError:
                        continue
            
            # Analyze contextual relationships
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PERSON", "GPE"]:
                    # Look for references to these entities in other questions
                    for other_idx, other_question in enumerate(questions):
                        if other_idx != idx and ent.text in other_question:
                            deps.add(other_idx)
            
            dependencies.append(QuestionDependency(
                question=question,
                index=idx,
                dependencies=deps,
                ordinal_refs=ordinals
            ))
        
        return dependencies
    
    def optimize_order(self, dependencies: List[QuestionDependency]) -> List[List[int]]:
        """Generate optimized batches of questions using topological sort."""
        # Build dependency graph
        graph: Dict[int, Set[int]] = {i: set() for i in range(len(dependencies))}
        for dep in dependencies:
            # Add explicit dependencies
            graph[dep.index].update(dep.dependencies)
            # Add ordinal reference dependencies
            graph[dep.index].update(dep.ordinal_refs)
        
        # Topological sort with batching
        visited = set()
        batches: List[List[int]] = []
        current_batch: List[int] = []
        
        def visit(node: int) -> None:
            if node in visited:
                return
            visited.add(node)
            
            # Visit dependencies first
            for dep in graph[node]:
                visit(dep)
            
            # Add to current batch
            current_batch.append(node)
            
            # Start new batch if current is full
            if len(current_batch) >= settings.BATCH_SIZE:
                batches.append(current_batch.copy())
                current_batch.clear()
        
        # Visit all nodes
        for node in range(len(dependencies)):
            if node not in visited:
                visit(node)
        
        # Add remaining nodes to final batch
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def validate_questions(self, questions: List[str]) -> Tuple[bool, List[str]]:
        """Validate questions for potential issues."""
        issues = []
        
        for idx, question in enumerate(questions):
            # Check for minimum length
            if len(question.strip()) < 5:
                issues.append(f"Question {idx + 1} is too short")
            
            # Check for common issues
            doc = self.nlp(question)
            if not any(token.pos_ in ["VERB", "AUX"] for token in doc):
                issues.append(f"Question {idx + 1} may not be a proper question")
            
            # Check for potential circular dependencies
            ordinals = [token for token in doc if token.pos_ == "NUM" and token.like_num]
            for ordinal in ordinals:
                try:
                    num = int(ordinal.text)
                    if num == idx + 1:
                        issues.append(f"Question {idx + 1} may reference itself")
                except ValueError:
                    continue
        
        return len(issues) == 0, issues 