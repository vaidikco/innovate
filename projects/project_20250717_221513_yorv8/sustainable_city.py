import pyvista as pv
import numpy as np

# --- 1. Setup the 3D Scene ---
plotter = pv.Plotter(window_size=[1600, 900])
plotter.set_background('skyblue')

# Create a ground plane
ground = pv.Plane(center=(0, 0, -0.05), direction=(0, 0, 1), i_size=50, j_size=50)
plotter.add_mesh(ground, color='tan', ambient=0.4, diffuse=0.6)

# --- 2. Define Functions to Create City Elements ---

def create_building(center, height, width, depth, has_green_roof=False, has_solar=False):
    """Creates a building mesh."""
    body = pv.Cube(center=(center[0], center[1], center[2] + height / 2),
                   x_length=width, y_length=depth, z_length=height)
    plotter.add_mesh(body, color='ivory', ambient=0.3, diffuse=0.7, metallic=0.2, roughness=0.5)

    if has_green_roof:
        roof = pv.Plane(center=(center[0], center[1], center[2] + height + 0.01),
                        direction=(0, 0, 1), i_size=width, j_size=depth)
        plotter.add_mesh(roof, color='green')
    elif has_solar:
        panel_center = (center[0], center[1], center[2] + height + 0.01)
        solar_panel = pv.Plane(center=panel_center, direction=(0, 0, 1), i_size=width*0.8, j_size=depth*0.8)
        plotter.add_mesh(solar_panel, color='darkblue')

def create_wind_turbine(center, height=15):
    """Creates a wind turbine model."""
    tower = pv.Cylinder(center=(center[0], center[1], center[2] + height / 2),
                        direction=(0, 0, 1), radius=0.3, height=height)
    plotter.add_mesh(tower, color='lightgrey')

    hub_center = (center[0], center[1], center[2] + height)
    hub = pv.Sphere(center=hub_center, radius=0.5)
    plotter.add_mesh(hub, color='grey')

    for i in range(3):
        angle = np.deg2rad(120 * i)
        blade = pv.Box(bounds=(-0.1, 0.1, -0.5, 5, -0.1, 0.1))
        blade.translate((0, 2.5, 0), inplace=True)
        blade.rotate('z', 120 * i, point=pv.vector(0,0,0), inplace=True)
        blade.translate(hub_center, inplace=True)
        plotter.add_mesh(blade, color='white')

def create_park(center, size):
    """Creates a green park area."""
    park_ground = pv.Plane(center=(center[0], center[1], 0), direction=(0, 0, 1),
                           i_size=size[0], j_size=size[1])
    plotter.add_mesh(park_ground, color='lightgreen')
    # Add some trees
    for _ in range(10):
        x_offset = np.random.uniform(-size[0]/2.2, size[0]/2.2)
        y_offset = np.random.uniform(-size[1]/2.2, size[1]/2.2)
        trunk = pv.Cylinder(center=(center[0]+x_offset, center[1]+y_offset, 1), radius=0.1, height=2)
        leaves = pv.Cone(center=(center[0]+x_offset, center[1]+y_offset, 2.5), radius=0.5, height=2)
        plotter.add_mesh(trunk, color='saddlebrown')
        plotter.add_mesh(leaves, color='darkgreen')

def create_road(start, end, width=1.0):
    """Creates a road segment."""
    path = np.array([start, end])
    # Use a simple box for a flat road
    mid_point = (path[0] + path[1]) / 2
    length = np.linalg.norm(path[1] - path[0])
    direction = path[1] - path[0]
    angle = np.degrees(np.arctan2(direction[1], direction[0]))
    road_mesh = pv.Cube(center=(mid_point[0], mid_point[1], mid_point[2]), x_length=length, y_length=width, z_length=0.02)
    road_mesh.rotate('z', angle, inplace=True)
    plotter.add_mesh(road_mesh, color='darkgrey')

# --- 3. Assemble the City ---

# Downtown area with tall buildings
create_building(center=(-10, 0, 0), height=10, width=4, depth=4, has_solar=True)
create_building(center=(-5, -2, 0), height=12, width=3, depth=5, has_solar=True)
create_building(center=(-8, 5, 0), height=8, width=5, depth=3, has_green_roof=True)

# Residential area
create_building(center=(5, 10, 0), height=3, width=2, depth=3, has_green_roof=True)
create_building(center=(8, 10, 0), height=2.5, width=2, depth=3, has_solar=True)
create_building(center=(5, 13, 0), height=3, width=3, depth=2, has_green_roof=True)

# Park
create_park(center=(10, 0, 0), size=(10, 15))

# Wind farm
create_wind_turbine(center=(-15, -15, 0))
create_wind_turbine(center=(-18, -12, 0))
create_wind_turbine(center=(-12, -18, 0))

# Roads
create_road((-20, -5, 0.01), (20, -5, 0.01), width=1.5)
create_road((-1, -20, 0.01), (-1, 20, 0.01), width=1.5)
create_road((-12, -5, 0.01), (-1, -5, 0.01), width=1.0)
create_road((-1, 8, 0.01), (15, 8, 0.01), width=1.0)


# --- 4. Finalize and Show the Scene ---
# Add a light source
light = pv.Light(position=(20, 20, 50), focal_point=(0, 0, 0), color='white')
light.intensity = 1.2
plotter.add_light(light)

# Set camera position and view
plotter.camera_position = 'xy'
plotter.camera.azimuth = 30
plotter.camera.elevation = 30
plotter.camera.zoom(1.2)

# Display the plotter
plotter.show()

# Powered by Innovate CLI, a product of vaidik.co
