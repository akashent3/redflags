'use client';

/**
 * PublicHeader
 *
 * Header for public (non-dashboard) pages.
 * Shows "Dashboard" link if the user is already logged in,
 * or "Sign in / Get Started" buttons if they are not.
 */

import Image from 'next/image';
import Link from 'next/link';
import { useAuth } from '@/lib/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { LayoutDashboard } from 'lucide-react';

export default function PublicHeader() {
  const { isAuthenticated, isLoading } = useAuth();

  return (
    <header className="border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href={isAuthenticated ? '/dashboard' : '/'} className="flex items-center">
            <Image
              src="/logo.png"
              alt="StockForensics"
              width={180}
              height={50}
              className="h-10 w-auto object-contain"
              priority
            />
          </Link>

          {/* Right side — auth-aware */}
          <div className="flex items-center gap-4">
            {isLoading ? (
              // Avoid layout shift while auth state loads
              <div className="h-9 w-32 rounded-md bg-gray-100 animate-pulse" />
            ) : isAuthenticated ? (
              <Link href="/dashboard">
                <Button className="flex items-center gap-2">
                  <LayoutDashboard className="h-4 w-4" />
                  Go to Dashboard
                </Button>
              </Link>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="ghost">Sign in</Button>
                </Link>
                <Link href="/signup">
                  <Button>Get Started</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
