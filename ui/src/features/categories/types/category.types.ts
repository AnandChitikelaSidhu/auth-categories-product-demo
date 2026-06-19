export interface Category {
  id: string;
  name: string;
  slug: string;
  created_at: string;
}

export interface CategoryCreateInput {
  name: string;
}
