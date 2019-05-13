import unittest
from src.logger import ProcessLogger


class TestLogger(unittest.TestCase):

    def test_logger(self):
        logger = ProcessLogger()
        self.assertIs(len(logger.processed_names), 2)
        self.assertIs(logger.processed_names[0] == '763a8z0163c5aau04_20181220_123945_-350694_-693875.jpg', True)
