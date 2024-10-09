import logging


def init_logging_basic_config():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('validator.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


if __name__ == '__main__':
    # 记录日志
    init_logging_basic_config()
    logger = logging.getLogger('my_logger')
    logger.info('这是一条信息日志')
    logger.error('这是一条错误日志')
