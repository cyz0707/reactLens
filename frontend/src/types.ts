export interface ComponentDebt {
  filename: string
  filepath: string
  loc: number
  props_count: number
  any_count: number
  todo_count: number
  component_count: number
  nested_ternary_count: number
  console_log_count: number
  missing_return_type_count: number
  debt_score: number
  debt_level: 'high' | 'medium' | 'low'
  issues: string[]
}

export interface AnalyseResponse {
  repo_name: string
  total_files: number
  high_debt_count: number
  medium_debt_count: number
  low_debt_count: number
  components: ComponentDebt[]
  ai_summary: string | null
  ai_top_issues: string[] | null
  ai_remediation_plan: string[] | null
  ai_overall_score: number | null
  ai_score_label: string | null
}
