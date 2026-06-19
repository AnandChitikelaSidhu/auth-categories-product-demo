import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { roleUpdateSchema, type RoleUpdateFormValues } from "@/features/users/api/users-api";
import { useUpdateUserRole, useUsers } from "@/features/users/hooks/useUsers";
import { usePagination } from "@/shared/hooks/usePagination";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Label } from "@/shared/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { Badge } from "@/shared/components/ui/badge";
import { Pagination } from "@/shared/components/ui/pagination";

export function AdminRolesPage() {
  const { page, pageSize, setPage, setPageSize } = usePagination();
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const { data } = useUsers(page, pageSize);
  const updateRole = useUpdateUserRole();
  const form = useForm<RoleUpdateFormValues>({
    resolver: zodResolver(roleUpdateSchema),
    defaultValues: { role: "customer" },
  });

  const selectedUser = data?.items.find((user) => user.id === selectedUserId);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Role Management</h1>
        <p className="text-muted-foreground">Super admin only — update user roles</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Users</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.items.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.full_name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell><Badge variant="secondary">{user.role}</Badge></TableCell>
                  <TableCell>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setSelectedUserId(user.id);
                        form.setValue("role", user.role);
                      }}
                    >
                      Change role
                    </Button>
                  </TableCell>
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
                totalCount={data.total}
                onPageChange={setPage}
                onPageSizeChange={setPageSize}
              />
            </div>
          ) : null}
        </CardContent>
      </Card>

      {selectedUser ? (
        <Card>
          <CardHeader><CardTitle>Update role for {selectedUser.full_name}</CardTitle></CardHeader>
          <CardContent>
            <form
              className="flex flex-col gap-4 sm:flex-row sm:items-end"
              onSubmit={form.handleSubmit((values) =>
                updateRole.mutate({ userId: selectedUser.id, ...values }),
              )}
            >
              <div className="space-y-2 sm:w-64">
                <Label>Role</Label>
                <Select value={form.watch("role")} onValueChange={(value) => form.setValue("role", value as RoleUpdateFormValues["role"])}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="customer">Customer</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="super_admin">Super Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button type="submit" disabled={updateRole.isPending}>
                {updateRole.isPending ? "Updating..." : "Update role"}
              </Button>
            </form>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
