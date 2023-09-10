from enum import Enum


class ReferenceRowOptions(Enum):
    IDENTIFIER = "#gcon:defs"
    STANDARD = "std"
    OPTIONAL = "opt"
    GENE = "gene"


class SourceGenomeEnum(Enum):
    NUCLEUS = "nuc"
    MITOCHONDRIA = "mit"
    PLASTID = "pla"
    UNKNOWN = "unk"
