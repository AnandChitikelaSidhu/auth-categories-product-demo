import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router";
import { toast } from "sonner";
import { authApi } from "@/features/auth/api/auth-api";
import { useAuthStore } from "@/features/auth/store/auth-store";
import type { LoginFormValues, ProfileFormValues, RegisterFormValues } from "@/features/auth/schemas/auth-schemas";
import { getErrorMessage } from "@/shared/lib/utils";

export function useProfile() {
  const setUser = useAuthStore((state) => state.setUser);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: ["profile"],
    queryFn: async () => {
      const { data } = await authApi.me();
      setUser(data);
      return data;
    },
    enabled: Boolean(accessToken),
  });
}

export function useLogin() {
  const navigate = useNavigate();
  const setSession = useAuthStore((state) => state.setSession);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: LoginFormValues) => {
      const { data: tokens } = await authApi.login(payload);
      setSession(tokens);
      const { data: user } = await authApi.me();
      setSession(tokens, user);
      return user;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      toast.success("Welcome back!");
      navigate("/");
    },
    onError: (error) => toast.error(getErrorMessage(error, "Login failed")),
  });
}

export function useRegister() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (payload: RegisterFormValues) => authApi.register(payload).then((res) => res.data),
    onSuccess: () => {
      toast.success("Account created. Please sign in.");
      navigate("/login");
    },
    onError: (error) => toast.error(getErrorMessage(error, "Registration failed")),
  });
}

export function useUpdateProfile() {
  const setUser = useAuthStore((state) => state.setUser);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ProfileFormValues) => authApi.updateMe(payload).then((res) => res.data),
    onSuccess: (user) => {
      setUser(user);
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      toast.success("Profile updated");
    },
    onError: (error) => toast.error(getErrorMessage(error, "Update failed")),
  });
}

export function useLogout() {
  const navigate = useNavigate();
  const clearSession = useAuthStore((state) => state.clearSession);
  const refreshToken = useAuthStore((state) => state.refreshToken);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      if (refreshToken) {
        await authApi.logout(refreshToken);
      }
    },
    onSettled: () => {
      clearSession();
      queryClient.clear();
      navigate("/login");
      toast.success("Logged out");
    },
  });
}
