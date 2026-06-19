import { Navigate, Route, Routes } from "react-router";
import { LoginPage } from "@/features/auth/pages/LoginPage";
import { RegisterPage } from "@/features/auth/pages/RegisterPage";
import { ProfilePage } from "@/features/auth/pages/ProfilePage";
import { ProductListPage } from "@/features/products/pages/ProductListPage";
import { ProductDetailPage } from "@/features/products/pages/ProductDetailPage";
import { AdminProductsPage } from "@/features/products/pages/AdminProductsPage";
import { CategoryListPage } from "@/features/categories/pages/CategoryListPage";
import { AdminCategoriesPage } from "@/features/categories/pages/AdminCategoriesPage";
import { AdminUsersPage } from "@/features/users/pages/AdminUsersPage";
import { AdminRolesPage } from "@/features/users/pages/AdminRolesPage";
import { AuthLayout, DashboardLayout } from "@/shared/components/layout/DashboardLayout";
import { AdminRoute, ProtectedRoute, SuperAdminRoute } from "@/routes/guards";

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<DashboardLayout />}>
        <Route index element={<ProductListPage />} />
        <Route path="products/:identifier" element={<ProductDetailPage />} />
        <Route path="categories" element={<CategoryListPage />} />

        <Route element={<ProtectedRoute />}>
          <Route path="profile" element={<ProfilePage />} />
        </Route>

        <Route element={<AdminRoute />}>
          <Route path="admin/products" element={<AdminProductsPage />} />
          <Route path="admin/categories" element={<AdminCategoriesPage />} />
          <Route path="admin/users" element={<AdminUsersPage />} />
        </Route>

        <Route element={<SuperAdminRoute />}>
          <Route path="admin/roles" element={<AdminRolesPage />} />
        </Route>
      </Route>

      <Route element={<AuthLayout />}>
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
