#!/usr/bin/env python
# -*- coding:utf-8 -*-# aFileName:factory.py:2026/7/7 15:56:48:雨霓同学# aAuthor
# aProject:0DPlatform
# aFunction
from __future__ import annotations
import logging
from typing import Any, Optional
from pathlib import Path

from .core.base import FrameSource
from .core.config import CameraConfig

from.core.types import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS
from.sources.camera import CameraSource
from .sources.video import VideoSource
from .sources.image import ImageSource, ImageFolderSource

logger = logging.getLogger(__name__)
_STREAM_SCHEMES = ("rtsp://","http://", "https://", "rtmp://")


def _build_source(
    source: str,
    camera_config: Optional[CameraConfig],
    options: dict[str, Any]
    ) -> FrameSource:
    #1，数字一>摄像头
    if source.isdigit():
        camera_id = int(source)
        cfg = camera_config or CameraConfig
        cfg = cfg.model_copy(update={"camera_id": camera_id})
        return CameraSource(cfg)

    #2 网络流
    if source.lower().startswith(_STREAM_SCHEMES):
        return VideoSource(source)

    #本地路径视频、图像.文件夹
    path = Path(source)
    if not path.exists():
        raise ValueError(f"Source {source} does not exist")

    if path.is_dir():
        return ImageFolderSource(source)

    ext = path.suffix.lower()
    if ext in VIDEO_EXTENSIONS:
        return VideoSource(source)
    if ext in IMAGE_EXTENSIONS:
        return ImageSource(source)
    raise ValueError(f"Source {source} is not a valid frame source")

def create_frame_source(
        source: str,
        camera_config: Optional[CameraConfig] = None,
        *,
        stride: int = 1,
        **options: Any,
    ) -> FrameSource:
    if stride < 1:
        raise ValueError(f"stride必须大于等于1")
    inner = _build_source(source, camera_config, options)
    if stride > 1:
        inner.set_stride(stride)
    return inner



