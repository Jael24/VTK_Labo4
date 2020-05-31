import vtk
import os


SKIN_COLOR = (225 / 255, 172 / 255, 150 / 255)
SKIN_ISO_VALUE = 50.0
BONE_ISO_VALUE = 72.0


# Based on https://lorensen.github.io/VTKExamples/site/Python/IO/ReadSLC/#code


def create_sphere(radius, center, thetaResolution=50, phiResolution=50):
    s = vtk.vtkSphere()
    s.SetRadius(radius)
    s.SetCenter(center)

    ss = vtk.vtkSphereSource()
    ss.SetThetaResolution(thetaResolution)
    ss.SetPhiResolution(phiResolution)
    ss.SetCenter(center)
    ss.SetRadius(radius)

    return s, ss


# Implementing Marching Cubes Algorithm to create the surface using vtkContourFilter object.
def create_contour(iso_value):
    contourFilter = vtk.vtkContourFilter()
    contourFilter.SetInputConnection(reader.GetOutputPort())
    contourFilter.SetValue(0, iso_value)

    return contourFilter


def create_bone():
    cf_bone = create_contour(BONE_ISO_VALUE)
    mapper_bone = vtk.vtkPolyDataMapper()
    mapper_bone.SetInputConnection(cf_bone.GetOutputPort())
    mapper_bone.SetScalarVisibility(0)

    bone = vtk.vtkActor()
    bone.SetMapper(mapper_bone)

    return bone


def create_skin(implicit_function=False):
    cf_skin = create_contour(SKIN_ISO_VALUE)

    clip = vtk.vtkClipPolyData()
    clip.SetInputConnection(cf_skin.GetOutputPort())
    if implicit_function:
        clip.SetClipFunction(implicit_function)
    clip.GenerateClippedOutputOn()

    mapper_skin = vtk.vtkPolyDataMapper()
    mapper_skin.SetInputConnection(clip.GetOutputPort())
    mapper_skin.SetScalarVisibility(0)

    skin = vtk.vtkActor()
    skin.SetMapper(mapper_skin)
    skin.GetProperty().SetColor(SKIN_COLOR)

    return skin


def create_sliced_skin():
    plane = vtk.vtkPlane()

    impl_plane = vtk.vtkImplicitBoolean()
    impl_plane.SetOperationTypeToDifference()
    impl_plane.AddFunction(plane)

    cf = create_contour(SKIN_ISO_VALUE)

    cutter = vtk.vtkCutter()
    cutter.SetInputConnection(cf.GetOutputPort())
    cutter.SetCutFunction(plane)

    for i in range(19):
        cutter.SetValue(i, i * 11)

    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(cutter.GetOutputPort())
    stripper.Update()

    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputConnection(stripper.GetOutputPort())
    tube_filter.SetRadius(2.0)

    mapper_skin = vtk.vtkPolyDataMapper()
    mapper_skin.SetInputConnection(tube_filter.GetOutputPort())
    mapper_skin.SetScalarVisibility(0)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper_skin)
    actor.GetProperty().SetColor(SKIN_COLOR)

    return actor


def create_or_get_bone_distanced():
    cf_bone = create_contour(BONE_ISO_VALUE)
    cf_skin = create_contour(SKIN_ISO_VALUE)
    color_mapper = vtk.vtkPolyDataMapper()

    if not os.path.exists("bone_distance.vtk"):
        distance_pdFilter = vtk.vtkDistancePolyDataFilter()
        distance_pdFilter.SetInputConnection(0, cf_bone.GetOutputPort())
        distance_pdFilter.SetInputConnection(1, cf_skin.GetOutputPort())
        distance_pdFilter.SignedDistanceOff()
        distance_pdFilter.Update()

        # write in the files
        writer = vtk.vtkPolyDataWriter()
        writer.SetFileName("bone_distance.vtk")
        writer.SetInputData(distance_pdFilter.GetOutput())
        writer.Write()

        color_mapper.SetInputData(distance_pdFilter.GetOutput())
        color_mapper.SetScalarRange(distance_pdFilter.GetOutput().GetPointData().GetScalars().GetRange())

    else:
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName("bone_distance.vtk")
        reader.Update()

        color_mapper.SetInputConnection(reader.GetOutputPort())
        color_mapper.SetScalarRange(reader.GetOutput().GetScalarRange())



    bone = vtk.vtkActor()
    bone.SetMapper(color_mapper)

    return bone

