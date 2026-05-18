export interface User {
  id: number
  username: string
  full_name: string
  email: string
  role: string
  status: number
  created_at?: string
}

export interface Project {
  id: number
  name: string
  description: string
  owner_id: number
  created_at?: string
  updated_at?: string
}

export interface SysModel {
  id: number
  project_id: number
  name: string
  version_tag: string
  file_path: string
  file_size: number
  file_type: string
  uploader_id: number
  upload_time?: string
  parse_status: string
  parse_message?: string
  created_at?: string
  updated_at?: string
}

export interface ModelElement {
  id: number
  model_id: number
  element_id: string
  element_name: string
  element_type: string
  parent_element_id: string
  description: string
}

export interface ElementTreeItem {
  id: number
  element_id: string
  element_name: string
  element_type: string
  parent_element_id: string
  children: ElementTreeItem[]
}

export interface Template {
  id: number
  name: string
  template_type: string
  content: string
  status: string
  creator_id: number
  created_at?: string
}

export interface Document {
  id: number
  project_id: number
  model_id: number
  template_id: number
  document_name: string
  content: string
  file_path?: string
  export_format?: string
  status: string
  generate_message?: string
  operator_id: number
  generate_time?: string
  created_at?: string
}

export interface DocumentListResponse {
  items: Document[]
  total: number
  page: number
  page_size: number
}

export interface LogOut {
  id: number
  log_type: string
  operator_id: number | null
  module_name: string
  operation_content: string
  result_status: string
  ip_address: string
  record_time?: string
}
