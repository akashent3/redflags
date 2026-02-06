'use client';

/**
 * Settings Page
 *
 * User profile, subscription, notifications, and data management
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  User,
  CreditCard,
  Bell,
  Shield,
  Trash2,
  Download,
  Mail,
  Smartphone,
  Crown,
  Check,
  Settings as SettingsIcon,
  Eye,
  EyeOff,
  Camera,
} from 'lucide-react';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<'profile' | 'subscription' | 'notifications' | 'privacy'>('profile');
  const [showPassword, setShowPassword] = useState(false);

  // Mock user data - TODO: Replace with auth hook
  const [user, setUser] = useState({
    name: 'John Investor',
    email: 'john@example.com',
    subscription_tier: 'pro', // free, pro, premium
    usage_this_month: 15,
    usage_limit: 50,
    notification_prefs: {
      email_alerts: true,
      weekly_digest: true,
      push_notifications: false,
      feature_announcements: true,
    },
  });

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'subscription', label: 'Subscription', icon: CreditCard },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'privacy', label: 'Data & Privacy', icon: Shield },
  ];

  const plans = [
    {
      tier: 'free',
      name: 'Free',
      price: 0,
      features: ['5 reports per month', 'Basic red flag detection', 'Single company analysis', 'Email support'],
    },
    {
      tier: 'pro',
      name: 'Pro',
      price: 999,
      features: ['50 reports per month', 'All red flags', 'Watchlist alerts (weekly)', 'Historical trends', 'Priority support'],
    },
    {
      tier: 'premium',
      name: 'Premium',
      price: 1999,
      features: ['Unlimited reports', 'Portfolio scanner', 'Real-time alerts', 'Push notifications', 'Export to PDF', 'API access', 'Dedicated support'],
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <SettingsIcon className="h-8 w-8 text-blue-600" />
          Settings
        </h1>
        <p className="text-gray-600 mt-2">Manage your account, subscription, and preferences</p>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow border border-gray-200">
        <div className="border-b border-gray-200">
          <div className="flex gap-0">
            {tabs.map((tab) => {
              const IconComponent = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 px-6 py-4 font-semibold transition-colors border-b-2 ${
                    activeTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <IconComponent className="h-5 w-5" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        <div className="p-6">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-4">Profile Information</h2>

                {/* Profile Picture */}
                <div className="flex items-center gap-6 mb-6">
                  <div className="w-24 h-24 rounded-full bg-blue-100 flex items-center justify-center text-3xl font-bold text-blue-600">
                    {user.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <Button variant="outline" className="flex items-center gap-2">
                      <Camera className="h-4 w-4" />
                      Upload Photo
                    </Button>
                    <p className="text-xs text-gray-500 mt-2">JPG, PNG or GIF. Max 2MB.</p>
                  </div>
                </div>

                {/* Form Fields */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                    <input
                      type="text"
                      value={user.name}
                      onChange={(e) => setUser({ ...user, name: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                    <input
                      type="email"
                      value={user.email}
                      onChange={(e) => setUser({ ...user, email: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Change Password</label>
                    <div className="relative">
                      <input
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Enter new password"
                        className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                      <button
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                      >
                        {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                      </button>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Leave blank to keep current password</p>
                  </div>

                  <Button className="mt-4">Save Changes</Button>
                </div>
              </div>
            </div>
          )}

          {/* Subscription Tab */}
          {activeTab === 'subscription' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Current Plan</h2>
                <div className="flex items-center gap-3 mb-6">
                  <span className="text-3xl font-bold text-blue-600 capitalize">{user.subscription_tier}</span>
                  {user.subscription_tier !== 'free' && (
                    <Crown className="h-8 w-8 text-yellow-500" />
                  )}
                </div>

                {/* Usage Stats */}
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Reports This Month</span>
                    <span className="text-sm font-bold text-gray-900">{user.usage_this_month} / {user.usage_limit}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${(user.usage_this_month / user.usage_limit) * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-4">Available Plans</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {plans.map((plan) => (
                    <div
                      key={plan.tier}
                      className={`border-2 rounded-lg p-6 ${
                        user.subscription_tier === plan.tier
                          ? 'border-blue-600 bg-blue-50'
                          : 'border-gray-200 bg-white'
                      }`}
                    >
                      <div className="mb-4">
                        <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
                        <div className="mt-2">
                          <span className="text-3xl font-bold text-gray-900">₹{plan.price}</span>
                          <span className="text-gray-600">/month</span>
                        </div>
                      </div>

                      <ul className="space-y-2 mb-6">
                        {plan.features.map((feature, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-sm">
                            <Check className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                            <span className="text-gray-700">{feature}</span>
                          </li>
                        ))}
                      </ul>

                      {user.subscription_tier === plan.tier ? (
                        <Button className="w-full" disabled>
                          Current Plan
                        </Button>
                      ) : (
                        <Button
                          className="w-full"
                          variant={plan.tier === 'free' ? 'outline' : 'default'}
                        >
                          {plans.findIndex(p => p.tier === user.subscription_tier) < plans.findIndex(p => p.tier === plan.tier)
                            ? 'Upgrade'
                            : 'Downgrade'}
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-4">Notification Preferences</h2>
                <p className="text-gray-600 mb-6">
                  Choose how you want to receive updates and alerts
                </p>

                <div className="space-y-4">
                  {/* Email Alerts */}
                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Mail className="h-5 w-5 text-gray-600" />
                      <div>
                        <div className="font-semibold text-gray-900">Email Alerts</div>
                        <div className="text-sm text-gray-600">Receive watchlist alerts via email</div>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={user.notification_prefs.email_alerts}
                        onChange={(e) =>
                          setUser({
                            ...user,
                            notification_prefs: { ...user.notification_prefs, email_alerts: e.target.checked },
                          })
                        }
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  {/* Weekly Digest */}
                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Bell className="h-5 w-5 text-gray-600" />
                      <div>
                        <div className="font-semibold text-gray-900">Weekly Digest</div>
                        <div className="text-sm text-gray-600">Summary of all watchlist changes</div>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={user.notification_prefs.weekly_digest}
                        onChange={(e) =>
                          setUser({
                            ...user,
                            notification_prefs: { ...user.notification_prefs, weekly_digest: e.target.checked },
                          })
                        }
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  {/* Push Notifications */}
                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Smartphone className="h-5 w-5 text-gray-600" />
                      <div>
                        <div className="font-semibold text-gray-900 flex items-center gap-2">
                          Push Notifications
                          {user.subscription_tier !== 'premium' && (
                            <Crown className="h-4 w-4 text-yellow-500" />
                          )}
                        </div>
                        <div className="text-sm text-gray-600">
                          {user.subscription_tier === 'premium'
                            ? 'Real-time browser notifications'
                            : 'Available on Premium plan'}
                        </div>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={user.notification_prefs.push_notifications}
                        onChange={(e) =>
                          setUser({
                            ...user,
                            notification_prefs: { ...user.notification_prefs, push_notifications: e.target.checked },
                          })
                        }
                        disabled={user.subscription_tier !== 'premium'}
                        className="sr-only peer"
                      />
                      <div className={`w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600 ${
                        user.subscription_tier !== 'premium' ? 'opacity-50 cursor-not-allowed' : ''
                      }`}></div>
                    </label>
                  </div>

                  {/* Feature Announcements */}
                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Bell className="h-5 w-5 text-gray-600" />
                      <div>
                        <div className="font-semibold text-gray-900">Feature Announcements</div>
                        <div className="text-sm text-gray-600">New features and product updates</div>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={user.notification_prefs.feature_announcements}
                        onChange={(e) =>
                          setUser({
                            ...user,
                            notification_prefs: { ...user.notification_prefs, feature_announcements: e.target.checked },
                          })
                        }
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>

                <Button className="mt-6">Save Preferences</Button>
              </div>
            </div>
          )}

          {/* Privacy Tab */}
          {activeTab === 'privacy' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-4">Data & Privacy</h2>
                <p className="text-gray-600 mb-6">
                  Manage your data and privacy settings
                </p>

                <div className="space-y-4">
                  {/* Download Data */}
                  <div className="border border-gray-200 rounded-lg p-6">
                    <div className="flex items-start gap-4">
                      <Download className="h-6 w-6 text-blue-600 mt-1" />
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 mb-2">Download Your Data</h3>
                        <p className="text-sm text-gray-600 mb-4">
                          Export all your analysis reports, watchlist, and preferences as a ZIP file
                        </p>
                        <Button variant="outline">Request Data Export</Button>
                      </div>
                    </div>
                  </div>

                  {/* Delete History */}
                  <div className="border border-gray-200 rounded-lg p-6">
                    <div className="flex items-start gap-4">
                      <Trash2 className="h-6 w-6 text-orange-600 mt-1" />
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 mb-2">Delete Analysis History</h3>
                        <p className="text-sm text-gray-600 mb-4">
                          Permanently delete all your past analysis reports. This action cannot be undone.
                        </p>
                        <Button variant="outline" className="border-orange-600 text-orange-600 hover:bg-orange-50">
                          Delete History
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Danger Zone */}
                  <div className="border-2 border-red-200 bg-red-50 rounded-lg p-6">
                    <div className="flex items-start gap-4">
                      <Trash2 className="h-6 w-6 text-red-600 mt-1" />
                      <div className="flex-1">
                        <h3 className="font-semibold text-red-900 mb-2">Delete Account</h3>
                        <p className="text-sm text-red-800 mb-4">
                          Permanently delete your account and all associated data. This action cannot be undone and will immediately cancel your subscription.
                        </p>
                        <Button className="bg-red-600 hover:bg-red-700">
                          Delete Account
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
