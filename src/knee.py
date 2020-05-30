import vtk

# Based on https://lorensen.github.io/VTKExamples/site/Python/IO/ReadSLC/#code


def create_sphere(radius, center, theta_resolution=50, phi_resolution=50):
    sphere = vtk.vtkSphereSource()
    sphere.SetThetaResolution(theta_resolution)
    sphere.SetPhiResolution(phi_resolution)
    sphere.SetCenter(center[0], center[1], center[2])
    sphere.SetRadius(radius)

    return sphere


if __name__ == '__main__':
    # vtkSLCReader to read.
    reader = vtk.vtkSLCReader()
    reader.SetFileName('vw_knee.slc')
    reader.Update()

    # Implementing Marching Cubes Algorithm to create the surface using vtkContourFilter object.
    contourFilterBone = vtk.vtkContourFilter()
    contourFilterBone.SetInputConnection(reader.GetOutputPort())
    contourFilterBone.SetValue(0, 72.0)

    contourFilterBoneAndSkin = vtk.vtkContourFilter()
    contourFilterBoneAndSkin.SetInputConnection(reader.GetOutputPort())
    contourFilterBoneAndSkin.SetValue(0, 72.0)
    contourFilterBoneAndSkin.SetValue(1, 50.0)

    sphere = vtk.vtkSphere()
    sphere.SetRadius(00.1)
    sphere.SetCenter(0, 0, 0)

    impliciteFunction = vtk.vtkImplicitBoolean()
    impliciteFunction.SetOperationTypeToDifference()
    impliciteFunction.AddFunction(sphere)

    sample = vtk.vtkSampleFunction()
    sample.SetImplicitFunction(impliciteFunction)
    #sample.SetModelBounds(-1, 2, -1, 1, -1, 1)
    #sample.SetSampleDimensions(40, 40, 40)
    sample.ComputeNormalsOff()

    contourFilterBoneAndSkin.SetInputConnection(sample.GetOutputPort())

    outliner = vtk.vtkOutlineFilter()
    outliner.SetInputConnection(reader.GetOutputPort())
    outliner.Update()

    # Create 4 mappers and actors.
    actors = []
    mappers = []
    contourFilters = []
    for i in range(4):
        mappers.append(vtk.vtkPolyDataMapper())
        mappers[i].SetInputConnection(contourFilterBoneAndSkin.GetOutputPort())
        if i == 1:
            mappers[i].SetInputConnection(contourFilterBone.GetOutputPort())

        mappers[i].SetScalarVisibility(0)

        actors.append(vtk.vtkActor())
        actors[i].SetMapper(mappers[i])

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
        renderers[i].AddActor(actors[i])
        renderers[i].SetBackground(bg_colors[i])

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
