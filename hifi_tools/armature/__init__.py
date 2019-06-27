
from . import (
    hifi_skeleton,
    vrc_skeleton
)

from enum import Enum

class SkeletonTypes(Enum):
    HIFI = (1, hifi_skeleton.structure)
    VRC = (2, vrc_skeleton.structure)

    def __init__(self, identifier, structure):
        self.identifier = identifier
        self.structure = structure 
