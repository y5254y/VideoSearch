# -*- coding: utf-8 -*-
"""
Search utilities for VideoSearch application.
Provides functions for computing ORB descriptors of query images,
scanning videos for matches, and formatting timestamps.
This module intentionally keeps OpenCV imports local to functions so
the application can still start without OpenCV for other features.
"""

from typing import List, Tuple, Generator, Any, Optional, Union


class AISearchEngine:
    """
    AI-powered search engine using CLIP and YOLO models.
    CLIP is used for text and image-based search.
    YOLO is used for category/object detection search.
    """

    def __init__(self):
        self.clip_model = None
        self.clip_processor = None
        self.yolo_model = None
        self._models_loaded = False

    def load_models(self) -> None:
        """
        Load CLIP (openai/clip-vit-base-patch32) and YOLO (yolov8n.pt) models.
        """
        if self._models_loaded:
            return

        import torch
        from transformers import CLIPProcessor, CLIPModel
        from ultralytics import YOLO

        # Load CLIP model
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        # Load YOLO model
        self.yolo_model = YOLO("yolov8n.pt")

        self._models_loaded = True

    def search(
        self,
        video_paths: List[str],
        query_data: Union[str, List[str]],
        mode: str,
        sample_interval_s: float = 1.0,
        score_threshold: float = 0.25
    ) -> Generator[Tuple[str, int, float], None, None]:
        """
        Generator function that searches videos for matches.

        Args:
            video_paths: List of video file paths to search.
            query_data: For 'text' mode: the text query string.
                       For 'image' mode: list of image file paths.
                       For 'category' mode: the category/object name to detect.
            mode: Search mode - 'text', 'image', or 'category'.
            sample_interval_s: Interval in seconds between sampled frames.
            score_threshold: Minimum similarity/confidence score for a match.

        Yields:
            Tuples of (video_path, timestamp_ms, score) for each match found.
        """
        import cv2
        import torch
        from PIL import Image
        import numpy as np

        if not self._models_loaded:
            self.load_models()

        for video_path in video_paths:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                continue

            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            step = max(1, int(round(fps * sample_interval_s)))
            frame_idx = 0

            # For image mode, precompute query image features
            query_features = None
            if mode == 'image':
                query_features = self._compute_image_query_features(query_data)
                if query_features is None:
                    cap.release()
                    continue

            # For text mode, precompute text features
            text_features = None
            if mode == 'text':
                text_features = self._compute_text_features(query_data)

            last_match_frame = -float('inf')
            min_frame_gap = int(round(fps * 2.0))  # Minimum 2 seconds between matches

            while True:
                ok, frame = cap.read()
                if not ok:
                    break

                if frame_idx % step == 0 and (frame_idx - last_match_frame) >= min_frame_gap:
                    timestamp_ms = int((frame_idx / fps) * 1000)
                    score = 0.0
                    is_match = False

                    if mode == 'text':
                        score = self._search_text(frame, text_features)
                        is_match = score >= score_threshold
                    elif mode == 'image':
                        score = self._search_image(frame, query_features)
                        is_match = score >= score_threshold
                    elif mode == 'category':
                        score = self._search_category(frame, query_data)
                        is_match = score >= score_threshold

                    if is_match:
                        last_match_frame = frame_idx
                        yield (video_path, timestamp_ms, score)

                frame_idx += 1

            cap.release()

    def _compute_text_features(self, text: str):
        """Compute CLIP text features for the query."""
        import torch

        inputs = self.clip_processor(text=[text], return_tensors="pt", padding=True)
        with torch.no_grad():
            text_features = self.clip_model.get_text_features(**inputs)
        return text_features / text_features.norm(dim=-1, keepdim=True)

    def _compute_image_query_features(self, image_paths: List[str]):
        """Compute averaged CLIP image features for query images."""
        import torch
        from PIL import Image

        features_list = []
        for path in image_paths:
            try:
                image = Image.open(path).convert("RGB")
                inputs = self.clip_processor(images=image, return_tensors="pt")
                with torch.no_grad():
                    features = self.clip_model.get_image_features(**inputs)
                features_list.append(features)
            except Exception:
                continue

        if not features_list:
            return None

        # Average all query image features
        avg_features = torch.mean(torch.stack(features_list), dim=0)
        return avg_features / avg_features.norm(dim=-1, keepdim=True)

    def _search_text(self, frame, text_features) -> float:
        """Search frame using CLIP text similarity."""
        import torch
        from PIL import Image
        import cv2

        # Convert OpenCV BGR frame to PIL RGB image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)

        inputs = self.clip_processor(images=pil_image, return_tensors="pt")
        with torch.no_grad():
            image_features = self.clip_model.get_image_features(**inputs)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        similarity = (image_features @ text_features.T).item()
        return similarity

    def _search_image(self, frame, query_features) -> float:
        """Search frame using CLIP image similarity."""
        import torch
        from PIL import Image
        import cv2

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)

        inputs = self.clip_processor(images=pil_image, return_tensors="pt")
        with torch.no_grad():
            image_features = self.clip_model.get_image_features(**inputs)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        similarity = (image_features @ query_features.T).item()
        return similarity

    def _search_category(self, frame, category: str) -> float:
        """Search frame using YOLO object detection."""
        # Run YOLO inference
        results = self.yolo_model(frame, verbose=False)

        category_lower = category.lower()
        max_confidence = 0.0

        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    class_name = self.yolo_model.names[cls_id].lower()
                    confidence = float(box.conf[0])

                    if category_lower in class_name or class_name in category_lower:
                        max_confidence = max(max_confidence, confidence)

        return max_confidence


