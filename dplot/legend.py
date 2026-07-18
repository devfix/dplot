from enum import Enum, auto
from typing import Optional, Tuple
from .common import HAlign, VAlign


class LegendPosition(Enum):
    INSIDE = auto()
    OUTSIDE = auto()


class LegendSetup:
    def __init__(
            self,
            enable: bool = False,
            position_mode: LegendPosition = LegendPosition.INSIDE,
            h_align: HAlign = HAlign.RIGHT,
            v_align: VAlign = VAlign.TOP,
            coordinates: Optional[Tuple[float, float]] = None,
            font_size_pt: float = 8.0,
            title: Optional[str] = None
    ):
        """
        Backend-agnostic legend layout definition.

        :param enable: show / hide legend
        :param position_mode: Inside or outside the active data plot area
        :param h_align: Horizontal alignment zone relative to the mode
        :param v_align: Vertical alignment zone relative to the mode
        :param coordinates: Optional raw (x, y) coordinates relative to data area (0.0 to 1.0)
                            If provided, this overrides standard h_align/v_align placement.
        :param font_size_pt: Absolute font scale/size in points (easier to translate than multiplier ratios)
        :param title: Optional legend box header text
        """
        self.enable = enable
        self.position_mode = position_mode
        self.h_align = h_align
        self.v_align = v_align
        self.coordinates = coordinates
        self.font_size_pt = font_size_pt
        self.title = title
