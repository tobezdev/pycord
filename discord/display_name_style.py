"""
The MIT License (MIT)

Copyright (c) 2021-present Pycord Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .colour import Colour
from .enums import DisplayNameEffect, DisplayNameFont, try_enum
from .utils import MISSING

__all__ = ("DisplayNameStyle",)


class DisplayNameStyle:
    """The font, effect, and colours used to display a user's name.

    This can be passed to :meth:`ClientUser.edit` or :meth:`Member.edit`.
    Discord controls where each part of the style is visible; in servers,
    role colours can take precedence over the style's colours.

    .. versionadded:: 2.8

    Parameters
    ----------
    font: Union[:class:`DisplayNameFont`, :class:`int`]
        The font to use. Defaults to :attr:`DisplayNameFont.default`.
    effect: Union[:class:`DisplayNameEffect`, :class:`int`]
        The effect to use. Defaults to :attr:`DisplayNameEffect.solid`.
    colours: Sequence[Union[:class:`Colour`, :class:`int`]]
        The RGB colours for the effect. Discord validates the number of colours
        supported by the chosen effect. Defaults to an empty sequence.
    colors: Sequence[Union[:class:`Colour`, :class:`int`]]
        An alias for ``colours``. Passing both spellings raises :class:`TypeError`.

    Attributes
    ----------
    font: :class:`DisplayNameFont`
        The font. Unknown values from Discord are preserved.
    effect: :class:`DisplayNameEffect`
        The effect. Unknown values from Discord are preserved.
    colours: Tuple[:class:`Colour`, ...]
        The colours used by the effect.
    """

    __slots__ = ("font", "effect", "_colours")

    def __init__(
        self,
        *,
        font: DisplayNameFont | int = DisplayNameFont.default,
        effect: DisplayNameEffect | int = DisplayNameEffect.solid,
        colours: Sequence[Colour | int] = MISSING,
        colors: Sequence[Colour | int] = MISSING,
    ) -> None:
        font_id = getattr(font, "value", font)
        effect_id = getattr(effect, "value", effect)
        for name, value in (("font", font_id), ("effect", effect_id)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an enum value or integer")
        self.font = try_enum(DisplayNameFont, font_id)
        self.effect = try_enum(DisplayNameEffect, effect_id)
        if colours is not MISSING and colors is not MISSING:
            raise TypeError("cannot pass both colours and colors")
        if colors is not MISSING:
            colours = colors
        self.colours = () if colours is MISSING else colours

    @property
    def colours(self) -> tuple[Colour, ...]:
        """Tuple[:class:`Colour`, ...]: The colours used by the effect."""
        return self._colours

    @colours.setter
    def colours(self, value: Sequence[Colour | int]) -> None:
        values = tuple(c.value if isinstance(c, Colour) else c for c in value)
        if any(isinstance(c, bool) or not isinstance(c, int) for c in values):
            raise TypeError("colours must contain Colour instances or integers")
        if any(not 0 <= c <= 0xFFFFFF for c in values):
            raise ValueError("colours must be between 0x000000 and 0xFFFFFF")
        self._colours = tuple(Colour(c) for c in values)

    @classmethod
    def _from_data(cls, data: dict[str, Any]) -> DisplayNameStyle:
        return cls(
            font=data["font_id"],
            effect=data["effect_id"],
            colours=data["colors"],
        )

    @property
    def colors(self) -> tuple[Colour, ...]:
        """Tuple[:class:`Colour`, ...]: An alias for :attr:`colours`."""
        return self.colours

    @colors.setter
    def colors(self, value: Sequence[Colour | int]) -> None:
        self.colours = value

    def to_dict(self) -> dict[str, Any]:
        """Returns the style in Discord's response format."""
        return {
            "font_id": self.font.value,
            "effect_id": self.effect.value,
            "colors": [c.value for c in self.colours],
        }

    def _to_edit_payload(self) -> dict[str, Any]:
        return {f"display_name_{key}": value for key, value in self.to_dict().items()}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DisplayNameStyle):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        return f"<DisplayNameStyle font={self.font!r} effect={self.effect!r} colours={self.colours!r}>"


def _display_name_style_payload(style: DisplayNameStyle | None) -> dict[str, Any]:
    if style is None:
        return dict.fromkeys(
            ("display_name_font_id", "display_name_effect_id", "display_name_colors")
        )
    if not isinstance(style, DisplayNameStyle):
        raise TypeError("display_name_style must be a DisplayNameStyle or None")
    return style._to_edit_payload()
