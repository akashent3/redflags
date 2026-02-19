'use client';

/**
 * Privacy Policy & Terms of Service Page (Combined)
 */

import Link from 'next/link';
import { Lock } from 'lucide-react';
import PublicHeader from '@/components/layout/PublicHeader';
import PublicFooter from '@/components/layout/PublicFooter';

export default function LegalPage() {
  return (
    <main className="min-h-screen bg-gray-50">
      <PublicHeader />

      {/* Hero */}
      <section className="bg-white border-b border-gray-200 py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-100 text-blue-700 text-sm font-medium mb-4">
            <Lock className="h-4 w-4" />
            Legal
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-3">
            Privacy Policy &amp; Terms of Service
          </h1>
          <p className="text-gray-600">Last updated: February 2026</p>
        </div>
      </section>

      {/* Tab navigation */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-16">

        {/* ── PRIVACY POLICY ── */}
        <div id="privacy">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 pb-3 border-b border-gray-200">
            Privacy Policy
          </h2>

          <div className="space-y-8 text-gray-700 leading-relaxed">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">1. Information We Collect</h3>
              <p>
                We collect information you provide directly, such as your name and email address when
                you create an account. We also collect information about how you use our services,
                including the annual reports you upload for analysis and the results generated.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">2. How We Use Your Information</h3>
              <p className="mb-2">We use the information we collect to:</p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>Provide, maintain, and improve our services</li>
                <li>Process your analyses and generate forensic reports</li>
                <li>Send you service-related communications</li>
                <li>Respond to your comments and questions</li>
                <li>Monitor usage patterns to improve user experience</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">3. Data Storage &amp; Security</h3>
              <p>
                Uploaded annual report PDFs are stored securely on AWS S3 with server-side
                encryption. Your analysis results are stored in an encrypted PostgreSQL database.
                We implement industry-standard security measures including HTTPS encryption for all
                data in transit.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">4. Third-Party Services</h3>
              <p>
                We use third-party AI services to process and analyze the documents you upload.
                Documents are transmitted to these services in accordance with their respective
                data processing terms. We do not sell your personal data to any third party.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">5. Data Retention</h3>
              <p>
                We retain your account information and analysis results for as long as your account
                is active. You may request deletion of your account and associated data at any time
                by contacting us at{' '}
                <a href="mailto:info@stockforensics.com" className="text-blue-600 hover:underline">
                  info@stockforensics.com
                </a>
                .
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">6. Cookies</h3>
              <p>
                We use essential cookies to maintain your session and authentication state. We do
                not use tracking or advertising cookies. You may disable cookies in your browser
                settings, but this may affect your ability to use our services.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">7. Your Rights</h3>
              <p>
                You have the right to access, correct, or delete your personal data. To exercise
                these rights, please contact us at{' '}
                <a href="mailto:info@stockforensics.com" className="text-blue-600 hover:underline">
                  info@stockforensics.com
                </a>
                .
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">8. Changes to This Policy</h3>
              <p>
                We may update this Privacy Policy from time to time. We will notify you of any
                significant changes by posting the new policy on this page with an updated date.
              </p>
            </div>
          </div>
        </div>

        {/* ── TERMS OF SERVICE ── */}
        <div id="terms">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 pb-3 border-b border-gray-200">
            Terms of Service
          </h2>

          <div className="space-y-8 text-gray-700 leading-relaxed">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">1. Acceptance of Terms</h3>
              <p>
                By accessing or using StockForensics, you agree to be bound by these Terms of
                Service. If you do not agree, please do not use our services.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">2. Use of Service</h3>
              <p className="mb-2">You agree to use our services only for lawful purposes. You may not:</p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>Upload documents you do not have the right to analyze</li>
                <li>Attempt to reverse-engineer or scrape our platform</li>
                <li>Share your account credentials with others</li>
                <li>Use the service for any illegal or unauthorized purpose</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">3. Disclaimer of Investment Advice</h3>
              <p>
                <strong>StockForensics is not a financial advisor.</strong> The analyses, risk scores,
                and red flags generated by our platform are for informational purposes only. They
                do not constitute investment advice, a recommendation to buy or sell securities, or
                a guarantee of accuracy. Always conduct your own due diligence and consult a
                qualified financial professional before making investment decisions.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">4. Subscription &amp; Billing</h3>
              <p>
                Paid subscriptions are billed monthly. You may cancel at any time and will retain
                access until the end of your billing period. We do not offer refunds for partial
                months. Pricing is subject to change with 30 days' notice to subscribers.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">5. Intellectual Property</h3>
              <p>
                All content, features, and functionality of the StockForensics platform are owned
                by StockForensics and are protected by copyright and other intellectual property
                laws. Analysis reports generated for your use remain yours; our underlying platform
                and AI integration remain ours.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">6. Limitation of Liability</h3>
              <p>
                To the fullest extent permitted by law, StockForensics shall not be liable for any
                indirect, incidental, special, or consequential damages arising from your use of
                our services or reliance on our analysis results.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">7. Termination</h3>
              <p>
                We reserve the right to suspend or terminate your account if you violate these
                Terms of Service. You may also delete your account at any time from the Settings
                page.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">8. Governing Law</h3>
              <p>
                These Terms of Service are governed by the laws of India. Any disputes shall be
                subject to the exclusive jurisdiction of the courts of India.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">9. Contact</h3>
              <p>
                For any questions regarding these terms, please contact us at{' '}
                <a href="mailto:info@stockforensics.com" className="text-blue-600 hover:underline">
                  info@stockforensics.com
                </a>
                .
              </p>
            </div>
          </div>
        </div>
      </section>

      <PublicFooter />
    </main>
  );
}
