import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { categoriesApi } from "@/features/categories/api/categories-api";
import type { CategoryFormValues } from "@/features/categories/schemas/category-schemas";
import { DEFAULT_PAGE_SIZE } from "@/shared/constants/pagination";
import { getErrorMessage } from "@/shared/lib/utils";

export function useCategories(page = 1, pageSize = DEFAULT_PAGE_SIZE) {
  return useQuery({
    queryKey: ["categories", page, pageSize],
    queryFn: () => categoriesApi.list(page, pageSize).then((res) => res.data),
  });
}

/** Load all categories for filter dropdowns (up to 100). */
export function useCategoryOptions() {
  return useCategories(1, 100);
}

export function useCreateCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CategoryFormValues) => categoriesApi.create(payload).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      toast.success("Category created");
    },
    onError: (error) => toast.error(getErrorMessage(error, "Create failed")),
  });
}
