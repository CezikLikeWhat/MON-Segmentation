import numpy as np
import vtk
import random
import sys
import vtk
from PyQt5 import QtCore, QtGui
from PyQt5 import Qt

from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class MainWindow(Qt.QMainWindow):

    def __init__(self, parent = None):
        Qt.QMainWindow.__init__(self, parent)

        self.frame = Qt.QFrame()
        self.vl = Qt.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)

        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

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
        
        mapper = vtk.vtkGPUVolumeRayCastMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        colorTransferFunction = vtk.vtkDiscretizableColorTransferFunction()
        colorTransferFunction.DiscretizeOn()
        colorTransferFunction.SetNumberOfValues(len(uniqueValues))

        rng = np.random.default_rng()

        for entry in uniqueValues:
            colorTransferFunction.AddRGBPoint(entry, rng.uniform(0.0, 1.0), rng.uniform(0.0, 1.0), rng.uniform(0.0, 1.0))
        
        opacityTransferFunction = vtk.vtkPiecewiseFunction()
        opacityTransferFunction.AddPoint(0.0, 0.0)
        opacityTransferFunction.AddPoint(1.0, 1.0)
        opacityTransferFunction.AddPoint(len(uniqueValues), 1.0)
        opacityTransferFunction.AddPoint(255.0, 1.0)

        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(colorTransferFunction)
        volumeProperty.SetScalarOpacity(opacityTransferFunction)

        volume = vtk.vtkVolume()
        volume.SetProperty(volumeProperty)
        volume.SetMapper(mapper)

        self.ren.AddVolume(volume)
        self.ren.ResetCamera()
        self.vtkWidget.GetRenderWindow()

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        self.show()
        self.iren.Initialize()
        self.iren.Start()


if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())