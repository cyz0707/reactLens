"""
Unit tests for the ReactLens static analysis engine.
Run: pytest tests/test_analyser.py -v
"""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.analyser import analyse_file, analyse_repository


# ── Fixtures ──────────────────────────────────────────────────────────

CLEAN_COMPONENT = """
import React from 'react';

interface ButtonProps {
  label: string;
  onClick: () => void;
}

const Button = ({ label, onClick }: ButtonProps): JSX.Element => {
  return <button onClick={onClick}>{label}</button>;
};

export default Button;
"""

HIGH_DEBT_COMPONENT = """
import React from 'react';

interface DashboardProps {
  userId: string;
  data: any;
  loading: boolean;
  error: any;
  onSubmit: (val: any) => void;
  onCancel: () => void;
  theme: string;
  locale: string;
  permissions: any;
  config: any;
  extra: string;
}

const Dashboard = (props: DashboardProps) => {
  // TODO: refactor this mess
  // FIXME: handle loading state properly
  // TODO: add error boundary
  console.log('render', props.data);
  console.log('user', props.userId);
  const result = props.loading ? <div>Loading</div>
    : props.error ? <div>Error</div>
    : props.data ? <div>{props.data.name}</div>
    : <div>Empty</div>;
  return result;
};

const Helper = () => <span>helper</span>;
const AnotherHelper = () => <span>another</span>;
const YetAnother = () => <span>yet</span>;

export default Dashboard;
""" * 5  # Repeat to push LOC over 200

COMPONENT_WITH_ANY = """
const process = (data: any): any => {
  const result: any = data.value;
  const extra: any = null;
  return result;
};
"""

COMPONENT_WITH_TODOS = """
// TODO: fix this
// FIXME: handle edge case
// TODO: add tests
// HACK: workaround for issue #123
const Component = () => <div />;
"""

COMPONENT_WITH_CONSOLE = """
const Component = () => {
  console.log('debug');
  console.warn('warning');
  console.error('error');
  return <div />;
};
"""

COMPONENT_NO_FALSE_POSITIVE = """
// This is a comment about console.log usage
const message = "Use console.log for debugging";
const template = `console.log is useful`;
const Component = (): JSX.Element => <div />;
"""

TEST_FILE = """
import { render } from '@testing-library/react';
describe('Button', () => {
  it('renders', () => {
    // TODO: add more tests
    console.log('test');
  });
});
"""


# ── LOC ───────────────────────────────────────────────────────────────

class TestLOC:
    def test_clean_component_low_loc(self):
        result = analyse_file("Button.tsx", CLEAN_COMPONENT)
        assert result.loc < 20

    def test_high_debt_component_high_score(self):
        result = analyse_file("Dashboard.tsx", HIGH_DEBT_COMPONENT)
        assert result.debt_score >= 60

    def test_blank_lines_excluded(self):
        result = analyse_file("x.ts", "\n\n\nconst x = 1;\n\n\n")
        assert result.loc == 1

    def test_comment_lines_excluded_from_loc(self):
        result = analyse_file("x.ts", "// comment\n// another\nconst x = 1;")
        assert result.loc == 1


# ── Props ─────────────────────────────────────────────────────────────

class TestProps:
    def test_counts_props_correctly(self):
        result = analyse_file("Dashboard.tsx", HIGH_DEBT_COMPONENT)
        assert result.props_count == 11

    def test_clean_component_few_props(self):
        result = analyse_file("Button.tsx", CLEAN_COMPONENT)
        assert result.props_count == 2

    def test_no_props_interface(self):
        result = analyse_file("Component.tsx", "const Component = () => <div />;")
        assert result.props_count == 0

    def test_optional_props_counted(self):
        code = """
interface CardProps {
  title: string;
  subtitle?: string;
  onClick?: () => void;
}
const Card = (props: CardProps) => <div />;
"""
        result = analyse_file("Card.tsx", code)
        assert result.props_count == 3


# ── Any type ──────────────────────────────────────────────────────────

