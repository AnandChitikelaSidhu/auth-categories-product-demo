import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { categorySchema, type CategoryFormValues } from "@/features/categories/schemas/category-schemas";
import { useCategories, useCreateCategory } from "@/features/categories/hooks/useCategories";
import { usePagination } from "@/shared/hooks/usePagination";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { Pagination } from "@/shared/components/ui/pagination";
import { Skeleton } from "@/shared/components/ui/badge";

export function AdminCategoriesPage() {
  const { page, pageSize, setPage, setPageSize } = usePagination();
  const { data, isLoading } = useCategories(page, pageSize);
  const createCategory = useCreateCategory();
  const form = useForm<CategoryFormValues>({
    resolver: zodResolver(categorySchema),
    defaultValues: { name: "" },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Manage Categories</h1>
        <p className="text-muted-foreground">Create new product categories</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Create category</CardTitle></CardHeader>
        <CardContent>
          <form
            className="flex flex-col gap-4 sm:flex-row"
            onSubmit={form.handleSubmit((values) =>
              createCategory.mutate(values, { onSuccess: () => form.reset() }),
            )}
          >
            <div className="flex-1 space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input id="name" {...form.register("name")} />
            </div>
            <Button className="self-end" type="submit" disabled={createCategory.isPending}>
              {createCategory.isPending ? "Creating..." : "Create"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Existing categories</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? <Skeleton className="h-48 w-full" /> : null}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Slug</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.items.map((category) => (
                <TableRow key={category.id}>
                  <TableCell>{category.name}</TableCell>
                  <TableCell>{category.slug}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {data ? (
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
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
