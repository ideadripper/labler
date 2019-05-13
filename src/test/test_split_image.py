import unittest
import shutil
import os
from src.logger import ProcessLogger as Logger
from src.main import get_image_category_dir_paths, create_image_output_dir, get_output_filename, did_processed


class TestSplitImages(unittest.TestCase):

    def setUp(self):
        self.root_path = './images'
        self.output_path = './outputs'

    def tearDown(self):
        shutil.rmtree(self.output_path, ignore_errors=True)

    def test_get_image_category_dir_paths(self):
        category_dirs = get_image_category_dir_paths(self.root_path)
        self.assertIsNotNone(category_dirs)
        self.assertEqual(len(category_dirs), 3)

    def test_create_image_output_dir(self):
        category = 'ACTL2F'
        output_normal_path, output_defect_path = create_image_output_dir(self.output_path, category)

        self.assertIs(os.path.exists(output_normal_path), True)
        self.assertIs(os.path.exists(output_defect_path), True)

        self.assertIs('normal' in output_normal_path, True)
        self.assertIs('defect' in output_defect_path, True)

    def test_get_output_filename(self):
        category = 'ACTL2F'
        file_name = '763a8z0163c5aau04_20181220_123945_-350694_-693875.jpg'
        output_file_name = get_output_filename(category, file_name, 0)

        self.assertIs('jpg' in output_file_name, True)
        self.assertIs(file_name in output_file_name, True)
        self.assertIs(category in output_file_name, True)

    def test_did_processed(self):
        logger = Logger()
        category = 'ACTL2F'
        true_file_name = '763a8z0163c5aau04_20181220_123945_-350694_-693875.jpg'
        processed_file_name = '763a8z0163c7aag03_20181220_124557_-516891_231788.jpg'
        false_file_name = '111a8z0163c5aau04_20181220_123945_-350694_-693875.jpg'

        output_normal_path, output_defect_path = create_image_output_dir(self.output_path, category)

        true_result = did_processed(
            true_file_name,
            category,
            output_normal_path, output_defect_path,
            logger=logger
        )

        self.assertIs(true_result, True, "Result True")

        false_result = did_processed(
            false_file_name,
            category,
            output_normal_path, output_defect_path,
            logger=logger
        )

        self.assertIs(false_result, False, "Image False")

        true_result = did_processed(
            processed_file_name,
            category,
            output_normal_path, output_defect_path,
            logger=logger
        )

        self.assertIs(true_result, True, "Processed True")




