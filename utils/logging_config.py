import logging
import os
from logging import Logger
from pathlib import Path


def get_project_root() -> str:
    current_dir = Path(__file__).resolve().parent
    while current_dir != current_dir.parent:
        if (current_dir / "pytest.ini").exists() or (current_dir / "requirements.txt").exists():
            return str(current_dir)
        current_dir = current_dir.parent
    raise FileNotFoundError("Could not find project root")

def setup_logger(name: str, log_file: str = "logs/test.log") -> Logger:
    """Настройка логгера с выводом в консоль и файл.

    Args:
        name: Имя логгера (обычно __name__).
        log_file: Путь к файлу логов (относительно корня проекта).

    Returns:
        Настроенный объект логгера.

    Note:
        Убедитесь, что папка `logs/` существует в корне проекта (`project_root/logs/`).
        Если файл логов не создаётся, проверьте права доступа к папке `logs/`.
    """
    print(f"DEBUG: Entering setup_logger with name={name}, log_file={log_file}")

    project_root = get_project_root()
    log_file_path = os.path.join(project_root, log_file)
    print(f"DEBUG: Log file path: {log_file_path}")

    log_dir = os.path.dirname(log_file_path)
    print(f"DEBUG: Log directory: {log_dir}")
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
            print(f"DEBUG: Created log directory: {log_dir}")
        except OSError as e:
            print(f"ERROR: Failed to create log directory {log_dir}: {e}")
            raise
    else:
        print(f"DEBUG: Log directory already exists: {log_dir}")

    if not os.access(log_dir, os.W_OK):
        print(f"ERROR: No write permission for log directory {log_dir}")
        raise PermissionError(f"No write permission for {log_dir}")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    print(f"DEBUG: Logger created with name={name}")

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    try:
        file_handler = logging.FileHandler(log_file_path, mode='a', delay=False)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        print(f"DEBUG: FileHandler created for: {log_file_path}")
    except Exception as e:
        print(f"ERROR: Failed to create FileHandler for {log_file_path}: {e}")
        raise

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logger initialized successfully")
    print(f"DEBUG: Logger initialized for {name}")

    return logger