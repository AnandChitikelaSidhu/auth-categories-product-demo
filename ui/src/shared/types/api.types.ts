export type UserRole = "customer" | "admin" | "super_admin";

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  last_name: string | null;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface PaginatedProductList {
  items: import("@/features/products/types/product.types").Product[];
  total_count: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface PaginatedCategoryList {
  items: import("@/features/categories/types/category.types").Category[];
  total_count: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface MessageResponse {
  message: string;
}

export const CACHE_HEADER = "x-cache";
