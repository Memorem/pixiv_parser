from loguru import logger
import sys

# sys.tracebacklimit = 2

def trace(message: str):
    logger.configure(**{
            'handlers': [
                {
                'sink': sys.stdout, 
                'level': 'TRACE', 
                'colorize': True, 
                'format': '<cyan>{level} {time:DD.MM.YYYY HH:mm:ss}</cyan> {message}'
                }
            ]
    })

    return logger.trace(message)



def debug(message: str):
    logger.configure(**{
            'handlers': [
                {
                'sink': 'debug.log', 
                'level': 'DEBUG', 
                'colorize': True, 
                'format': '<red>{level} {time:DD.MM.YYYY HH:mm:ss}</red> {message}',
                }
            ]
    })

    return logger.debug(message)


def info(message: str):
    logger.configure(**{
            'handlers': [
                {
                'sink': sys.stdout, 
                'level': 'INFO', 
                'colorize': True, 
                'format': '<yellow>{message}</yellow> ' #{time:DD.MM.YYYY HH:mm:ss}
                }
            ]
    })

    return logger.info(message)

def success(message: str):
    logger.configure(**{
            'handlers': [
                {
                'sink': sys.stdout, 
                'level': 'SUCCESS', 
                'colorize': True, 
                'format': '<green>{level}{message}</green>'
                }
            ]
    })

    return logger.success(message)

def warning(message: str):
    logger.configure(**{
            'handlers': [
                {
                'sink': sys.stdout, 
                'level': 'WARNING', 
                'colorize': True, 
                'format': '<yellow>{level} {time:DD.MM.YYYY HH:mm:ss} {message}</yellow>'
                }
            ]
    })

    return logger.warning(message)

def error(message: str):
    logger.configure(**{
            'handlers': [
                {
                'sink': sys.stdout, 
                'level': 'ERROR', 
                'colorize': True, 
                'format': '<red>{level} {time:DD.MM.YYYY HH:mm:ss} {message}</red>'
                }
            ]
    })
    
    return logger.error(message)

def critical(message: str):
    logger.configure(**{
            'handlers': [
                {
                'sink': sys.stdout, 
                'level': 'CRITICAL', 
                'colorize': True, 
                'format': '<red>{level}</red> {time:DD.MM.YYYY HH:mm:ss}</red> <yellow>{message}</yellow>'
                }
            ]
    }) 

    return logger.critical(message)