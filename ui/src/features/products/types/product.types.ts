export interface CategoryBrief {
  id: string;
  name: string;
  slug: string;
}

export interface Product {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  price: string;
  stock_quantity: number;
  category_id: string;
  category: CategoryBrief | null;
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface ProductListParams {
  page?: number;
  page_size?: number;
  category_id?: string;
  min_price?: number;
  max_price?: number;
  include_inactive?: boolean;
  search?: string;
}

export interface ProductCreateInput {
  name: string;
  description?: string | null;
  price: number;
  stock_quantity: number;
  category_id: string;
  is_active: boolean;
}

export interface ProductUpdateInput extends ProductCreateInput {}

export interface StockDeltaInput {
  delta: number;
}

export interface ProductWithCache extends Product {
  cacheStatus?: "HIT" | "MISS" | null;
}
