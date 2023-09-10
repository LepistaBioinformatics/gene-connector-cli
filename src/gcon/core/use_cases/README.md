# USE-CASES

The use-cases module contains the business logic of the application. The main steps executed by the application are:

1. Load, parse, and sanitize source tables containing sequences data ([load_and_validate_source_table](./load_and_validate_source_table/__init__.py) sub-module).
2. Collect associated metadata from Genbank ([collect_metadata](./collect_metadata/__init__.py) sub-module).
3. Perform metadata matches and build metadata match scores ([build_metadata_match_scores](./build_metadata_match_scores/__init__.py) sub-module).
4. Persist the results to GeneConnector remote server ([persist_metadata_on_gc_server](./persist_metadata_on_gc_server/__init__.py) sub-module *not already implemented*).

All above cited steps are orchestrated by the [main module](./__init__.py) use-case.
