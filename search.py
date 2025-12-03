# -*- coding: utf-8 -*-
"""
Search utilities for VideoSearch application.
Provides AISearchEngine class for AI-powered video search using CLIP and YOLO.
This module intentionally keeps imports local to functions so
the application can still start without dependencies for other features.
"""

from typing import List, Tuple, Generator, Optional


def format_ms(ms: int) -> str:
    s = ms // 1000
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    return f"{h:02d}:{m:02d}:{sec:02d}"


class AISearchEngine:
    """
    AI-powered search engine using CLIP for text/image search and YOLO for category/object search.
    """
    
    def __init__(self):
        """Initialize the AISearchEngine. Models are loaded lazily on first use."""
        self._clip_model = None
        self._clip_processor = None
        self._yolo_model = None
        self._device = None
    
    def _ensure_clip_loaded(self):
        """Lazy load CLIP model and processor."""
        if self._clip_model is None:
            import torch
            from transformers import CLIPModel, CLIPProcessor
            
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            self._clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self._clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self._clip_model.to(self._device)
            self._clip_model.eval()
    
    def _ensure_yolo_loaded(self):
        """Lazy load YOLO model."""
        if self._yolo_model is None:
            from ultralytics import YOLO
            self._yolo_model = YOLO("yolov8n.pt")
    
    def _get_clip_image_embedding(self, image):
        """Get CLIP embedding for an image (PIL Image or numpy array)."""
        import torch
        from PIL import Image
        import numpy as np
        
        self._ensure_clip_loaded()
        
        if isinstance(image, np.ndarray):
            # Convert BGR (OpenCV) to RGB
            image = Image.fromarray(image[:, :, ::-1])
        
        inputs = self._clip_processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self._device) for k, v in inputs.items()}
        
        with torch.no_grad():
            image_features = self._clip_model.get_image_features(**inputs)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        return image_features
    
    def _get_clip_text_embedding(self, text: str):
        """Get CLIP embedding for text."""
        import torch
        
        self._ensure_clip_loaded()
        
        inputs = self._clip_processor(text=[text], return_tensors="pt", padding=True)
        inputs = {k: v.to(self._device) for k, v in inputs.items()}
        
        with torch.no_grad():
            text_features = self._clip_model.get_text_features(**inputs)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        
        return text_features
    
    def search(
        self,
        video_paths: List[str],
        mode: str,
        query_images: Optional[List[str]] = None,
        query_text: Optional[str] = None,
        query_category: Optional[str] = None,
        sample_interval_s: float = 1.0,
        similarity_threshold: float = 0.25,
        confidence_threshold: float = 0.5
    ) -> Generator[Tuple[str, int, float], None, None]:
        """
        Search videos for matches based on the specified mode.
        
        Args:
            video_paths: List of video file paths to search.
            mode: One of 'image', 'text', or 'category'.
            query_images: List of query image paths (for 'image' mode).
            query_text: Text query string (for 'text' mode).
            query_category: Category/object name to detect (for 'category' mode).
            sample_interval_s: Interval between sampled frames in seconds.
            similarity_threshold: Minimum similarity score for CLIP matches.
            confidence_threshold: Minimum confidence for YOLO detections.
        
        Yields:
            Tuples of (video_path, timestamp_ms, score) for each match found.
        """
        import cv2
        
        if mode == 'image':
            yield from self._search_by_image(
                video_paths, query_images, sample_interval_s, similarity_threshold
            )
        elif mode == 'text':
            yield from self._search_by_text(
                video_paths, query_text, sample_interval_s, similarity_threshold
            )
        elif mode == 'category':
            yield from self._search_by_category(
                video_paths, query_category, sample_interval_s, confidence_threshold
            )
    
    def _search_by_image(
        self,
        video_paths: List[str],
        query_images: List[str],
        sample_interval_s: float,
        similarity_threshold: float
    ) -> Generator[Tuple[str, int, float], None, None]:
        """Search videos using query images with CLIP similarity."""
        import cv2
        import torch
        from PIL import Image
        
        self._ensure_clip_loaded()
        
        # Pre-compute embeddings for all query images
        query_embeddings = []
        for img_path in query_images:
            try:
                img = Image.open(img_path).convert('RGB')
                embedding = self._get_clip_image_embedding(img)
                query_embeddings.append(embedding)
            except Exception:
                continue
        
        if not query_embeddings:
            return
        
        # Stack all query embeddings for batch comparison
        query_stack = torch.cat(query_embeddings, dim=0)
        
        for video_path in video_paths:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                continue
            
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            step = max(1, int(round(fps * sample_interval_s)))
            frame_idx = 0
            last_match_frame = -1
            skip_frames = int(round(fps * 2.0))
            
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                
                if frame_idx % step == 0 and frame_idx > last_match_frame + skip_frames:
                    try:
                        frame_embedding = self._get_clip_image_embedding(frame)
                        
                        # Compute similarity with all query images (match any)
                        similarities = torch.matmul(query_stack, frame_embedding.T).squeeze(-1)
                        max_similarity = similarities.max().item()
                        
                        if max_similarity >= similarity_threshold:
                            pos_ms = int((frame_idx / fps) * 1000)
                            yield (video_path, pos_ms, max_similarity)
                            last_match_frame = frame_idx
                    except Exception:
                        pass
                
                frame_idx += 1
            
            cap.release()
    
    def _search_by_text(
        self,
        video_paths: List[str],
        query_text: str,
        sample_interval_s: float,
        similarity_threshold: float
    ) -> Generator[Tuple[str, int, float], None, None]:
        """Search videos using text query with CLIP."""
        import cv2
        import torch
        
        self._ensure_clip_loaded()
        
        # Pre-compute text embedding
        text_embedding = self._get_clip_text_embedding(query_text)
        
        for video_path in video_paths:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                continue
            
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            step = max(1, int(round(fps * sample_interval_s)))
            frame_idx = 0
            last_match_frame = -1
            skip_frames = int(round(fps * 2.0))
            
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                
                if frame_idx % step == 0 and frame_idx > last_match_frame + skip_frames:
                    try:
                        frame_embedding = self._get_clip_image_embedding(frame)
                        
                        similarity = torch.matmul(text_embedding, frame_embedding.T).item()
                        
                        if similarity >= similarity_threshold:
                            pos_ms = int((frame_idx / fps) * 1000)
                            yield (video_path, pos_ms, similarity)
                            last_match_frame = frame_idx
                    except Exception:
                        pass
                
                frame_idx += 1
            
            cap.release()
    
    def _search_by_category(
        self,
        video_paths: List[str],
        query_category: str,
        sample_interval_s: float,
        confidence_threshold: float
    ) -> Generator[Tuple[str, int, float], None, None]:
        """Search videos for objects matching the category using YOLO."""
        import cv2
        
        self._ensure_yolo_loaded()
        
        # Normalize category name for comparison
        query_category_lower = query_category.lower().strip()
        
        for video_path in video_paths:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                continue
            
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            step = max(1, int(round(fps * sample_interval_s)))
            frame_idx = 0
            last_match_frame = -1
            skip_frames = int(round(fps * 2.0))
            
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                
                if frame_idx % step == 0 and frame_idx > last_match_frame + skip_frames:
                    try:
                        results = self._yolo_model(frame, verbose=False)
                        
                        found_match = False
                        for result in results:
                            if found_match:
                                break
                            if result.boxes is None:
                                continue
                            
                            for box in result.boxes:
                                cls_id = int(box.cls[0])
                                conf = float(box.conf[0])
                                class_name = self._yolo_model.names[cls_id].lower()
                                
                                # Check for exact match or partial match
                                if class_name == query_category_lower or query_category_lower in class_name:
                                    if conf >= confidence_threshold:
                                        pos_ms = int((frame_idx / fps) * 1000)
                                        yield (video_path, pos_ms, conf)
                                        last_match_frame = frame_idx
                                        found_match = True
                                        break
                    except Exception:
                        pass
                
                frame_idx += 1
            
            cap.release()
