import pytest
from src.video_transcript_analysis.core.question_optimizer import QuestionOptimizer, QuestionDependency

@pytest.fixture
def optimizer():
    return QuestionOptimizer()

@pytest.fixture
def sample_questions():
    return [
        "What is the main topic of the video?",
        "Who are the key speakers mentioned?",
        "What are the three main points discussed?",
        "Can you summarize the conclusion?",
        "What examples were given for point 3?"
    ]

def test_analyze_dependencies(optimizer, sample_questions):
    """Test dependency analysis for questions."""
    dependencies = optimizer.analyze_dependencies(sample_questions)
    
    # Verify dependencies are created
    assert len(dependencies) == len(sample_questions)
    
    # Verify structure of each dependency
    for dep in dependencies:
        assert isinstance(dep, QuestionDependency)
        assert dep.question in sample_questions
        assert isinstance(dep.dependencies, set)
        assert isinstance(dep.ordinal_refs, list)
        assert dep.index >= 0 and dep.index < len(sample_questions)

def test_ordinal_references(optimizer):
    """Test detection of ordinal references in questions."""
    questions = [
        "What is the first point?",
        "Can you explain the second example?",
        "What about the third topic?",
        "Summarize points 1 and 2",
        "Compare the first and third points"
    ]
    
    dependencies = optimizer.analyze_dependencies(questions)
    
    # Verify ordinal references are detected
    assert any(0 in dep.ordinal_refs for dep in dependencies)  # "first" references
    assert any(1 in dep.ordinal_refs for dep in dependencies)  # "second" references
    assert any(2 in dep.ordinal_refs for dep in dependencies)  # "third" references

def test_contextual_relationships(optimizer):
    """Test detection of contextual relationships between questions."""
    questions = [
        "Who is John Smith?",
        "What role did John Smith play in the project?",
        "What were the project outcomes?",
        "How did John Smith contribute to these outcomes?"
    ]
    
    dependencies = optimizer.analyze_dependencies(questions)
    
    # Verify contextual relationships are detected
    john_smith_deps = [dep for dep in dependencies if "John Smith" in dep.question]
    assert len(john_smith_deps) > 0
    
    # Verify dependencies between related questions
    for dep in john_smith_deps:
        assert len(dep.dependencies) > 0

def test_optimize_order(optimizer, sample_questions):
    """Test question order optimization."""
    dependencies = optimizer.analyze_dependencies(sample_questions)
    batches = optimizer.optimize_order(dependencies)
    
    # Verify batches are created
    assert len(batches) > 0
    
    # Verify batch structure
    for batch in batches:
        assert isinstance(batch, list)
        assert len(batch) > 0
        assert all(isinstance(idx, int) for idx in batch)
        assert all(0 <= idx < len(sample_questions) for idx in batch)

def test_batch_size_limits(optimizer):
    """Test that batches respect size limits."""
    # Create many questions to ensure multiple batches
    questions = [f"Question {i}" for i in range(20)]
    dependencies = optimizer.analyze_dependencies(questions)
    batches = optimizer.optimize_order(dependencies)
    
    # Verify batch sizes
    for batch in batches:
        assert len(batch) <= optimizer.settings.BATCH_SIZE

def test_dependency_resolution(optimizer):
    """Test that dependencies are properly resolved in ordering."""
    questions = [
        "What is the main topic?",
        "What are the key points about the main topic?",
        "Who are the speakers?",
        "What did the speakers say about the main topic?",
        "What are the conclusions?"
    ]
    
    dependencies = optimizer.analyze_dependencies(questions)
    batches = optimizer.optimize_order(dependencies)
    
    # Verify main topic question comes before dependent questions
    main_topic_idx = next(i for i, q in enumerate(questions) if "main topic" in q.lower())
    dependent_indices = [i for i, q in enumerate(questions) if "main topic" in q.lower() and i != main_topic_idx]
    
    for batch in batches:
        if main_topic_idx in batch:
            batch_idx = batches.index(batch)
            for dep_idx in dependent_indices:
                dep_batch_idx = next(i for i, b in enumerate(batches) if dep_idx in b)
                assert dep_batch_idx > batch_idx

def test_validate_questions(optimizer):
    """Test question validation functionality."""
    questions = [
        "Valid question about the topic?",
        "Too short",  # Invalid: too short
        "What did they discuss?",  # Valid
        "Not a question",  # Invalid: no question mark
        "What about this one?"  # Valid
    ]
    
    is_valid, issues = optimizer.validate_questions(questions)
    
    # Verify validation results
    assert not is_valid
    assert len(issues) > 0
    assert any("too short" in issue.lower() for issue in issues)
    assert any("not a proper question" in issue.lower() for issue in issues)

def test_circular_dependencies(optimizer):
    """Test handling of potential circular dependencies."""
    questions = [
        "What is point 1?",
        "How does point 1 relate to point 2?",
        "What about point 2 and point 1?",
        "Can you compare points 1, 2, and 3?"
    ]
    
    is_valid, issues = optimizer.validate_questions(questions)
    
    # Verify circular dependencies are detected
    assert not is_valid
    assert any("reference itself" in issue.lower() for issue in issues)

def test_empty_questions(optimizer):
    """Test handling of empty question list."""
    dependencies = optimizer.analyze_dependencies([])
    assert len(dependencies) == 0
    
    batches = optimizer.optimize_order(dependencies)
    assert len(batches) == 0
    
    is_valid, issues = optimizer.validate_questions([])
    assert is_valid
    assert len(issues) == 0