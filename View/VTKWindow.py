import numpy as np
import vtk
from PyQt5 import Qt
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class VTKSegmentation:
    def __init__(self):
        self.frame = Qt.QFrame()
        self.renderWidget = QVTKRenderWindowInteractor(self.frame)
        self.renderWindow = self.renderWidget.GetRenderWindow()
        self.renderer = vtk.vtkRenderer()
        self.renderWindow.AddRenderer(self.renderer)
        self.renderWidget.SetRenderWindow(self.renderWindow)

        self.polyData = vtk.vtkPolyData()
        self.firstPolyData = vtk.vtkPolyData()
        self.secondPolyData = vtk.vtkPolyData()
        self.lookupTable = vtk.vtkLookupTable()
        self.uniqueValues = set()
        self.firstActor: vtk.vtkActor | None = None
        self.secondActor: vtk.vtkActor | None = None
        self.secondActorCenter: float | None = None

        self.translation = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0]
        self.scale = [1.0, 1.0, 1.0]

    def create_mesh(self, nifti_file_path: str) -> Qt.QFrame:
        # Logger.info('Start create_mesh')

        # iren = self.renderWindow.GetInteractor()

        # Logger.info('Before reader')
        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(nifti_file_path)
        reader.Update()

        # Logger.info('Before imagedata')
        imageData: vtk.vtkImageData = reader.GetOutput()

        dimensions = imageData.GetDimensions()

        rawValues = np.array(imageData.GetPointData().GetScalars(), copy=False)
        rawValues = np.reshape(rawValues, (dimensions[0] * dimensions[1] * dimensions[2]))

        for i in range(len(rawValues)):
            self.uniqueValues.add(rawValues[i])

        # Logger.info('Before marching cubes')
        marchingCubes = vtk.vtkDiscreteMarchingCubes()
        marchingCubes.SetInputData(imageData)
        marchingCubes.GenerateValues(len(self.uniqueValues) + 1, 0, len(self.uniqueValues))
        marchingCubes.Update()
        self.polyData = marchingCubes.GetOutput()

        # Logger.info('Before lookup table')
        self.lookupTable.SetNumberOfColors(len(self.uniqueValues) + 1)
        self.lookupTable.SetTableRange(0.0, len(self.uniqueValues))
        self.lookupTable.SetScaleToLinear()
        self.lookupTable.Build()
        self.lookupTable.SetTableValue(0, 1.0, 1.0, 1.0)

        # Logger.info('Before random Sequence')
        randomSequence = vtk.vtkMinimalStandardRandomSequence()
        randomSequence.SetSeed(2137)

        for i in range(1, len(self.uniqueValues) + 1):
            r = randomSequence.GetRangeValue(0.0, 1.0)
            randomSequence.Next()
            g = randomSequence.GetRangeValue(0.0, 1.0)
            randomSequence.Next()
            b = randomSequence.GetRangeValue(0.0, 1.0)
            randomSequence.Next()
            self.lookupTable.SetTableValue(i, r, g, b)

        # Logger.info('Before mesh mapper')
        if self.firstActor is not None:
            self.renderer.RemoveActor(self.firstActor)
            self.firstActor.FastDelete()
            self.firstActor = None

        self.firstActor = self.create_actor(self.polyData, self.lookupTable)
        self.renderer.AddActor(self.firstActor)

        camera: vtk.vtkCamera = self.renderer.GetActiveCamera()
        camera.Elevation(100)
        camera.Roll(180)
        self.renderer.SetActiveCamera(camera)

        self.renderer.ResetCamera()
        self.renderWindow.Render()

        return self.frame

    def match(self, first_organ_value: float, second_organ_value: float) -> Qt.QFrame | None:
        if self.polyData is None:
            return

        if self.firstActor is not None:
            self.renderer.RemoveActor(self.firstActor)
            self.firstActor.SetMapper(None)
            self.firstActor = None

        self.firstPolyData = self.separatePolyData(self.polyData, first_organ_value, first_organ_value, False)
        self.firstActor = self.create_actor(self.firstPolyData, self.lookupTable)
        self.renderer.AddActor(self.firstActor)

        if self.secondActor is not None:
            self.renderer.RemoveActor(self.secondActor)
            self.secondActor.SetMapper(None)
            self.secondActor = None

        self.secondPolyData = self.separatePolyData(self.polyData, second_organ_value, second_organ_value, True)
        self.secondActor = self.create_actor(self.secondPolyData, self.lookupTable)
        self.renderer.AddActor(self.secondActor)
        self.secondActorCenter = self.secondActor.GetCenter()

        self.renderer.ResetCamera()
        self.renderWindow.Render()
        return self.frame

    def adjust(self) -> Qt.QFrame:
        distance = vtk.vtkHausdorffDistancePointSetFilter()
        distance.SetInputData(0, self.firstPolyData)
        distance.SetInputData(1, self.secondPolyData)
        distance.Update()

        distance_before_fit: vtk.VTK_POINT_SET = (distance.
                                                  GetOutput(0).
                                                  GetFieldData().
                                                  GetArray("HausdorffDistance").
                                                  GetComponent(0, 0)
                                                  )

        icp = vtk.vtkIterativeClosestPointTransform()
        icp.SetSource(self.secondPolyData)
        icp.SetTarget(self.firstPolyData)
        icp.GetLandmarkTransform().SetModeToRigidBody()
        icp.SetMaximumNumberOfLandmarks(500)
        icp.SetMaximumMeanDistance(.00001)
        icp.SetMaximumNumberOfIterations(500)
        icp.CheckMeanDistanceOn()
        icp.StartByMatchingCentroidsOn()
        icp.Update()

        lmTransform = icp.GetLandmarkTransform()
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInputData(self.secondPolyData)
        transformFilter.SetTransform(lmTransform)
        transformFilter.SetTransform(icp)
        transformFilter.Update()

        distance.SetInputData(0, self.firstPolyData)
        distance.SetInputData(1, transformFilter.GetOutput())
        distance.Update()

        distance_after_fit: vtk.VTK_POINT_SET = (distance.
                                                 GetOutput(0).
                                                 GetFieldData().
                                                 GetArray("HausdorffDistance").
                                                 GetComponent(0, 0)
                                                 )

        print(f'Distance before fit: {distance_before_fit}')
        print(f'Distance after fit: {distance_after_fit}')

        transformedPolyData = transformFilter.GetOutput()

        if self.secondActor is not None:
            self.renderer.RemoveActor(self.secondActor)
            self.secondActor.SetMapper(None)
            self.secondActor = None

        self.secondActor = self.create_actor(transformedPolyData, self.lookupTable)

        self.renderer.ResetCamera()

        self.renderer.AddActor(self.secondActor)
        self.renderWindow.Render()

        return self.frame

    def create_actor(self, poly_data: vtk.vtkPolyData, lookup_table: vtk.vtkLookupTable) -> vtk.vtkActor:
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)
        mapper.SetLookupTable(lookup_table)
        mapper.SetScalarRange(0.0, lookup_table.GetNumberOfColors())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        return actor

    def separatePolyData(self, poly_data: vtk.vtkPolyData, min_value: float, max_value: float,
                         reflection: bool = False) -> vtk.vtkPolyData:
        threshold = vtk.vtkThreshold()
        threshold.SetInputData(poly_data)
        threshold.SetLowerThreshold(min_value)
        threshold.SetUpperThreshold(max_value)
        threshold.Update()

        surfaceFilter = vtk.vtkDataSetSurfaceFilter()

        if reflection:
            reflectionFilter = vtk.vtkReflectionFilter()
            reflectionFilter.SetInputConnection(threshold.GetOutputPort())
            reflectionFilter.CopyInputOff()
            reflectionFilter.Update()
            surfaceFilter.SetInputConnection(reflectionFilter.GetOutputPort())
        else:
            surfaceFilter.SetInputConnection(threshold.GetOutputPort())

        surfaceFilter.Update()

        output = vtk.vtkPolyData()
        output.DeepCopy(surfaceFilter.GetOutput())

        return output

    # @staticmethod
    # def create_mesh(nifti_file_path: str) -> Qt.QFrame:
    #     # Logger.info('Start create_mesh')
    #     frame = Qt.QFrame()
    #     vtkWidget = QVTKRenderWindowInteractor(frame)
    #
    #     # Logger.info('Before rendered')
    #     ren = vtk.vtkRenderer()
    #     vtkWidget.GetRenderWindow().AddRenderer(ren)
    #     iren = vtkWidget.GetRenderWindow().GetInteractor()
    #
    #     # Logger.info('Before reader')
    #     reader = vtk.vtkNIFTIImageReader()
    #     reader.SetFileName(nifti_file_path)
    #     reader.Update()
    #
    #     # Logger.info('Before imagedata')
    #     imageData: vtk.vtkImageData = reader.GetOutput()
    #
    #     dimensions = imageData.GetDimensions()
    #
    #     rawValues = np.array(imageData.GetPointData().GetScalars(), copy=False)
    #     rawValues = np.reshape(rawValues, (dimensions[0] * dimensions[1] * dimensions[2]))
    #     uniqueValues = set()
    #
    #     for i in range(len(rawValues)):
    #         uniqueValues.add(rawValues[i])
    #
    #     # Logger.info('Before lookup table')
    #     lookupTable = vtk.vtkLookupTable()
    #     lookupTable.SetNumberOfColors(len(uniqueValues) + 1)
    #     lookupTable.SetTableRange(0.0, len(uniqueValues))
    #     lookupTable.SetScaleToLinear()
    #     lookupTable.Build()
    #     lookupTable.SetTableValue(0, 1.0, 1.0, 1.0)
    #
    #     # Logger.info('Before random Sequence')
    #     randomSequence = vtk.vtkMinimalStandardRandomSequence()
    #     randomSequence.SetSeed(2137)
    #
    #     for i in range(1, len(uniqueValues) + 1):
    #         r = randomSequence.GetRangeValue(0.0, 1.0)
    #         randomSequence.Next()
    #         g = randomSequence.GetRangeValue(0.0, 1.0)
    #         randomSequence.Next()
    #         b = randomSequence.GetRangeValue(0.0, 1.0)
    #         randomSequence.Next()
    #         lookupTable.SetTableValue(i, r, g, b)
    #
    #     # Logger.info('Before marching cubes')
    #     marchingCubes = vtk.vtkDiscreteMarchingCubes()
    #     marchingCubes.SetInputData(imageData)
    #     marchingCubes.GenerateValues(len(uniqueValues) + 1, 0, len(uniqueValues))
    #
    #     # Logger.info('Before mesh mapper')
    #     mesh_mapper = vtk.vtkPolyDataMapper()
    #     mesh_mapper.SetInputConnection(marchingCubes.GetOutputPort())
    #     mesh_mapper.SetLookupTable(lookupTable)
    #     mesh_mapper.SetScalarRange(0.0, lookupTable.GetNumberOfColors())
    #
    #     # Logger.info('Before actor')
    #     mesh_actor = vtk.vtkActor()
    #     mesh_actor.SetMapper(mesh_mapper)
    #
    #     # Logger.info('Before add actor')
    #     ren.AddActor(mesh_actor)
    #     ren.ResetCamera()  # setup camera that all objects will be visible
    #
    #     camera: vtk.vtkCamera = ren.GetActiveCamera()
    #     camera.Elevation(100)
    #     camera.Roll(180)
    #     ren.SetActiveCamera(camera)
    #
    #     vtkWidget.GetRenderWindow()
    #
    #     # Logger.info('Before initialize and start')
    #     iren.Initialize()
    #     iren.Start()
    #
    #     return frame