class TestAnyType:
    def test_detects_any_usage(self):
        result = analyse_file("process.ts", COMPONENT_WITH_ANY)
        assert result.any_count == 4

    def test_no_any_in_clean_component(self):
        result = analyse_file("Button.tsx", CLEAN_COMPONENT)
        assert result.any_count == 0

    def test_any_in_string_not_counted(self):
        code = 'const msg = "this is any type";\nconst C = (): JSX.Element => <div />;'
        result = analyse_file("Component.tsx", code)
        assert result.any_count == 0

    def test_any_in_comment_not_counted(self):
        code = '// avoid using any type\nconst C = (): JSX.Element => <div />;'
        result = analyse_file("Component.tsx", code)
        assert result.any_count == 0


# ── TODOs ─────────────────────────────────────────────────────────────

class TestTodos:
    def test_counts_all_todo_variants(self):
        result = analyse_file("Component.tsx", COMPONENT_WITH_TODOS)
        assert result.todo_count == 4

    def test_no_todos_in_clean_component(self):
        result = analyse_file("Button.tsx", CLEAN_COMPONENT)
        assert result.todo_count == 0

    def test_case_insensitive(self):
        code = "// todo: fix\n// Todo: fix\nconst x = 1;"
        result = analyse_file("x.ts", code)
        assert result.todo_count == 2


# ── Console logs ──────────────────────────────────────────────────────

class TestConsoleLogs:
    def test_counts_console_calls(self):
        result = analyse_file("Component.tsx", COMPONENT_WITH_CONSOLE)
        assert result.console_log_count == 3

    def test_no_false_positive_in_strings(self):
        result = analyse_file("Component.tsx", COMPONENT_NO_FALSE_POSITIVE)
        assert result.console_log_count == 0

    def test_no_console_in_clean_component(self):
        result = analyse_file("Button.tsx", CLEAN_COMPONENT)
        assert result.console_log_count == 0


# ── Component count ───────────────────────────────────────────────────

class TestComponentCount:
    def test_single_component(self):
        result = analyse_file("Button.tsx", CLEAN_COMPONENT)
        assert result.component_count == 1

    def test_multiple_components(self):
        result = analyse_file("Dashboard.tsx", HIGH_DEBT_COMPONENT)
        assert result.component_count >= 4

    def test_no_component_in_utility(self):
        code = """
export const formatDate = (d: Date): string => d.toISOString();
export const formatCurrency = (n: number): string => `$${n}`;
"""
        result = analyse_file("utils.ts", code)
        assert result.component_count == 0


# ── Missing return types ──────────────────────────────────────────────

class TestMissingReturnTypes:
    def test_detects_missing_return_type(self):
        result = analyse_file("Comp.tsx", "const MyComponent = () => <div />;")
        assert result.missing_return_type_count >= 1

    def test_no_flag_when_return_type_present(self):
        result = analyse_file("Button.tsx", CLEAN_COMPONENT)
        assert result.missing_return_type_count == 0


# ── Debt score & level ────────────────────────────────────────────────

class TestDebtScore:
    def test_clean_component_low_score(self):
        result = analyse_file("Button.tsx", CLEAN_COMPONENT)
        assert result.debt_score < 30
        assert result.debt_level == "low"

    def test_high_debt_component_high_score(self):
        result = analyse_file("Dashboard.tsx", HIGH_DEBT_COMPONENT)
        assert result.debt_score >= 60
        assert result.debt_level == "high"

    def test_score_capped_at_100(self):
        result = analyse_file("Dashboard.tsx", HIGH_DEBT_COMPONENT)
        assert result.debt_score <= 100

    def test_score_never_negative(self):
        result = analyse_file("empty.tsx", "")
        assert result.debt_score >= 0

    def test_medium_level_range(self):
        code = """
interface Props {
  a: string;
  b: string;
  c: string;
  d: string;
  e: string;
  f: string;
  g: string;
  h: string;
  i: string;
  j: string;
  k: string;
}
const Component = (props: Props) => {
  console.log(props);
  // TODO: fix this
  // TODO: fix that
  // TODO: fix more
  // TODO: fix again
  return <div />;
};
"""
        result = analyse_file("Component.tsx", code)
        assert result.debt_level in ("medium", "high")

    def test_issues_populated_for_high_debt(self):
        result = analyse_file("Dashboard.tsx", HIGH_DEBT_COMPONENT)
        assert len(result.issues) > 0

    def test_no_issues_for_clean_component(self):
        result = analyse_file("Button.tsx", CLEAN_COMPONENT)
        assert result.debt_score < 10


