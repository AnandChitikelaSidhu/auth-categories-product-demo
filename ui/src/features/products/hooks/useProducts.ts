import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { productsApi } from "@/features/products/api/products-api";
import type { ProductListParams } from "@/features/products/types/product.types";
import type { ProductFormValues, StockDeltaFormValues } from "@/features/products/schemas/product-schemas";
import { getErrorMessage } from "@/shared/lib/utils";

export function useProducts(params: ProductListParams) {
  return useQuery({
    queryKey: ["products", params],
    queryFn: () => productsApi.list(params).then((res) => res.data),
  });
}

export function useProduct(identifier: string | undefined) {
  return useQuery({
    queryKey: ["product", identifier],
    queryFn: () => productsApi.getById(identifier!).then((res) => res.data),
    enabled: Boolean(identifier),
  });
}

export function useCreateProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ProductFormValues) => productsApi.create(payload).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      toast.success("Product created");
    },
    onError: (error) => toast.error(getErrorMessage(error, "Create failed")),
  });
}

export function useUpdateProduct(identifier: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ProductFormValues) => productsApi.update(identifier, payload).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      queryClient.invalidateQueries({ queryKey: ["product", identifier] });
      toast.success("Product updated");
    },
    onError: (error) => toast.error(getErrorMessage(error, "Update failed")),
  });
}

export function useUpdateStock(identifier: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: StockDeltaFormValues) =>
      productsApi.updateStock(identifier, payload).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      queryClient.invalidateQueries({ queryKey: ["product", identifier] });
      toast.success("Stock updated");
    },
    onError: (error) => toast.error(getErrorMessage(error, "Stock update failed")),
  });
}

export function useDeleteProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (identifier: string) => productsApi.remove(identifier).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      toast.success("Product deleted");
    },
    onError: (error) => toast.error(getErrorMessage(error, "Delete failed")),
  });
}
