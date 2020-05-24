import vtk

# Based on https://lorensen.github.io/VTKExamples/site/Python/IO/ReadSLC/#code

if __name__ == '__main__':
    colors = vtk.vtkNamedColors()

    # vtkSLCReader to read.
    reader = vtk.vtkSLCReader()
    reader.SetFileName('vw_knee.slc')
    reader.Update()

    # Create a mapper.
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    # Implementing Marching Cubes Algorithm to create the surface using vtkContourFilter object.
    contourFilter = vtk.vtkContourFilter()
    contourFilter.SetInputConnection(reader.GetOutputPort())
    contourFilter.SetValue(0, 72.0)

    outliner = vtk.vtkOutlineFilter()
    outliner.SetInputConnection(reader.GetOutputPort())
    outliner.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(contourFilter.GetOutputPort())
    mapper.SetScalarVisibility(0)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

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
        renderers[i].AddActor(actor)
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
