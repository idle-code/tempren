import textwrap
from typing import Optional, Type

from docstring_parser import parse as parse_docstring

from tempren.primitives import Tag, TagFactory, TagName


class TagFactoryFromClass(TagFactory):
    """Produces tag instances by instantiating provided python class"""

    _tag_class: Type[Tag]
    _tag_name: TagName

    @property
    def tag_name(self) -> TagName:
        return self._tag_name

    @property
    def configuration_signature(self) -> str:
        single_line_signature = self._create_configuration_signature()
        argument_description = self._create_arguments_description()
        if argument_description is None:
            return single_line_signature
        signature_start_length = 1 + len(self.tag_name) + 1
        return "\n".join(
            (
                single_line_signature,
                textwrap.indent(argument_description, " " * signature_start_length),
            )
        )

    def _create_configuration_signature(self) -> str:
        import inspect

        signature = inspect.signature(self._tag_class.configure)
        parameters_without_self = list(
            filter(lambda param: param.name != "self", signature.parameters.values())
        )
        signature_str = str(signature.replace(parameters=parameters_without_self))
        if self._tag_class.require_context is None:
            context_metavar = "[{...}]"
        elif self._tag_class.require_context is True:
            context_metavar = "{...}"  # TODO: test?
            if not parameters_without_self:
                # Empty argument list can be skipped for context-only tags
                signature_str = ""
        else:
            context_metavar = ""
        single_line_signature = f"%{self._tag_name}{signature_str}{context_metavar}"
        return single_line_signature

    def _create_arguments_description(self) -> Optional[str]:
        argument_description = []
        for argument in self._parsed_configure_docstring.params:
            argument_description.append(f"{argument.arg_name} - {argument.description}")
        if not argument_description:
            return None
        return "\n".join(argument_description)

    @property
    def short_description(self) -> str:
        if self._parsed_class_docstring.short_description:
            return self._parsed_class_docstring.short_description
        return ""

    @property
    def long_description(self) -> Optional[str]:
        return self._parsed_class_docstring.long_description

    def __init__(self, tag_class: Type[Tag], tag_name: TagName):
        self._tag_class = tag_class
        self._tag_name = tag_name
        self._parsed_class_docstring = parse_docstring(
            tag_class.__doc__ if tag_class.__doc__ else ""
        )
        self._parsed_configure_docstring = parse_docstring(
            tag_class.configure.__doc__ if tag_class.configure.__doc__ else ""
        )

    def __call__(self, *args, **kwargs) -> Tag:
        tag = self._tag_class()
        tag.configure(*args, **kwargs)  # type: ignore
        return tag
