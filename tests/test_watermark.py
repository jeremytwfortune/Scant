from unittest.mock import Mock

import pytest

from scant.watermark import Watermark, Watermarker


@pytest.mark.parametrize("value, expected", [(None, 0), ("42", 42)])
def test_watermark_should_read_environment_without_a_parameter(
    monkeypatch: pytest.MonkeyPatch, aws_client: Mock, value: str | None, expected: int
) -> None:
    monkeypatch.delenv("SCANT_WATERMARK_LAST_KNOWN_ID", raising=False)
    if value is not None:
        monkeypatch.setenv("SCANT_WATERMARK_LAST_KNOWN_ID", value)

    assert Watermarker(None).get() == Watermark(expected)
    aws_client.get_parameter.assert_not_called()


def test_watermark_should_read_configured_parameter(aws_client: Mock) -> None:
    aws_client.get_parameter.return_value = {"Parameter": {"Value": '{"lastKnownID": 42}'}}

    assert Watermarker("test-watermark").get() == Watermark(42)
    aws_client.get_parameter.assert_called_once_with(Name="test-watermark")


def test_watermark_should_save_last_known_id(aws_client: Mock) -> None:
    Watermarker("test-watermark").set(Watermark(42))

    aws_client.put_parameter.assert_called_once_with(
        Name="test-watermark", Value='{"lastKnownID": 42}', Type="String", Overwrite=True
    )


def test_watermark_should_skip_writes_without_a_parameter(aws_client: Mock) -> None:
    Watermarker(None).set(Watermark(42))

    aws_client.put_parameter.assert_not_called()
