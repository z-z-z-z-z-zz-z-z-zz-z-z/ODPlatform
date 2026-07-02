# 数据集检查项开发与性能优化计划

## 一、现状分析

### 1.1 当前架构

- **CheckContext**（registry.py）：仅包含 `yaml_path` 字段
- **每个 check 函数**：独立解析 yaml、独立 glob 扫盘
- **已有检查项**：
  - `yaml_schema`：验证 yaml 文件结构（已实现）
  - `placeholder`：冒烟测试（已实现）

### 1.2 待实现检查项

| 检查项 | 功能描述 |
|--------|----------|
| `pair_existence` | 遍历每个 split 的图像，检查对应的 .txt 标签文件是否存在 |
| `label_format` | 遍历每个 .txt 文件，逐行验证字段数、类别范围、坐标格式 |
| `split_uniqueness` | 收集每个 split 的图像 stem，两两计算交集，检查是否有重复 |

### 1.3 性能问题

每个检查项重复执行以下操作：
1. **重复解析 yaml**：每个 check 都 `open + yaml.safe_load` 一次
2. **重复扫盘**：每个 check 都独立 glob 遍历图像/标签目录

对于 10 万张图的数据集，3 个检查项意味着约 30 万次文件系统操作，SSD 上耗时数秒，机械硬盘上耗时数十秒，纯资源浪费。

---

## 二、优化方案

### 2.1 核心思路

**预加载 + 上下文共享**：在运行所有 check 之前，一次性加载 yaml 配置和目录扫描结果，放入扩展后的 `CheckContext` 中，供所有 check 共享使用。

### 2.2 CheckContext 扩展

在 `CheckContext` 中增加以下字段（均为懒加载/预加载）：

```python
@dataclass
class CheckContext:
    yaml_path: Path
    # 以下为预加载字段，由 service 层填充
    yaml_config: dict | None = None          # 解析后的 yaml 配置
    dataset_root: Path | None = None         # 数据集根目录 (path 字段)
    split_image_dirs: dict[str, Path] | None = None   # {split: images_dir}
    split_label_dirs: dict[str, Path] | None = None   # {split: labels_dir}
    split_images: dict[str, list[Path]] | None = None  # {split: [image_paths]}
    split_labels: dict[str, list[Path]] | None = None  # {split: [label_paths]}
```

### 2.3 预加载逻辑

在 `service.py` 的 `run_all_checks` 中，调用 check 之前先执行预加载：

1. 解析 yaml → `yaml_config`
2. 从 yaml 中提取 `path`（数据集根目录）、`train`/`val`/`test` 路径
3. 构建 split 目录映射（images 和 labels）
4. 一次性 glob 扫描所有 split 的图像文件列表
5. 标签文件列表按需扫描（pair_existence 不需要，label_format 需要）

**注意**：如果 yaml_schema 检查失败（yaml 无法解析），后续依赖 yaml 的检查应优雅降级或跳过。

---

## 三、新增文件清单

### 3.1 修改文件

| 文件 | 修改内容 |
|------|----------|
| `registry.py` | 扩展 `CheckContext` 数据类，增加预加载字段 |
| `service.py` | 在 `run_all_checks` 中增加预加载逻辑，填充 CheckContext |
| `checks/yaml_schema.py` | 优先使用 ctx.yaml_config（如果已加载），避免重复解析 |

### 3.2 新增文件

| 文件 | 功能描述 |
|------|----------|
| `checks/pair_existence.py` | 图像-标签配对存在性检查 |
| `checks/label_format.py` | 标签格式验证检查 |
| `checks/split_uniqueness.py` | split 间图像唯一性检查 |

---

## 四、各检查项详细设计

### 4.1 pair_existence（配对存在性检查）

**输入**：`ctx.split_images`（预加载的图像列表）

**逻辑**：
1. 遍历每个 split（train/val/test）
2. 对每张图像，计算对应标签路径（`labels_dir / stem + '.txt'`）
3. 检查标签文件是否存在
4. 统计每个 split 的缺失数量、缺失列表（最多记录前 N 个）

