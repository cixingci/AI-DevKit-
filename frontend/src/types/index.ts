export interface Project {
  id: number
  name: string
  description: string
  card_count: number
  created_at: string
  updated_at: string
}

export interface Card {
  id: number
  title: string
  content: Record<string, any>
  card_type: {
    id: number
    name: string
    json_schema: Record<string, any> | null
  } | null
  parent_id: number | null
  display_order: number
  ai_params: Record<string, any> | null
  ai_generated: boolean
  needs_review: boolean
  created_at: string
  updated_at: string
}

export interface CardType {
  id: number
  name: string
  model_name: string | null
  description: string | null
  json_schema: Record<string, any> | null
  ai_params: Record<string, any> | null
  is_ai_enabled: boolean
  is_singleton: boolean
  built_in: boolean
  default_ai_context_template: string | null
}

export interface Workflow {
  id: number
  name: string
  description: string | null
  status: string
  progress: number
  created_at: string
  started_at: string | null
  finished_at: string | null
}

export interface LLMConfig {
  id: number
  provider: string
  display_name: string | null
  model_name: string
  api_base: string | null
  api_key: string
  token_limit: number
  call_limit: number
  used_tokens_input: number
  used_tokens_output: number
  used_calls: number
}