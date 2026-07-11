# Ingestion Buffer

The buffer receives individual normalized `SourceRecord` values and emits `AggregatedTranscript` values. It does not create Artifacts, invoke EKPP, or communicate with queues or storage systems.

Threaded records are isolated by `thread_ts`; non-threaded records share a channel sliding window. A session emits after five minutes of inactivity or at 50 messages. This preserves conversational context while bounding transcript size, so downstream EKPP work is scheduled as one meaningful unit instead of one task per message.

`BufferStore` separates the grouping algorithm from state persistence. `InMemoryBufferStore` supports local development and deterministic unit tests; a Redis-backed store can later implement the same interface. Per-session async locks ensure active threads and channels progress independently.
