from enum import Enum


class Organs(str, Enum):
    KIDNEY = 'Kidney'
    LUNG_LOWER = 'Lung lower'

    @staticmethod
    def get_all_options():
        return [m.value for m in Organs]
