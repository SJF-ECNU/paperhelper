from app.workflow.nodes import PaperAnalysisWorkflow, WorkflowState


def test_workflow_generates_artifacts():
    sections = [
        ("Intro", "Machine learning improves performance of models."),
        ("Methods", "We trained neural networks on datasets."),
    ]
    workflow = PaperAnalysisWorkflow()
    state = WorkflowState(document_id="doc1", filename="paper.md", sections=sections)
    artifacts = workflow.run(state)

    assert artifacts.summary
    assert artifacts.mind_map.nodes
    assert artifacts.glossary
    assert state.embeddings is not None
