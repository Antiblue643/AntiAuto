#The Accelerator extension.

from external import * #numpy (np), pygame (pg), json
import math

if __name__ == "__main__":
    print("\nwrong file opened brochacho, it's main.py\n")

class Accelerator:
    def __init__(self, screen):
        self.screen = screen
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
        import numpy as _np
        self._np = np
        rx, ry, rw, rh = self.renderwindow
        self.zbuffer = _np.full((rh, rw), float("inf"), dtype=_np.float32)

    #Idk what happened to the docstrings sorry

    def load_aai(self, path, frame=0, crop=[0,0,0,0]):
        key = (path, frame, tuple(crop))
        if key in self.aai_cache:
            return self.aai_cache[key]
        try:
            with open(path, "r") as f:
                lines = f.read().strip().splitlines()
            if not lines or not lines[0].startswith("pdaai_"):
                return None
            header = lines[0]
            dim = header.split("_")[1].split("x")
            w, h = int(dim[0]), int(dim[1])
            frames = lines[1:]
            chosen = frames[frame % len(frames)]
            BASE64 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/="
            flat = []
            i = 0
            while i + 1 < len(chosen):
                raw = BASE64.index(chosen[i])
                color = -1 if raw == 64 else raw  # 63 is '=' in BASE64, used as transparent
                run = BASE64.index(chosen[i + 1])
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
                sx, sy = proj
                proj_verts.append(((sx, sy), tz))  # store (screen coords), camera-space z
                depth_vals.append(tz)
        if len(proj_verts) == 4:
            avg_depth = sum(depth_vals) / len(depth_vals)
            if texturedata:
                path, frame, crop = texturedata
                tex = self.load_aai(path, frame, crop)
                if tex:
                    # Enqueue a perspective textured quad (pass per-vertex (x,y,z))
                    verts_with_z = [(p[0][0], p[0][1], p[1]) for p in proj_verts]  # list of (x,y,z)
                    self.render_queue.append(("perspective_quad", avg_depth, verts_with_z, tex))
            else:
                verts = [v[0] for v in proj_verts]
                self.render_queue.append(("poly", avg_depth, verts, color))

    def blit_perspective_triangle(self, tex_array, src_tri_uv, dst_tri_xy_z):
        """
        tex_array: H x W numpy array of palette indices (-1 transparent).
        src_tri_uv: [(u,v), (u,v), (u,v)] in texture pixel coordinates.
        dst_tri_xy_z: [(x,y,z), ...] in screen coords with camera-space z (positive forward).
        Uses barycentric coordinates with perspective correction (interpolate u/z, v/z and 1/z).
        Updates per-pixel zbuffer and writes pixels via self.screen.draw_pixel((x,y), color).
        """
        h_tex, w_tex = tex_array.shape
        # Unpack
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = dst_tri_xy_z
        (u0, v0), (u1, v1), (u2, v2) = src_tri_uv

        # Bounding box (integer) clipped to render window
        rx, ry, rw, rh = self.renderwindow
        x_min = max(rx, int(math.floor(min(x0, x1, x2))))
        x_max = min(rx + rw - 1, int(math.ceil(max(x0, x1, x2))))
        y_min = max(ry, int(math.floor(min(y0, y1, y2))))
        y_max = min(ry + rh - 1, int(math.ceil(max(y0, y1, y2))))
        if x_min > x_max or y_min > y_max:
            return

        # Precompute edge function denominator (triangle area * 2)
        denom = ( (y1 - y2)*(x0 - x2) + (x2 - x1)*(y0 - y2) )
        if abs(denom) < 1e-6:
            return  # degenerate

        inv_denom = 1.0 / denom

        # Precompute u_over_z, v_over_z, and one_over_z at vertices
        # (Note: z is camera-space Z; ensure non-zero)
        # If z <= 0 (behind camera or too close), bail out for safety on that vertex - we'll still rasterize if barycentric avoids it.
        # But best to skip triangles with any z <= self.near_clip (clipping should have handled most).
        one_over_z0 = 1.0 / z0
        one_over_z1 = 1.0 / z1
        one_over_z2 = 1.0 / z2

        uoz0 = u0 * one_over_z0
        uoz1 = u1 * one_over_z1
        uoz2 = u2 * one_over_z2
        voz0 = v0 * one_over_z0
        voz1 = v1 * one_over_z1
        voz2 = v2 * one_over_z2

        # Convenience references
        np = self._np
        zbuf = self.zbuffer  # shape (rh, rw) row-major
        # For indexing into zbuffer: idx_x = x - rx, idx_y = y - ry

        # Rasterize
        for py in range(y_min, y_max + 1):
            for px in range(x_min, x_max + 1):
                # Compute barycentric coordinates using edge functions
                w0 = ( (y1 - y2)*(px - x2) + (x2 - x1)*(py - y2) ) * inv_denom
                w1 = ( (y2 - y0)*(px - x2) + (x0 - x2)*(py - y2) ) * inv_denom
                w2 = 1.0 - w0 - w1
                # If pixel is inside triangle (allow top/left rule: >=0)
                if w0 >= -1e-6 and w1 >= -1e-6 and w2 >= -1e-6:
                    # Interpolate 1/z, u/z, v/z
                    one_over_z = w0 * one_over_z0 + w1 * one_over_z1 + w2 * one_over_z2
                    if one_over_z <= 0:
                        continue
                    z = 1.0 / one_over_z
                    # Depth test: smaller z is closer (camera looks down +Z)
                    idx_x = px - rx
                    idx_y = py - ry
                    if idx_x < 0 or idx_x >= rw or idx_y < 0 or idx_y >= rh:
                        continue
                    if z >= zbuf[idx_y, idx_x]:
                        continue
                    # interpolate tex coords
                    u_over_z = w0 * uoz0 + w1 * uoz1 + w2 * uoz2
                    v_over_z = w0 * voz0 + w1 * voz1 + w2 * voz2
                    u = u_over_z * z
                    v = v_over_z * z
                    ui = int(u)
                    vi = int(v)
                    if 0 <= ui < w_tex and 0 <= vi < h_tex:
                        color = int(tex_array[vi, ui])  # palette index (possibly -1)
                        if color != -1:
                            # Pass to display; update zbuffer
                            self.screen.draw_pixel((px, py), color)
                            zbuf[idx_y, idx_x] = z

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

        # Reset zbuffer each frame (far away)
        self.zbuffer.fill(float("inf"))

        for obj in sorted(self.render_queue, key=lambda o: o[1], reverse=True):
            kind = obj[0]
            if kind == "point":
                _, _, (sx, sy), color = obj
                if x_min <= sx <= x_max and y_min <= sy <= y_max:
                    self.screen.draw_pixel((sx, sy), color)

            elif kind == "line":
                _, _, (sx1, sy1), (sx2, sy2), color, width = obj
                if (sx1 > x_max and sx2 > x_max) or (sx1 < x_min and sx2 < x_min) or \
                (sy1 > y_max and sy2 > y_max) or (sy1 < y_min and sy2 < y_min):
                    continue  # fully outside
                self.screen.draw_line((sx1, sy1), (sx2, sy2), color, width)

            elif kind == "poly":
                _, _, verts, color = obj
                if any(x_min <= vx <= x_max and y_min <= vy <= y_max for vx, vy in verts):
                    self.screen.draw_poly(verts, color, 1 if self.wireframe else 0)

            elif kind == "perspective_quad":
                _, _, verts_with_z, tex = obj
                (tw, th, arr) = tex
                # Split quad into two triangles, but provide per-vertex z values
                # verts_with_z: list of (x,y,z) in order [v0, v1, v2, v3]
                tris = [
                    ( (verts_with_z[0], verts_with_z[1], verts_with_z[2]),
                      ( (0,0), (tw,0), (tw,th) ) ),
                    ( (verts_with_z[0], verts_with_z[2], verts_with_z[3]),
                      ( (0,0), (tw,th), (0,th) ) ),
                ]
                for dst_verts, src_uvs in tris:
                    # Quick viewport check
                    if any(x_min <= v[0] <= x_max and y_min <= v[1] <= y_max for v in dst_verts):
                        # call perspective-correct triangle blitter
                        self.blit_perspective_triangle(arr, src_uvs, dst_verts)

        self.render_queue.clear()
        self.clock.tick(self.framerate_cap)