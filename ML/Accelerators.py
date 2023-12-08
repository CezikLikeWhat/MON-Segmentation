from enum import Enum


class Accelerators(str, Enum):
    CPU = 'cpu'
    CUDA = 'cuda'

    @staticmethod
    def get_all_options():
        return [m.value for m in Accelerators]
