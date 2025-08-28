from .pay_per_call import pay_per_call

class Demo:
    @pay_per_call(price=1)
    def greet(self, name):
        return f"Hello, {name}!"
