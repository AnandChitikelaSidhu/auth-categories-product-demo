import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { productFormSchema, type ProductFormValues } from "@/features/products/schemas/product-schemas";
import type { Product } from "@/features/products/types/product.types";
import { useCategoryOptions } from "@/features/categories/hooks/useCategories";
import { Button } from "@/shared/components/ui/button";
import { Input, Textarea } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Switch } from "@/shared/components/ui/switch";

interface ProductFormProps {
  defaultValues?: Partial<Product>;
  onSubmit: (values: ProductFormValues) => void;
  loading?: boolean;
  submitLabel?: string;
}

export function ProductForm({ defaultValues, onSubmit, loading, submitLabel = "Save" }: ProductFormProps) {
  const { data: categoriesData } = useCategoryOptions();
  const form = useForm<ProductFormValues>({
    resolver: zodResolver(productFormSchema),
    defaultValues: {
      name: defaultValues?.name ?? "",
      description: defaultValues?.description ?? "",
      price: defaultValues ? Number(defaultValues.price) : 0,
      stock_quantity: defaultValues?.stock_quantity ?? 0,
      category_id: defaultValues?.category_id ?? "",
      is_active: defaultValues?.is_active ?? true,
    },
  });

  useEffect(() => {
    if (defaultValues) {
      form.reset({
        name: defaultValues.name,
        description: defaultValues.description ?? "",
        price: Number(defaultValues.price),
        stock_quantity: defaultValues.stock_quantity,
        category_id: defaultValues.category_id,
        is_active: defaultValues.is_active,
      });
    }
  }, [defaultValues, form]);

  return (
    <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
      <div className="space-y-2">
        <Label htmlFor="name">Name</Label>
        <Input id="name" {...form.register("name")} />
      </div>
      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea id="description" {...form.register("description")} />
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="price">Price</Label>
          <Input id="price" type="number" step="0.01" {...form.register("price", { valueAsNumber: true })} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="stock_quantity">Stock</Label>
          <Input id="stock_quantity" type="number" {...form.register("stock_quantity", { valueAsNumber: true })} />
        </div>
      </div>
      <div className="space-y-2">
        <Label>Category</Label>
        <Select value={form.watch("category_id")} onValueChange={(value) => form.setValue("category_id", value)}>
          <SelectTrigger><SelectValue placeholder="Select category" /></SelectTrigger>
          <SelectContent>
            {categoriesData?.items.map((category) => (
              <SelectItem key={category.id} value={category.id}>{category.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex items-center justify-between rounded-lg border p-3">
        <Label htmlFor="is_active">Active</Label>
        <Switch id="is_active" checked={form.watch("is_active")} onCheckedChange={(checked) => form.setValue("is_active", checked)} />
      </div>
      <Button type="submit" disabled={loading}>{loading ? "Saving..." : submitLabel}</Button>
    </form>
  );
}
