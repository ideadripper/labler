import os
import src.file_utils as futils


# TODO : SingleTone
class ProcessLogger:
    PROCESSED_IMAGE_LOG = "./processed.log"

    def __init__(self, path="./"):
        if not os.path.exists(path):
            futils.makedirs_if_not(path)

        self.log_path = path
        self.processed_names = self._load_processed_log()

    def _load_processed_log(self):
        processed_log_name = os.path.join(self.log_path, ProcessLogger.PROCESSED_IMAGE_LOG)
        if not os.path.exists(processed_log_name):
            return []

        names = []
        with open(processed_log_name, mode='r') as log_file:
            print(log_file)
            for line in log_file:
                names.append(line.replace("\n", ""))

        return names

    def append_processed_image(self, image_file_name):
        self.processed_names.append(image_file_name)
        with open(os.path.join(self.log_path, ProcessLogger.PROCESSED_IMAGE_LOG), mode='a') as log_file:
            log_file.write(image_file_name)
            log_file.write("\n")

    def exist_name_in_log(self, file_name):
        return file_name in self.processed_names

