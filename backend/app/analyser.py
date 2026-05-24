import re
from dataclasses import dataclass, field


@dataclass
class ComponentDebt:
    filename: str
    filepath: str
    loc: int = 0
    props_count: int = 0
    any_count: int = 0
    todo_count: int = 0
    component_count: int = 0
    nested_ternary_count: int = 0
    console_log_count: int = 0
    missing_return_type_count: int = 0
    debt_score: float = 0.0
    debt_level: str = "low"
    issues: list = field(default_factory=list)


def _strip_strings_and_comments(code: str) -> str:
    """Remove string literals and comments to avoid false positives."""
    code = re.sub(r'//[^\n]*', '', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'`[^`]*`', '""', code, flags=re.DOTALL)
    code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', code)
    code = re.sub(r"'(?:[^'\\]|\\.)*'", "''", code)
    return code


def _count_props(content: str) -> int:
    """Count individual props in the first Props interface/type found."""
    match = re.search(
        r'(?:interface|type)\s+\w*[Pp]rops\s*=?\s*\{([^}]*)\}',
        content, re.DOTALL
    )
    if not match:
        return 0
    block = match.group(1)
    prop_lines = [
        l.strip() for l in block.splitlines()
        if l.strip()
        and not l.strip().startswith('//')
        and re.search(r'\w+\s*\??\s*:', l)
    ]
    return len(prop_lines)


def _count_components(content: str) -> int:
    """Count PascalCase function/const components, excluding test helpers."""
    clean = _strip_strings_and_comments(content)
    matches = re.findall(
        r'(?:^|export\s+)(?:default\s+)?(?:const|function)\s+([A-Z][a-zA-Z0-9]*)\s*'
        r'(?:=\s*(?:React\.memo\s*\(|React\.forwardRef\s*\(|\([^)]*\)\s*(?::\s*\w[^=]*)?\s*=>|\([^)]*\)\s*\{)|'
        r'\([^)]*\)\s*(?::\s*\w[^{]*)?\s*\{)',
        clean, re.MULTILINE
    )
    excluded = {'describe', 'it', 'test', 'expect', 'beforeEach', 'afterEach'}
    return len([m for m in matches if m not in excluded])


def _count_missing_return_types(content: str) -> int:
    """Count arrow-function components missing a JSX return type."""
    clean = _strip_strings_and_comments(content)
    with_type = len(re.findall(
        r'(?:const|function)\s+[A-Z][a-zA-Z0-9]*\s*=\s*\([^)]*\)\s*:\s*'
        r'(?:JSX\.Element|React\.FC|React\.ReactElement|ReactElement|ReactNode)',
        clean
    ))
    without_type = len(re.findall(
        r'(?:const|function)\s+[A-Z][a-zA-Z0-9]*\s*=\s*\([^)]*\)\s*=>',
        clean
    ))
    return max(0, without_type - with_type)


def analyse_file(filepath: str, content: str) -> ComponentDebt:
    filename = filepath.split("/")[-1]
    debt = ComponentDebt(filename=filename, filepath=filepath)

    lines = content.splitlines()
    debt.loc = len([
        l for l in lines
        if l.strip() and not l.strip().startswith('//')
    ])

    clean = _strip_strings_and_comments(content)

    debt.props_count = _count_props(content)
    debt.any_count = len(re.findall(r':\s*any\b', clean))
    debt.todo_count = len(re.findall(
        r'//\s*(TODO|FIXME|HACK|XXX)\b', content, re.IGNORECASE
    ))
    debt.component_count = _count_components(content)
    debt.nested_ternary_count = len(re.findall(r'\?[^:?\n]{1,80}\?', clean))
    debt.console_log_count = len(re.findall(
        r'\bconsole\.(log|warn|error|debug|info)\s*\(', clean
    ))
    debt.missing_return_type_count = _count_missing_return_types(content)

    # ── Score calculation ────────────────────────────────────────────
    score = 0.0

    if debt.loc > 300:
        score += 25
        debt.issues.append(f"Very large component ({debt.loc} lines). Consider splitting.")
    elif debt.loc > 200:
        score += 15
        debt.issues.append(f"Large component ({debt.loc} lines). Consider splitting.")
    elif debt.loc > 100:
        score += 5

    if debt.props_count > 10:
        score += 20
        debt.issues.append(f"Too many props ({debt.props_count}). Use composition or context.")
    elif debt.props_count > 6:
        score += 10
        debt.issues.append(f"High prop count ({debt.props_count}). Review responsibilities.")

    if debt.any_count > 5:
        score += 20
        debt.issues.append(f"Heavy 'any' usage ({debt.any_count}\u00d7). Add proper TypeScript types.")
    elif debt.any_count > 2:
        score += 12
        debt.issues.append(f"Multiple 'any' usages ({debt.any_count}\u00d7). Improve type safety.")
    elif debt.any_count > 0:
        score += 5
        debt.issues.append(f"'any' used {debt.any_count}\u00d7. Consider stronger typing.")

    if debt.todo_count > 3:
        score += 10
        debt.issues.append(f"{debt.todo_count} unresolved TODO/FIXME comments.")
    elif debt.todo_count > 0:
        score += debt.todo_count * 3
        debt.issues.append(f"{debt.todo_count} TODO/FIXME comment(s) found.")

    if debt.component_count > 3:
        score += 10
        debt.issues.append(f"{debt.component_count} components in one file. One component per file recommended.")
    elif debt.component_count > 2:
        score += 5
        debt.issues.append(f"{debt.component_count} components in one file.")

    if debt.nested_ternary_count > 2:
        score += 8
        debt.issues.append(f"{debt.nested_ternary_count} nested ternaries. Extract to variables.")
    elif debt.nested_ternary_count > 0:
        score += debt.nested_ternary_count * 2

    if debt.console_log_count > 0:
        score += min(debt.console_log_count * 2, 5)
        debt.issues.append(f"{debt.console_log_count} console.log(s). Remove before production.")

    if debt.missing_return_type_count > 2:
        score += 5
        debt.issues.append(f"{debt.missing_return_type_count} components missing return type annotations.")
    elif debt.missing_return_type_count > 0:
        score += 2
        debt.issues.append(f"{debt.missing_return_type_count} component(s) missing return type annotations.")

    debt.debt_score = round(min(score, 100), 1)
    debt.debt_level = (
        "high"   if debt.debt_score >= 60 else
        "medium" if debt.debt_score >= 30 else
        "low"
    )
    return debt


def analyse_repository(files: list[dict]) -> list[ComponentDebt]:
    """
    files: list of { "path": str, "content": str }
    Returns list of ComponentDebt sorted by debt_score descending.
    """
    SKIP = {
        ".test.", ".spec.", ".d.ts",
        "vite.config", "tailwind.config", "jest.config",
        "next.config", "webpack.config", "__mocks__",
        ".stories.", "stories.",
    }
    results = []
    for f in files:
        path = f["path"]
        if not (path.endswith(".tsx") or path.endswith(".ts")):
            continue
        if any(p in path for p in SKIP):
            continue
        results.append(analyse_file(path, f["content"]))

    return sorted(results, key=lambda x: x.debt_score, reverse=True)
