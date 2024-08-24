import os

# Define the directory and file structure
structure = {
        "app": {
            "__init__.py": "",
            "main.py": "",
            "api": {
                "__init__.py": "",
                "libraries.py": "",
                "documents.py": "",
                "search.py": "",
            },
            "core": {
                "__init__.py": "",
                "config.py": "",
                "database.py": "",
            },
            "models": {
                "__init__.py": "",
                "data_models.py": "",
            },
            "services": {
                "__init__.py": "",
                "indexing.py": "",
            },
        },
        "tests": {
            "__init__.py": "",
            "test_api.py": "",
            "test_models.py": "",
            "test_indexing.py": "",
        },
        "Dockerfile": "",
        "docker-compose.yml": "",
        "requirements.txt": "",
        "README.md": "",
    }


# Function to create directories and files
def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, 'w') as f:
                f.write(content)

# Create the directory and file structure
create_structure(".", structure)
