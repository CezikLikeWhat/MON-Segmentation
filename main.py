# import napari
# import nrrd

# with napari.gui_qt():
#     data, header = nrrd.read('data_segmentation/Segmentation_preview.nrrd')

#     viewer = napari.Viewer(title="Segmentation viewer", ndisplay=3, order=(0,1,2))
#     viewer.add_image(data=data, name="Segmentation", colormap="plasma", rendering='minip')



# from DicomRTTool import DicomReaderWriter
# from NiftiResampler.ResampleTools import ImageResampler, sitk

# Resampler = ImageResampler()
# img_handle = sitk.ReadImage('data_segmentation/CT.nii.gz')
# desired_dimensions = (1.0, 1.0, 3.0)
# resampled = Resampler.resample_image(input_image_handle=img_handle, output_spacing=desired_dimensions, interpolator='Linear')
# sitk.WriteImage(resampled, r'.\Image_Resampled.nii.gz')


# import slicerio.server

# slicerio.server.file_load("data_segmentation/Segmentation_preview.nrrd", slicer_executable="/home/cmackowski/Downloads/Slicer-5.4.0-linux-amd64/Slicer")

# from brainrender.actors import Volume
# from brainrender import Scene
# from imio import load
# import numpy as np

# cos = load.load_nrrd('data_segmentation/Segmentation_preview.nrrd')
# # cos.tofile('data_segmentation/cos.npy')
# np.save('data_segmentation/cos.npy', cos)
# print('wczytane')

# vol = Volume(np.load('data_segmentation/cos.npy'))

# print('po volume')

# # mesh = vol.mesh

# # print('po mesh')

# scene = Scene(atlas_name='azba_zfish_4um')
# scene.add(vol)

# print('po scene')

# scene.render()

# print('po render')


# import brainrender
# from imio import load
# from brainrender import Scene, actors

# brainrender.settings.WHOLE_SCREEN = False 

# img_stack = load.load_nrrd('data_segmentation/Segmentation_preview.nrrd') 

# scene = Scene()
# scene.add(actors.Volume(img_stack))

# scene.render()


# from brainrender.actors import Volume
# from brainrender import Scene
# from bg_space import AnatomicalSpace
# from imio import load
# import numpy as np
# from myterial import blue_grey

# # 1. load the data
# print("Loading data")
# data = load.load_any('data_segmentation/Segmentation_preview.nrrd')

# # 2. aligned the data to the scene's atlas' axes
# print("Transforming data")
# scene = Scene(atlas_name="azba_zfish_4um")

# # source_space = AnatomicalSpace(
# #     "ira"
# # )  # for more info: https://docs.brainglobe.info/bg-space/usage
# # target_space = scene.atlas.space
# # transformed_stack = source_space.map_stack_to(target_space, data)

# # 3. create a Volume vedo actor and smooth
# print("Creating volume")
# vol = Volume(data)


# # 4. Extract a surface mesh from the volume actor
# print("Extracting surface")
# # SHIFT = [-20, 15, 30]  # fine tune mesh position
# # mesh = (
# #     vol.isosurface(threshold=20).c(blue_grey).decimate().clean().addPos(*SHIFT)
# # )

# # 5. render
# print("Rendering")
# scene.add(vol)
# scene.render(zoom=13)


from PyQt5 import Qt
import sys

from View.MainWindow import MainWindow

if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
