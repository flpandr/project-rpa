import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from src.config import settings

def setup_logging():
    """Configura o sistema de logging centralizado"""
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL.upper())
    
    # Remove handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Formato comum para todos handlers
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_dir = Path('logs')
    log_dir.mkdir(parents=True, exist_ok=True)  # Garante que o diretório existe
    
    file_handler = RotatingFileHandler(
        filename='logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# Interface padrão para o logger
logger = logging.getLogger(__name__)