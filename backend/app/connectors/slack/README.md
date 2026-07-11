# Slack Connector

The Slack Connector is the source-connector boundary for public Slack channels. It uses a bot token supplied through `SLACK_BOT_TOKEN` and returns only normalized `SourceRecord` instances.

Each Slack message, including a thread root or reply, becomes one record. The record metadata retains only `channel_id`, `thread_ts`, `message_ts`, `message_type`, and normalized attachments when present. It does not create Artifacts or group messages.

The future Ingestion Buffer consumes these individual records and is solely responsible for grouping them by `thread_ts` or channel inactivity windows before an Artifact is created.
