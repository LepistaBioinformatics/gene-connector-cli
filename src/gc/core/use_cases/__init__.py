"""
The use cases module contains the business logic of the application.

The main steps of the application are:
    - Load, parse, and sanitize source tables containing sequences data.
    - Collect associated metadata from Genbank.
    - Perform metadata matches and build metadata match scores.
    - Persist the results to GeneConnector remote server.
"""
