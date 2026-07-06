from od_platform.validate_dataset.registry import (check,CheckContext,CheckResult,CheckSeverity)

@check("冒烟测试")
def placeholder_check(ctx: CheckContext) -> CheckResult:
    return CheckResult(
        name = "冒烟测试",
        severity= CheckSeverity.PASS,
        summary = "<UNK>",
        details = {"yaml_path": str(ctx.yaml_path)}
    )