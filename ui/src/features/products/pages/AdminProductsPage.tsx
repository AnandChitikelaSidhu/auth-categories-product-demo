import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Pencil, Plus, Trash2 } from "lucide-react";
import {
  useCreateProduct,
  useDeleteProduct,
  useProducts,
  useUpdateProduct,
  useUpdateStock,
} from "@/features/products/hooks/useProducts";
import { ProductForm } from "@/features/products/components/ProductForm";
import { stockDeltaSchema, type StockDeltaFormValues } from "@/features/products/schemas/product-schemas";
import type { Product } from "@/features/products/types/product.types";
import { usePagination } from "@/shared/hooks/usePagination";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/shared/components/ui/dialog";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { Badge } from "@/shared/components/ui/badge";
import { Skeleton } from "@/shared/components/ui/badge";
import { Pagination } from "@/shared/components/ui/pagination";
import { ConfirmDialog } from "@/shared/components/ConfirmDialog";
import { EmptyState } from "@/shared/components/EmptyState";
import { formatCurrency } from "@/shared/lib/utils";

export function AdminProductsPage() {
  const { page, pageSize, setPage, setPageSize } = usePagination();
  const [createOpen, setCreateOpen] = useState(false);
  const [editProduct, setEditProduct] = useState<Product | null>(null);
  const [stockProduct, setStockProduct] = useState<Product | null>(null);
  const [deleteProduct, setDeleteProduct] = useState<Product | null>(null);

  const { data, isLoading } = useProducts({ page, page_size: pageSize, include_inactive: true });
  const createProduct = useCreateProduct();
  const updateProduct = useUpdateProduct(editProduct?.slug ?? "");
  const updateStock = useUpdateStock(stockProduct?.slug ?? "");
  const deleteMutation = useDeleteProduct();

  const stockForm = useForm<StockDeltaFormValues>({
    resolver: zodResolver(stockDeltaSchema),
    defaultValues: { delta: 1 },
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Manage Products</h1>
          <p className="text-muted-foreground">Create, edit, update stock, and soft delete products</p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4" />
          New product
        </Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Product table</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? <Skeleton className="h-64 w-full" /> : null}
          {!isLoading && data?.items.length === 0 ? (
            <EmptyState title="No products yet" description="Create your first product to get started." action={<Button onClick={() => setCreateOpen(true)}>Create product</Button>} />
          ) : null}
          {!isLoading && data && data.items.length > 0 ? (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Price</TableHead>
                    <TableHead>Stock</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.items.map((product) => (
                    <TableRow key={product.id}>
                      <TableCell className="font-medium">{product.name}</TableCell>
                      <TableCell>{formatCurrency(product.price)}</TableCell>
                      <TableCell>{product.stock_quantity}</TableCell>
                      <TableCell>
                        <Badge variant={product.is_active ? "success" : "secondary"}>
                          {product.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="outline" size="sm" onClick={() => setEditProduct(product)}>
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button variant="outline" size="sm" onClick={() => setStockProduct(product)}>
                            Stock
                          </Button>
                          <Button variant="destructive" size="sm" onClick={() => setDeleteProduct(product)}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <div className="mt-4">
                <Pagination
                  page={data.page}
                  pages={data.pages}
                  pageSize={data.page_size}
                  totalCount={data.total_count}
                  onPageChange={setPage}
                  onPageSizeChange={setPageSize}
                />
              </div>
            </>
          ) : null}
        </CardContent>
      </Card>

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Create product</DialogTitle></DialogHeader>
          <ProductForm
            loading={createProduct.isPending}
            submitLabel="Create"
            onSubmit={(values) =>
              createProduct.mutate(values, { onSuccess: () => setCreateOpen(false) })
            }
          />
        </DialogContent>
      </Dialog>

      <Dialog open={Boolean(editProduct)} onOpenChange={(open) => !open && setEditProduct(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>Edit product</DialogTitle></DialogHeader>
          {editProduct ? (
            <ProductForm
              defaultValues={editProduct}
              loading={updateProduct.isPending}
              onSubmit={(values) =>
                updateProduct.mutate(values, { onSuccess: () => setEditProduct(null) })
              }
            />
          ) : null}
        </DialogContent>
      </Dialog>

      <Dialog open={Boolean(stockProduct)} onOpenChange={(open) => !open && setStockProduct(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>Update stock</DialogTitle></DialogHeader>
          {stockProduct ? (
            <form
              className="space-y-4"
              onSubmit={stockForm.handleSubmit((values) =>
                updateStock.mutate(values, { onSuccess: () => setStockProduct(null) }),
              )}
            >
              <p className="text-sm text-muted-foreground">
                Current stock for <strong>{stockProduct.name}</strong>: {stockProduct.stock_quantity}
              </p>
              <div className="space-y-2">
                <Label htmlFor="delta">Delta (+ restock, - sell)</Label>
                <Input id="delta" type="number" {...stockForm.register("delta", { valueAsNumber: true })} />
              </div>
              <Button type="submit" disabled={updateStock.isPending}>Apply delta</Button>
            </form>
          ) : null}
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={Boolean(deleteProduct)}
        onOpenChange={(open) => !open && setDeleteProduct(null)}
        title="Delete product?"
        description="This performs a soft delete and marks the product as inactive."
        confirmLabel="Delete"
        loading={deleteMutation.isPending}
        onConfirm={() => {
          if (deleteProduct) {
            deleteMutation.mutate(deleteProduct.slug, { onSuccess: () => setDeleteProduct(null) });
          }
        }}
      />
    </div>
  );
}
