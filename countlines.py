import os

def count_lines_in_directory(directory, exclude_dirs=None, extensions=None):
    total_lines = 0
    if exclude_dirs is None:
        exclude_dirs = []
    if extensions is None:
        extensions = ['.py']

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', errors='ignore') as f:
                    lines = sum(1 for _ in f)
                    total_lines += lines
    return total_lines

if __name__ == '__main__':
    project_root = '.'  # Current directory
    excluded_directories = ['.venv', 'migrations', '__pycache__', 'static', 'media']
    file_extensions = ['.py', '.js', '.html', '.css']

    total_lines = count_lines_in_directory(project_root, excluded_directories, file_extensions)
    print(f"Total lines of code: {total_lines}")