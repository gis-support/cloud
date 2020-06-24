import inspect
import os

from flasgger import swag_from


def swag_from_docs(filename, docs_directory_name="docs", *args, **kwargs):
    """
        Funkcja-nakładka dla dekoratora swag_from.
        Generuje ścieżkę do pliku `filename`,
        znajdującego się w folderze `docs_directory_name`.
        Ścieżka do folderu `docs_directory_name` to folder,
        w którym znajduje się plik wywołujący tą funkcję
        Może być używana jako dekorator.
    """

    calling_file_directory = os.path.dirname(inspect.stack()[1].filename)

    file_path = os.path.join(calling_file_directory, docs_directory_name, filename)

    return swag_from(file_path, *args, **kwargs)