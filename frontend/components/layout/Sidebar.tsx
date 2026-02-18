'use client';

/**
 * Sidebar Component
 *
 * Side navigation for dashboard pages
 */

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  FileSearch,
  Briefcase,
  Eye,
  GraduationCap,
  Settings,
  Shield,
  X,
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

// Check if user is admin (from localStorage)
const isAdmin = () => {
  if (typeof window === 'undefined') return false;
  try {
    const user = localStorage.getItem('user');
    if (user) {
      const userData = JSON.parse(user);
      return userData.is_admin === true;
    }
  } catch (e) {
    return false;
  }
  return false;
};

const getNavItems = () => {
  const baseItems = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: LayoutDashboard,
      description: 'Overview and stats',
    },
    {
      name: 'Analyze',
      href: '/analyze',
      icon: FileSearch,
      description: 'Upload or search reports',
    },
    {
      name: 'Portfolio',
      href: '/portfolio',
      icon: Briefcase,
      description: 'Bulk portfolio scanner',
    },
    {
      name: 'Watchlist',
      href: '/watchlist',
      icon: Eye,
      description: 'Track companies',
    },
    {
      name: 'Learn',
      href: '/learn',
      icon: GraduationCap,
      description: 'Fraud database',
    },
    {
      name: 'Settings',
      href: '/settings',
      icon: Settings,
      description: 'Account settings',
    },
  ];

  // Add admin item if user is admin
  if (isAdmin()) {
    baseItems.push({
      name: 'Admin',
      href: '/admin',
      icon: Shield,
      description: 'System administration',
    });
  }

  return baseItems;
};

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-50
          w-64 bg-white border-r border-gray-200
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Mobile Close Button */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 lg:hidden">
            <Image
              src="/logo.png"
              alt="RedFlag AI"
              width={130}
              height={36}
              className="h-9 w-auto object-contain"
              priority
            />
            <button
              onClick={onClose}
              className="p-2 rounded-md hover:bg-gray-100"
            >
              <X className="h-5 w-5 text-gray-600" />
            </button>
          </div>

          {/* Navigation Links */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            {getNavItems().map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || pathname.startsWith(item.href + '/');

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => {
                    // Close mobile menu on navigation
                    if (window.innerWidth < 1024) {
                      onClose();
                    }
                  }}
                  className={`
                    flex items-center gap-3 px-3 py-2.5 rounded-lg
                    transition-colors duration-150
                    ${
                      isActive
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }
                  `}
                >
                  <Icon
                    className={`h-5 w-5 flex-shrink-0 ${
                      isActive ? 'text-blue-700' : 'text-gray-500'
                    }`}
                  />
                  <div className="flex-1">
                    <div
                      className={`text-sm font-medium ${
                        isActive ? 'text-blue-700' : 'text-gray-900'
                      }`}
                    >
                      {item.name}
                    </div>
                    <div className="text-xs text-gray-500">
                      {item.description}
                    </div>
                  </div>
                </Link>
              );
            })}
          </nav>

          {/* Footer Section */}
          <div className="p-4 border-t border-gray-200">
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-blue-900 mb-1">
                Pro+ Features
              </h3>
              <p className="text-xs text-blue-700 mb-3">
                Unlock trends, peer comparison, and more
              </p>
              <button className="w-full px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded-md hover:bg-blue-700 transition-colors">
                Upgrade Now
              </button>
            </div>
          </div>

          {/* Version Info */}
          <div className="px-4 py-3 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              RedFlag AI v1.0.0
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
