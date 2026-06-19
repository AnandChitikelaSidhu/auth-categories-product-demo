import { useMemo, useState } from "react";
import { Link } from "react-router";
import { Search } from "lucide-react";
import { useProducts } from "@/features/products/hooks/useProducts";
import { useCategoryOptions } from "@/features/categories/hooks/useCategories";
import { usePagination } from "@/shared/hooks/usePagination";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { Skeleton } from "@/shared/components/ui/badge";
import { Pagination } from "@/shared/components/ui/pagination";
import { EmptyState } from "@/shared/components/EmptyState";
import { formatCurrency } from "@/shared/lib/utils";

export function ProductListPage() {
  const { page, pageSize, setPage, setPageSize, resetPage } = usePagination();
  const [search, setSearch] = useState("");
  const [categoryId, setCategoryId] = useState<string>("all");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");

  const { data: categoriesData } = useCategoryOptions();
  const params = useMemo(
    () => ({
      page,
      page_size: pageSize,
      category_id: categoryId === "all" ? undefined : categoryId,
      min_price: minPrice ? Number(minPrice) : undefined,
      max_price: maxPrice ? Number(maxPrice) : undefined,
    }),
    [page, pageSize, categoryId, minPrice, maxPrice],
  );

  const { data, isLoading, isError } = useProducts(params);

  const filteredItems = useMemo(() => {
    if (!data?.items) return [];
    if (!search.trim()) return data.items;
    const query = search.toLowerCase();
    return data.items.filter(
      (product) =>
        product.name.toLowerCase().includes(query) ||
        product.description?.toLowerCase().includes(query) ||
        product.slug.toLowerCase().includes(query),
    );
  }, [data?.items, search]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Products</h1>
        <p className="text-muted-foreground">Browse the catalog with filters and pagination</p>
      </div>

      <Card>
        <CardContent className="grid gap-4 pt-6 md:grid-cols-2 lg:grid-cols-5">
          <div className="space-y-2 lg:col-span-2">
            <Label htmlFor="search">Search</Label>
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input id="search" className="pl-9" placeholder="Search on this page..." value={search} onChange={(e) => setSearch(e.target.value)} />
            </div>
          </div>
          <div className="space-y-2">
            <Label>Category</Label>
            <Select
              value={categoryId}
              onValueChange={(value) => {
                setCategoryId(value);
                resetPage();
              }}
            >
              <SelectTrigger><SelectValue placeholder="All categories" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All categories</SelectItem>
                {categoriesData?.items.map((category) => (
                  <SelectItem key={category.id} value={category.id}>{category.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="min_price">Min price</Label>
            <Input
              id="min_price"
              type="number"
              min="0"
              value={minPrice}
              onChange={(e) => {
                setMinPrice(e.target.value);
                resetPage();
              }}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="max_price">Max price</Label>
            <Input
              id="max_price"
              type="number"
              min="0"
              value={maxPrice}
              onChange={(e) => {
                setMaxPrice(e.target.value);
                resetPage();
              }}
            />
          </div>
        </CardContent>
      </Card>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: pageSize }).map((_, index) => (
            <Skeleton key={index} className="h-48 w-full" />
          ))}
        </div>
      ) : null}

      {isError ? <p className="text-destructive">Failed to load products.</p> : null}

      {!isLoading && filteredItems.length === 0 ? (
        <EmptyState title="No products found" description="Try adjusting your filters or search query." />
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {filteredItems.map((product) => (
          <Link key={product.id} to={`/products/${product.slug}`}>
            <Card className="h-full transition-shadow hover:shadow-md">
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-lg">{product.name}</CardTitle>
                  {!product.is_active ? <Badge variant="secondary">Inactive</Badge> : null}
                </div>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p className="line-clamp-2 text-muted-foreground">{product.description ?? "No description"}</p>
                <div className="flex items-center justify-between font-medium">
                  <span>{formatCurrency(product.price)}</span>
                  <span>Stock: {product.stock_quantity}</span>
                </div>
              </CardContent>
            </Card>
          </Link>
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