# ── analyse_repository ────────────────────────────────────────────────

class TestAnalyseRepository:
    def test_skips_test_files(self):
        files = [
            {"path": "src/Button.test.tsx", "content": TEST_FILE},
            {"path": "src/Button.spec.tsx", "content": TEST_FILE},
            {"path": "src/Button.tsx",      "content": CLEAN_COMPONENT},
        ]
        results = analyse_repository(files)
        paths = [r.filepath for r in results]
        assert "src/Button.test.tsx" not in paths
        assert "src/Button.spec.tsx" not in paths
        assert "src/Button.tsx" in paths

    def test_skips_declaration_files(self):
        files = [
            {"path": "src/types.d.ts", "content": "declare module 'x' {}"},
            {"path": "src/utils.ts",   "content": "export const x = 1;"},
        ]
        results = analyse_repository(files)
        assert all(r.filepath != "src/types.d.ts" for r in results)

    def test_skips_non_ts_files(self):
        files = [
            {"path": "src/Button.tsx", "content": CLEAN_COMPONENT},
            {"path": "src/styles.css", "content": ".btn { color: red; }"},
            {"path": "README.md",      "content": "# readme"},
        ]
        results = analyse_repository(files)
        assert len(results) == 1

    def test_sorted_descending(self):
        files = [
            {"path": "src/Clean.tsx",     "content": CLEAN_COMPONENT},
            {"path": "src/Dashboard.tsx", "content": HIGH_DEBT_COMPONENT},
        ]
        results = analyse_repository(files)
        assert results[0].debt_score >= results[-1].debt_score

    def test_empty_repository(self):
        assert analyse_repository([]) == []

    def test_skips_config_files(self):
        files = [
            {"path": "vite.config.ts",     "content": "export default {}"},
            {"path": "tailwind.config.ts", "content": "export default {}"},
            {"path": "src/App.tsx",        "content": CLEAN_COMPONENT},
        ]
        results = analyse_repository(files)
        assert len(results) == 1
        assert results[0].filepath == "src/App.tsx"

    def test_skips_stories_files(self):
        files = [
            {"path": "src/Button.stories.tsx", "content": CLEAN_COMPONENT},
            {"path": "src/Button.tsx",          "content": CLEAN_COMPONENT},
        ]
        results = analyse_repository(files)
        assert len(results) == 1
        assert results[0].filepath == "src/Button.tsx"


# ── Edge cases ────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_empty_file(self):
        result = analyse_file("empty.tsx", "")
        assert result.debt_score == 0.0
        assert result.debt_level == "low"

    def test_file_with_only_comments(self):
        result = analyse_file("comments.tsx", "// comment\n// another\n")
        assert result.loc == 0

    def test_filename_extracted_correctly(self):
        result = analyse_file("src/components/Button/index.tsx", CLEAN_COMPONENT)
        assert result.filename == "index.tsx"
        assert result.filepath == "src/components/Button/index.tsx"

    def test_all_fields_present(self):
        result = analyse_file("Button.tsx", CLEAN_COMPONENT)
        assert hasattr(result, "loc")
        assert hasattr(result, "props_count")
        assert hasattr(result, "any_count")
        assert hasattr(result, "todo_count")
        assert hasattr(result, "component_count")
        assert hasattr(result, "nested_ternary_count")
        assert hasattr(result, "console_log_count")
        assert hasattr(result, "missing_return_type_count")
        assert hasattr(result, "debt_score")
        assert hasattr(result, "debt_level")
        assert hasattr(result, "issues")
