export interface Link {
  id: number;
  url: string;
  title?: string;
  description?: string;
  tags?: string[];
  source?: string;
  created_at: string;
  resource_type: "article" | "resource";
}
