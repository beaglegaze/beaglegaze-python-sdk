import logging
from .pay_per_call import pay_per_call

logger = logging.getLogger(__name__)

class Demo:
    @pay_per_call(price=1)
    def greet(self, name):
        logger.info(f"Demo.greet called with: {name}")
        return f"Hello, {name}!"
