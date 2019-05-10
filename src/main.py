import src.file_utils as futil
import os
import cv2
import json
from src.image_grid_viewer import ImageViewer as GridViewer
from src.logger import ProcessLogger as Logger


def did_split(file_name, output_path):
    return os.path.exists(os.path.join(output_path, file_name))


def get_output_filename(category, base_name, index):
    return "{}_{}_{}.jpg".format(category, base_name, i)


def split_images(files, output_dir_path, category):
    logger = Logger()
    defect_dir_path = "{}/defect".format(output_dir_path)
    normal_dir_path = "{}/normal".format(output_dir_path)

    category_normal_path = os.path.join(normal_dir_path, category)
    category_defect_path = os.path.join(defect_dir_path, category)

    futil.makedirs_if_not(category_normal_path)
    futil.makedirs_if_not(category_defect_path)

    grid_viewer = GridViewer()
    json_datas = []

    for image_path in files:
        _, file_name = os.path.split(image_path)
        if did_split(get_output_filename(category, file_name, 0), category_normal_path) or did_split(
                get_output_filename(category, file_name, 0), category_defect_path):
            continue

        if logger.exist_name_in_log(file_name):
            continue

        image = cv2.imread(image_path)
        return_key_code = grid_viewer.show(image, rgb_image=False)

        if return_key_code is ord('1'):
            logger.append_processed_image(file_name)
            print("Skip : {}".format(file_name))
            continue
        elif return_key_code is ord('0'):
            break

        normal_images, defect_images = grid_viewer.split_images_by_marks()
        logger.append_processed_image(file_name)

        for norm_i, image in enumerate(normal_images):
            futil.save_image_with(
                image,
                output_root_path=category_normal_path,
                file_name=get_output_filename(category, file_name, norm_i),
                is_ndarray=True
            )

        for defect_i, image in enumerate(defect_images):
            futil.save_image_with(
                image,
                output_root_path=category_defect_path,
                file_name=get_output_filename(category, file_name, defect_i),
                is_ndarray=True
            )

        json_datas.append({"file": file_name, "data": grid_viewer.get_summary()})

    return json_datas


def augment_categories(sub_dirs, output_dir_path, begin_file_index=0):
    defect_dir_path = "{}/defect".format(output_dir_path)
    normal_dir_path = "{}/normal".format(output_dir_path)

    futil.makedirs_if_not(defect_dir_path)
    futil.makedirs_if_not(normal_dir_path)

    # detect_selector = DefectPointSelector()
    number_of_targets = 10
    for category_dir in sub_dirs:
        _, category = os.path.split(category_dir)
        try:
            files = futil.get_files(category_dir)
            files = files[begin_file_index:begin_file_index + number_of_targets]
            print("\n=== {} ===\n".format(category))
            summaries = split_images(files, output_dir_path, category)
            print(summaries)
            summary_file_name = "summary_{}_{}.json".format(category, begin_file_index)
            with open(os.path.join(output_dir_path, summary_file_name), mode='w') as file:
                for summary in summaries:
                    file.write(json.dumps(summary))
                    file.write("\n")

            # print("\n=== END {} === {}\n".format(category, count))

        except KeyboardInterrupt as e:
            print("Exit!!")
        except KeyError as e:
            print(e)


if __name__ == "__main__":
    sub_dirs = futil.get_sub_dirs('./images', max_depth=1)
    sub_dirs = sorted(sub_dirs)

    output_root = "./outputs"

    for i in range(10):
        augment_categories(sub_dirs, output_root, begin_file_index=i*10)
        key = input("작업을 이어서 하시겠습니까 ? (이어하기 : y, 그만하기 : 그외 아무거나)")
        if key is not 'y':
            break
