export interface FileDetails {
  filename?: string;
  files_accessed_count?: number;
  download_size_mb?: number;
  upload_size_mb?: number;
}

export interface ActivityLog {
  activity_id: string;
  user_id: string;
  timestamp: string;
  event_type: 'LOGIN' | 'LOGOUT' | 'FILE_ACCESS' | 'FILE_DOWNLOAD' | 'FILE_UPLOAD' | 'APP_USAGE';
  location_ip: string;
  location_name: string;
  device_id: string;
  app_used: string;
  file_details: FileDetails;
  after_hours: boolean;
  failed_logins: number;
  is_demo_synthetic?: boolean;
}

export interface ActivityListResponse {
  activities: ActivityLog[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}
