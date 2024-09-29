import pathlib
import logging
from logging.handlers import RotatingFileHandler



def setup_logger(name:str,
                filename:str=None,
                display_level:logging=logging.DEBUG,
                max_file_size_megabytes:int=5,
                backup_log_count:int=3):
    new_log = logging.getLogger(name)
    new_log.setLevel(logging.DEBUG)

    m_formatter = logging.Formatter('|%(name)s| %(asctime)s - %(levelname)s - %(message)s')
    
    if filename:
        path_to_log_folder = pathlib.Path(__file__).parent.resolve()
        path_to_log_folder = f"{path_to_log_folder}/LOGS/{filename}"
        fh = RotatingFileHandler(path_to_log_folder,
                                mode='a', 
                                maxBytes=max_file_size_megabytes * 1024 * 1024,
                                backupCount=backup_log_count,
                                encoding=None,
                                delay=0)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(m_formatter)
        new_log.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(display_level)
    sh.setFormatter(m_formatter)
    new_log.addHandler(sh)

    new_log.info(f"{name} initialised")