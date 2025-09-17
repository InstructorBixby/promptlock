"""Readers that turn another tool's run artefact into an eval record.

Each importer owes two things: the metrics, and enough provenance that
somebody could re-run the thing. Nothing here invents a number -- if
the artefact does not say how many sends there were, the record does
not claim a rate.
"""
