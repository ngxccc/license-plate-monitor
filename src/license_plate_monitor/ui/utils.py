from typing import cast

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QDoubleSpinBox, QPushButton, QWidget


class UIConfig:
    PRIMARY_COLOR = "#3498db"
    DANGER_COLOR = "#c62828"
    SUCCESS_COLOR = "#2e7d32"
    BG_DARK = "#1a1a1a"
    CARD_BG = "#2c2c2c"

    # CSS mẫu cho Detection Card
    CARD_STYLE = f"""
        DetectionCard {{
            background-color: {CARD_BG};
            border-radius: 8px;
            border: 1px solid #444;
        }}
        DetectionCard:hover {{
            border: 1px solid {PRIMARY_COLOR};
        }}
    """


class StyleMixin:
    """Mixin cung cấp phương thức update_style cho các widget"""

    def update_style(
        self,
        default: str,
        hover: str | None = None,
        disabled: str | None = None,
    ) -> None:
        """Cập nhật stylesheet động cho widget

        Args:
            default: CSS cho trạng thái mặc định
            hover: CSS cho trạng thái hover (optional)
            disabled: CSS cho trạng thái disabled (optional)
        """
        old_style = cast(QWidget, self).styleSheet()
        style_sheet = f"""
            {self.__class__.__bases__[0].__name__} {{
                {default}
            }}
        """

        if hover:
            style_sheet += f"""
            {self.__class__.__bases__[0].__name__}:hover {{
                {hover}
            }}
            """
        if disabled:
            style_sheet += f"""
            {self.__class__.__bases__[0].__name__}:disabled {{
                {disabled}
            }}
            """

        new_style = old_style + style_sheet
        cast(QWidget, self).setStyleSheet(new_style)


class StyledButton(QPushButton, StyleMixin):
    """Nút bấm với style mặc định của hệ thống"""

    def __init__(
        self,
        text: str,
        color: str = "#444",
        hover_color: str = "#555",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 5px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:disabled {{
                background-color: #222;
                color: #666;
            }}
        """)


class StyledCheckBox(QCheckBox, StyleMixin):
    """Checkbox với màu chữ trắng mặc định"""

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 12px;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class StyledSpinBox(QDoubleSpinBox, StyleMixin):
    """SpinBox cấu hình sẵn cho các thông số AI"""

    def __init__(
        self,
        min_val: float,
        max_val: float,
        step: float,
        default: float,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setRange(min_val, max_val)
        self.setSingleStep(step)
        self.setValue(default)
        self.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                padding: 3px;
                border-radius: 4px;
            }
        """)
