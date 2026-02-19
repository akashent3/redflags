'use client';

/**
 * About Us Page
 *
 * Same look and feel as the homepage.
 * Uses PublicHeader so signed-in users see "Go to Dashboard" instead of Sign In/Get Started.
 * Includes an FAQ section at the bottom.
 */

import Link from 'next/link';
import { ArrowRight, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import PublicHeader from '@/components/layout/PublicHeader';
import PublicFooter from '@/components/layout/PublicFooter';

const faqs = [
  {
    question: 'What is StockForensics?',
    answer:
      'StockForensics is an AI-powered forensic accounting platform that analyzes corporate annual reports to detect financial red flags and help investors make informed decisions. We check 44 distinct risk indicators for non-financial companies and 35 specialized indicators for banks and NBFCs.',
  },
  {
    question: 'How do I get started?',
    answer:
      "Sign up for a free account — no credit card required. You get 3 free reports per month. Once logged in, go to the Analyze page, upload a company's annual report PDF or search from our database of 500+ NIFTY-listed companies, and receive a full forensic analysis in under 60 seconds.",
  },
  {
    question: 'What types of reports can I analyze?',
    answer:
      "You can upload any company's annual report in PDF format. We also maintain a pre-indexed database of 500+ NIFTY-listed companies whose reports can be analyzed directly without uploading.",
  },
  {
    question: 'What are "red flags" in financial reports?',
    answer:
      'Red flags are warning signs in financial statements that may indicate accounting manipulation, earnings quality issues, or financial distress. Our AI checks for things like cash flow divergence, related-party transaction concerns, auditor qualifications, governance issues, and more.',
  },
  {
    question: 'How does the risk score work?',
    answer:
      'Every analysis produces a 0–100 risk score. A higher score means more red flags were detected. The score is broken down by category — Auditor, Cash Flow, Related Party, Promoter, Governance, Balance Sheet, Revenue, and Textual Analysis — so you can see exactly where risks lie.',
  },
  {
    question: 'How many red flags do you check?',
    answer:
      'For non-financial companies (manufacturing, services, etc.) we check 44 red flags across 8 categories using a combination of AI document analysis and quantitative financial data checks. For banks and NBFCs we run a specialized set of 35 bank-specific checks including NPA quality, capital adequacy, liquidity, and credit concentration.',
  },
  {
    question: 'What are the 8 categories of red flags?',
    answer:
      'For non-financial companies: (1) Auditor & Audit Quality, (2) Cash Flow Analysis, (3) Related Party Transactions, (4) Promoter Behaviour, (5) Governance, (6) Balance Sheet Quality, (7) Revenue Recognition, and (8) Textual/MD&A Analysis. Banks have their own specialized categories including NPA quality, capital ratios, liquidity, and credit concentration.',
  },
  {
    question: 'How does the AI analysis work?',
    answer:
      'Our platform uses two layers of analysis: (1) an AI model that reads and interprets the actual PDF text to detect qualitative flags like auditor opinions, governance issues, and management tone; and (2) a quantitative engine that uses structured financial data to calculate ratio-based checks like cash flow divergence, debt levels, and working capital trends.',
  },
  {
    question: 'Can I analyze multiple companies at once?',
    answer:
      'Yes. Pro and Pro+ subscribers can use the Portfolio Scanner to run analyses across multiple companies and the Watchlist feature to track companies over time.',
  },
  {
    question: 'What is the Fraud Database?',
    answer:
      'The Fraud Database (accessible via the Learn section) is a curated collection of historical corporate fraud cases. You can study past cases to understand how red flags appeared in real-world accounting scandals.',
  },
  {
    question: 'Is my data secure?',
    answer:
      'Yes. Uploaded reports are processed securely and stored with encryption. We do not share your data or analyses with third parties. Please review our Privacy & Terms page for full details.',
  },
  {
    question: 'What is the difference between Free, Pro, and Pro+?',
    answer:
      'Free gives you 3 reports/month with basic risk scoring. Pro (₹499/month) includes 50 reports/month, advanced visualizations, portfolio scanning, and watchlists. Pro+ (₹999/month) adds unlimited reports and priority support.',
  },
  {
    question: 'How do I contact support?',
    answer:
      'You can reach us via the Contact page, or email us directly at info@stockforensics.com. We aim to respond within 1–2 business days.',
  },
];

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden">
      <button
        className="w-full flex items-center justify-between px-6 py-5 text-left bg-white hover:bg-gray-50 transition-colors"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
      >
        <span className="font-semibold text-gray-900 text-base">{question}</span>
        <ChevronDown
          className={`h-5 w-5 text-gray-500 flex-shrink-0 ml-4 transition-transform ${open ? 'rotate-180' : ''}`}
        />
      </button>
      {open && (
        <div className="px-6 pb-5 bg-white">
          <p className="text-gray-600 leading-relaxed">{answer}</p>
        </div>
      )}
    </div>
  );
}

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex flex-col">
      <PublicHeader />

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">
        <div className="text-center max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-100 text-blue-700 text-sm font-medium mb-6">
            About StockForensics
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Your AI Forensic Accountant
          </h1>
          <p className="text-lg md:text-xl text-gray-600 mb-8">
            We built StockForensics to give every investor access to the same forensic accounting
            tools that professionals use — powered by advanced AI, available in seconds.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/signup">
              <Button size="lg" className="text-lg px-8 w-full sm:w-auto">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="text-lg px-8 w-full sm:w-auto">
                Sign In
              </Button>
            </Link>
          </div>
          <p className="mt-4 text-sm text-gray-500">
            Free tier: 3 reports per month • No credit card required
          </p>
        </div>
      </section>

      {/* Mission */}
      <section className="bg-gray-50 py-16 md:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">Our Mission</h2>
            <p className="text-lg text-gray-600 mb-4">
              Retail investors rarely have access to the deep forensic analysis that institutional
              players take for granted. Annual reports are dense, jargon-heavy, and deliberately
              complex — often hiding material risks in plain sight.
            </p>
            <p className="text-lg text-gray-600">
              StockForensics exists to change that. By combining AI with a rigorous forensic
              checklist, we surface hidden risks in any annual report in under 60 seconds — so
              you can invest with confidence.
            </p>
          </div>
        </div>
      </section>

      {/* Why Choose Us */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Why Choose StockForensics?
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            A complete forensic toolkit built for individual investors and professionals alike
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8 hover:shadow-xl transition-shadow">
            <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">
              44 Checks for Non-Banks, 35 for Banks
            </h3>
            <p className="text-gray-600">
              Separate forensic frameworks for non-financial companies and banks/NBFCs, covering
              auditor quality, cash flow, related parties, promoter behaviour, governance,
              balance sheet, revenue, and textual analysis.
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8 hover:shadow-xl transition-shadow">
            <div className="bg-green-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Dual-Layer Analysis</h3>
            <p className="text-gray-600">
              Our AI reads and interprets the actual PDF document for qualitative flags, while a
              separate quantitative engine checks financial ratios using structured data — both
              in under 60 seconds.
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8 hover:shadow-xl transition-shadow">
            <div className="bg-purple-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <svg className="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Evidence-Backed Risk Score</h3>
            <p className="text-gray-600">
              Get a comprehensive 0–100 risk score with category-level breakdowns and
              evidence-backed explanations for every triggered flag.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="bg-gray-50 py-16 md:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">How It Works</h2>
            <p className="text-lg text-gray-600">Three simple steps to forensic insights</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { n: 1, title: 'Upload Report', desc: 'Upload any annual report PDF or search from 500+ NIFTY-listed companies' },
              { n: 2, title: 'AI Analysis', desc: 'Our AI reads the document and runs quantitative checks across all flag categories' },
              { n: 3, title: 'Get Insights', desc: 'Review your risk score, triggered flags, and evidence-backed explanations' },
            ].map(({ n, title, desc }) => (
              <div key={n} className="text-center">
                <div className="bg-blue-600 text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                  {n}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{title}</h3>
                <p className="text-gray-600">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-blue-600 py-16 md:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Built for Indian Investors</h2>
          <p className="text-xl text-blue-100 mb-12">
            A purpose-built forensic platform for NIFTY-listed companies
          </p>
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

      {/* FAQ */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Everything you need to know about using StockForensics
          </p>
        </div>
        <div className="max-w-3xl mx-auto space-y-4">
          {faqs.map((faq, i) => (
            <FAQItem key={i} question={faq.question} answer={faq.answer} />
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 md:pb-24">
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl shadow-2xl p-8 md:p-12 text-center text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Uncover Hidden Risks?</h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Start analyzing annual reports with AI-powered forensic accounting today.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/signup">
              <Button size="lg" variant="secondary" className="text-lg px-8 w-full sm:w-auto">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="text-lg px-8 w-full sm:w-auto bg-transparent border-white text-white hover:bg-blue-500">
                Sign In
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <PublicFooter />
    </main>
  );
}
