from dataclasses import dataclass
from enum import Enum
from typing import Union, List, Tuple


@dataclass(frozen=True)
class RGBAColor:
    """
    Backend-agnostic representation of an RGBA color.
    Used for custom colors or when transparency (alpha) is needed.
    """
    r: int
    g: int
    b: int
    a: float = 1.0

    def __post_init__(self):
        assert 0 <= self.r <= 255, f"Red component {self.r} out of bounds [0, 255]"
        assert 0 <= self.g <= 255, f"Green component {self.g} out of bounds [0, 255]"
        assert 0 <= self.b <= 255, f"Blue component {self.b} out of bounds [0, 255]"
        assert 0.0 <= self.a <= 1.0, f"Alpha component {self.a} out of bounds [0.0, 1.0]"


class Color(Enum):
    """
    Comprehensive color enumeration where values equal their (R, G, B) tuple.
    """
    # --- Core Library Literals ---
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 128, 0)
    BLUE = (0, 0, 255)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    YELLOW = (255, 255, 0)
    GRAY = (128, 128, 128)
    WHITE = (255, 255, 255)
    DARKGRAY = (169, 169, 169)
    LIGHTGRAY = (211, 211, 211)
    BROWN = (165, 42, 42)
    LIME = (0, 255, 0)
    OLIVE = (128, 128, 0)
    ORANGE = (255, 165, 0)
    PINK = (255, 192, 203)
    PURPLE = (128, 0, 128)
    TEAL = (0, 128, 128)
    VIOLET = (238, 130, 238)

    # --- Extended W3C / SVG Standard Colors ---
    ALICEBLUE = (240, 248, 255)
    ANTIQUEWHITE = (250, 235, 215)
    AQUAMARINE = (127, 255, 212)
    AZURE = (240, 255, 255)
    BEIGE = (245, 245, 220)
    BISQUE = (255, 228, 196)
    BLANCHEDALMOND = (255, 235, 205)
    BLUEVIOLET = (138, 43, 226)
    BURLYWOOD = (222, 184, 135)
    CADETBLUE = (95, 158, 160)
    CHARTREUSE = (127, 255, 0)
    CHOCOLATE = (210, 105, 30)
    CORAL = (255, 127, 80)
    CORNFLOWERBLUE = (100, 149, 237)
    CORNSILK = (255, 248, 220)
    CRIMSON = (220, 20, 60)
    DARKBLUE = (0, 0, 139)
    DARKCYAN = (0, 139, 139)
    DARKGOLDENROD = (184, 134, 11)
    DARKGREEN = (0, 100, 0)
    DARKKHAKI = (189, 183, 107)
    DARKMAGENTA = (139, 0, 139)
    DARKOLIVEGREEN = (85, 107, 47)
    DARKORANGE = (255, 140, 0)
    DARKORCHID = (153, 50, 204)
    DARKRED = (139, 0, 0)
    DARKSALMON = (233, 150, 122)
    DARKSEAGREEN = (143, 188, 143)
    DARKSLATEBLUE = (72, 61, 139)
    DARKSLATEGRAY = (47, 79, 79)
    DARKTURQUOISE = (0, 206, 209)
    DARKVIOLET = (148, 0, 211)
    DEEPPINK = (255, 20, 147)
    DEEPSKYBLUE = (0, 191, 255)
    DIMGRAY = (105, 105, 105)
    DODGERBLUE = (30, 144, 255)
    FIREBRICK = (178, 34, 34)
    FLORALWHITE = (255, 250, 240)
    FORESTGREEN = (34, 139, 34)
    FUCHSIA = (255, 0, 255)
    GAINSBORO = (220, 220, 220)
    GHOSTWHITE = (248, 248, 255)
    GOLD = (255, 215, 0)
    GOLDENROD = (218, 165, 32)
    GREENYELLOW = (173, 255, 47)
    HONEYDEW = (240, 255, 240)
    HOTPINK = (255, 105, 180)
    INDIANRED = (205, 92, 92)
    INDIGO = (75, 0, 130)
    IVORY = (255, 255, 240)
    KHAKI = (240, 230, 140)
    LAVENDER = (230, 230, 250)
    LAVENDERBLUSH = (255, 240, 245)
    LAWNGREEN = (124, 252, 0)
    LEMONCHIFFON = (255, 250, 205)
    LIGHTBLUE = (173, 216, 230)
    LIGHTCORAL = (240, 128, 128)
    LIGHTCYAN = (224, 255, 255)
    LIGHTGOLDENRODYELLOW = (250, 250, 210)
    LIGHTGREEN = (144, 238, 144)
    LIGHTPINK = (255, 182, 193)
    LIGHTSALMON = (255, 160, 122)
    LIGHTSEAGREEN = (32, 178, 170)
    LIGHTSKYBLUE = (135, 206, 250)
    LIGHTSLATEGRAY = (119, 136, 153)
    LIGHTSTEELBLUE = (176, 196, 222)
    LIGHTYELLOW = (255, 255, 224)
    LIMEGREEN = (50, 205, 50)
    LINEN = (250, 240, 230)
    MAROON = (128, 0, 0)
    MEDIUMAQUAMARINE = (102, 205, 170)
    MEDIUMBLUE = (0, 0, 205)
    MEDIUMORCHID = (186, 85, 211)
    MEDIUMPURPLE = (147, 112, 219)
    MEDIUMSEAGREEN = (60, 179, 113)
    MEDIUMSLATEBLUE = (123, 104, 238)
    MEDIUMSPRINGGREEN = (0, 250, 154)
    MEDIUMTURQUOISE = (72, 209, 204)
    MEDIUMVIOLETRED = (199, 21, 133)
    MIDNIGHTBLUE = (25, 25, 112)
    MINTCREAM = (245, 255, 250)
    MISTYROSE = (255, 228, 225)
    MOCCASIN = (255, 228, 181)
    NAVAJOWHITE = (255, 222, 173)
    NAVY = (0, 0, 128)
    OLDLACE = (253, 245, 230)
    OLIVEDRAB = (107, 142, 35)
    ORANGERED = (255, 69, 0)
    ORCHID = (218, 112, 214)
    PALEGOLDENROD = (238, 232, 170)
    PALEGREEN = (152, 251, 152)
    PALETURQUOISE = (175, 238, 238)
    PALEVIOLETRED = (219, 112, 147)
    PAPAYAWHIP = (255, 239, 213)
    PEACHPUFF = (255, 218, 185)
    PERU = (205, 133, 63)
    PLUM = (221, 160, 221)
    POWDERBLUE = (176, 224, 230)
    ROSYBROWN = (188, 143, 143)
    ROYALBLUE = (65, 105, 225)
    SADDLEBROWN = (139, 69, 19)
    SALMON = (250, 128, 114)
    SANDYBROWN = (244, 164, 96)
    SEAGREEN = (46, 139, 87)
    SEASHELL = (255, 245, 238)
    SIENNA = (160, 82, 45)
    SILVER = (192, 192, 192)
    SKYBLUE = (135, 206, 235)
    SLATEBLUE = (106, 90, 205)
    SLATEGRAY = (112, 128, 144)
    SNOW = (255, 250, 250)
    SPRINGGREEN = (0, 255, 127)
    STEELBLUE = (70, 130, 180)
    TAN = (210, 180, 140)
    THISTLE = (216, 191, 216)
    TOMATO = (255, 99, 71)
    TURQUOISE = (64, 224, 208)
    WHEAT = (245, 222, 179)
    WHITESMOKE = (245, 245, 245)
    YELLOWGREEN = (154, 205, 50)

    # --- Matplotlib / Tableau 10 Palette ---
    TAB_BLUE = (31, 119, 180)
    TAB_ORANGE = (255, 127, 14)
    TAB_GREEN = (44, 160, 44)
    TAB_RED = (214, 39, 40)
    TAB_PURPLE = (148, 103, 189)
    TAB_BROWN = (140, 86, 75)
    TAB_PINK = (227, 119, 194)
    TAB_GRAY = (127, 127, 127)
    TAB_OLIVE = (188, 189, 34)
    TAB_CYAN = (23, 190, 207)

    @property
    def r(self) -> int:
        return self.value[0]

    @property
    def g(self) -> int:
        return self.value[1]

    @property
    def b(self) -> int:
        return self.value[2]

    def with_alpha(self, alpha: float) -> RGBAColor:
        """Conveniently create a transparent RGBAColor from this enum member."""
        return RGBAColor(self.r, self.g, self.b, alpha=alpha)

    @classmethod
    def _missing_(cls, value):
        """
        Allows smart string lookup.
        Examples: Color('tab:blue'), Color('dark-gray'), or Color('DARK_GRAY') all resolve cleanly.
        Also resolves if someone passes an explicit RGB tuple like (255, 0, 0).
        """
        if isinstance(value, str):
            clean_name = value.upper().replace(':', '_').replace(' ', '_').replace('-', '_')
            for member in cls:
                if member.name == clean_name or member.name.replace('_', '') == clean_name.replace('_', ''):
                    return member
        elif isinstance(value, tuple) and len(value) == 3:
            for member in cls:
                if member.value == value:
                    return member
        return super()._missing_(value)


