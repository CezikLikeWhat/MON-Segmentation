from moosez import moose

class MooseManager():
    def __init__(self, model_name: str, input_dir: str, output_dir: str, accelerator: str) -> None:
        self.model_name = model_name
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.accelerator = accelerator

    def run(self) -> None:
        moose(self.model_name, self.input_dir, self.output_dir, self.accelerator)