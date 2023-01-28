from typing import List

from tempren.template.ast import Location, TagName


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
    tag_name: TagName

    def __init__(self, tag_name: TagName, message: str):
        assert tag_name
        self.tag_name = tag_name
        super().__init__(f"Error in tag '{self.tag_name}': {message}")


class UnknownTagError(TagError):
    def __init__(self, tag_name: TagName):
        super().__init__(tag_name, f"Unknown tag name: {tag_name.name}")

    def with_location(self, whole_name_location: Location) -> "TemplateError":
        if not self.tag_name.category:
            return super().with_location(whole_name_location)
        name_location = Location(
            whole_name_location.line,
            whole_name_location.column + len(self.tag_name.category) + 1,
            len(self.tag_name.name),
        )
        return super().with_location(name_location)


class UnknownCategoryError(TagError):
    def __init__(self, tag_name: TagName):
        super().__init__(tag_name, f"Unknown category name: {tag_name.category}")

    def with_location(self, whole_name_location: Location) -> "TemplateError":
        assert self.tag_name.category
        category_location = Location(
            whole_name_location.line,
            whole_name_location.column,
            len(self.tag_name.category),
        )
        return super().with_location(category_location)


class AmbiguousTagError(TagError):
    category_names: List[str]

    def __init__(self, tag_name: TagName, category_names: List[str]):
        super().__init__(
            tag_name,
            f"This tag name is present in multiple categories: {', '.join(category_names)}",
        )
        self.category_names = category_names


class ContextMissingError(TagError):
    def __init__(self, tag_name: TagName):
        super().__init__(tag_name, f"Context is required for this tag")


class ContextForbiddenError(TagError):
    def __init__(self, tag_name: TagName):
        super().__init__(tag_name, f"This tag cannot be used with context")


class ConfigurationError(TagError):
    def __init__(self, tag_name: TagName, message: str):
        super().__init__(tag_name, f"Configuration not valid: {message}")
