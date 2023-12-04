import numpy as np
import vtk
import random
import sys
import vtk
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import Qt

from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class MainWindow(Qt.QMainWindow):
    def __init__(self, parent = None):
        Qt.QMainWindow.__init__(self, parent)
        self.setFixedSize(2560, 1440)

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

        # Wygeneruj mesh za pomocą vtkMarchingCubes
        contour = vtk.vtkMarchingCubes()
        contour.SetInputConnection(reader.GetOutputPort())
        contour.SetValue(0, 1)  # Ustaw wartość konturu na poziomie, które chcesz wyodrębnić

        # Ustawienie mappera dla meshu
        mesh_mapper = vtk.vtkPolyDataMapper()
        mesh_mapper.SetInputConnection(contour.GetOutputPort())

        # Utworzenie aktora na podstawie mappera
        mesh_actor = vtk.vtkActor()
        mesh_actor.SetMapper(mesh_mapper)

        self.ren.AddActor(mesh_actor)
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
