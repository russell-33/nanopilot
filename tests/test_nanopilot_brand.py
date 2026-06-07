from nanopilot import FakeModelClient, NanoPilot, SessionStore, WorkspaceContext
from nanopilot.cli import build_welcome


def test_nanopilot_branding_and_local_state_root(tmp_path):
    workspace = WorkspaceContext.build(tmp_path)
    agent = NanoPilot(
        model_client=FakeModelClient(["<final>ok</final>"]),
        workspace=workspace,
        session_store=SessionStore(tmp_path / ".nanopilot" / "sessions"),
    )

    welcome = build_welcome(agent, model="test-model", host="test-host")

    assert "NanoPilot" in welcome
    assert "You are NanoPilot" in agent.prefix
    assert agent.run_store.root == tmp_path / ".nanopilot" / "runs"
