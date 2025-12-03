# -*- coding: utf-8 -*-
"""
Search utilities for VideoSearch application.
Provides AISearchEngine class for CLIP and YOLO based search,
scanning videos for matches, and formatting timestamps.
This module intentionally keeps heavy imports local to methods so
the application can still start without them for other features.
"""

from typing import List, Generator, Tuple, Union

# Attempt imports; set flags if unavailable
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from transformers import CLIPProcessor, CLIPModel
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


def format_ms(ms: int) -> str:
    """Format milliseconds to HH:MM:SS string."""
    s = ms // 1000
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    return f"{h:02d}:{m:02d}:{sec:02d}"


class AISearchEngine:
    """
    AI-based search engine using CLIP for text/image similarity
    and YOLO for object detection.
    """

    def __init__(self):
        """Initialize the search engine. Models are loaded lazily."""
        self.device = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"
        self.clip_model = None
        self.clip_processor = None
        self.yolo_model = None

    def load_models(self):
        """Load CLIP and YOLO models."""
        if CLIP_AVAILABLE and TORCH_AVAILABLE:
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model.to(self.device)
            self.clip_model.eval()

        if YOLO_AVAILABLE:
            self.yolo_model = YOLO("yolov8n.pt")

    def _encode_text(self, text: str):
        """Encode text using CLIP and return normalized embedding."""
        if not self.clip_model or not self.clip_processor:
            return None
        inputs = self.clip_processor(text=[text], return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            text_features = self.clip_model.get_text_features(**inputs)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        return text_features

    def _encode_image(self, image):
        """Encode PIL Image using CLIP and return normalized embedding."""
        if not self.clip_model or not self.clip_processor:
            return None
        inputs = self.clip_processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            image_features = self.clip_model.get_image_features(**inputs)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        return image_features

    def _cosine_similarity(self, a, b) -> float:
        """Compute cosine similarity between two tensors."""
        return (a @ b.T).item()

    def search(
        self,
        video_paths: List[str],
        query_data: Union[str, List[str]],
        mode: str,
        threshold: float = 0.25
    ) -> Generator[Tuple[str, int, float], None, None]:
        """
        Generator function to search videos for matches.

        Args:
            video_paths: List of video file paths to search.
            query_data: For 'text' mode: a string query.
                        For 'image' mode: a list of image paths (uses first).
                        For 'category' mode: category name string.
            mode: One of 'text', 'image', or 'category'.
            threshold: Similarity threshold for CLIP modes (0-1).

        Yields:
            Tuples of (video_path, timestamp_ms, score).
        """
        if not CV2_AVAILABLE:
            return

        # Prepare query embedding for CLIP modes
        query_embedding = None
        if mode == 'text':
            if not CLIP_AVAILABLE or not TORCH_AVAILABLE:
                return
            if self.clip_model is None:
                self.load_models()
            query_embedding = self._encode_text(query_data)
            if query_embedding is None:
                return

        elif mode == 'image':
            if not CLIP_AVAILABLE or not TORCH_AVAILABLE or not PIL_AVAILABLE:
                return
            if self.clip_model is None:
                self.load_models()
            # Use first image path
            image_path = query_data[0] if isinstance(query_data, list) else query_data
            try:
                query_image = Image.open(image_path).convert("RGB")
                query_embedding = self._encode_image(query_image)
            except (FileNotFoundError, OSError, ValueError):
                # Handle file not found, corrupt image, or invalid format
                return
            if query_embedding is None:
                return

        elif mode == 'category':
            if not YOLO_AVAILABLE:
                return
            if self.yolo_model is None:
                self.load_models()
            # query_data is the category name
            category_name = query_data.lower() if isinstance(query_data, str) else str(query_data).lower()

        else:
            return

        # Iterate through videos
        for video_path in video_paths:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                continue

            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            # Sample every 1 second
            sample_interval_frames = max(1, int(round(fps)))

            frame_idx = 0
            last_match_frame = -sample_interval_frames * 2  # Allow first frame to match

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Only process sampled frames
                if frame_idx % sample_interval_frames == 0:
                    timestamp_ms = int((frame_idx / fps) * 1000)

                    if mode in ('text', 'image'):
                        # CLIP-based similarity
                        try:
                            # Convert BGR to RGB and create PIL Image
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            pil_image = Image.fromarray(frame_rgb)
                            frame_embedding = self._encode_image(pil_image)

                            if frame_embedding is not None:
                                similarity = self._cosine_similarity(query_embedding, frame_embedding)
                                if similarity >= threshold:
                                    # Avoid duplicate matches too close together
                                    if frame_idx - last_match_frame >= sample_interval_frames * 2:
                                        yield (video_path, timestamp_ms, similarity)
                                        last_match_frame = frame_idx
                        except (RuntimeError, ValueError, cv2.error):
                            # Skip frame on CLIP/tensor/cv2 errors
                            pass

                    elif mode == 'category':
                        # YOLO object detection
                        try:
                            results = self.yolo_model(frame, verbose=False)
                            match_found_in_frame = False
                            for result in results:
                                if match_found_in_frame:
                                    break
                                if result.boxes is not None:
                                    for box in result.boxes:
                                        cls_id = int(box.cls[0])
                                        cls_name = self.yolo_model.names[cls_id].lower()
                                        if category_name in cls_name or cls_name in category_name:
                                            confidence = float(box.conf[0])
                                            # Avoid duplicate matches too close together
                                            if frame_idx - last_match_frame >= sample_interval_frames * 2:
                                                yield (video_path, timestamp_ms, confidence)
                                                last_match_frame = frame_idx
                                                match_found_in_frame = True
                                                break
                        except (RuntimeError, ValueError):
                            # Skip frame on YOLO inference errors
                            pass

                frame_idx += 1

            cap.release()
