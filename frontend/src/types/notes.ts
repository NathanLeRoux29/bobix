export interface Note {
  id: number;
  title: string;
  content: string;
  folder_id: number | null;
  is_favorite: boolean;
  created_at: string;
  updated_at: string;
}

export interface Folder {
  id: number;
  name: string;
  parent_id: number | null;
  created_at: string;
}
