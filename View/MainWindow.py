from PyQt5 import Qt
from PyQt5.QtWidgets import QFileDialog, QComboBox, QGroupBox, QPushButton, QGridLayout, QLabel, QHBoxLayout, \
    QVBoxLayout
from moosez.resources import check_cuda
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from ML.Accelerators import Accelerators
from ML.Models import Models
from ML.MooseManager import MooseManager
from Utils import Utils
from Utils.Logger import Logger
from View.MessageBox import MessageBox, MessageBoxType
from View.VTKWindow import VTKSegmentation


class MainWindow(Qt.QMainWindow):

    def __init__(self, parent=None) -> None:
        Qt.QMainWindow.__init__(self, parent)

        # Init variables
        self.model_type = ''
        self.model_accelerator = ''
        self.model_input_dir = ''
        self.model_output_dir = ''
        self.model_input_dir_button = None
        self.model_output_dir_button = None

        self.vtkWidget = None

        self.setup_main_window()

        self.show()

    def setup_main_window(self, updated_frame: Qt.QFrame = None) -> None:
        # General options
        # self.setFixedSize(2560, 1440)
        self.setWindowTitle('Segmentation tool - MON 2023/2024')

        if updated_frame is None:
            # initial state
            vtkFrame = Qt.QFrame()
            self.vtkWidget = QVTKRenderWindowInteractor(vtkFrame)
        else:
            # after read NIFTI file
            vtkFrame = updated_frame
            self.vtkWidget = vtkFrame.children()[0]

        self.vtkWidget.setMinimumSize(500, 600)

        # Moose group box
        moose_groupbox = QGroupBox()
        moose_groupbox.setTitle('Moose')
        moose_groupbox.setMaximumSize(400, 400)

        moose_layout = QGridLayout()
        moose_layout.setColumnMinimumWidth(0, 20)
        moose_layout.setColumnMinimumWidth(1, 40)

        model_type_label = QLabel('Model:')
        model_type_combobox = QComboBox()
        model_type_combobox.currentTextChanged.connect(self.model_type_changed)
        model_type_combobox.setFixedWidth(210)
        model_type_combobox.addItems(Models.get_all_options())

        model_input_dir_label = QLabel('DICOM directory:')
        self.model_input_dir_button = QPushButton('Choose input directory')
        self.model_input_dir_button.setFixedWidth(210)
        self.model_input_dir_button.clicked.connect(self.load_input_directory_path)

        model_output_dir_label = QLabel('NIFTI directory:')
        self.model_output_dir_button = QPushButton('Choose output directory')
        self.model_output_dir_button.setFixedWidth(210)
        self.model_output_dir_button.clicked.connect(self.load_output_directory_path)

        model_accelerator_label = QLabel('Accelerator:')
        model_accelerator_combobox = QComboBox()
        model_accelerator_combobox.currentTextChanged.connect(self.model_accelerator_changed)
        model_accelerator_combobox.setFixedWidth(210)
        model_accelerator_combobox.addItems(Accelerators.get_all_options())

        start_predict_button = QPushButton('Start predict')
        start_predict_button.setFixedWidth(210)
        start_predict_button.clicked.connect(self.start_predict)

        read_nifti_file_button = QPushButton('Load NIFTI file')
        start_predict_button.setFixedWidth(210)
        read_nifti_file_button.clicked.connect(lambda: self.load_nifti_file(None))

        moose_layout.addWidget(model_type_label, 0, 0)
        moose_layout.addWidget(model_type_combobox, 0, 2)
        moose_layout.addWidget(model_input_dir_label, 1, 0)
        moose_layout.addWidget(self.model_input_dir_button, 1, 2)
        moose_layout.addWidget(model_output_dir_label, 2, 0)
        moose_layout.addWidget(self.model_output_dir_button, 2, 2)
        moose_layout.addWidget(model_accelerator_label, 3, 0)
        moose_layout.addWidget(model_accelerator_combobox, 3, 2)
        moose_layout.addWidget(start_predict_button, 4, 2)
        moose_layout.addWidget(read_nifti_file_button, 5, 2)

        moose_groupbox.setLayout(moose_layout)

        # Group boxes layout
        groupbox_layout = QVBoxLayout()
        groupbox_layout.addWidget(moose_groupbox)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.addLayout(groupbox_layout)
        main_layout.addWidget(self.vtkWidget)

        vtkFrame.setLayout(main_layout)
        self.setCentralWidget(vtkFrame)

    def load_nifti_file(self, filepath: str | None) -> None:
        if filepath is None:
            filepath = QFileDialog.getOpenFileName(self, 'Choose NIFTI file', '.', '*.nii.gz')[0]
            if filepath == '':
                Logger.error('NIFTI file path not specified')
                (MessageBox())(self, MessageBoxType.ERROR, 'NIFTI file path not specified')
                return

        frame = VTKSegmentation.create_mesh(filepath)

        self.setup_main_window(frame)  # update gui with new VTK frame
        self.show()
        Logger.info('After update gui')

    def start_predict(self) -> None:
        if self.model_input_dir == '':
            Logger.error('Input model catalog not specified')
            (MessageBox())(self, MessageBoxType.ERROR, 'Input model catalog not specified')
            return
        if self.model_output_dir == '':
            Logger.error('Output model catalog not specified')
            (MessageBox())(self, MessageBoxType.ERROR, 'Output model catalog not specified')
            return
        if self.model_accelerator == 'cuda':
            Utils.disable_stdout()
            available_accelerator = check_cuda()
            Utils.enable_stdout()
            if available_accelerator == 'cpu':
                Logger.error('CUDA not available on this device')
                (MessageBox())(self, MessageBoxType.ERROR, 'CUDA not available on this device')
                return

        model = self.model_type
        input_dir = self.model_input_dir
        output_dir = self.model_output_dir
        accelerator = self.model_accelerator

        (MessageBox())(self, MessageBoxType.INFO,
                       'Model forecasting is underway. Do not use the application until it is finished. Please confirm by button')

        moose_manager = MooseManager(model, input_dir, output_dir, accelerator)
        nifti_filepath = moose_manager.run()

        self.load_nifti_file(nifti_filepath)

    def load_input_directory_path(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, 'Choose input directory', '.')
        self.model_input_dir = directory
        self.model_input_dir_button.setText(directory)

    def load_output_directory_path(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, 'Choose output directory', '.')
        self.model_output_dir = directory
        self.model_output_dir_button.setText(directory)

    def model_type_changed(self, value: str) -> None:
        self.model_type = value

    def model_accelerator_changed(self, value: str) -> None:
        self.model_accelerator = value
