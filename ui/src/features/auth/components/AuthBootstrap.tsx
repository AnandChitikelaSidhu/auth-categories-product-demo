import { useProfile } from "@/features/auth/hooks/useAuth";
import { selectIsAuthenticated, useAuthStore } from "@/features/auth/store/auth-store";

export function AuthBootstrap() {
  const isAuthenticated = useAuthStore(selectIsAuthenticated);
  useProfile();
  if (!isAuthenticated) return null;
  return null;
}
