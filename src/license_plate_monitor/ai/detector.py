from typing import Any

import numpy.typing as npt
import torch
from ultralytics import YOLO


class LicensePlateDetector:
    def __init__(self, model_name: str = r"models\yolo26n-trained_int8_openvino_model"):
        self.model = YOLO(model_name, task="detect")
        self.last_tracked_ids: set[int] = set()

    def process_frame(
        self,
        frame: npt.NDArray[Any],
        conf_threshold: float,
        show_labels: bool,
        show_boxes: bool,
    ) -> tuple[npt.NDArray[Any], list[dict[str, Any]]]:
        """
        Xử lý frame và trả về ảnh đã vẽ cùng danh sách các đối tượng mới phát hiện.
        """
        results = self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            imgsz=800,
            conf=conf_threshold,
            verbose=False,
        )

        if not results or results[0].boxes is None or results[0].boxes.id is None:
            return frame, []

        res = results[0]
        annotated_frame = res.plot(labels=show_labels, boxes=show_boxes)
        new_detections = []

        ids_raw = res.boxes.id if res.boxes is not None else None

        if ids_raw is None:
            return annotated_frame, []

        # Chuyển IDs sang list Python tùy theo thiết bị chạy (CPU/GPU)
        if isinstance(ids_raw, torch.Tensor):
            ids = ids_raw.cpu().numpy().astype(int).tolist()
        else:
            ids = ids_raw.astype(int).tolist()

        for i, obj_id in enumerate(ids):
            if res.boxes is None:
                continue

            if obj_id not in self.last_tracked_ids:
                box = res.boxes[i]

                # Cắt ảnh đối tượng
                coords = box.xyxy[0].cpu().tolist()
                x1, y1, x2, y2 = coords
                h, w = frame.shape[:2]

                # Chỉ chấp nhận nếu box nằm hoàn toàn bên trong khung hình
                margin = 25  # cách lề 'margin' pixel
                if (
                    x1 > margin
                    and y1 > margin
                    and x2 < (w - margin)
                    and y2 < (h - margin)
                ):
                    self.last_tracked_ids.add(obj_id)

                    # Giới hạn kích thước bộ nhớ ID để tránh tràn vùng nhớ
                    if len(self.last_tracked_ids) > 100:
                        self.last_tracked_ids.clear()
                    crop = self.crop_box(frame, coords)

                    if crop.size > 0:
                        label = res.names[int(box.cls[0])]
                        conf = float(box.conf[0])

                        new_detections.append(
                            {"id": obj_id, "label": label, "conf": conf, "image": crop}
                        )

        return annotated_frame, new_detections

    def crop_box(
        self,
        image: npt.NDArray[Any],
        box: tuple[float, float, float, float] | list[float],
    ) -> npt.NDArray[Any]:
        """Cắt ảnh dựa trên tọa độ bounding box"""
        x1, y1, x2, y2 = map(int, box)
        # Đảm bảo tọa độ không vượt quá kích thước ảnh
        y1, y2 = max(0, y1), min(image.shape[0], y2)
        x1, x2 = max(0, x1), min(image.shape[1], x2)
        return image[y1:y2, x1:x2]
