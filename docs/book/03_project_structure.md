# PROJECT ARCHITECTURE AND STRUCTURE 🏛️

[◀️ Home](https://github.com/sgelias/gene-connector-cli/blob/main/README.md) | [◀️ Documentation](https://github.com/sgelias/gene-connector-cli/blob/main/docs/README.md)

___

Gene Connector seems the clean architecture proposed by Robert C. Martin (aka Uncle Bob) in his book [Clean Architecture](https://www.amazon.com.br/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164). The main idea is to separate the application in layers, where each layer has a specific responsibility. The layers are:

- **Core**: That includes the business rules and the domain model. It is the most inner layer of the application and it is independent of any other layer. Here lives the use-cases and the domain models.
- **Adapters**: That includes the interfaces to the external world. It is the most outer layer of the application and it is dependent of the core layer. Here lives the `Pickle` database connector responsible for the cache data persistence during metadata collection.
- **Ports**: That includes the interfaces to the core layer. User will interact with the application through the ports. Here lives the CLI (Command Line Interface) interface.

Owr project mirrors these three layers, which should exists into src/gcon folder. The following command shows the project (including files) structure:

```bash
tree -I "*__.py" -I "test_*" -I "tests" -I "README*" src/gcon
```

Result:

```bash
src/gcon
├── adapters
│   └── pickledb
│       └── repositories
│           ├── connector.py
│           ├── node_fetching.py
│           └── node_registration.py
├── core
│   ├── domain
│   │   ├── dtos
│   │   │   ├── connection.py
│   │   │   ├── metadata.py
│   │   │   ├── node.py
│   │   │   ├── reference_data
│   │   │   │   └── schemas.py
│   │   │   └── score.py
│   │   └── entities
│   │       ├── node_fetching.py
│   │       └── node_registration.py
│   └── use_cases
│       ├── build_metadata_match_scores
│       │   ├── _calculate_connection_match_score.py
│       │   └── _calculate_connection_observed_score.py
│       ├── collect_metadata
│       │   ├── _chunks_accessions.py
│       │   ├── _collect_single_gene_metadata.py
│       │   ├── _collect_unique_identifiers.py
│       │   └── _place_qualifiers.py
│       ├── load_and_validate_source_table
│       │   ├── _dtos.py
│       │   ├── _validate_genes_fields.py
│       │   ├── _validate_optional_fields.py
│       │   └── _validate_required_fields.py
│       └── persist_metadata_on_gc_server
├── ports
│   └── cli
│       └── main.py
└── settings.py
```

In the next section (Data Modelling) we will see the main data structures of the application which contains the gcon's Connection, Nodes, and Metadata representation.

___

[◀️ Prev: Usage](https://github.com/sgelias/gene-connector-cli/blob/main/docs/book/02_usage.md)

[▶️ Next: Data Modelling](https://github.com/sgelias/gene-connector-cli/blob/main/docs/book/04_data_modelling.md)
