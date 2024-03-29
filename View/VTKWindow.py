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

        colors = vtk.vtkNamedColors()
        axes = vtk.vtkAxesActor()
        self.widget = vtk.vtkOrientationMarkerWidget()
        rgba = [0.0, 0.0, 0.0, 0.0]
        colors.GetColor("Carrot", rgba)
        self.widget.SetOutlineColor(rgba[0], rgba[1], rgba[2])
        self.widget.SetOrientationMarker(axes)
        self.widget.SetInteractor(self.renderWidget)
        self.widget.SetViewport(0.8, 0.8, 1.0, 1.0)
        self.widget.EnabledOn()
        self.widget.SetInteractive(0)

        # self.camOrientManipulator = vtk.vtkCameraOrientationWidget()
        # self.camOrientManipulator.SetParentRenderer(self.renderer)
        # self.camOrientManipulator.On()

    def create_mesh(self, nifti_file_path: str) -> Qt.QFrame:
        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(nifti_file_path)
        reader.Update()

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
        randomSequence.SetSeed(303091)

        for i in range(1, len(self.uniqueValues) + 1):
            r = randomSequence.GetRangeValue(0.0, 1.0)
            randomSequence.Next()
            g = randomSequence.GetRangeValue(0.0, 1.0)
            randomSequence.Next()
            b = randomSequence.GetRangeValue(0.0, 1.0)
            randomSequence.Next()
            self.lookupTable.SetTableValue(i, r, g, b)

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

    def perform_icp_step(self, max_iterations: int):
        icp = vtk.vtkIterativeClosestPointTransform()
        icp.SetSource(self.secondPolyData)
        icp.SetTarget(self.firstPolyData)
        icp.GetLandmarkTransform().SetModeToRigidBody()
        icp.SetMaximumNumberOfLandmarks(500)
        icp.SetMaximumMeanDistance(.00001)
        icp.SetMaximumNumberOfIterations(max_iterations)
        icp.CheckMeanDistanceOn()
        icp.Update()

        return icp

    def update_actor_transform(self, poly_data: vtk.vtkPolyData):
        if self.secondActor is not None:
            self.renderer.RemoveActor(self.secondActor)
            self.secondActor.SetMapper(None)
            self.secondActor = None

        self.secondActor = self.create_actor(poly_data, self.lookupTable)
        self.renderer.AddActor(self.secondActor)
        self.renderWindow.Render()

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
