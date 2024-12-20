import typing

import chalice.app

if typing.TYPE_CHECKING:
    import mypy_boto3_sqs.type_defs

    type RecordType = "mypy_boto3_sqs.type_defs.MessageTypeDef"
else:
    type RecordType = dict[str, typing.Any]


def test_handler(app: chalice.app.Chalice, record: RecordType) -> RecordType:
    print(record)
    return record


workers = [test_handler]
