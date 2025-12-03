# -*- coding: utf-8 -*-
"""
Search utilities for VideoSearch application.
Provides functions for computing ORB descriptors of query images,
scanning videos for matches, and formatting timestamps.
This module intentionally keeps OpenCV imports local to functions so
the application can still start without OpenCV for other features.
"""

from typing import List, Tuple


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