**输出级别**：
- 存在缺失 → ERROR
- 全部配对成功 → PASS

**details 字段**：
```python
{
    "missing_count": int,
    "per_split": {
        "train": {"total": int, "missing": int, "missing_samples": [str, ...]},
        "val": {...},
        "test": {...}
    }
}
```

### 4.2 label_format（标签格式检查）

**输入**：`ctx.split_labels`（需额外扫描标签目录，或从图像推导）

**逻辑**：
1. 遍历每个 split 的所有 .txt 文件
2. 逐行解析，验证：
   - 字段数：YOLO 格式为 5 个（class + 4坐标）
   - 类别：0 <= class_id < nc（从 yaml_config 取 nc）
   - 坐标：0.0 <= x_center, y_center, width, height <= 1.0
   - 宽高 > 0
3. 统计错误文件数、错误行数、错误类型分布

**输出级别**：
- 存在格式错误 → ERROR
- 全部合法 → PASS

**details 字段**：
```python
{
    "error_file_count": int,
    "error_line_count": int,
    "error_types": {"wrong_field_count": int, "invalid_class": int, "invalid_coord": int, ...},
    "per_split": {
        "train": {"total_files": int, "error_files": int, "error_samples": [{"file": str, "errors": [str, ...]}, ...]},
        ...
    }
}
```

### 4.3 split_uniqueness（split 唯一性检查）

**输入**：`ctx.split_images`（预加载的图像列表）

**逻辑**：
1. 收集每个 split 的图像 stem 集合
2. 两两计算交集（train∩val, train∩test, val∩test）
3. 报告交集大小和样本（最多前 N 个）

**输出级别**：
- 存在交集 → ERROR
- 无交集 → PASS

**details 字段**：
```python
{
    "has_overlap": bool,
    "overlaps": {
        "train_val": {"count": int, "samples": [str, ...]},
        "train_test": {"count": int, "samples": [str, ...]},
        "val_test": {"count": int, "samples": [str, ...]}
    },
    "per_split_count": {"train": int, "val": int, "test": int}
}
```

---

## 五、预加载实现细节

### 5.1 预加载时机与位置

在 `service.py` 中新增 `_prepare_context(ctx: CheckContext) -> CheckContext` 函数，在 `run_all_checks` 开始时调用。

### 5.2 错误处理策略

- **yaml 解析失败**：不填充 yaml_config 及后续依赖字段，下游 check 需判断字段是否为 None，返回"无法执行"类结果
- **某个 split 目录不存在**：该 split 对应的列表为空，check 按需报告
- **预加载异常**：捕获异常，记录日志，check 仍可运行（但缺少缓存数据）

### 5.3 支持的 split 路径格式

yaml 中 train/val/test 可以是：
- 相对路径（相对于 path）：如 `"train/images"`
- 绝对路径
- 列表形式（暂不支持，遇到时报告 WARNING 并跳过）

---

## 六、风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|----------|
| CheckContext 字段变多，check 编写复杂度上升 | 低 | 字段有默认值 None，老 check 不受影响；新 check 按需取用 |
| 预加载失败导致所有 check 无法运行 | 中 | 预加载做异常隔离，失败后 check 仍可自己解析 yaml（回退到旧模式） |
| 数据集很大时，预加载本身耗时 | 低 | 预加载只做一次，相比 N 次重复扫盘仍是优化 |
| yaml 中 split 路径格式多样（列表/绝对路径/相对路径） | 中 | 先支持最常见的相对路径字符串，其他格式降级处理 |

---

## 七、验证方式

1. 运行单元测试（如有）
2. 构造一个小型测试数据集，包含：
   - 正常样本
   - 缺失标签的图像（用于 pair_existence）
   - 格式错误的标签文件（用于 label_format）
   - split 间重复的图像（用于 split_uniqueness）
3. 对比优化前后的执行时间（日志中有 `time_it` 装饰器的耗时输出）
