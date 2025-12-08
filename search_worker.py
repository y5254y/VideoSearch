# -*- coding: utf-8 -*-
"""
SearchWorker runs AI-powered search in a background QThread and emits
signals back to the UI thread. Kept in a separate module to keep UI
code (app.py) smaller.
"""
from typing import List, Optional
from PySide6.QtCore import QThread, Signal
import os

# import the search engine interface (must exist in search.py)
from search import AISearchEngine


class SearchWorker(QThread):
    """Worker thread to run AI search without freezing the UI."""

    match_found = Signal(str, int, float)  # video_path, timestamp_ms, score
    error = Signal(str)  # error message
    finished_search = Signal()  # search completed
    progress = Signal(object)  # structured progress: ('video', completed_count, total) or ('frame', video_idx, processed, total_samples, total_videos)
    message = Signal(object)  # structured message for i18n: (key, params_dict) or plain str

    def __init__(
        self,
        search_engine: AISearchEngine,
        video_paths: List[str],
        mode: str,
        query_images: Optional[List[str]] = None,
        query_text: Optional[str] = None,
        query_category: Optional[str] = None,
        score_threshold: float = 0.25,
        parent=None
    ):
        super().__init__(parent)
        self.search_engine = search_engine
        self.video_paths = video_paths
        self.mode = mode
        self.query_images = query_images or []
        self.query_text = query_text or ""
        self.query_category = query_category or ""
        self.score_threshold = float(score_threshold)
        self._stopped = False

    def stop(self):
        """Request the search to stop."""
        self._stopped = True

    def run(self):
        """Execute the search in a background thread."""
        total = len(self.video_paths)
        try:
            for idx, video in enumerate(self.video_paths, start=1):
                if self._stopped:
                    break

                # Emit a structured message to indicate which video is being searched
                try:
                    self.message.emit(('searching_video', {'name': os.path.basename(video), 'idx': idx, 'total': total}))
                except Exception:
                    # fallback plain message
                    self.message.emit(f"Searching video {idx}/{total}...")

                # emit per-video progress so UI can switch context — use completed count so first video shows 0%
                try:
                    self.progress.emit(('video', max(0, idx-1), total))
                except Exception:
                    pass

                # per-sample/frame progress callback — emit frame-level progress including video index and total videos
                def _progress_callback(video_path, processed, total_samples):
                    try:
                        if total_samples is None:
                            return
                        # only emit frame progress when there is more than one sample
                        if int(total_samples) <= 1:
                            return
                        # send video index, processed samples, total_samples, total videos
                        self.progress.emit(('frame', idx, int(processed), int(total_samples), total))
                    except Exception:
                        pass

                # call search for single video and pass per-sample progress callback
                try:
                    kwargs = {}
                    if self.mode in ('image', 'text'):
                        kwargs['similarity_threshold'] = self.score_threshold
                    elif self.mode == 'category':
                        kwargs['confidence_threshold'] = self.score_threshold

                    gen = self.search_engine.search(
                        video_paths=[video],
                        mode=self.mode,
                        query_images=self.query_images if self.mode == 'image' else None,
                        query_text=self.query_text if self.mode == 'text' else None,
                        query_category=self.query_category if self.mode == 'category' else None,
                        progress_callback=_progress_callback,
                        stop_check=lambda: self._stopped,
                        **kwargs
                    )

                    # iterate generator using next() to catch GeneratorExit clearly
                    while True:
                        if self._stopped:
                            break
                        try:
                            item = next(gen)
                        except StopIteration:
                            break
                        except GeneratorExit:
                            # generator was closed externally; stop gracefully
                            break
                        except BaseException as e:
                            # emit error and stop this video's processing
                            try:
                                self.error.emit(str(e))
                            except Exception:
                                pass
                            break

                        try:
                            video_path, timestamp_ms, score = item
                            # emit match found
                            self.match_found.emit(video_path, timestamp_ms, float(score))
                            try:
                                self.message.emit(('found_match', {'name': os.path.basename(video_path), 'sec': int(timestamp_ms/1000), 'score': float(score)}))
                            except Exception:
                                self.message.emit("Found match")
                        except Exception:
                            # malformed item, ignore
                            pass

                    # emit per-video completion progress (this video done)
                    try:
                        self.progress.emit(('video', idx, total))
                    except Exception:
                        pass
                except BaseException as e:
                    try:
                        self.error.emit(str(e))
                    except Exception:
                        pass
                    continue

                if self._stopped:
                    break
        except BaseException as e:
            try:
                self.error.emit(str(e))
            except Exception:
                pass
        finally:
            try:
                self.finished_search.emit()
            except Exception:
                pass
