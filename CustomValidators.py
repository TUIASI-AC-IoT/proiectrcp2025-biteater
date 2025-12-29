from textual.validation import Validator, ValidationResult

def is_valid_path(path: str):
    pass


class GoodWindowSize(Validator):
    def validate(self, value: str) -> ValidationResult | None:
        try:
            window_size = int(value)
            if window_size > 0:
                return self.success()
            else:
                return self.failure("The window size must be a positive value")
        except ValueError:  # when int() fails
            return self.failure("Invalid value, window size must be an int :/")



class GoodTimeout(Validator):
    def validate(self, value: str) -> ValidationResult | None:
        try:
            timeout = float(value)
            if timeout > 0.0:
                return self.success()
            else:
                return self.failure("The timeout must be a positive value")
        except ValueError: # when float() fails
            return self.failure("Invalid value, timeout must be a float :/")

