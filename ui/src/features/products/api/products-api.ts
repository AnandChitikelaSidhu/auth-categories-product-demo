import type { PaginatedProductList } from "@/shared/types/api.types";
import { CACHE_HEADER } from "@/shared/types/api.types";
import { productClient } from "@/shared/lib/api-client";
import type {
  Product,
  ProductCreateInput,
  ProductListParams,
  ProductUpdateInput,
  ProductWithCache,
  StockDeltaInput,
} from "@/features/products/types/product.types";

export const productsApi = {
  list: (params: ProductListParams = {}) =>
    productClient.get<PaginatedProductList>("/products", { params }),

  getById: async (identifier: string): Promise<{ data: ProductWithCache; cacheStatus: "HIT" | "MISS" | null }> => {
    const response = await productClient.get<Product>(`/products/${identifier}`);
    const cacheHeader = response.headers[CACHE_HEADER] ?? response.headers["X-Cache"];
    const cacheStatus = cacheHeader === "HIT" || cacheHeader === "MISS" ? cacheHeader : null;
    return { data: { ...response.data, cacheStatus }, cacheStatus };
  },

  create: (payload: ProductCreateInput) => productClient.post<Product>("/products", payload),

  update: (identifier: string, payload: ProductUpdateInput) =>
    productClient.put<Product>(`/products/${identifier}`, payload),

  updateStock: (identifier: string, payload: StockDeltaInput) =>
    productClient.patch<Product>(`/products/${identifier}/stock`, payload),

  remove: (identifier: string) => productClient.delete<Product>(`/products/${identifier}`),
};
