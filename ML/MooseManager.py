import os

import dicom2nifti
from moosez import moose

from Utils.Logger import Logger


class MooseManager:
    def __init__(self, model_name: str, input_dir: str, output_dir: str, accelerator: str) -> None:
        self.model_name = model_name
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.accelerator = accelerator

    def run(self) -> str:
        self.__prepare_dicoms_to_nifti()

        Logger.info('Start moose predict')
        moose(self.model_name, './temp', self.output_dir, self.accelerator)
        Logger.info('Finish moose predict')

        self.__clear_up_temp_files()
        return self.__find_newest_nifti_file()

    def __find_newest_nifti_file(self) -> str:
        list_of_segmentation_files = os.listdir(self.output_dir)
        return f'{self.output_dir}/{list_of_segmentation_files[0]}'

    def __prepare_dicoms_to_nifti(self) -> None:
        Logger.info('Creating temp directory')
        os.mkdir('./temp', 0o777)
        dicom2nifti.convert_directory(self.input_dir, './temp')
        Logger.info('Finished creating temp directory')

    def __clear_up_temp_files(self) -> None:
        Logger.info('Deleting temp directory')
        list_of_temp_files = os.listdir('./temp')
        os.remove(f'./temp/{list_of_temp_files[0]}')
        os.rmdir('./temp')
        Logger.info('Finished deleting temp directory')
