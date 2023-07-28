import logging
from typing import List, Optional

from tempren.primitives import QualifiedTagName
from tempren.template.ast import Pattern, PatternElement, TagInstance, TagPlaceholder
from tempren.template.exceptions import TagError, TemplateError
from tempren.template.parser import TemplateParser
from tempren.template.registry import TagRegistry


class TemplateCompiler:
    log: logging.Logger

    registry: TagRegistry

    def __init__(self, registry: TagRegistry):
        self.log = logging.getLogger(__name__)
        self.parser = TemplateParser()
        self.registry = registry

    def compile(self, template_text: str) -> Pattern:
        self.log.debug("Compiling template %r", template_text)
        try:
            return self._bind(self.parser.parse(template_text))
        except TemplateError as template_error:
            template_error.template = template_text
            raise

    def _bind(self, pattern: Pattern) -> Pattern:
        return self._rewrite_pattern(pattern)

    def _rewrite_pattern(self, pattern: Pattern) -> Pattern:
        new_elements: List[PatternElement] = []
        for element in pattern.sub_elements:
            if isinstance(element, TagPlaceholder):
                new_elements.append(self._rewrite_tag_placeholder(element))
            else:
                new_elements.append(element)
        bound_pattern = Pattern(new_elements)
        bound_pattern.source_representation = pattern.source_representation
        return bound_pattern

    def _rewrite_tag_placeholder(self, tag_placeholder: TagPlaceholder) -> TagInstance:
        try:
            tag_factory = self.registry.get_tag_factory(tag_placeholder.tag_name)

            self.log.debug(
                "Creating tag '%s' with arguments: %s %s",
                tag_placeholder.tag_name,
                tag_placeholder.args,
                tag_placeholder.kwargs,
            )
            tag = tag_factory(*tag_placeholder.args, **tag_placeholder.kwargs)
        except TemplateError as template_error:
            raise template_error.with_location(tag_placeholder.location)
        except Exception as exc:
            raise ConfigurationError(tag_placeholder.tag_name, str(exc)).with_location(
                tag_placeholder.location
            ) from exc

        if tag.require_context is not None:
            if tag_placeholder.context and not tag.require_context:
                raise ContextForbiddenError(tag_placeholder.tag_name).with_location(
                    tag_placeholder.location
                )
            elif tag_placeholder.context is None and tag.require_context:
                raise ContextMissingError(tag_placeholder.tag_name).with_location(
                    tag_placeholder.location
                )

        context_pattern: Optional[Pattern] = None
        if tag_placeholder.context:
            context_pattern = self._rewrite_pattern(tag_placeholder.context)

        return TagInstance(tag, context=context_pattern)


class ContextMissingError(TagError):
    def __init__(self, tag_name: QualifiedTagName):
        super().__init__(tag_name, f"Context is required for this tag")


class ContextForbiddenError(TagError):
    def __init__(self, tag_name: QualifiedTagName):
        super().__init__(tag_name, f"This tag cannot be used with context")


class ConfigurationError(TagError):
    def __init__(self, tag_name: QualifiedTagName, message: str):
        super().__init__(tag_name, f"Configuration not valid: {message}")