def read_SLC_file(filename):
    # vtkSLCReader to read.
    read = vtk.vtkSLCReader()
    read.SetFileName(filename)
    read.Update()

    return read




if __name__ == '__main__':
    reader = read_SLC_file('vw_knee.slc')

    sphere, sphere_source = create_sphere(50, (60, 50, 105))

    impl_sphere = vtk.vtkImplicitBoolean()
    impl_sphere.SetOperationTypeToDifference()
    impl_sphere.AddFunction(sphere)

    outliner = vtk.vtkOutlineFilter()
    outliner.SetInputConnection(reader.GetOutputPort())
    outliner.Update()

    # Create mappers and actors.

    # Knee with lot of transparent slices
    actor_sliced = create_sliced_skin()

    # Knee with opacity on front-face and a sphere to see the patella
    actor_opaque = create_skin(impl_sphere)
    inside_skin = vtk.vtkProperty()
    inside_skin.SetColor(SKIN_COLOR)
    actor_opaque.SetBackfaceProperty(inside_skin)

    actor_opaque.GetProperty().SetOpacity(0.5)

    # Knee without opacity and with an opaque sphere to see the patella
    actor_knee_sphere = create_skin(impl_sphere)
    mapper = vtk.vtkPolyDataMapper()

    mapper.SetInputConnection(sphere_source.GetOutputPort())

    actor_sphere = vtk.vtkActor()
    actor_sphere.SetMapper(mapper)
    actor_sphere.GetProperty().SetOpacity(0.25)

    # Knee without skin
    bone_color = create_or_get_bone_distanced()


    # Create a rendering window.
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(500, 500)

    viewports = [(0.0, 0.0, 0.5, 0.5), (0.5, 0.0, 1.0, 0.5), (0.0, 0.5, 0.5, 1.0), (0.5, 0.5, 1.0, 1.0)]
    # Black Grey, Broken White, Silver, Space Grey
    bg_colors = [(0.1, 0.1, 0.1), (1.0, 0.95, 0.90), (0.902, 0.902, 0.902), (0.4, 0.4, 0.4)]

    camera = vtk.vtkCamera()

    # Create 4 renderers.
    # Add renderers to rendering window.
    renderers = []
    for i in range(4):
        renderers.append(vtk.vtkRenderer())
        renderers[i].SetViewport(viewports[i])
        renderWindow.AddRenderer(renderers[i])

        if i == 0:
            camera = renderers[i].GetActiveCamera()
        else:
            renderers[i].SetActiveCamera(camera)

        if i != 1:
            # Assign actor to the renderers.
            renderers[i].AddActor(create_bone())

        renderers[i].SetBackground(bg_colors[i])

    renderers[0].AddActor(actor_knee_sphere)
    renderers[0].AddActor(actor_sphere)
    renderers[1].AddActor(bone_color)
    renderers[2].AddActor(actor_sliced)
    renderers[3].AddActor(actor_opaque)

    # Pick a good view
    renderers[0].GetActiveCamera().SetPosition(-382.606608, -3.308563, 223.475751)
    renderers[0].GetActiveCamera().SetFocalPoint(77.311562, 72.821162, 100.000000)
    renderers[0].GetActiveCamera().SetViewUp(0.235483, 0.137775, 0.962063)
    renderers[0].GetActiveCamera().SetDistance(482.25171)
    renderers[0].GetActiveCamera().SetClippingRange(27.933848, 677.669341)

    # Create a renderwindowinteractor.
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    renderWindow.Render()

    # Enable user interface interactor.
    renderWindowInteractor.Initialize()
    renderWindow.Render()
    renderWindowInteractor.Start()
