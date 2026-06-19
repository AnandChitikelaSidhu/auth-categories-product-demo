import { useCategories } from "@/features/categories/hooks/useCategories";
import { usePagination } from "@/shared/hooks/usePagination";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/badge";
import { Pagination } from "@/shared/components/ui/pagination";
import { EmptyState } from "@/shared/components/EmptyState";

export function CategoryListPage() {
  const { page, pageSize, setPage, setPageSize } = usePagination();
  const { data, isLoading, isError } = useCategories(page, pageSize);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Categories</h1>
        <p className="text-muted-foreground">Browse product categories</p>
      </div>

      {isLoading ? <Skeleton className="h-64 w-full" /> : null}
      {isError ? <p className="text-destructive">Failed to load categories.</p> : null}

      {!isLoading && data?.items.length === 0 ? (
        <EmptyState title="No categories yet" description="Categories will appear here once created by an admin." />
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {data?.items.map((category) => (
          <Card key={category.id}>
            <CardHeader>
              <CardTitle>{category.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Slug: {category.slug}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {data ? (
        <Pagination
          page={data.page}
          pages={data.pages}
          pageSize={data.page_size}
          totalCount={data.total_count}
          onPageChange={setPage}
          onPageSizeChange={setPageSize}
        />
      ) : null}
    </div>
  );
}
