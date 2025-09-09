# Additional class(es) that mimic(s) the expansion port in the fantasy hardware.

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
        self.render_queue = []
        self.wireframe = False
        self.aai_cache = {}

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
            x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
            x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
            y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
            x += position[0] + offset[0]
            y += position[1] + offset[1]
            z += position[2] + offset[2]
            rotated.append((x, y, z))
        if cull_backface:
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
                return
        proj_verts = []
        depth_vals = []
        for vx, vy, vz in rotated:
            tx, ty, tz = self.camera_transform(vx, vy, vz)
            proj = self.perspective_transform(tx, ty, tz)
            if proj:
                proj_verts.append(proj)
                depth_vals.append(tz)
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
        Rasterize affine triangle using a general-purpose scanline approach.
        tex_array: HxW numpy array of palette indices (-1 transparent).
        src_tri: [(u,v),...] in texture space (pixels).
        dst_tri: [(x,y),...] in screen space.
        """
        h_tex, w_tex = tex_array.shape
        verts = sorted(zip(dst_tri, src_tri), key=lambda p: p[0][1])
        (p1, t1), (p2, t2), (p3, t3) = verts

        if p1[1] == p3[1]:
            return # A degenerate triangle with no height

        # Calculate bounding box for the triangle
        y_min = max(0, int(p1[1]))
        y_max = min(191, int(p3[1]))

        # Pre-calculate inverse slopes for the edges
        if p2[1] != p1[1]:
            dx1_dy = (p2[0] - p1[0]) / (p2[1] - p1[1])
            du1_dy = (t2[0] - t1[0]) / (p2[1] - p1[1])
            dv1_dy = (t2[1] - t1[1]) / (p2[1] - p1[1])
        else:
            dx1_dy, du1_dy, dv1_dy = 0, 0, 0

        if p3[1] != p1[1]:
            dx2_dy = (p3[0] - p1[0]) / (p3[1] - p1[1])
            du2_dy = (t3[0] - t1[0]) / (p3[1] - p1[1])
            dv2_dy = (t3[1] - t1[1]) / (p3[1] - p1[1])
        else:
            dx2_dy, du2_dy, dv2_dy = 0, 0, 0

        # Rasterize top half
        for y in range(y_min, min(int(p2[1]), y_max)):
            if y < 0: continue
            
            x_start = p1[0] + (y - p1[1]) * dx1_dy
            x_end = p1[0] + (y - p1[1]) * dx2_dy
            u_start = t1[0] + (y - p1[1]) * du1_dy
            v_start = t1[1] + (y - p1[1]) * dv1_dy
            u_end = t1[0] + (y - p1[1]) * du2_dy
            v_end = t1[1] + (y - p1[1]) * dv2_dy

            if x_start > x_end:
                x_start, x_end = x_end, x_start
                u_start, u_end = u_end, u_start
                v_start, v_end = v_end, v_start
            
            dx = x_end - x_start
            if dx != 0:
                du_dx = (u_end - u_start) / dx
                dv_dx = (v_end - v_start) / dx
            else:
                du_dx, dv_dx = 0, 0

            u, v = u_start, v_start
            for x in range(max(0, int(x_start)), min(255, int(x_end) + 1)):
                ui, vi = int(u), int(v)
                if 0 <= ui < w_tex and 0 <= vi < h_tex:
                    color = tex_array[vi, ui]
                    if color != -1:
                        screen.draw_pixel((x, y), color)
                u += du_dx
                v += dv_dx

        # Pre-calculate inverse slopes for the second part of the triangle (from p2 to p3)
        if p3[1] != p2[1]:
            dx3_dy = (p3[0] - p2[0]) / (p3[1] - p2[1])
            du3_dy = (t3[0] - t2[0]) / (p3[1] - p2[1])
            dv3_dy = (t3[1] - t2[1]) / (p3[1] - p2[1])
        else:
            dx3_dy, du3_dy, dv3_dy = 0, 0, 0

        # Rasterize bottom half
        for y in range(int(p2[1]), y_max):
            if y < 0: continue
            
            x_start = p2[0] + (y - p2[1]) * dx3_dy
            x_end = p1[0] + (y - p1[1]) * dx2_dy
            u_start = t2[0] + (y - p2[1]) * du3_dy
            v_start = t2[1] + (y - p2[1]) * dv3_dy
            u_end = t1[0] + (y - p1[1]) * du2_dy
            v_end = t1[1] + (y - p1[1]) * dv2_dy

            if x_start > x_end:
                x_start, x_end = x_end, x_start
                u_start, u_end = u_end, u_start
                v_start, v_end = v_end, v_start

            dx = x_end - x_start
            if dx != 0:
                du_dx = (u_end - u_start) / dx
                dv_dx = (v_end - v_start) / dx
            else:
                du_dx, dv_dx = 0, 0
                
            u, v = u_start, v_start
            for x in range(max(0, int(x_start)), min(255, int(x_end) + 1)):
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
                    self.blit_affine(arr, src, dst)
        self.render_queue.clear()