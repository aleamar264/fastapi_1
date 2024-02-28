from fastapi import Request
from tools.logger import logger
import time


async def log_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start

    log_dict = {
        "url": request.url.path,
        "method": request.method,
        "process_time": process_time,
    }
    logger.info(log_dict, extra=log_dict)
    return response
