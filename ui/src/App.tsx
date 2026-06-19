import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router";
import { Toaster } from "sonner";
import { AppRoutes } from "@/routes/AppRoutes";
import { ThemeProvider } from "@/shared/components/ThemeProvider";
import { ErrorBoundary } from "@/shared/components/ErrorBoundary";
import { AuthBootstrap } from "@/features/auth/components/AuthBootstrap";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <ErrorBoundary>
            <AuthBootstrap />
            <AppRoutes />
            <Toaster richColors closeButton position="top-right" />
          </ErrorBoundary>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
