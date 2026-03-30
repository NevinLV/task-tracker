export type TaskStatus =
  | 'familiarization'
  | 'development'
  | 'testing'
  | 'deployment'
  | 'done'

export interface TimeEntry {
  id: string
  started_at: string
  ended_at: string | null
  duration_seconds: number | null
}

export interface Task {
  id: string
  title: string
  content_json: string | null
  status: TaskStatus
  created_at: string
  updated_at: string
  total_tracked_seconds: number
  active_timer_entry_id: string | null
  time_entries: TimeEntry[]
}

export interface UserProfile {
  id: string
  email: string
  first_name: string | null
  last_name: string | null
  hourly_rate: string
  avatar_url: string | null
}

export interface CommentAuthor {
  id: string
  first_name: string | null
  last_name: string | null
  avatar_url: string | null
  display_name: string
}

export interface TaskComment {
  id: string
  user_id: string
  body: string
  created_at: string
  author: CommentAuthor
}

export interface TimeMoneySummary {
  total_seconds: number
  hourly_rate: string
  total_amount: string
}
