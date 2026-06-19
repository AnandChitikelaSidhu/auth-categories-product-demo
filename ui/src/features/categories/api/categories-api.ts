import type { PaginatedCategoryList } from "@/shared/types/api.types";
import { productClient } from "@/shared/lib/api-client";
import type { Category, CategoryCreateInput } from "@/features/categories/types/category.types";
import { DEFAULT_PAGE_SIZE } from "@/shared/constants/pagination";

export const categoriesApi = {
  list: (page = 1, page_size = DEFAULT_PAGE_SIZE) =>
    productClient.get<PaginatedCategoryList>("/categories", { params: { page, page_size } }),

  create: (payload: CategoryCreateInput) => productClient.post<Category>("/categories", payload),
};
