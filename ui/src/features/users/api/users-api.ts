import { z } from "zod";
import type { PaginatedResponse, User, UserRole } from "@/shared/types/api.types";
import { authClient } from "@/shared/lib/api-client";
import { DEFAULT_PAGE_SIZE } from "@/shared/constants/pagination";

export const roleUpdateSchema = z.object({
  role: z.enum(["customer", "admin", "super_admin"]),
});

export type RoleUpdateFormValues = z.infer<typeof roleUpdateSchema>;

export const usersApi = {
  list: (page = 1, page_size = DEFAULT_PAGE_SIZE) =>
    authClient.get<PaginatedResponse<User>>("/auth/users", { params: { page, page_size } }),

  updateRole: (userId: string, role: UserRole) =>
    authClient.patch<User>(`/auth/users/${userId}/role`, { role }),
};
