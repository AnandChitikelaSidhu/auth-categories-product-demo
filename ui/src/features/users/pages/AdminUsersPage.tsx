import { useUsers } from "@/features/users/hooks/useUsers";
import { usePagination } from "@/shared/hooks/usePagination";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { Pagination } from "@/shared/components/ui/pagination";

export function AdminUsersPage() {
  const { page, pageSize, setPage, setPageSize } = usePagination();
  const { data, isLoading, isError } = useUsers(page, pageSize);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Users</h1>
        <p className="text-muted-foreground">Admin view of registered users</p>
      </div>

      <Card>
        <CardHeader><CardTitle>User list</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? <Skeleton className="h-64 w-full" /> : null}
          {isError ? <p className="text-destructive">Failed to load users.</p> : null}
          {data ? (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.items.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell>{user.full_name}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell><Badge variant="secondary">{user.role}</Badge></TableCell>
                      <TableCell>{user.is_active ? "Active" : "Disabled"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <div className="mt-4">
                <Pagination
                  page={data.page}
                  pages={data.pages}
                  pageSize={data.page_size}
                  totalCount={data.total}
                  onPageChange={setPage}
                  onPageSizeChange={setPageSize}
                />
              </div>
            </>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
