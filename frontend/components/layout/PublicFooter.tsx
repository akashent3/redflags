'use client';

/**
 * PublicFooter — shared footer for all public pages.
 */

import Image from 'next/image';
import Link from 'next/link';

export default function PublicFooter() {
  return (
    <footer className="border-t border-gray-200 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="col-span-1">
            <Link href="/" className="inline-flex mb-3">
              <Image
                src="/logo.png"
                alt="StockForensics"
                width={160}
                height={44}
                className="h-9 w-auto object-contain"
              />
            </Link>
            <p className="text-sm text-gray-600">
              AI-powered forensic accounting for smarter investment decisions.
            </p>
          </div>

          {/* Product */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Product</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/features" className="text-sm text-gray-600 hover:text-blue-600">
                  Features &amp; Pricing
                </Link>
              </li>
              <li>
                <Link href="/learn" className="text-sm text-gray-600 hover:text-blue-600">
                  Fraud Database
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Company</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/about" className="text-sm text-gray-600 hover:text-blue-600">
                  About Us
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-sm text-gray-600 hover:text-blue-600">
                  Contact
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Legal</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/legal" className="text-sm text-gray-600 hover:text-blue-600">
                  Privacy &amp; Terms
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-gray-500">
            © {new Date().getFullYear()} StockForensics. All rights reserved.
          </p>
          <p className="text-sm text-gray-500">Powered by AI</p>
        </div>
      </div>
    </footer>
  );
}
