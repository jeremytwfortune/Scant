from dataclasses import dataclass
import json
import boto3
import os


@dataclass
class Watermark:
    last_known_id: int


class Watermarker:
    def __init__(self, parameter_name: str | None) -> None:
        self.__parameter_name = parameter_name
        self.__client = boto3.client("ssm")

    def get(self) -> Watermark:
        if self.__parameter_name is None:
            env_id = os.environ.get("SCANT_WATERMARK_LAST_KNOWN_ID", "0")
            return Watermark(int(env_id))

        response = self.__client.get_parameter(Name=self.__parameter_name)
        parameter_value = json.loads(response["Parameter"]["Value"])

        return Watermark(parameter_value["lastKnownID"])

    def set(self, watermark: Watermark) -> None:
        if self.__parameter_name is None:
            return

        self.__client.put_parameter(
            Name=self.__parameter_name,
            Value=json.dumps({"lastKnownID": watermark.last_known_id}),
            Type="String",
            Overwrite=True,
        )
