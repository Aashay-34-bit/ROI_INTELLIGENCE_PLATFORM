from app.validation.retry_manager import RetryManager
from app.validation.validators import SchemaValidator


def test_validation_and_retry_budget() -> None:
    assert not SchemaValidator().validate("extraction", "", ["email"]).valid
    manager = RetryManager(max_per_node=2, max_per_request=2)
    assert manager.consume("a") and manager.consume("a")
    assert not manager.consume("a")
