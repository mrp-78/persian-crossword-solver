from enum import Enum


class Direction(Enum):
    HORIZONTAL = 1
    VERTICAL = 2


class AppEnvironment(Enum):
    DEVELOPMENT = 'development'
    PRODUCTION = 'production'
