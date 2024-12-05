import typing

import chalice.app

if typing.TYPE_CHECKING:
    import mypy_boto3_sqs.type_defs


def test_handler(
    app: chalice.app.Chalice,
    record: "mypy_boto3_sqs.type_defs.MessageTypeDef",
) -> "mypy_boto3_sqs.type_defs.MessageTypeDef":
    print(record)
    return record


worker_patterns = {
    "test_handler": test_handler,
}
