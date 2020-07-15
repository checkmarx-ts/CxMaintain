from PyInquirer import Validator, ValidationError

class PortValidator(Validator):
    def validate(self, document):
        # To-Do
        # Maybe I should do regex here
        try:
            int(document.text)
        except Exception as ex:
            # Cannot get integer here
            raise ValidationError