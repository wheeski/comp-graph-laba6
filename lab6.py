import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.messagebox import showinfo
import math


class PixelTransformation:
    def __init__(self, root):
        self.root = root
        self.root.title("Аффинные и нелинейные преобразования")
        self.root.geometry("1400x700")

        # Создание фреймов для изображений в один ряд
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Исходное изображение
        self.frame1_container = ttk.Frame(self.main_frame)
        self.frame1_container.pack(side=tk.LEFT, anchor=tk.N, padx=10, pady=10)

        ttk.Label(self.frame1_container, text="Исходное изображение").pack(pady=5)
        self.f1 = tk.Frame(self.frame1_container, width=300, height=300, relief="solid", bg="white")
        self.f1.pack(pady=5)
        self.f1.pack_propagate(False)

        self.frame1 = tk.Label(self.f1, bg="white")
        self.frame1.pack(expand=True)

        ttk.Button(self.frame1_container, text="Открыть фото", command=self.open_image).pack(pady=5)

        # Аффинное преобразование
        self.frame2_container = ttk.Frame(self.main_frame)
        self.frame2_container.pack(side=tk.LEFT, anchor=tk.N, padx=10, pady=10)

        ttk.Label(self.frame2_container, text="Аффинное преобразование").pack(pady=5)
        self.f2 = tk.Frame(self.frame2_container, width=300, height=300, relief="solid", bg="white")
        self.f2.pack(pady=5)
        self.f2.pack_propagate(False)

        self.frame2 = tk.Label(self.f2, bg="white")
        self.frame2.pack(expand=True)

        ttk.Label(self.frame2_container, text="Масштаб:").pack(pady=2)
        self.scale_entry = ttk.Entry(self.frame2_container, width=10)
        self.scale_entry.insert(0, "1.5")
        self.scale_entry.pack(pady=2)

        ttk.Label(self.frame2_container, text="Перенос X, Y:").pack(pady=2)
        self.shift_entry = ttk.Entry(self.frame2_container, width=10)
        self.shift_entry.insert(0, "30 15")
        self.shift_entry.pack(pady=2)

        ttk.Button(self.frame2_container, text="Применить", command=self.affine_transform).pack(pady=2)
        ttk.Button(self.frame2_container, text="Сохранить", command=lambda: self.save_specific_result("affine")).pack(
            pady=2)

        # Восстановленное изображение
        self.frame3_container = ttk.Frame(self.main_frame)
        self.frame3_container.pack(side=tk.LEFT, anchor=tk.N, padx=10, pady=10)

        ttk.Label(self.frame3_container, text="Восстановленное изображение").pack(pady=5)
        self.f3 = tk.Frame(self.frame3_container, width=300, height=300, relief="solid", bg="white")
        self.f3.pack(pady=5)
        self.f3.pack_propagate(False)

        self.frame3 = tk.Label(self.f3, bg="white")
        self.frame3.pack(expand=True)

        ttk.Button(self.frame3_container, text="Восстановить", command=self.restore_affine).pack(pady=5)
        ttk.Button(self.frame3_container, text="Сохранить", command=lambda: self.save_specific_result("restored")).pack(
            pady=2)

        # Нелинейное преобразование
        self.frame4_container = ttk.Frame(self.main_frame)
        self.frame4_container.pack(side=tk.LEFT, anchor=tk.N, padx=10, pady=10)

        ttk.Label(self.frame4_container, text="Нелинейное преобразование").pack(pady=5)
        self.f4 = tk.Frame(self.frame4_container, width=300, height=300, relief="solid", bg="white")
        self.f4.pack(pady=5)
        self.f4.pack_propagate(False)

        self.frame4 = tk.Label(self.f4, bg="white")
        self.frame4.pack(expand=True)

        ttk.Button(self.frame4_container, text="Применить", command=self.nonlinear_transform).pack(pady=5)
        ttk.Button(self.frame4_container, text="Сохранить",
                   command=lambda: self.save_specific_result("nonlinear")).pack(pady=2)

        self.original_img = None
        self.original_bytes = None
        self.affine_result = None
        self.nonlinear_result = None
        self.restored_result = None

    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Выберите PPM файл",
            filetypes=[("PPM files", "*.ppm"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            image = tk.PhotoImage(file=file_path)
            self.original_img = image
            scaled_img = self.scale_image(image, 300, 300)
            self.frame1.config(image=scaled_img)
            self.frame1.image = scaled_img
            self.original_bytes = self.get_file_bytes(file_path)
            self.affine_result = None
            self.restored_result = None
            self.nonlinear_result = None
        except Exception as e:
            showinfo("Ошибка", f"Не удалось загрузить изображение: {e}")

    def get_file_bytes(self, file_path):
        with open(file_path, 'rb') as f:
            signature = f.readline().strip()
            if signature != b'P6':
                raise ValueError("Это не PPM файл")
            width, height = f.readline().split()
            width, height = int(width), int(height)
            f.readline()
            pixels = list(f.read())
        return width, height, pixels

    def affine_transform(self):
        """Прямое аффинное преобразование: масштабирование + перенос с сохранением краев"""
        if not self.original_bytes:
            showinfo("Ошибка", "Сначала откройте изображение")
            return

        try:
            scale = float(self.scale_entry.get())
            shift_x, shift_y = map(float, self.shift_entry.get().split())
            if not math.isfinite(scale) or scale <= 0 or not all(map(math.isfinite, (shift_x, shift_y))):
                raise ValueError
        except:
            scale = 1.5
            shift_x, shift_y = 30, 15
        orig_width, orig_height, orig_pixels = self.original_bytes

        # Увеличиваем размер изображения, чтобы вместить преобразованное
        scale_factor = max(2, scale)
        new_width = math.ceil(orig_width * scale_factor + 2 * abs(shift_x))
        new_height = math.ceil(orig_height * scale_factor + 2 * abs(shift_y))

        # Создаем новое изображение большего размера
        new_pixels = [255] * (new_width * new_height * 3)  # Белый фон

        # Центры для нового и исходного изображений
        center_x_orig = orig_width // 2
        center_y_orig = orig_height // 2
        center_x_new = new_width // 2
        center_y_new = new_height // 2

        # ОБРАТНОЕ отображение для каждого пикселя результата
        for i_new in range(new_width):
            for j_new in range(new_height):
                # Относительные координаты нового изображения
                x_rel = i_new - center_x_new
                y_rel = j_new - center_y_new

                # Обратный перенос, затем обратное масштабирование
                x_unscaled = (x_rel - shift_x) / scale
                y_unscaled = (y_rel - shift_y) / scale

                # Перенос обратно к исходной системе координат
                i_orig = x_unscaled + center_x_orig
                j_orig = y_unscaled + center_y_orig

                # Билинейная интерполяция
                if 0 <= i_orig <= orig_width - 1 and 0 <= j_orig <= orig_height - 1:
                    x0 = int(math.floor(i_orig))
                    y0 = int(math.floor(j_orig))
                    x1 = min(x0 + 1, orig_width - 1)
                    y1 = min(y0 + 1, orig_height - 1)

                    dx = i_orig - x0
                    dy = j_orig - y0

                    # Получаем цвета четырех соседних пикселей
                    colors = []
                    for y in [y0, y1]:
                        for x in [x0, x1]:
                            if 0 <= x < orig_width and 0 <= y < orig_height:
                                idx = (y * orig_width + x) * 3
                                colors.append((orig_pixels[idx], orig_pixels[idx + 1], orig_pixels[idx + 2]))
                            else:
                                colors.append((255, 255, 255))  # Белый для граничных пикселей

                    # Билинейная интерполяция
                    if len(colors) == 4:
                        c00, c10, c01, c11 = colors

                        # Интерполяция по X
                        top_r = c00[0] * (1 - dx) + c10[0] * dx
                        top_g = c00[1] * (1 - dx) + c10[1] * dx
                        top_b = c00[2] * (1 - dx) + c10[2] * dx

                        bottom_r = c01[0] * (1 - dx) + c11[0] * dx
                        bottom_g = c01[1] * (1 - dx) + c11[1] * dx
                        bottom_b = c01[2] * (1 - dx) + c11[2] * dx

                        # Интерполяция по Y
                        final_r = top_r * (1 - dy) + bottom_r * dy
                        final_g = top_g * (1 - dy) + bottom_g * dy
                        final_b = top_b * (1 - dy) + bottom_b * dy

                        dst_idx = (j_new * new_width + i_new) * 3
                        new_pixels[dst_idx] = int(final_r)
                        new_pixels[dst_idx + 1] = int(final_g)
                        new_pixels[dst_idx + 2] = int(final_b)

        self.affine_parameters = (scale, shift_x, shift_y)
        self.affine_result = (new_width, new_height, new_pixels)
        img_data = self.create_photoimage_from_bytes(new_width, new_height, new_pixels)
        img = tk.PhotoImage(data=img_data, format='PPM')

        # Масштабируем для отображения
        scaled_img = self.affine_preview(new_width, new_height, new_pixels, 300, 300)
        self.frame2.config(image=scaled_img)
        self.frame2.image = scaled_img

    def restore_affine(self):
        """Обратное аффинное преобразование с сохранением краев"""
        if not self.affine_result:
            showinfo("Ошибка", "Сначала выполните аффинное преобразование")
            return

        scale, shift_x, shift_y = self.affine_parameters
        affine_width, affine_height, affine_pixels = self.affine_result

        # Восстанавливаем исходный размер
        orig_width, orig_height, _ = self.original_bytes
        restored_pixels = [255] * (orig_width * orig_height * 3)  # Белый фон

        # Центры
        center_x_affine = affine_width // 2
        center_y_affine = affine_height // 2
        center_x_orig = orig_width // 2
        center_y_orig = orig_height // 2

        # ОБРАТНОЕ отображение для восстановления
        for i_rest in range(orig_width):
            for j_rest in range(orig_height):
                # Относительные координаты восстанавливаемого изображения
                x_rel = i_rest - center_x_orig
                y_rel = j_rest - center_y_orig

                # Прямое масштабирование и перенос
                x_transformed = x_rel * scale + shift_x
                y_transformed = y_rel * scale + shift_y

                # Перенос обратно к системе координат преобразованного изображения
                i_affine = x_transformed + center_x_affine
                j_affine = y_transformed + center_y_affine

                # Билинейная интерполяция
                if 0 <= i_affine <= affine_width - 1 and 0 <= j_affine <= affine_height - 1:
                    x0 = int(math.floor(i_affine))
                    y0 = int(math.floor(j_affine))
                    x1 = min(x0 + 1, affine_width - 1)
                    y1 = min(y0 + 1, affine_height - 1)

                    dx = i_affine - x0
                    dy = j_affine - y0

                    # Получаем цвета четырех соседних пикселей
                    colors = []
                    for y in [y0, y1]:
                        for x in [x0, x1]:
                            if 0 <= x < affine_width and 0 <= y < affine_height:
                                idx = (y * affine_width + x) * 3
                                colors.append((affine_pixels[idx], affine_pixels[idx + 1], affine_pixels[idx + 2]))
                            else:
                                colors.append((255, 255, 255))

                    # Билинейная интерполяция
                    if len(colors) == 4:
                        c00, c10, c01, c11 = colors

                        # Интерполяция по X
                        top_r = c00[0] * (1 - dx) + c10[0] * dx
                        top_g = c00[1] * (1 - dx) + c10[1] * dx
                        top_b = c00[2] * (1 - dx) + c10[2] * dx

                        bottom_r = c01[0] * (1 - dx) + c11[0] * dx
                        bottom_g = c01[1] * (1 - dx) + c11[1] * dx
                        bottom_b = c01[2] * (1 - dx) + c11[2] * dx

                        # Интерполяция по Y
                        final_r = top_r * (1 - dy) + bottom_r * dy
                        final_g = top_g * (1 - dy) + bottom_g * dy
                        final_b = top_b * (1 - dy) + bottom_b * dy

                        dst_idx = (j_rest * orig_width + i_rest) * 3
                        restored_pixels[dst_idx] = int(final_r)
                        restored_pixels[dst_idx + 1] = int(final_g)
                        restored_pixels[dst_idx + 2] = int(final_b)

        self.restored_result = (orig_width, orig_height, restored_pixels)
        img_data = self.create_photoimage_from_bytes(orig_width, orig_height, restored_pixels)
        img = tk.PhotoImage(data=img_data, format='PPM')

        # Масштабируем для отображения
        scaled_img = self.scale_image(img, 300, 300)
        self.frame3.config(image=scaled_img)
        self.frame3.image = scaled_img

    def affine_preview(self, width, height, pixels, view_width, view_height):
        """Показывает результат в масштабе оригинала, без подгонки холста."""
        original_width, original_height, _ = self.original_bytes
        scale = min(view_width / original_width, view_height / original_height)
        # Используем те же центры, что и при аффинном преобразовании.
        result = bytearray([255]) * (view_width * view_height * 3)
        for y in range(view_height):
            source_y = math.floor((y - view_height / 2 + 0.5) / scale + height // 2)
            if not 0 <= source_y < height:
                continue
            for x in range(view_width):
                source_x = math.floor((x - view_width / 2 + 0.5) / scale + width // 2)
                if 0 <= source_x < width:
                    source_index = (source_y * width + source_x) * 3
                    target_index = (y * view_width + x) * 3
                    result[target_index:target_index + 3] = bytes(pixels[source_index:source_index + 3])
        data = self.create_photoimage_from_bytes(view_width, view_height, result)
        return tk.PhotoImage(data=data, format='PPM')

    def scale_image(self, photo, max_width, max_height):
        """Вписывает изображение целиком, сохраняя пропорции."""
        width = photo.width()
        height = photo.height()
        if width <= 0 or height <= 0:
            return photo
        scale = min(max_width / width, max_height / height)
        new_width = max(1, min(max_width, round(width * scale)))
        new_height = max(1, min(max_height, round(height * scale)))
        if (new_width, new_height) == (width, height):
            return photo
        pixels = bytearray()
        for y in range(new_height):
            source_y = min(height - 1, int((y + 0.5) * height / new_height))
            for x in range(new_width):
                source_x = min(width - 1, int((x + 0.5) * width / new_width))
                pixels.extend(photo.get(source_x, source_y))
        data = self.create_photoimage_from_bytes(new_width, new_height, pixels)
        return tk.PhotoImage(data=data, format='PPM')

    def nonlinear_transform(self):
        """Нелинейное преобразование по формуле i = 2**x', j = y'"""
        if not self.original_bytes:
            showinfo("Ошибка", "Сначала откройте изображение")
            return

        width, height, pixels = self.original_bytes

        # Создаем изображение для результата (сохраняем исходные размеры)
        new_pixels = [255] * (width * height * 3)  # Белый фон

        # Функциональное преобразование с нормализацией
        for y in range(height):
            for x in range(width):
                try:
                    # Нормализуем координаты x к диапазону [0, 1]
                    x_norm = x / (width - 1) if width > 1 else 0

                    # i = 2**x' переводит [0, 1] в [1, 2].
                    # Нормализуем результат: i_norm = 2**x' - 1.
                    # Обратное отображение: x' = log2(i_norm + 1).
                    x_orig_norm_normalized = math.log2(x_norm + 1)

                    # Возвращаем к масштабу исходного изображения
                    x_orig = int(x_orig_norm_normalized * (width - 1))
                    y_orig = y

                    # Обеспечиваем попадание в границы
                    x_orig = max(0, min(width - 1, x_orig))
                    y_orig = max(0, min(height - 1, y_orig))

                    # Копируем пиксель
                    src_idx = (y_orig * width + x_orig) * 3
                    dst_idx = (y * width + x) * 3

                    if src_idx + 2 < len(pixels) and dst_idx + 2 < len(new_pixels):
                        new_pixels[dst_idx] = pixels[src_idx]
                        new_pixels[dst_idx + 1] = pixels[src_idx + 1]
                        new_pixels[dst_idx + 2] = pixels[src_idx + 2]

                except Exception as e:
                    # В случае ошибки используем белый пиксель
                    dst_idx = (y * width + x) * 3
                    new_pixels[dst_idx] = 255
                    new_pixels[dst_idx + 1] = 255
                    new_pixels[dst_idx + 2] = 255

        self.nonlinear_result = (width, height, new_pixels)
        img_data = self.create_photoimage_from_bytes(width, height, new_pixels)
        img = tk.PhotoImage(data=img_data, format='PPM')

        # Масштабируем для отображения
        scaled_img = self.scale_image(img, 300, 300)
        self.frame4.config(image=scaled_img)
        self.frame4.image = scaled_img

    def create_photoimage_from_bytes(self, width, height, pixels):
        ppm_header = f"P6\n{width} {height}\n255\n".encode()
        if isinstance(pixels, list):
            pixels = bytes(pixels)
        return ppm_header + pixels

    def save_specific_result(self, result_type):
        """Сохраняет конкретный тип результата"""
        data = None
        filename = ""

        if result_type == "affine" and self.affine_result:
            width, height, pixels = self.affine_result
            data = self.create_photoimage_from_bytes(width, height, pixels)
            filename = "affine_result.ppm"
        elif result_type == "nonlinear" and self.nonlinear_result:
            width, height, pixels = self.nonlinear_result
            data = self.create_photoimage_from_bytes(width, height, pixels)
            filename = "nonlinear_result.ppm"
        elif result_type == "restored" and self.restored_result:
            width, height, pixels = self.restored_result
            data = self.create_photoimage_from_bytes(width, height, pixels)
            filename = "restored_result.ppm"
        else:
            showinfo("Ошибка", f"Нет {result_type} результата для сохранения")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".ppm",
            initialfile=filename,
            filetypes=[("PPM files", "*.ppm"), ("All files", "*.*")],
            title=f"Сохранить {result_type} результат"
        )
        if not file_path:
            return

        with open(file_path, 'wb') as f:
            f.write(data)
        showinfo("Успех", f"{result_type} изображение сохранено")


def main():
    root = tk.Tk()
    app = PixelTransformation(root)
    root.mainloop()


if __name__ == '__main__':
    main()
