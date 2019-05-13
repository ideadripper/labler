from src.image_grid_viewer import SelectMark


def convert_summary_to_marks(summary):
    marks_in_files = {}
    print(summary.rows)
    for row in summary.rows:
        marks = []
        # file_name = row['file']
        for mark_value in row['data']:
            marks.append(SelectMark(mark_value['index'], mark_value['code']))

        marks_in_files[row['file']] = marks

    return marks_in_files

