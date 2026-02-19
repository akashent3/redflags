'use client';

/**
 * Features & Pricing Page
 */

import React from 'react';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import PublicHeader from '@/components/layout/PublicHeader';
import PublicFooter from '@/components/layout/PublicFooter';

const featureCategories: {
  bg: string;
  iconColor: string;
  title: string;
  badge?: string;
  icon: React.ReactNode;
  features: string[];
}[] = [
  {
    bg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    title: 'Forensic Analysis Engine',
    icon: (
      <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
    features: [
      '44 checks for non-financial companies across 8 categories',
      '35 specialized checks for banks and NBFCs',
      'Auditor quality & opinion analysis',
      'Cash flow divergence & earnings quality checks',
      'Related-party transaction screening',
      'Promoter behaviour & pledge detection',
      'Governance & regulatory compliance flags',
      'Balance sheet quality checks (debt, intangibles, CWIP)',
      'Revenue recognition & textual/MD&A analysis',
    ],
  },
  {
    bg: 'bg-green-100',
    iconColor: 'text-green-600',
    title: 'Dual-Layer AI Analysis',
    icon: (
      <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    features: [
      'AI reads and interprets the full PDF document',
      'Detects qualitative flags: auditor opinions, governance issues, MD&A tone',
      'Quantitative engine calculates ratio-based checks',
      'Financial data checks: cash flow, debt ratios, working capital',
      'Full analysis in under 60 seconds',
      'Upload any annual report PDF',
      'Pre-indexed 500+ NIFTY company database',
      'Evidence-backed explanation for every flag',
    ],
  },
  {
    bg: 'bg-purple-100',
    iconColor: 'text-purple-600',
    title: 'Risk Scoring & Reports',
    icon: (
      <svg className="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    features: [
      'Comprehensive 0–100 risk score',
      'Category-level score breakdowns',
      'Visual risk gauge and spider chart',
      'Detailed red flag cards with evidence',
      'Report history & search',
      'Consolidated vs standalone report detection',
    ],
  },
  {
    bg: 'bg-orange-100',
    iconColor: 'text-orange-600',
    title: 'Portfolio & Watchlist',
    badge: 'Pro+',
    icon: (
      <svg className="h-6 w-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
    ),
    features: [
      'Portfolio scanner — analyze multiple companies',
      'Portfolio heatmap for quick risk overview',
      'Watchlist for tracking companies over time',
      'Watchlist alerts when new filings are available',
    ],
  },
  {
    bg: 'bg-red-100',
    iconColor: 'text-red-600',
    title: 'Fraud Database',
    badge: 'Pro+',
    icon: (
      <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    features: [
      'Curated database of historical corporate fraud cases',
      'Case studies showing how red flags appeared in real scandals',
      'Searchable by company, sector, or fraud type',
      'Educational resources for forensic accounting',
    ],
  },
];

const pricingPlans = [
  {
    name: 'Free',
    price: '₹0',
    period: '/month',
    description: 'Perfect for trying out',
    highlight: false,
    badge: null,
    features: [
      '3 reports per month',
      'Full forensic analysis (44 / 35 checks)',
      'Risk score with category breakdown',
      'Evidence-backed flag explanations',
      'Report history',
    ],
    cta: 'Get Started',
    ctaVariant: 'outline' as const,
    href: '/signup',
  },
  {
    name: 'Pro',
    price: '₹499',
    period: '/month',
    description: 'For serious investors',
    highlight: true,
    badge: 'Most Popular',
    features: [
      '50 reports per month',
      'Everything in Free',
      'Advanced visualizations (spider chart, risk gauge)',
      'Watchlist & company tracking',
      'Watchlist alerts',
    ],
    cta: 'Start Pro Trial',
    ctaVariant: 'default' as const,
    href: '/signup',
  },
  {
    name: 'Pro+',
    price: '₹999',
    period: '/month',
    description: 'For professionals',
    highlight: false,
    badge: null,
    features: [
      'Unlimited reports',
      'Everything in Pro',
      'Portfolio scanner & heatmap',
      'Fraud database access',
      'Priority support',
      'Early access to new features',
    ],
    cta: 'Get Pro+',
    ctaVariant: 'outline' as const,
    href: '/signup',
  },
];

function CheckIcon() {
  return (
    <svg className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  );
}

export default function FeaturesPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex flex-col">
      <PublicHeader />

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-24 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-100 text-blue-700 text-sm font-medium mb-6">
          Features &amp; Pricing
        </div>
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
          Everything You Need to<br className="hidden md:block" /> Invest with Confidence
        </h1>
        <p className="text-lg md:text-xl text-gray-600 max-w-2xl mx-auto mb-8">
          StockForensics combines AI with forensic accounting expertise to surface hidden risks
          in any corporate annual report — in seconds.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link href="/signup">
            <Button size="lg" className="text-lg px-8 w-full sm:w-auto">
              Start Free Trial
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
          <Link href="/about">
            <Button size="lg" variant="outline" className="text-lg px-8 w-full sm:w-auto">
              Learn More
            </Button>
          </Link>
        </div>
        <p className="mt-4 text-sm text-gray-500">
          Free tier: 3 reports per month • No credit card required
        </p>
      </section>

      {/* Feature Categories */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 md:pb-24">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Platform Features</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            A complete forensic toolkit built for individual investors and professionals alike
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {featureCategories.map((cat) => (
            <div
              key={cat.title}
              className="bg-white rounded-xl shadow-lg border border-gray-200 p-8 hover:shadow-xl transition-shadow relative"
            >
              {cat.badge && (
                <span className="absolute top-4 right-4 bg-blue-600 text-white text-xs font-semibold px-2 py-0.5 rounded-full">
                  {cat.badge}
                </span>
              )}
              <div className={`${cat.bg} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
                {cat.icon}
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">{cat.title}</h3>
              <ul className="space-y-2">
                {cat.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm text-gray-600">
                    <CheckIcon />
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* Stats */}
      <section className="bg-blue-600 py-16 md:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-12">By the Numbers</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            <div>
              <div className="text-5xl font-bold mb-2">44</div>
              <div className="text-blue-100">Checks (Non-Banks)</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">35</div>
              <div className="text-blue-100">Checks (Banks/NBFCs)</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">500+</div>
              <div className="text-blue-100">NIFTY Companies</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">&lt;60s</div>
              <div className="text-blue-100">Analysis Time</div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-lg text-gray-600">Choose the plan that fits your needs</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {pricingPlans.map((plan) => (
            <div
              key={plan.name}
              className={`bg-white rounded-xl shadow-lg p-8 relative ${
                plan.highlight ? 'border-2 border-blue-600 shadow-xl' : 'border border-gray-200'
              }`}
            >
              {plan.badge && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                    {plan.badge}
                  </span>
                </div>
              )}
              <h3 className="text-2xl font-bold text-gray-900 mb-1">{plan.name}</h3>
              <p className="text-gray-600 mb-5">{plan.description}</p>
              <div className="mb-6">
                <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                <span className="text-gray-600">{plan.period}</span>
              </div>
              <ul className="space-y-3 mb-8">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2">
                    <CheckIcon />
                    <span className="text-gray-700 text-sm">{f}</span>
                  </li>
                ))}
              </ul>
              <Link href={plan.href}>
                <Button variant={plan.ctaVariant} className="w-full">
                  {plan.cta}
                </Button>
              </Link>
            </div>
          ))}
        </div>
        <p className="text-center text-sm text-gray-500 mt-8">
          All prices in INR. Billed monthly. Cancel anytime.
        </p>
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 md:pb-24">
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl shadow-2xl p-8 md:p-12 text-center text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Uncover Hidden Risks?</h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Start with 3 free reports — no credit card required.
          </p>
          <Link href="/signup">
            <Button size="lg" variant="secondary" className="text-lg px-8">
              Start Free Trial
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      <PublicFooter />
    </main>
  );
}