# ==========================================
# Backend Conversion Functions
# ==========================================

AnyColor = Union[Color, RGBAColor, Tuple[int, int, int], str]


def color_to_pgfplots_color(color: AnyColor) -> str:
    """
    Converts a Color enum, RGBAColor, tuple, or string name to an inline pgfplots color string.
    Example output: '{rgb,255:red,255; green,165; blue,0}'
    """
    col = _resolve_color(color)
    return f"{{rgb,255:red,{col.r}; green,{col.g}; blue,{col.b}}}"


def color_to_pgfplots_options(color: AnyColor) -> str:
    """
    Returns a string of pgfplots key-value strings for both color and opacity.
    Example output: 'color={rgb,255:red,255; green,128; blue,0},opacity=0.5'
    """
    col = _resolve_color(color)
    opts = [f"color={color_to_pgfplots_color(col)}"]
    if col.a < 1.0:
        opts.append(f"opacity={col.a:.3g}")
    return ','.join(opts)


def color_to_lilaq_color(color: AnyColor) -> str:
    """
    Converts a Color enum, RGBAColor, tuple, or string name to a valid Typst/Lilaq color string.
    Example output: 'rgb(31, 119, 180)' or 'rgb(255, 0, 0, 50%)'
    """
    col = _resolve_color(color)
    if col.a < 1.0:
        alpha_pct = round(col.a * 100, 1)
        alpha_str = f"{int(alpha_pct)}%" if alpha_pct.is_integer() else f"{alpha_pct}%"
        return f'rgb({col.r}, {col.g}, {col.b}, {alpha_str})'
    return f'rgb({col.r}, {col.g}, {col.b})'


def _resolve_color(val: AnyColor) -> RGBAColor:
    """Helper to convert any acceptable color format into a standardized RGBAColor."""
    if isinstance(val, RGBAColor):
        return val
    if isinstance(val, Color):
        return RGBAColor(val.r, val.g, val.b)
    if isinstance(val, tuple):
        if len(val) == 3:
            return RGBAColor(*val)
        elif len(val) == 4:
            return RGBAColor(*val)
    if isinstance(val, str):
        try:
            enum_col = Color(val)
            return RGBAColor(enum_col.r, enum_col.g, enum_col.b)
        except ValueError:
            raise ValueError(f"Color name '{val}' could not be resolved to a known Color.")
    raise TypeError(f"Expected Color enum, RGBAColor, tuple, or str, got {type(val)}")