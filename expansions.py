# Additional classes that mimic the expansion port in the fantasy hardware.

from display import Display
from external import *
import math

screen = Display()

class Accelerator:
    def __init__(self):
        self.camX = 0
        self.camY = 0
        self.camZ = 0
        self.fov = 90
        self.pitch = 0  # X rotation
        self.yaw = 0    # Y rotation
        self.roll = 0   # Z rotation (optional)
        self.near_clip = 0.1
        self.render_queue = []  # store objects for depth sorting
        self.wireframe = False # render polygons as wireframe (no fill)
        self.texture_cache = {}

    def camera_transform(self, x, y, z):
        """Transform world coordinates into camera space"""
        x -= self.camX
        y -= self.camY
        z -= self.camZ

        # Convert angles
        pitch = math.radians(self.pitch)
        yaw   = math.radians(self.yaw)
        roll  = math.radians(self.roll)

        # Rotation around Y (yaw)
        xz = math.cos(yaw) * x + math.sin(yaw) * z
        zz = -math.sin(yaw) * x + math.cos(yaw) * z
        x, z = xz, zz

        # Rotation around X (pitch)
        yz = math.cos(pitch) * y - math.sin(pitch) * z
        zz = math.sin(pitch) * y + math.cos(pitch) * z
        y, z = yz, zz

        # Rotation around Z (roll)
        xx = math.cos(roll) * x - math.sin(roll) * y
        yy = math.sin(roll) * x + math.cos(roll) * y
        x, y = xx, yy

        return x, y, z

    def perspective_transform(self, x, y, z):
        if z < self.near_clip:
            return None
        fov_rad = math.radians(self.fov)
        scale = 1.0 / math.tan(fov_rad / 2.0)
        sx = (x / z) * scale * 128 + 128
        sy = (y / z) * scale * 96 + 96
        return int(sx), int(sy)

    def draw_3d_point(self, position, color=0):
        tx, ty, tz = self.camera_transform(*position)
        proj = self.perspective_transform(tx, ty, tz)
        if proj:
            sx, sy = proj
            self.render_queue.append(("point", tz, (sx, sy), color))

    def draw_3d_line(self, position1, position2, color=23, width=1):
        """
        Draw a 3D line between 2 points.
        Args:
            position1: The (x, y, z) coordinates of the first point.
            position2: The (x, y, z) coordinates of the second point.
            color: The color of the line.
            width: The width of the line.
        """
        p1 = self.camera_transform(*position1)
        p2 = self.camera_transform(*position2)
        depth = (p1[2] + p2[2]) / 2.0

        proj1 = self.perspective_transform(*p1)
        proj2 = self.perspective_transform(*p2)

        if proj1 and proj2:
            self.render_queue.append(("line", depth, proj1, proj2, color, width))

    def draw_3d_poly(self, vertices, color=23):
        """
        Draw a convex polygon in 3D space with near-plane clipping.
        Args:
            vertices: list of (x,y,z) world coords
            color: fill color
        """
        # Transform into camera space
        cam_verts = [self.camera_transform(x,y,z) for (x,y,z) in vertices]

        # Clip against near plane
        cam_verts = self.clip_polygon_near(cam_verts, self.near_clip)
        if len(cam_verts) < 3:
            return  # fully clipped

        # Project to screen
        screen_verts = []
        depth_vals = []
        for vx, vy, vz in cam_verts:
            proj = self.perspective_transform(vx, vy, vz)
            if proj:
                screen_verts.append(proj)
                depth_vals.append(vz)

        if len(screen_verts) >= 3:
            avg_depth = sum(depth_vals) / len(depth_vals)
            self.render_queue.append(("poly", avg_depth, screen_verts, color))

    def get_texture(self, path, frame=0, crop=[0,0,0,0]):
        key = (path, frame, tuple(crop))
        if key not in self.texture_cache:
            surf = screen.get_aai_surface(path, frame, crop)
            if surf:
                self.texture_cache[key] = surf
        return self.texture_cache.get(key)


    def draw_quad(self, position, rotation, size, color=23, pivot=(0, 0), offset=(0, 0, 0), backface_culling=True, texturedata=()):
        """
        Draw a 3D quad with optional backface culling.
        Args:
            position: The (x, y, z) coordinates of the quad's center.
            rotation: The (pitch, yaw, roll) rotation angles.
            size: The (width, height) dimensions of the quad.
            color: The color of the quad.
            pivot: The (x, y) pivot point on the quad for the quad's rotation (0, 0) is the center.
            offset: The (x, y, z) offset from the pivot for the quad's rotation.
            backface_culling: Whether to cull the backface of the quad.
            texturedata: The (path, mode, u, v, scale) of the aai texture. Doesn't work for now.
        """
        w, h = size
        corners = [
            (-w / 2, -h / 2, 0),
            (w / 2, -h / 2, 0),
            (w / 2, h / 2, 0),
            (-w / 2, h / 2, 0),
        ]

        rx, ry, rz = [math.radians(r) for r in rotation]
        offset_x, offset_y, offset_z = offset

        rotated = []
        for x, y, z in corners:
            # Translate pivot offset
            x -= pivot[0]
            y -= pivot[1]

            # Z
            x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
            # Y
            x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
            # X
            y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)

            # Translate offset
            x += offset_x
            y += offset_y
            z += offset_z

            # Translate to new position
            x += position[0]
            y += position[1]
            z += position[2]
            rotated.append((x, y, z))

        # Backface culling
        if backface_culling:
            v1 = (rotated[1][0] - rotated[0][0], rotated[1][1] - rotated[0][1], rotated[1][2] - rotated[0][2])
            v2 = (rotated[2][0] - rotated[0][0], rotated[2][1] - rotated[0][1], rotated[2][2] - rotated[0][2])
            normal = (
                v1[1] * v2[2] - v1[2] * v2[1],
                v1[2] * v2[0] - v1[0] * v2[2],
                v1[0] * v2[1] - v1[1] * v2[0],
            )
            view_dir = (
                rotated[0][0] - self.camX,
                rotated[0][1] - self.camY,
                rotated[0][2] - self.camZ,
            )
            dot_product = sum(n * v for n, v in zip(normal, view_dir))
            if dot_product >= 0:
                return  # Backface is facing away, so skip rendering

        # if texturedata:
            # path, frame, crop = texturedata
            # surf = self.get_texture(path, frame, crop)
            # if surf:
                # self.render_queue.append(("textured_quad", sum(v[2] for v in rotated)/4, rotated, surf))
        # else:
        self.draw_3d_poly(rotated, color)

    def clip_polygon_near(self, vertices, near):
        #jeez
        """
        Clip a polygon against the near plane z=near.
        vertices: list of (x,y,z) in camera space
        Returns: list of clipped vertices in camera space
        """
        if not vertices:
            return []

        clipped = []
        prev = vertices[-1]
        prev_inside = prev[2] >= near

        for curr in vertices:
            curr_inside = curr[2] >= near

            if prev_inside and curr_inside:
                # both inside
                clipped.append(curr)

            elif prev_inside and not curr_inside:
                # leaving – add intersection
                t = (near - prev[2]) / (curr[2] - prev[2])
                xi = prev[0] + t * (curr[0] - prev[0])
                yi = prev[1] + t * (curr[1] - prev[1])
                zi = near
                clipped.append((xi, yi, zi))

            elif not prev_inside and curr_inside:
                # entering – add intersection + current
                t = (near - prev[2]) / (curr[2] - prev[2])
                xi = prev[0] + t * (curr[0] - prev[0])
                yi = prev[1] + t * (curr[1] - prev[1])
                zi = near
                clipped.append((xi, yi, zi))
                clipped.append(curr)

            # else: both outside then add nothing

            prev = curr
            prev_inside = curr_inside

        return clipped

    def flush(self):
        # Sort farthest to nearest
        for obj in sorted(self.render_queue, key=lambda o: o[1], reverse=True):
            kind = obj[0]
            if kind == "point":
                _, _, (sx, sy), color = obj
                screen.draw_pixel((sx, sy), color)

            elif kind == "line":
                _, _, (sx1, sy1), (sx2, sy2), color, width = obj
                screen.draw_line((sx1, sy1), (sx2, sy2), color, width)

            elif kind == "poly":
                _, _, verts, color = obj
                screen.draw_poly(verts, color, 1 if self.wireframe else 0)

            elif kind == "textured_quad":
                _, _, verts, surf = obj
                if len(verts) == 4:
                    pts = [(vx, vy) for vx, vy, vz in (self.camera_transform(*v) for v in verts)]
                    pts = [self.perspective_transform(x,y,z) for (x,y,z) in verts]
                    if None not in pts:
                        # Transform AAI surface to match quad shape
                        # Use pygame.transform.scale/rotate or a warp if available
                        # For simplicity: just blit centered at avg point
                        cx = sum(p[0] for p in pts)//4
                        cy = sum(p[1] for p in pts)//4
                        screen_surface = surf
                        screen_surface = pg.transform.scale(surf, (int(abs(pts[1][0]-pts[0][0])), int(abs(pts[2][1]-pts[1][1]))))
                        screen_surface.set_colorkey((0,0,0))  # optional transparency
                        screen_surface.convert_alpha()
                        screen.blit(screen_surface, (cx - screen_surface.get_width()//2, cy - screen_surface.get_height()//2))

        self.render_queue.clear()

class Inverter: # Inverts colors
    def __init__(self):
        pass