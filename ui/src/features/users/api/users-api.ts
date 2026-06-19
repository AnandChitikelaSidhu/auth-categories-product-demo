import { z } from "zod";
import type { PaginatedResponse, Role, User } from "@/shared/types/api.types";
import { authClient } from "@/shared/lib/api-client";
import { DEFAULT_PAGE_SIZE } from "@/shared/constants/pagination";

export const roleUpdateSchema = z.object({
  role: z.string().min(1),
});

export type RoleUpdateFormValues = z.infer<typeof roleUpdateSchema>;

export const usersApi = {
  list: (page = 1, page_size = DEFAULT_PAGE_SIZE) =>
    authClient.get<PaginatedResponse<User>>("/auth/users", { params: { page, page_size } }),

  listRoles: () => authClient.get<Role[]>("/auth/roles"),

  updateRole: (userId: string, role: string) =>
    authClient.patch<User>(`/auth/users/${userId}/role`, { role }),
};
