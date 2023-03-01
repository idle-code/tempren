from tempren.primitives import Location, QualifiedTagName


class TemplateError(Exception):
    """Represents an error in the template itself"""

    message: str
    location: Location
    template: str

    def __init__(self, message: str):
        self.message = message
        self.location = Location(0, 0, 0)

    def with_location(self, location: Location) -> "TemplateError":
        self.location = location
        return self

    def __str__(self) -> str:
        if self.location:
            return f"{self.location}: {self.message}"
        else:
            return self.message


class TemplateSyntaxError(TemplateError):
    pass


class TemplateSemanticError(TemplateError):
    pass


class TagError(TemplateSemanticError):
    tag_name: QualifiedTagName

    def __init__(self, tag_name: QualifiedTagName, message: str):
        assert tag_name
        self.tag_name = tag_name
        super().__init__(f"Error in tag '{self.tag_name}': {message}")


class InvalidFilenameError(Exception):
    generated_name: str

    def __init__(self, invalid_name: str):
        super().__init__(f"Invalid name: '{invalid_name}'")
        self.generated_name = invalid_name
