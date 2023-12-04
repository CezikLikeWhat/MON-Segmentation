import numpy as np
import vtk
import random
import sys
import vtk
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QComboBox, QFileDialog
from PyQt5 import Qt
from ML.Models import Models

from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class MainWindow(Qt.QMainWindow):

    def __init__(self, parent = None):
        Qt.QMainWindow.__init__(self, parent)
        
        self.setup_main_window()
        

        self.show()
        self.iren.Initialize()
        self.iren.Start()

    def setup_main_window(self):
        # General options
        # self.setFixedSize(2560, 1440)
        self.setWindowTitle('Segmentation tool - MON 2023/2024')
        
        vtkFrame = Qt.QFrame()
        vtkWidget = QVTKRenderWindowInteractor(vtkFrame)
        
        # Combobox
        # model_type_combobox = QComboBox()
        # model_type_combobox.addItems(Models.get_all_options())

        # File dialog
        file_dialog = QFileDialog()
        file_dialog.getExistingDirectory(self, 'Choose NIFTI file', 'NIFTI (*.nii.gz)')

        # Init buttons


        # Layout
        vl = Qt.QHBoxLayout()
        vl.addWidget(vtkWidget)

        # Else
        self.ren = vtk.vtkRenderer()
        vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = vtkWidget.GetRenderWindow().GetInteractor()

        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName('MOOSEv2_data/S1/moosez-clin_ct_organs-2023-11-20-18-50-45/segmentations/CT_Organs_CT_8_abdpanc_30_b31f_0000.nii.gz')
        reader.Update()

        imageData: vtk.vtkImageData = reader.GetOutput()

        dimensions = imageData.GetDimensions()
        
        rawValues = np.array(imageData.GetPointData().GetScalars(), copy=False)
        rawValues = np.reshape(rawValues, (dimensions[0] * dimensions[1] * dimensions[2]))
        uniqueValues = set()

        for i in range(len(rawValues)):
            uniqueValues.add(rawValues[i])

        lookupTable = vtk.vtkLookupTable()
        lookupTable.SetNumberOfColors(len(uniqueValues)+1)
        lookupTable.SetTableRange(0.0, len(uniqueValues))
        lookupTable.SetScaleToLinear()
        lookupTable.Build()
        lookupTable.SetTableValue(0, 1.0, 1.0, 1.0)

        randomSequence = vtk.vtkMinimalStandardRandomSequence()
        randomSequence.SetSeed(2137)

        for i in range(1, len(uniqueValues)+1):
            r = randomSequence.GetRangeValue(0.0, 1.0)
            randomSequence.Next()
            g = randomSequence.GetRangeValue(0.0, 1.0)
            randomSequence.Next()
            b = randomSequence.GetRangeValue(0.0, 1.0)
            randomSequence.Next()
            lookupTable.SetTableValue(i, r, g, b)

        marchingCubes = vtk.vtkDiscreteMarchingCubes()
        marchingCubes.SetInputData(imageData)
        marchingCubes.GenerateValues(len(uniqueValues)+1, 0, len(uniqueValues))

        mesh_mapper = vtk.vtkPolyDataMapper()
        mesh_mapper.SetInputConnection(marchingCubes.GetOutputPort())
        mesh_mapper.SetLookupTable(lookupTable)
        mesh_mapper.SetScalarRange(0.0, lookupTable.GetNumberOfColors())

        mesh_actor = vtk.vtkActor()
        mesh_actor.SetMapper(mesh_mapper)

        self.ren.AddActor(mesh_actor)
        self.ren.ResetCamera()
        vtkWidget.GetRenderWindow()

        vtkFrame.setLayout(vl)
        self.setCentralWidget(vtkFrame)