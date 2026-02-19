'use client';

/**
 * Footer Component
 *
 * Footer for dashboard pages
 */

import Link from 'next/link';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Left Section - Copyright */}
          <div className="text-sm text-gray-600">
            © {currentYear} StockForensics. All rights reserved.
          </div>

          {/* Center Section - Links */}
          <div className="flex items-center gap-6">
            <Link
              href="/about"
              className="text-sm text-gray-600 hover:text-blue-600 transition-colors"
            >
              About
            </Link>
            <Link
              href="/features"
              className="text-sm text-gray-600 hover:text-blue-600 transition-colors"
            >
              Features
            </Link>
            <Link
              href="/legal"
              className="text-sm text-gray-600 hover:text-blue-600 transition-colors"
            >
              Privacy &amp; Terms
            </Link>
            <Link
              href="/contact"
              className="text-sm text-gray-600 hover:text-blue-600 transition-colors"
            >
              Contact
            </Link>
          </div>

          {/* Right Section - Attribution */}
          <div className="text-sm text-gray-500">
            Powered by AI
          </div>
        </div>
      </div>
    </footer>
  );
}
