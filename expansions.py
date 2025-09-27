# Additional class(es) that mimic(s) the expansion port in the fantasy hardware.

from display import Display
from external import * #numpy (np), pygame (pg), json
import math

screen = Display()

if __name__ == "__main__":
    print("\nwrong file opened brochacho, it's main.py\n")

class Accelerator:
    def __init__(self):
        self.camX = 0
        self.camY = 0
        self.camZ = 0
        self.fov = 90
        self.pitch = 0  # X rotation
        self.yaw = 0    # Y rotation
        self.roll = 0   # Z rotation (optional)
        self.near_clip = 0.001
        self.render_queue = []
        self.wireframe = False
        self.aai_cache = {}
        self.framerate_cap = 60
        self.clock = pg.time.Clock()
        self.renderwindow = (0, 0, 256, 192) #crop the whole 3d rendering area to this size (x, y, w, h)

    def load_aai(self, path, frame=0, crop=[0,0,0,0]):
        key = (path, frame, tuple(crop))
        if key in self.aai_cache:
            return self.aai_cache[key]
        try:
            with open(path, "r") as f:
                lines = f.read().strip().splitlines()
            if not lines or not lines[0].startswith("aai_"):
                return None
            header = lines[0]
            dim = header.split("_")[1].split("x")
            w, h = int(dim[0]), int(dim[1])
            frames = lines[1:]
            chosen = frames[frame % len(frames)]
            BASE25 = "0123456789ABCDEFGHIJKLMNO"
            flat = []
            i = 0
            while i + 1 < len(chosen):
                raw = BASE25.index(chosen[i])
                color = -1 if raw == 24 else raw
                run = BASE25.index(chosen[i + 1])
                flat.extend([color] * run)
                i += 2
            max_pixels = w * h
            if len(flat) > max_pixels:
                flat = flat[:max_pixels]
            elif len(flat) < max_pixels:
                flat.extend([-1] * (max_pixels - len(flat)))
            if crop != [0,0,0,0]:
                x1, y1, x2, y2 = crop
                x1 = max(0, min(x1, w))
                y1 = max(0, min(y1, h))
                x2 = max(0, min(x2, w))
                y2 = max(0, min(y2, h))
                if x2 > x1 and y2 > y1:
                    new_w = x2 - x1
                    new_h = y2 - y1
                    cropped = []
                    for yy in range(y1, y2):
                        row = flat[yy*w + x1 : yy*w + x2]
                        cropped.extend(row)
                    w, h = new_w, new_h
                    flat = cropped
            arr = np.array(flat, dtype=np.int16).reshape(h, w)
            self.aai_cache[key] = (w, h, arr)
            return self.aai_cache[key]
        except Exception as e:
            print(f"Error decoding AAI file {path}: {e}")
            return None

    def camera_transform(self, x, y, z):
        x -= self.camX
        y -= self.camY
        z -= self.camZ
        pitch = math.radians(self.pitch)
        yaw   = math.radians(self.yaw)
        roll  = math.radians(self.roll)
        xz = math.cos(yaw) * x + math.sin(yaw) * z
        zz = -math.sin(yaw) * x + math.cos(yaw) * z
        x, z = xz, zz
        yz = math.cos(pitch) * y - math.sin(pitch) * z
        zz = math.sin(pitch) * y + math.cos(pitch) * z
        y, z = yz, zz
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
        p1 = self.camera_transform(*position1)
        p2 = self.camera_transform(*position2)
        depth = (p1[2] + p2[2]) / 2.0
        proj1 = self.perspective_transform(*p1)
        proj2 = self.perspective_transform(*p2)
        if proj1 and proj2:
            self.render_queue.append(("line", depth, proj1, proj2, color, width))

    def draw_3d_poly(self, vertices, color=23):
        cam_verts = [self.camera_transform(x,y,z) for (x,y,z) in vertices]
        cam_verts = self.clip_polygon_near(cam_verts, self.near_clip)
        if len(cam_verts) < 3:
            return
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

    def draw_quad(self, position, rotation, size, color=23, offset=(0, 0, 0), cull_backface=True, texturedata=()):
        w, h = size
        corners = [
            (-w / 2, -h / 2, 0),
            ( w / 2, -h / 2, 0),
            ( w / 2,  h / 2, 0),
            (-w / 2,  h / 2, 0),
        ]
        rx, ry, rz = [math.radians(r) for r in rotation]
        rotated = []
        for x, y, z in corners:
            # Apply rotations in order: Z (roll), Y (yaw), X (pitch)
            x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
            x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
            y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
            #this is just about what I know about 3d math
            x += position[0] + offset[0]
            y += position[1] + offset[1]
            z += position[2] + offset[2]
            rotated.append((x, y, z))
        
        if cull_backface:
            # Calculate face normal using proper winding order
            # Use vertices 0, 1, 2 to determine face orientation
            v1 = (rotated[1][0] - rotated[0][0], rotated[1][1] - rotated[0][1], rotated[1][2] - rotated[0][2])
            v2 = (rotated[2][0] - rotated[0][0], rotated[2][1] - rotated[0][1], rotated[2][2] - rotated[0][2])
            
            # Cross product: v1 × v2
            normal = (
                v1[1] * v2[2] - v1[2] * v2[1],
                v1[2] * v2[0] - v1[0] * v2[2],
                v1[0] * v2[1] - v1[1] * v2[0],
            )
            
            # Calculate face center
            face_center = (
                sum(v[0] for v in rotated) / 4,
                sum(v[1] for v in rotated) / 4,
                sum(v[2] for v in rotated) / 4,
            )
            
            # View direction: from face center to camera
            view_dir = (
                self.camX - face_center[0],
                self.camY - face_center[1],
                self.camZ - face_center[2],
            )
            
            # Dot product: if positive, face is pointing toward camera (visible)
            # if negative, face is pointing away from camera (should be culled)
            dot_product = sum(n * v for n, v in zip(normal, view_dir))
            
            # Cull faces pointing away from camera (dot product < 0)
            if dot_product < 0:
                return
            
        #Wikipedia & stack overflow helped a lot

        # Transform to camera space and project to screen
        proj_verts = []
        depth_vals = []
        for vx, vy, vz in rotated:
            tx, ty, tz = self.camera_transform(vx, vy, vz)
            proj = self.perspective_transform(tx, ty, tz)
            if proj:
                proj_verts.append(proj)
                depth_vals.append(tz)
        
        # Partial clipping??
        if len(proj_verts) == 4:
            avg_depth = sum(depth_vals) / len(depth_vals)
            if texturedata:
                path, frame, crop = texturedata
                tex = self.load_aai(path, frame, crop)
                if tex:
                    self.render_queue.append(("affine_quad", avg_depth, proj_verts, tex))
            else:
                self.render_queue.append(("poly", avg_depth, proj_verts, color))

    def blit_affine(self, tex_array, src_tri, dst_tri):
        """
        Rasterize affine triangle with clipping to self.renderwindow. blahhh
        tex_array: HxW numpy array of palette indices (-1 transparent).
        src_tri: [(u,v),...] in texture space (pixels).
        dst_tri: [(x,y),...] in screen space.
        """
        h_tex, w_tex = tex_array.shape
        verts = sorted(zip(dst_tri, src_tri), key=lambda p: p[0][1])
        (p1, t1), (p2, t2), (p3, t3) = verts

        # Check if triangle has any area
        if abs(p1[1] - p3[1]) < 0.001:
            return  # Degenerate triangle. Stupid ahh triangle. Stewpid!!!

        # Get render window bounds
        rx, ry, rw, rh = self.renderwindow
        x_min_win, x_max_win = rx, rx + rw - 1
        y_min_win, y_max_win = ry, ry + rh - 1

        # Calculate bounding box but clip to render window vertically
        y_min = max(y_min_win, int(math.floor(p1[1])))
        y_max = min(y_max_win, int(math.ceil(p3[1])))

        # Skip if completely off-screen vertically
        if y_min > y_max:
            return

        # Pre-calc inverse slopes for the edges
        if abs(p2[1] - p1[1]) > 0.001:
            dx1_dy = (p2[0] - p1[0]) / (p2[1] - p1[1])
            du1_dy = (t2[0] - t1[0]) / (p2[1] - p1[1])
            dv1_dy = (t2[1] - t1[1]) / (p2[1] - p1[1])
        else:
            dx1_dy = du1_dy = dv1_dy = 0

        if abs(p3[1] - p1[1]) > 0.001:
            dx2_dy = (p3[0] - p1[0]) / (p3[1] - p1[1])
            du2_dy = (t3[0] - t1[0]) / (p3[1] - p1[1])
            dv2_dy = (t3[1] - t1[1]) / (p3[1] - p1[1])
        else:
            dx2_dy = du2_dy = dv2_dy = 0

        # Rasterize top half (p1 -> p2)
        y_split = min(int(math.ceil(p2[1])), y_max)
        for y in range(y_min, y_split):
            dy = y - p1[1]
            x_start = p1[0] + dy * dx1_dy
            x_end   = p1[0] + dy * dx2_dy
            u_start = t1[0] + dy * du1_dy
            v_start = t1[1] + dy * dv1_dy
            u_end   = t1[0] + dy * du2_dy
            v_end   = t1[1] + dy * dv2_dy

            if x_start > x_end:
                x_start, x_end = x_end, x_start
                u_start, u_end = u_end, u_start
                v_start, v_end = v_end, v_start

            x_min = max(x_min_win, int(math.ceil(x_start)))
            x_max = min(x_max_win, int(math.floor(x_end)))
            if x_min <= x_max:
                dx = x_end - x_start
                if abs(dx) > 0.001:
                    du_dx = (u_end - u_start) / dx
                    dv_dx = (v_end - v_start) / dx
                    u = u_start + (x_min - x_start) * du_dx
                    v = v_start + (x_min - x_start) * dv_dx
                    for x in range(x_min, x_max + 1):
                        ui, vi = int(u), int(v)
                        if 0 <= ui < w_tex and 0 <= vi < h_tex:
                            color = tex_array[vi, ui]
                            if color != -1:
                                screen.draw_pixel((x, y), color)
                        u += du_dx
                        v += dv_dx

        # Slopes for bottom half (p2 -> p3)
        if abs(p3[1] - p2[1]) > 0.001:
            dx3_dy = (p3[0] - p2[0]) / (p3[1] - p2[1])
            du3_dy = (t3[0] - t2[0]) / (p3[1] - p2[1])
            dv3_dy = (t3[1] - t2[1]) / (p3[1] - p2[1])
        else:
            dx3_dy = du3_dy = dv3_dy = 0

        # Rasterize bottom half (p2 -> p3)
        y_start_bottom = max(y_split, y_min)
        for y in range(y_start_bottom, y_max + 1):
            dy_p2 = y - p2[1]
            dy_p1 = y - p1[1]
            x_start = p2[0] + dy_p2 * dx3_dy
            x_end   = p1[0] + dy_p1 * dx2_dy
            u_start = t2[0] + dy_p2 * du3_dy
            v_start = t2[1] + dy_p2 * dv3_dy
            u_end   = t1[0] + dy_p1 * du2_dy
            v_end   = t1[1] + dy_p1 * dv2_dy

            if x_start > x_end:
                x_start, x_end = x_end, x_start
                u_start, u_end = u_end, u_start
                v_start, v_end = v_end, v_start

            # Ahh muy estudioso

            x_min = max(x_min_win, int(math.ceil(x_start)))
            x_max = min(x_max_win, int(math.floor(x_end)))
            if x_min <= x_max:
                dx = x_end - x_start
                if abs(dx) > 0.001:
                    du_dx = (u_end - u_start) / dx
                    dv_dx = (v_end - v_start) / dx
                    u = u_start + (x_min - x_start) * du_dx
                    v = v_start + (x_min - x_start) * dv_dx
                    for x in range(x_min, x_max + 1):
                        ui, vi = int(u), int(v)
                        if 0 <= ui < w_tex and 0 <= vi < h_tex:
                            color = tex_array[vi, ui]
                            if color != -1:
                                screen.draw_pixel((x, y), color)
                        u += du_dx
                        v += dv_dx


    def clip_polygon_near(self, vertices, near):
        if not vertices:
            return []
        clipped = []
        prev = vertices[-1]
        prev_inside = prev[2] >= near
        for curr in vertices:
            curr_inside = curr[2] >= near
            if prev_inside and curr_inside:
                clipped.append(curr)
            elif prev_inside and not curr_inside:
                t = (near - prev[2]) / (curr[2] - prev[2])
                xi = prev[0] + t * (curr[0] - prev[0])
                yi = prev[1] + t * (curr[1] - prev[1])
                zi = near
                clipped.append((xi, yi, zi))
            elif not prev_inside and curr_inside:
                t = (near - prev[2]) / (curr[2] - prev[2])
                xi = prev[0] + t * (curr[0] - prev[0])
                yi = prev[1] + t * (curr[1] - prev[1])
                zi = near
                clipped.append((xi, yi, zi))
                clipped.append(curr)
            prev = curr
            prev_inside = curr_inside
        return clipped

    def flush(self):
        rx, ry, rw, rh = self.renderwindow
        x_min, y_min = rx, ry
        x_max, y_max = rx + rw - 1, ry + rh - 1

        for obj in sorted(self.render_queue, key=lambda o: o[1], reverse=True):
            kind = obj[0]
            if kind == "point":
                _, _, (sx, sy), color = obj
                if x_min <= sx <= x_max and y_min <= sy <= y_max:
                    screen.draw_pixel((sx, sy), color)

            elif kind == "line":
                _, _, (sx1, sy1), (sx2, sy2), color, width = obj
                if (sx1 > x_max and sx2 > x_max) or (sx1 < x_min and sx2 < x_min) or \
                (sy1 > y_max and sy2 > y_max) or (sy1 < y_min and sy2 < y_min):
                    continue  # fully outside
                screen.draw_line((sx1, sy1), (sx2, sy2), color, width)

            elif kind == "poly":
                _, _, verts, color = obj
                if any(x_min <= vx <= x_max and y_min <= vy <= y_max for vx, vy in verts):
                    screen.draw_poly(verts, color, 1 if self.wireframe else 0)

            elif kind == "affine_quad":
                _, _, verts, tex = obj
                (tw, th, arr) = tex
                tris = [
                    (verts[0], verts[1], verts[2], [(0,0),(tw,0),(tw,th)]),
                    (verts[0], verts[2], verts[3], [(0,0),(tw,th),(0,th)])
                ]
                for tri in tris:
                    dst = tri[0:3]
                    src = tri[3]
                    # only draw if any vertex is inside viewport
                    if any(x_min <= vx <= x_max and y_min <= vy <= y_max for vx, vy in dst):
                        self.blit_affine(arr, src, dst)
        self.render_queue.clear()
        self.clock.tick(self.framerate_cap)
