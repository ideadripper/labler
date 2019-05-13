import src.file_utils as futil
import os
import cv2
import numpy as np
import json
from src.image_grid_viewer import ImageViewer as GridViewer
from src.logger import ProcessLogger as Logger
from absl import app, flags
from src.summary import LabelSummaryReader
from src.data_converter import convert_summary_to_marks


def did_split(file_name, category, output_path):
    output_file_name = get_output_filename(category, file_name, 0)

    return os.path.exists(os.path.join(output_path, output_file_name))


def get_output_filename(category, base_name, index):
    return "{}_{}_{}.jpg".format(category, base_name, index)


def save_split_images(images, save_path, category, base_name):
    for image_index, image in enumerate(images):
        futil.save_image_with(
            image,
            output_root_path=save_path,
            file_name=get_output_filename(category, base_name, image_index),
            is_ndarray=True
        )


def split_image_by_grid_marks(image, marks):
    np_image = np.array(image)
    width, height, _ = np_image.shape

    grid_map = GridViewer.calculate_grid_map(width, height)
    normals = []
    defects = []

    for h_i in range(0, grid_map.horizontal_number):
        for v_i in range(0, grid_map.vertical_number):
            index = v_i * grid_map.horizontal_number + h_i
            code = -1
            for mark in marks:
                if mark['index'] == index:
                    code = mark['code']

            if code == GridViewer.MARK_CODE_UNUSED:
                continue

            x_point = h_i * GridViewer.GRID_BOX_SIZE[0]
            y_point = v_i * GridViewer.GRID_BOX_SIZE[1]

            right = x_point + GridViewer.GRID_BOX_SIZE[0]
            bottom = y_point + GridViewer.GRID_BOX_SIZE[1]

            crop_image = image[y_point:bottom, x_point:right, :]

            if code == -1:
                normals.append(crop_image)
            elif code == GridViewer.MARK_CODE_DEFECT:
                defects.append(crop_image)

    return normals, defects


def create_image_output_dir(output_root_dir, category_name):
    defect_dir_path = "{}/defect".format(output_root_dir)
    normal_dir_path = "{}/normal".format(output_root_dir)

    normal_path = os.path.join(normal_dir_path, category_name)
    defect_path = os.path.join(defect_dir_path, category_name)

    futil.makedirs_if_not(normal_path)
    futil.makedirs_if_not(defect_path)

    return normal_path, defect_path


def did_processed(file_name, category, normal_dir_path, defect_dir_path, logger):
    # Deprecated
    if did_split(file_name, category, normal_dir_path) or did_split(file_name, category, defect_dir_path):
        return True

    if logger.exist_name_in_log(file_name):
        return True

    return False


def get_summary_file_name(output_path, category):
    return os.path.join(output_path, "summary_{}.json".format(category))


def save_summary(output_path, category, summary):
    with open(get_summary_file_name(output_path, category), mode='a') as file:
        file.write(json.dumps(summary))
        file.write("\n")


def load_pre_select_marks(summary_path, category):
    marks = {}
    try:
        reader = LabelSummaryReader(summary_file_path=get_summary_file_name(summary_path, category))
        marks = convert_summary_to_marks(reader.summary)
    except FileNotFoundError as fe:
        print("not exist summary file for {}".format(category))

    return marks


def find_pre_select_marks_by_file_name(marks_in_files, target_name):
    return marks_in_files.setdefault(target_name, [])


def split_images(files, output_root_path, category):
    logger = Logger()
    show_viewer = not FLAGS.using_only_summary
    pre_select_marks = load_pre_select_marks(output_root_path, category)

    output_normal_path, output_defect_path = create_image_output_dir(output_root_path, category)
    grid_viewer = GridViewer()
    json_datas = []

    for image_path in files:
        _, file_name = os.path.split(image_path)
        if did_processed(file_name, category,
                         output_normal_path,
                         output_defect_path,
                         logger):
            continue

        image = cv2.imread(image_path)
        selected_marks = find_pre_select_marks_by_file_name(pre_select_marks, file_name)

        if show_viewer:
            return_flag, selected_marks = grid_viewer.select_mark(image, rgb_image=False)

            if return_flag.skip:
                logger.append_processed_image(file_name)
                continue
            elif return_flag.stop:
                break
        elif len(selected_marks) == 0:
            continue

        normal_images, defect_images = split_image_by_grid_marks(
            image,
            selected_marks
        )
        print("normal {} / defect {}".format(len(normal_images), len(defect_images)))

        save_split_images(normal_images, output_normal_path, category, base_name=file_name)
        save_split_images(defect_images, output_defect_path, category, base_name=file_name)

        logger.append_processed_image(file_name)
        summary = {"file": file_name, "data": grid_viewer.get_summary()}
        json_datas.append(summary)

        save_summary(output_root_path, category, summary)

    return json_datas


def augment_categories(sub_dirs, output_dir_path, begin_file_index=0):
    number_of_targets = 10
    for category_dir in sub_dirs:
        _, category = os.path.split(category_dir)
        try:
            files = futil.get_files(category_dir)
            if begin_file_index >= 0:
                files = files[begin_file_index:begin_file_index + number_of_targets]

            print("\n=== {} ===\n".format(category))
            summaries = split_images(files, output_dir_path, category)

        except KeyboardInterrupt as e:
            print("Exit!!")
        except KeyError as e:
            print(e)


def get_image_category_dir_paths(root_dir):
    sub_dirs = futil.get_sub_dirs(root_dir, max_depth=1)
    return sorted(sub_dirs)


def main(args):
    category_dirs = get_image_category_dir_paths(FLAGS.image_root_path)

    if FLAGS.using_only_summary:
        augment_categories(category_dirs, FLAGS.output_root, begin_file_index=-1)
    else:
        for i in range(10):
            augment_categories(category_dirs, FLAGS.output_root, begin_file_index=i * 10)
        # key = input("작업을 이어서 하시겠습니까 ? (이어하기 : y, 그만하기 : 그외 아무거나)")
        # if key is not 'y':
        #     break


if __name__ == "__main__":
    flags.DEFINE_string('image_root_path', './images', 'image dir path')
    flags.DEFINE_string('output_root', './outputs', 'outputs dir path')
    flags.DEFINE_boolean('using_only_summary', False,
                        'skip to grid viewer. if it is True, summary files should be located in output_root')

    FLAGS = flags.FLAGS

    app.run(main)