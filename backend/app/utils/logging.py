import logging
from colorama import Fore, Style, init

from app.config import settings

# Initialize colorama for Windows support
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels and logger names."""
    
    # Color mapping for log levels
    LEVEL_COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    # Color mapping for logger names (by prefix)
    NAME_COLORS = {
        'app.routers': Fore.MAGENTA,
        'app.services': Fore.BLUE,
        'app.clients': Fore.CYAN,
        'uvicorn': Fore.YELLOW,
        'httpx': Fore.WHITE + Style.DIM,
    }
    
    def _get_name_color(self, name: str) -> str:
        """Get color for logger name based on its prefix."""
        for prefix, color in self.NAME_COLORS.items():
            if name.startswith(prefix):
                return color
        return Fore.WHITE  # Default color
    
    def format(self, record):
        reset_color = Style.RESET_ALL
        
        # Get colors
        level_color = self.LEVEL_COLORS.get(record.levelname, '')
        name_color = self._get_name_color(record.name)
        
        # Temporarily modify levelname and name for formatting
        original_levelname = record.levelname
        original_name = record.name
        record.levelname = f"{level_color}{original_levelname}{reset_color}"
        record.name = f"{name_color}{original_name}{reset_color}"
        
        try:
            # Format the message
            formatted = super().format(record)
        finally:
            # Restore original values
            record.levelname = original_levelname
            record.name = original_name
        
        return formatted


def setup_logging():
    """Configure logging based on settings."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Create colored formatter (time only, no date)
    formatter = ColoredFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configure uvicorn loggers to use our format
    uvicorn_loggers = [
        logging.getLogger("uvicorn"),
        logging.getLogger("uvicorn.access"),
        logging.getLogger("uvicorn.error"),
    ]
    for logger in uvicorn_loggers:
        logger.setLevel(log_level)
        logger.handlers.clear()
        logger.addHandler(console_handler)
        logger.propagate = False  # Prevent duplicate logs from root logger
    
    # Configure httpx logger to use our format (for API client logs)
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(log_level)
    httpx_logger.handlers.clear()
    httpx_logger.addHandler(console_handler)
    httpx_logger.propagate = False

