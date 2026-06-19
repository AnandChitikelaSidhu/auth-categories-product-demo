import { NavLink } from "react-router";
import { FolderTree, LayoutDashboard, Package, Shield, Users } from "lucide-react";
import { cn } from "@/shared/lib/utils";
import { useAuthStore, selectIsAdmin, selectIsSuperAdmin } from "@/features/auth/store/auth-store";

const linkClass = ({ isActive }: { isActive: boolean }) =>
  cn(
    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
    isActive ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
  );

export function Sidebar() {
  const isAdmin = useAuthStore(selectIsAdmin);
  const isSuperAdmin = useAuthStore(selectIsSuperAdmin);

  return (
    <aside className="hidden w-64 shrink-0 border-r bg-card md:block">
      <div className="flex h-16 items-center border-b px-6">
        <span className="text-lg font-bold">Kalo Catalog</span>
      </div>
      <nav className="space-y-1 p-4">
        <NavLink to="/" end className={linkClass}>
          <LayoutDashboard className="h-4 w-4" />
          Products
        </NavLink>
        <NavLink to="/categories" className={linkClass}>
          <FolderTree className="h-4 w-4" />
          Categories
        </NavLink>
        {isAdmin ? (
          <>
            <NavLink to="/admin/products" className={linkClass}>
              <Package className="h-4 w-4" />
              Manage Products
            </NavLink>
            <NavLink to="/admin/categories" className={linkClass}>
              <Shield className="h-4 w-4" />
              Manage Categories
            </NavLink>
            <NavLink to="/admin/users" className={linkClass}>
              <Users className="h-4 w-4" />
              Users
            </NavLink>
          </>
        ) : null}
        {isSuperAdmin ? (
          <NavLink to="/admin/roles" className={linkClass}>
            <Shield className="h-4 w-4" />
            Role Management
          </NavLink>
        ) : null}
      </nav>
    </aside>
  );
}
