import { useState } from "react";
import { Outlet } from "react-router";
import { Navbar } from "@/shared/components/layout/Navbar";
import { Sidebar } from "@/shared/components/layout/Sidebar";
import { cn } from "@/shared/lib/utils";

export function DashboardLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <Navbar onMenuClick={() => setMobileOpen((open) => !open)} />
      <div className="flex">
        <Sidebar />
        <div
          className={cn(
            "fixed inset-0 z-30 bg-black/50 md:hidden",
            mobileOpen ? "block" : "hidden",
          )}
          onClick={() => setMobileOpen(false)}
        />
        <aside
          className={cn(
            "fixed inset-y-0 left-0 z-40 w-64 border-r bg-card pt-16 transition-transform md:hidden",
            mobileOpen ? "translate-x-0" : "-translate-x-full",
          )}
        >
          <Sidebar />
        </aside>
        <main className="flex-1 p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
      <div className="w-full max-w-md">
        <Outlet />
      </div>
    </div>
  );
}
