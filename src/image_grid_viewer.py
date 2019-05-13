import cv2
import traceback
import numpy as np
import json
import os

EVENT_LBUTTONDOWN = cv2.EVENT_LBUTTONDOWN
EVENT_LBUTTONDBLCLK = cv2.EVENT_LBUTTONDBLCLK
EVENT_MOUSEMOVE = cv2.EVENT_MOUSEMOVE


class SelectMark:
    def __init__(self, index, code):
        self._index = index
        self._code = code

    @property
    def index(self):
        return self._index

    @property
    def code(self):
        return self._code

    def set_code(self, new_code):
        self._code = new_code

    def __getitem__(self, item):
        if item == 'code':
            return self._code
        elif item == 'index':
            return self._index
        else:
            raise Exception('not found item {}'.format(item))

    def to_json(self):
        return json.dumps({'code': self.code, 'index': self.index})

    def __str__(self):
        return self.to_json()


class GridMap:
    def __init__(self, horizontal_number, vertical_number, total_width, total_height):
        self._horizontal_number = horizontal_number
        self._vertical_number = vertical_number
        self._total_width = total_width
        self._total_height = total_height

    @property
    def horizontal_number(self):
        return self._horizontal_number

    @property
    def vertical_number(self):
        return self._vertical_number

    @property
    def total_width(self):
        return self._total_width

    @property
    def total_height(self):
        return self._total_height


class KeyInputFlag:
    def __init__(self, key, error_message=None):
        self._key = key
        self.message = error_message

    @property
    def input_key(self):
        return self._key

    @property
    def skip(self):
        return self._key == ord('1')

    @property
    def stop(self):
        return self._key == ord('0')

    @property
    def error(self):
        return self._key == -1, self.message


class ImageViewer:
    GRID_BOX_SIZE = (128, 256)
    MARK_CODE_NORMAL = 0
    MARK_CODE_DEFECT = 1
    MARK_CODE_UNUSED = 2
    WORKING_INSTANCE = None

    def __init__(self, default_image=None, name="viewer"):
        self.name = name
        self.selected_marks = []
        self.current_image = None

        cv2.namedWindow(self.name)
        ImageViewer.WORKING_INSTANCE = self

    @classmethod
    def calculate_grid_map(cls, image_width, image_height):
        horizontal_number = image_width // cls.GRID_BOX_SIZE[0]
        vertical_number = image_height // cls.GRID_BOX_SIZE[1]

        grid_total_width = horizontal_number * cls.GRID_BOX_SIZE[0]
        grid_total_height = vertical_number * cls.GRID_BOX_SIZE[1]

        return GridMap(horizontal_number, vertical_number, grid_total_width, grid_total_height)

    @classmethod
    def draw_grid_lines_on_image(cls, image):
        np_image = np.array(image)
        width, height, _ = np_image.shape
        grid_map = cls.calculate_grid_map(width, height)

        for h_i in range(1, grid_map.horizontal_number + 1):
            point_x = cls.GRID_BOX_SIZE[0] * h_i
            cv2.line(np_image, (point_x, 0), (point_x, grid_map.total_height), (0, 0, 255), 2)

        for v_i in range(1, grid_map.vertical_number + 1):
            piont_y = cls.GRID_BOX_SIZE[1] * v_i
            cv2.line(np_image, (0, piont_y), (grid_map.total_width, piont_y), (0, 0, 255), 2)

        return np_image

    @classmethod
    def draw_selected_marks(cls, image, marks):
        np_image = np.array(image)
        width, height, _ = np_image.shape
        grid_map = cls.calculate_grid_map(width, height)
        font = cv2.FONT_HERSHEY_SIMPLEX

        for mark in marks:
            label = "D"
            if mark['code'] == cls.MARK_CODE_UNUSED:
                label = "X"
            elif mark['code'] == cls.MARK_CODE_NORMAL:
                continue

            h_i = (mark['index'] % grid_map.horizontal_number) + 0.3
            v_i = (mark['index'] // grid_map.horizontal_number) + 0.5

            cv2.putText(np_image,
                        label,
                        (int(h_i * cls.GRID_BOX_SIZE[0]), int(v_i * cls.GRID_BOX_SIZE[1])),
                        font,
                        2,
                        (255, 0, 0),
                        5,
                        cv2.LINE_AA)

        return np_image

    @classmethod
    def create_new_defect(cls, click_position, image):
        width, height, _ = np.array(image).shape
        grid_map = cls.calculate_grid_map(width, height)

        h_i = click_position[0] // cls.GRID_BOX_SIZE[0]
        v_i = click_position[1] // cls.GRID_BOX_SIZE[1]

        mark = SelectMark(index=((v_i * grid_map.horizontal_number) + h_i), code=cls.MARK_CODE_DEFECT)

        return mark

    def append_mark(self, new_mark):
        is_updated = False
        for mark in self.selected_marks:
            if mark['index'] == new_mark['index']:
                if mark['code'] == ImageViewer.MARK_CODE_DEFECT:
                    mark.set_code(ImageViewer.MARK_CODE_UNUSED)
                elif mark['code'] == ImageViewer.MARK_CODE_UNUSED:
                    mark.set_code(ImageViewer.MARK_CODE_NORMAL)
                else:
                    mark.set_code(ImageViewer.MARK_CODE_DEFECT)

                is_updated = True

        if not is_updated:
            self.selected_marks.append(new_mark)

        self._update_view()

    def _mouse_click(self, *args):
        if args[0] == EVENT_LBUTTONDOWN:
            defect_mark = self.create_new_defect((args[1], args[2]), self.current_image)
            self.append_mark(defect_mark)

    def _update_view(self):
        grid_image = self.draw_grid_lines_on_image(self.current_image)
        output_image = self.draw_selected_marks(grid_image, self.selected_marks)

        cv2.imshow(self.name, output_image)

    def select_mark(self, image, rgb_image=True):
        cv2.setMouseCallback(self.name, self._mouse_click)
        self.selected_marks.clear()
        self.current_image = image

        error_message = None

        if rgb_image:
            self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_RGB2BGR)

        self._update_view()

        try:
            print("다음 : Space, 안하고 넘기기 : 1, 다음 카테고리 : 0, ")
            key = cv2.waitKey(0)

        except Exception as e:
            error_message = e.message
            print(e.message)
            print(e.__class__.__name__)
            traceback.print_exc(e)

        return KeyInputFlag(key, error_message), self.selected_marks

    def save_summary(self, file_name, path):
        with open(os.path.join(path, file_name)) as file:
            json.dumps(self.selected_marks, file)

    def get_summary(self):
        jsons = []
        for mark in self.selected_marks:
            jsons.append({"index": mark.index, "code": mark.code})

        return json.dumps(jsons)

