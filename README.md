# promptlock

A stable content hash for a prompt.

The problem, stated as narrowly as I can: a system prompt is
production-critical configuration, it ships as a string in a repo or a
row in a database, and nobody treats it like configuration. Nobody can
tell me which exact text produced a given eval number, and nobody
notices when the text in production stops matching the text that was
tested.

Right now this is one script. It prints a hash of a prompt file.

    python lock.py prompts/triage.md
