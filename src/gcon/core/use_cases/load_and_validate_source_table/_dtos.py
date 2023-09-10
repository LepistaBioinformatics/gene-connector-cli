from enum import Enum


class ReferenceRowOptions(Enum):
    IDENTIFIER = "#gcon:defs"
    STANDARD = "std"
    OPTIONAL = "opt"
    GENE = "gene"
