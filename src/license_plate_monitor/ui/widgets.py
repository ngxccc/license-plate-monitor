from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)


class DetectionCard(QFrame):
    """Widget hiển thị một đối tượng trong Sidebar"""

    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__()
        self.setup_ui(data)

    def setup_ui(self, data: dict[str, Any]) -> None:
        self.setStyleSheet("""
            DetectionCard {
                background-color: #2c2c2c;
                border-radius: 8px;
                border: 1px solid #444;
                margin-bottom: 5px;
            }
            DetectionCard:hover {
                background-color: #3d3d3d;
                border: 1px solid #3498db;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Hiển thị ảnh cắt
        img_label = QLabel()
        img_label.setFixedSize(80, 80)

        h, w, ch = data["image"].shape
        qimg = QImage(
            data["image"].tobytes(), w, h, w * ch, QImage.Format.Format_RGB888
        )

        pixmap = QPixmap.fromImage(qimg).scaled(
            80,
            80,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Thông tin chi tiết
        info_layout = QVBoxLayout()
        id_label = QLabel(f"<b>ID: {data['id']}</b> | {data['label'].upper()}")
        id_label.setStyleSheet("color: #3498db; font-size: 13px; margin-left: 5px;")

        conf_label = QLabel(f"Độ tin cậy: {data['conf']:.2f}")
        conf_label.setStyleSheet("color: #bbb; font-size: 11px; margin-left: 5px;")

        time_label = QLabel(f"{data['time']}")
        time_label.setStyleSheet("color: #888; font-size: 11px; margin-left: 5px;")

        info_layout.addWidget(id_label)
        info_layout.addWidget(conf_label)
        info_layout.addWidget(time_label)

        layout.addWidget(img_label)
        layout.addLayout(info_layout)
