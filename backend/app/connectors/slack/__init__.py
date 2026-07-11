"""Slack source connector package."""

from backend.app.connectors.slack.connector import SlackConnector, get_slack_connector
from backend.app.connectors.slack.service import SlackService, get_slack_service

__all__ = ["SlackConnector", "SlackService", "get_slack_connector", "get_slack_service"]
