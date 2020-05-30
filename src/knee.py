import vtk

SKIN_COLOR = (225 / 255, 172 / 255, 150 / 255)

# Based on https://lorensen.github.io/VTKExamples/site/Python/IO/ReadSLC/#code


def create_sphere(radius, center, thetaResolution = 50, phiResolution = 50):
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
    cf_bone = create_contour(72.0)
    mapper_bone = vtk.vtkPolyDataMapper()
    mapper_bone.SetInputConnection(cf_bone.GetOutputPort())
    mapper_bone.SetScalarVisibility(0)

    bone = vtk.vtkActor()
    bone.SetMapper(mapper_bone)

    return bone


def create_skin(implicit_function = False):
    cf_skin = create_contour(50.0)

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
    actor_sliced = create_skin()

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
    actor_bone = create_bone()

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

        # Assign actor to the renderers.
        renderers[i].AddActor(actor_bone)
        renderers[i].SetBackground(bg_colors[i])

    renderers[0].AddActor(actor_knee_sphere)
    renderers[0].AddActor(actor_sphere)
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
