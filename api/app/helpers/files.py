import os


def make_unique_file_name(directory: str, file_name: str):
    file_path = os.path.join(directory, file_name)
    candidate_file_path = file_path
    suffix = 0

    while os.path.exists(candidate_file_path):
        base_name, extension = os.path.splitext(file_path)

        suffix += 1
        candidate_file_path = f"{base_name}_{suffix}{extension}"

    if suffix > 0:
        base_name, extension = os.path.splitext(file_path)
        file_path = f"{base_name}_{suffix}{extension}"

    return os.path.split(file_path)[1]