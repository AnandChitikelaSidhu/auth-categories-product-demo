import { Link } from "react-router";
import { LogOut, Menu, Moon, Sun, UserCircle } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { useTheme } from "@/shared/components/ThemeProvider";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useLogout } from "@/features/auth/hooks/useAuth";

interface NavbarProps {
  onMenuClick?: () => void;
}

export function Navbar({ onMenuClick }: NavbarProps) {
  const { theme, toggleTheme } = useTheme();
  const user = useAuthStore((state) => state.user);
  const logout = useLogout();

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b bg-background/95 px-4 backdrop-blur md:px-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" className="md:hidden" onClick={onMenuClick}>
          <Menu className="h-5 w-5" />
        </Button>
        <Link to="/" className="font-semibold md:hidden">
          Kalo Catalog
        </Link>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
          {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>

        {user ? (
          <>
            <Button variant="ghost" asChild>
              <Link to="/profile" className="gap-2">
                <UserCircle className="h-4 w-4" />
                <span className="hidden sm:inline">{user.full_name}</span>
              </Link>
            </Button>
            <Button variant="outline" size="sm" onClick={() => logout.mutate()} disabled={logout.isPending}>
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </>
        ) : (
          <Button asChild>
            <Link to="/login">Sign in</Link>
          </Button>
        )}
      </div>
    </header>
  );
}
