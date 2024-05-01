from dataclasses import dataclass

from scant.authentication import Authentication, get_authentication
from scant.slack import SlackNotifier
from scant.watermark import Watermark, Watermarker


@dataclass
class Infrastructure:
    slack: SlackNotifier
    watermark: Watermark
    authentication: Authentication


def get_infrastructure(authentication_name: str | None, watermarker: Watermarker) -> Infrastructure:
    try:
        authentication = get_authentication(authentication_name)
        slack = SlackNotifier(authentication.slack_webhook)
        watermark = watermarker.get()

        return Infrastructure(slack, watermark, authentication)
    except Exception as e:
        raise Exception("Failed to create infrastructure") from e
