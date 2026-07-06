import os
import shutil
from pathlib import Path

# 数据集根目录
root = Path(r"/data/processed/garbageinthesea")

# 需要处理的子目录（train, valid, test）
splits = ["train", "valid", "test"]

for split in splits:
    split_dir = root / split
    if not split_dir.exists():
        print(f"警告: {split_dir} 不存在，跳过")
        continue

    # 创建 images 和 labels 目录
    images_dir = split_dir / "images"
    labels_dir = split_dir / "labels"
    images_dir.mkdir(exist_ok=True)
    labels_dir.mkdir(exist_ok=True)

    # 遍历目录中的所有文件
    for file in split_dir.iterdir():
        if file.is_file():
            if file.suffix.lower() == ".jpg":
                shutil.move(str(file), str(images_dir / file.name))
                print(f"移动 {file.name} -> images/")
            elif file.suffix.lower() == ".xml":
                shutil.move(str(file), str(labels_dir / file.name))
                print(f"移动 {file.name} -> labels/")
            # 其他文件（如 .txt 等）不处理，保留在原位置

print("整理完成！")