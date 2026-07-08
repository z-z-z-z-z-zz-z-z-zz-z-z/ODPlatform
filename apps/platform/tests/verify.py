#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :verify.py
# @Time      :2026/7/7 16:12:25
# @Author    :雨霓同学
# @Project   :ODPlatform
# @Function  :
from od_platform.frame_source import create_frame_source
from od_platform.frame_source import CameraConfig
# base = CameraConfig(width=1920, height=1080, fps=30, backend='msmf')
import cv2

if __name__ == "__main__":
    with create_frame_source(source = "demo2.mp4") as src:
        src.seek(time_sec=120)
        for frame in src:
            img = frame.image
            cv2.putText(img, f"FPS: {frame.info.fps:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("frame", img)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
    cv2.destroyAllWindows()


