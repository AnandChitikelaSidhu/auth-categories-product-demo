import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { usersApi } from "@/features/users/api/users-api";
import type { RoleUpdateFormValues } from "@/features/users/api/users-api";
import { DEFAULT_PAGE_SIZE } from "@/shared/constants/pagination";
import { getErrorMessage } from "@/shared/lib/utils";

export function useUsers(page: number, pageSize = DEFAULT_PAGE_SIZE) {
  return useQuery({
    queryKey: ["users", page, pageSize],
    queryFn: () => usersApi.list(page, pageSize).then((res) => res.data),
  });
}

export function useUpdateUserRole() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, role }: { userId: string } & RoleUpdateFormValues) =>
      usersApi.updateRole(userId, role).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success("Role updated");
    },
    onError: (error) => toast.error(getErrorMessage(error, "Role update failed")),
  });
}
