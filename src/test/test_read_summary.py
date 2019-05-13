import unittest
from src.summary import LabelSummaryReader
from src.data_converter import convert_summary_to_marks
from src.image_grid_viewer import SelectMark


class TestSummaryReader(unittest.TestCase):

    def setUp(self):
        self.summary_file_path = './summary_ACTL2F.json'

    def tearDown(self):
        pass

    def test_read_summary_file(self):
        reader = LabelSummaryReader(summary_file_path=self.summary_file_path)

        self.assertIsNotNone(reader.summary)
        self.assertIs(reader.summary.number_of_rows, 10)

        row = reader.summary.rows[2]
        correct_datas = [{"index": 11, "code": 1}, {"index": 19, "code": 2}, {"index": 20, "code": 2}, {"index": 12, "code": 2}, {"index": 10, "code": 2}, {"index": 18, "code": 2}]
        self.assertIs(row['file'] == "763a8z0163b3aae05_20181220_120243_-117574_363592.jpg", True)

        print(row['data'])
        print(len(row['data']))
        self.assertIs(len(row['data']), 6)

        for i, select_mark in enumerate(row['data']):
            self.assertIs(select_mark['index'], correct_datas[i]['index'])
            self.assertIs(select_mark['code'], correct_datas[i]['code'])

    def test_convert_summary_to_marks(self):
        reader = LabelSummaryReader(summary_file_path=self.summary_file_path)
        marks_in_files = convert_summary_to_marks(reader.summary)

        self.assertIs(len(marks_in_files), 10)
        test_file_name = "763a8z0163b3aae05_20181220_120243_-117574_363592.jpg"
        marks = marks_in_files[test_file_name]
        correct_datas = [{"index": 11, "code": 1}, {"index": 19, "code": 2}, {"index": 20, "code": 2}, {"index": 12, "code": 2}, {"index": 10, "code": 2}, {"index": 18, "code": 2}]

        self.assertIs(len(marks), len(correct_datas))
        for i, mark in enumerate(marks):
            self.assertIs(isinstance(mark, SelectMark), True)
            self.assertIs(mark['index'], correct_datas[i]['index'])
            self.assertIs(mark['code'], correct_datas[i]['code'])

