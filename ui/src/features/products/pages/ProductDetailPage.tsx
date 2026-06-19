import { Link, useParams } from "react-router";
import { ArrowLeft } from "lucide-react";
import { useProduct } from "@/features/products/hooks/useProducts";
import { Button } from "@/shared/components/ui/button";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/badge";
import { formatCurrency } from "@/shared/lib/utils";

export function ProductDetailPage() {
  const { identifier } = useParams<{ identifier: string }>();
  const { data: product, isLoading, isError } = useProduct(identifier);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <Skeleton className="h-10 w-32" />
        <Skeleton className="h-72 w-full" />
      </div>
    );
  }

  if (isError || !product) {
    return <p className="text-destructive">Product not found.</p>;
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Button variant="ghost" asChild>
        <Link to="/">
          <ArrowLeft className="h-4 w-4" />
          Back to products
        </Link>
      </Button>

      <Card>
        <CardHeader className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <CardTitle className="text-3xl">{product.name}</CardTitle>
            {!product.is_active ? <Badge variant="secondary">Inactive</Badge> : null}
            {product.cacheStatus ? (
              <Badge variant={product.cacheStatus === "HIT" ? "success" : "outline"}>
                Cache: {product.cacheStatus}
              </Badge>
            ) : null}
          </div>
          <p className="text-sm text-muted-foreground">Slug: {product.slug}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <p>{product.description ?? "No description provided."}</p>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground">Price</p>
              <p className="text-2xl font-semibold">{formatCurrency(product.price)}</p>
            </div>
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground">Stock</p>
              <p className="text-2xl font-semibold">{product.stock_quantity}</p>
            </div>
          </div>
          {product.category ? (
            <p className="text-sm">
              Category: <span className="font-medium">{product.category.name}</span>
            </p>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
