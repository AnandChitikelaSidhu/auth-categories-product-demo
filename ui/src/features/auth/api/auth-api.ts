import type { MessageResponse, TokenResponse, User } from "@/shared/types/api.types";
import { authClient } from "@/shared/lib/api-client";
import type { LoginFormValues, ProfileFormValues, RegisterFormValues } from "@/features/auth/schemas/auth-schemas";

export const authApi = {
  login: (payload: LoginFormValues) => authClient.post<TokenResponse>("/auth/login", payload),
  register: (payload: RegisterFormValues) => authClient.post<User>("/auth/register", payload),
  refresh: (refresh_token: string) => authClient.post<TokenResponse>("/auth/refresh", { refresh_token }),
  logout: (refresh_token: string) => authClient.post<MessageResponse>("/auth/logout", { refresh_token }),
  me: () => authClient.get<User>("/auth/me"),
  updateMe: (payload: ProfileFormValues) => authClient.patch<User>("/auth/me", payload),
};