def format_ms(ms: int) -> str:
    s = ms // 1000
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    return f"{h:02d}:{m:02d}:{sec:02d}"


def compute_query_descriptors(image_paths: List[str]):
    """
    Compute ORB descriptors for each image in image_paths.
    Returns a list of tuples (path, keypoints, descriptors).
    If OpenCV is not available or no valid descriptors found, returns [].
    """
    try:
        import cv2
    except Exception:
        return []

    orb = cv2.ORB_create(500)
    query_descs = []
    for p in image_paths:
        try:
            img = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            kps, desc = orb.detectAndCompute(img, None)
            if desc is None:
                continue
            query_descs.append((p, kps, desc))
        except Exception:
            continue
    return query_descs


def image_search_for_video(video_path: str, query_descs, sample_interval_s: float = 1.0,
                           match_ratio_thresh: float = 0.15, min_good_matches: int = 10):
    """
    Scan video frames at approximately sample_interval_s and try to match any query descriptor
    using ORB + BF kNN + ratio test. Returns list of tuples (position_ms, query_path, num_good_matches).
    """
    try:
        import cv2
    except Exception:
        return []

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    step = max(1, int(round(fps * sample_interval_s)))
    # create BF matcher for Hamming (ORB)
    try:
        bf = cv2.BFMatcher_create(cv2.NORM_HAMMING, crossCheck=False)
    except Exception:
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    matches_found = []
    frame_idx = 0
    orb = cv2.ORB_create(500)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_idx % step == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            kps_f, desc_f = orb.detectAndCompute(gray, None)
            if desc_f is None:
                frame_idx += 1
                continue

            for (qpath, kps_q, desc_q) in query_descs:
                try:
                    knn = bf.knnMatch(desc_q, desc_f, k=2)
                except Exception:
                    continue
                good = 0
                for m_n in knn:
                    if len(m_n) < 2:
                        continue
                    m, n = m_n
                    if m.distance < 0.75 * n.distance:
                        good += 1
                if good >= min_good_matches:
                    denom = max(1, min(len(desc_q), len(desc_f)))
                    ratio = good / denom
                    if ratio >= match_ratio_thresh:
                        pos_ms = int((frame_idx / fps) * 1000)
                        matches_found.append((pos_ms, qpath, good))
                        # skip ahead to avoid duplicate nearby detections
                        skip_frames = int(round(fps * 2.0))
                        frame_idx += skip_frames
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                        break
        frame_idx += 1

    cap.release()
    matches_found.sort(key=lambda x: x[0])
    return matches_found
