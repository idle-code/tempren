from bisect import bisect_right
from dataclasses import dataclass

from tempren.exceptions import MissingMetadataError


@dataclass(frozen=True)
class ResolutionTier:
    height: int
    name: str


# Display resolution standards sorted by height ascending.
# Source: https://en.wikipedia.org/wiki/Graphics_display_resolution
_RESOLUTION_TIERS: tuple[ResolutionTier, ...] = (
    ResolutionTier(120, "QQVGA"),
    ResolutionTier(240, "QVGA"),
    ResolutionTier(360, "nHD"),
    ResolutionTier(480, "VGA"),
    ResolutionTier(540, "qHD"),
    ResolutionTier(600, "SVGA"),
    ResolutionTier(720, "HD"),
    ResolutionTier(768, "XGA"),
    ResolutionTier(900, "HD+"),
    ResolutionTier(1080, "FHD"),
    ResolutionTier(1200, "WUXGA"),
    ResolutionTier(1440, "2K"),
    ResolutionTier(1600, "WQXGA"),
    ResolutionTier(1800, "QHD+"),
    ResolutionTier(2160, "4K"),
    ResolutionTier(2880, "5K"),
    ResolutionTier(4320, "8K"),
    ResolutionTier(8640, "16K"),
)

_TIER_HEIGHTS: tuple[int, ...] = tuple(tier.height for tier in _RESOLUTION_TIERS)


def resolve_resolution_name(width: int, height: int, p_notation: bool = False) -> str:
    """Map pixel dimensions to a standard display resolution name.

    The smaller dimension (``min(width, height)``) is used so that portrait and
    landscape orientations map to the same tier. The matched tier is the largest
    standard whose height does not exceed the effective dimension.

    :param width: image/video width in pixels
    :param height: image/video height in pixels
    :param p_notation: return height-based ``<H>p`` notation (e.g. ``1080p``)
        instead of the display-standard abbreviation (e.g. ``FHD``)
    :raises MissingMetadataError: when the effective dimension is smaller than
        the lowest known tier
    """
    effective = min(width, height)
    # bisect_right yields the index after any entries equal to `effective`;
    # the matched tier is therefore the one just before it (floor bucketing).
    index = bisect_right(_TIER_HEIGHTS, effective) - 1
    if index < 0:
        raise MissingMetadataError()
    tier = _RESOLUTION_TIERS[index]
    if p_notation:
        return f"{tier.height}p"
    return tier.name
