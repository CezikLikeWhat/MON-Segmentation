from enum import Enum


class Organs(str, Enum):
    KIDNEY = 'kidney'
    ADRENAL_GLAND = 'adrenal gland'
    LUNG_UPPER = 'lung upper'
    LUNG_LOWER = 'lung lower'

    @staticmethod
    def get_all_options():
        return [m.value for m in Organs]
