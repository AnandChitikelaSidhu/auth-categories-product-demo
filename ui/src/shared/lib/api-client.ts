import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "@/features/auth/store/auth-store";
import type { TokenResponse } from "@/shared/types/api.types";

const AUTH_BASE_URL = import.meta.env.VITE_AUTH_API_URL ?? "http://localhost:8000";
const PRODUCT_BASE_URL = import.meta.env.VITE_PRODUCT_API_URL ?? "http://localhost:8001";

export const authClient = axios.create({ baseURL: AUTH_BASE_URL });
export const productClient = axios.create({ baseURL: PRODUCT_BASE_URL });

let refreshPromise: Promise<string> | null = null;

const attachAuthHeader = (config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

authClient.interceptors.request.use(attachAuthHeader);
productClient.interceptors.request.use(attachAuthHeader);

async function refreshAccessToken(): Promise<string> {
  const refreshToken = useAuthStore.getState().refreshToken;
  if (!refreshToken) throw new Error("No refresh token");

  if (!refreshPromise) {
    refreshPromise = axios
      .post<TokenResponse>(`${AUTH_BASE_URL}/auth/refresh`, { refresh_token: refreshToken })
      .then(({ data }) => {
        useAuthStore.getState().setSession(data);
        return data.access_token;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }

  return refreshPromise;
}

function attachRefreshInterceptor(client: typeof authClient) {
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
      if (!original || error.response?.status !== 401 || original._retry) {
        return Promise.reject(error);
      }

      if (original.url?.includes("/auth/refresh") || original.url?.includes("/auth/login")) {
        return Promise.reject(error);
      }

      original._retry = true;

      try {
        const accessToken = await refreshAccessToken();
        original.headers.Authorization = `Bearer ${accessToken}`;
        return client(original);
      } catch (refreshError) {
        useAuthStore.getState().clearSession();
        return Promise.reject(refreshError);
      }
    },
  );
}

attachRefreshInterceptor(authClient);
attachRefreshInterceptor(productClient);
