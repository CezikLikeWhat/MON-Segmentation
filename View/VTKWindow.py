import numpy as np
import vtk
from PyQt5 import Qt
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from Utils.Logger import Logger


class VTKSegmentation:

    @staticmethod
    def create_mesh(nifti_file_path: str) -> Qt.QFrame:
        Logger.info('Start create_mesh')
        frame = Qt.QFrame()
        vtkWidget = QVTKRenderWindowInteractor(frame)

        Logger.info('Before rendered')
        ren = vtk.vtkRenderer()
        vtkWidget.GetRenderWindow().AddRenderer(ren)
        iren = vtkWidget.GetRenderWindow().GetInteractor()

        Logger.info('Before reader')
        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(nifti_file_path)
        reader.Update()

        Logger.info('Before imagedata')
        imageData: vtk.vtkImageData = reader.GetOutput()

        dimensions = imageData.GetDimensions()

        rawValues = np.array(imageData.GetPointData().GetScalars(), copy=False)
        rawValues = np.reshape(rawValues, (dimensions[0] * dimensions[1] * dimensions[2]))
        uniqueValues = set()

        for i in range(len(rawValues)):
            uniqueValues.add(rawValues[i])

        Logger.info('Before lookup table')
        lookupTable = vtk.vtkLookupTable()
        lookupTable.SetNumberOfColors(len(uniqueValues) + 1)
        lookupTable.SetTableRange(0.0, len(uniqueValues))
        lookupTable.SetScaleToLinear()
        lookupTable.Build()
        lookupTable.SetTableValue(0, 1.0, 1.0, 1.0)

        Logger.info('Before random Sequence')
        randomSequence = vtk.vtkMinimalStandardRandomSequence()
        randomSequence.SetSeed(2137)

        for i in range(1, len(uniqueValues) + 1):
            r = randomSequence.GetRangeValue(0.0, 1.0)
            randomSequence.Next()
            g = randomSequence.GetRangeValue(0.0, 1.0)
            randomSequence.Next()
            b = randomSequence.GetRangeValue(0.0, 1.0)
            randomSequence.Next()
            lookupTable.SetTableValue(i, r, g, b)

        Logger.info('Before marching cubes')
        marchingCubes = vtk.vtkDiscreteMarchingCubes()
        marchingCubes.SetInputData(imageData)
        marchingCubes.GenerateValues(len(uniqueValues) + 1, 0, len(uniqueValues))

        Logger.info('Before mesh mapper')
        mesh_mapper = vtk.vtkPolyDataMapper()
        mesh_mapper.SetInputConnection(marchingCubes.GetOutputPort())
        mesh_mapper.SetLookupTable(lookupTable)
        mesh_mapper.SetScalarRange(0.0, lookupTable.GetNumberOfColors())

        Logger.info('Before actor')
        mesh_actor = vtk.vtkActor()
        mesh_actor.SetMapper(mesh_mapper)

        Logger.info('Before add actor')
        ren.AddActor(mesh_actor)
        ren.ResetCamera()  # setup camera that all objects will be visible

        camera: vtk.vtkCamera = ren.GetActiveCamera()
        camera.Elevation(100)
        camera.Roll(180)
        ren.SetActiveCamera(camera)

        vtkWidget.GetRenderWindow()

        Logger.info('Before initialize and start')
        iren.Initialize()
        iren.Start()

        return frame
