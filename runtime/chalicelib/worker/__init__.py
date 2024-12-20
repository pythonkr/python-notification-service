import json
import pathlib
import typing

import chalice.app
import chalicelib.config as config_module
import chalicelib.util.import_util as import_util

if typing.TYPE_CHECKING:
    import mypy_boto3_sqs.type_defs

    type RecordType = "mypy_boto3_sqs.type_defs.MessageTypeDef"
else:
    type RecordType = dict[str, typing.Any]

SQSEventType = typing.TypedDict("SQSEventType", {"Records": list[RecordType]})
WorkerType = typing.Callable[[chalice.app.Chalice, RecordType], dict[str, typing.Any]]


def register_worker(app: chalice.app.Chalice) -> None:
    workers: dict[str, WorkerType] = {}

    for _workers in typing.cast(
        list[list[WorkerType]],
        import_util.auto_import_patterns(pattern="workers", file_prefix="", dir=pathlib.Path(__file__).parent),
    ):
        _func_names = {worker.__name__ for worker in _workers}
        if _duplicated := _func_names & workers.keys():
            raise ValueError(f"Worker {_duplicated} is already registered")

        workers.update({worker.__name__: worker for worker in _workers})

    @app.on_sqs_message(queue=config_module.config.infra.queue_name)
    def sqs_handler(event: chalice.app.SQSEvent) -> list[dict[str, typing.Any]]:
        parsed_event: SQSEventType = event.to_dict()
        app.log.info(f"{parsed_event=}")

        results: list[dict[str, typing.Any]] = []
        for record in parsed_event["Records"]:
            try:
                worker_name = json.loads(record["body"])["worker"]
                result = workers[worker_name](app, record)
                results.append(result)
            except Exception as e:
                app.log.error(f"Failed to handle event: {record}", exc_info=e)
                results.append({"error": "Failed to handle event"})

        app.log.info(f"{results=}")
        return results
