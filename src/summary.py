import os
import json


class LabelSummary:
    def __init__(self):
        self._rows = []
        self._next_index = 0

    def append(self, json_row):
        row = json.loads(json_row)
        row['data'] = json.loads(row['data'])

        self._rows.append(row)

    @property
    def number_of_rows(self):
        return len(self._rows)

    def __len__(self):
        return len(self._rows)

    @property
    def rows(self):
        return self._rows

    def __iter__(self):
        return self._rows

    def __next__(self):
        next_row = self._rows[self._next_index]
        self._next_index += 1
        return next_row


class LabelSummaryReader:
    def __init__(self, summary_file_path):
        self.file_path = summary_file_path
        self._label_summary = self._read_file()

    @property
    def summary(self):
        return self._label_summary

    def _read_file(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError('Not found label summary file {}'.format(self.file_path))

        summary = LabelSummary()
        with open(self.file_path, 'r') as file:
            for line in file:
                summary.append(line)

        return summary
