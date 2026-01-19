from typing import Any, cast

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from license_plate_monitor.ui.utils import StyledButton, StyledCheckBox, StyledSpinBox


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
        id_label.setStyleSheet("color: #3498db; font-size: 13px; margin-left: 10px;")

        conf_label = QLabel(f"Độ tin cậy: {data['conf']:.2f}")
        conf_label.setStyleSheet("color: #bbb; font-size: 11px; margin-left: 10px;")

        time_label = QLabel(f"{data['time']}")
        time_label.setStyleSheet("color: #888; font-size: 11px; margin-left: 10px;")

        info_layout.addWidget(id_label)
        info_layout.addWidget(conf_label)
        info_layout.addWidget(time_label)

        layout.addWidget(img_label)
        layout.addLayout(info_layout)


class DetectionSidebar(QScrollArea):
    """Lớp chuyên trách quản lý danh sách các biển số nhận diện được"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFixedWidth(300)

        self.container = QWidget()
        self.sidebar_layout = QVBoxLayout(self.container)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.container.setLayout(self.sidebar_layout)
        self.setWidget(self.container)

        self.max_cards = 20

    def add_card(self, data: dict[str, Any]) -> None:
        """Thêm card mới và tự động xóa card cũ nếu vượt giới hạn"""
        while self.sidebar_layout.count() >= self.max_cards:
            item = self.sidebar_layout.takeAt(self.sidebar_layout.count() - 1)
            if item and item.widget():
                # Ép kiểu để IDE đần độn không báo lỗi
                cast(QWidget, item.widget()).deleteLater()

        card = DetectionCard(data)
        self.sidebar_layout.insertWidget(0, card)

        # Tự động cuộn lên đầu
        scrollbar = self.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(0)

    def clear_history(self) -> None:
        """Xóa toàn bộ lịch sử hiển thị"""
        while self.sidebar_layout.count() > 0:
            item = self.sidebar_layout.takeAt(0)
            if item and item.widget():
                cast(QWidget, item.widget()).deleteLater()


class SourceTab(QWidget):
    """Quản lý cấu hình nguồn vào"""

    def __init__(self) -> None:
        super().__init__()
        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setVerticalSpacing(10)

        self.combo = QComboBox()
        self.combo.addItems(["YouTube", "Webcam", "Local File", "RTSP"])
        self.combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Nhập URL YouTube")

        self.res_combo = QComboBox()
        self.res_combo.setEnabled(False)
        self.res_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        layout.addWidget(QLabel("Loại nguồn:"), 0, 0)
        layout.addWidget(self.combo, 0, 1)
        layout.addWidget(QLabel("Đường dẫn:"), 1, 0)
        layout.addWidget(self.input, 1, 1)
        layout.addWidget(QLabel("Độ phân giải:"), 2, 0)
        layout.addWidget(self.res_combo, 2, 1)


class AISettingTab(QWidget):
    """Quản lý các thông số AI và lưu trữ"""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.conf_spin = StyledSpinBox(0.1, 1.0, 0.05, 0.65)

        self.show_labels = StyledCheckBox("Hiện nhãn văn bản")
        self.show_boxes = StyledCheckBox("Hiện khung bao (Boxes)")

        self.auto_save = StyledCheckBox("Tự động lưu ảnh vào máy")
        self.auto_save.setToolTip("Lưu ảnh cắt biển số vào thư mục 'detections'")
        self.auto_save.setChecked(True)

        self.reset_btn = StyledButton("Đặt lại mặc định", hover_color="#c62828")
        self.reset_btn.update_style("margin-top: 10px")

        layout.addWidget(QLabel("Độ tin cậy (Confidence):"))
        layout.addWidget(self.conf_spin)
        layout.addWidget(self.show_labels)
        layout.addWidget(self.show_boxes)
        layout.addWidget(self.auto_save)
        layout.addWidget(self.reset_btn)
        layout.addStretch()


class SettingsDock(QDockWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Cài đặt hệ thống", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        # Cho phép đóng, di chuyển và tắt
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )


class StatsDock(QDockWidget):
    """Dock hiển thị thông tin thống kê số lượng phương tiện"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Thống kê dữ liệu", parent)

        self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        # Widget bên trong Dock
        self.inner_widget = QWidget()
        self.setWidget(self.inner_widget)
        self.inner_widget.setStyleSheet("background-color: #252525;")

        layout = QHBoxLayout(self.inner_widget)
        self.stats_label = QLabel("Thống kê: Chưa có dữ liệu")
        self.stats_label.setStyleSheet(
            "color: #00FF00; font-weight: bold; font-size: 16px;"
        )
        layout.addWidget(self.stats_label)

    def update_text(self, text: str) -> None:
        """Cập nhật nội dung hiển thị"""
        self.stats_label.setText(text)
