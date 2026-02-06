/**
 * Auth Layout
 *
 * Shared layout for authentication pages (login, signup)
 */

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Authentication - RedFlag AI",
  description: "Login or sign up for RedFlag AI",
};

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Logo and Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-blue-600">
            RedFlag AI
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Your AI Forensic Accountant
          </p>
        </div>

        {/* Auth Form Container */}
        <div className="bg-white py-8 px-6 shadow-lg rounded-lg border border-gray-200">
          {children}
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-gray-500">
          <p>
            By continuing, you agree to our{" "}
            <a href="#" className="text-blue-600 hover:underline">
              Terms of Service
            </a>{" "}
            and{" "}
            <a href="#" className="text-blue-600 hover:underline">
              Privacy Policy
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
