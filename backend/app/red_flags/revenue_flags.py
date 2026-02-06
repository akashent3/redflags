"""Category 7: Revenue Quality Red Flags (5 flags, 5% weight).

Revenue quality is critical for assessing earnings sustainability. Red flags include
Q4 concentration, customer concentration, policy changes, and unusual patterns.
"""

import logging
from typing import Dict

from app.models.red_flag import FlagCategory, FlagSeverity
from app.red_flags.base import RedFlagBase, RedFlagResult
from app.red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class Q4RevenueConcentrationFlag(RedFlagBase):
    """Flag #44: Revenue Concentrated in Q4 (MEDIUM)."""

    def __init__(self):
        self.flag_number = 44
        self.flag_name = "Revenue Concentrated in Q4"
        self.category = FlagCategory.REVENUE
        self.severity = FlagSeverity.MEDIUM
        self.description = "More than 40% of annual revenue from Q4 (potential channel stuffing)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if revenue is disproportionately concentrated in Q4."""
        financial_data = data.get("financial_data", {})

        # Check for quarterly revenue data
        quarterly_revenue = financial_data.get("quarterly_revenue", {})

        q4_revenue = self.extract_value(quarterly_revenue, "q4", "value", default=0.0)
        annual_revenue = self.extract_value(financial_data, "profit_loss", "revenue", "value", default=0.0)

        # Also try to get Q1, Q2, Q3 to verify
        q1_revenue = self.extract_value(quarterly_revenue, "q1", "value", default=0.0)
        q2_revenue = self.extract_value(quarterly_revenue, "q2", "value", default=0.0)
        q3_revenue = self.extract_value(quarterly_revenue, "q3", "value", default=0.0)

        # If quarterly data available, sum it up
        if all([q1_revenue, q2_revenue, q3_revenue, q4_revenue]):
            annual_from_quarters = q1_revenue + q2_revenue + q3_revenue + q4_revenue
            # Use this if more accurate than annual figure
            if abs(annual_from_quarters - annual_revenue) / annual_revenue < 0.05:  # Within 5%
                annual_revenue = annual_from_quarters

        if not annual_revenue or annual_revenue == 0:
            return self.create_not_triggered_result("Annual revenue data not available")

        if not q4_revenue or q4_revenue == 0:
            return self.create_not_triggered_result("Q4 revenue data not available")

        # Calculate Q4 percentage
        q4_percentage = (q4_revenue / annual_revenue) * 100

        # Trigger if Q4 > 40% of annual
        if q4_percentage > 40:
            evidence = (
                f"Q4 revenue is {q4_percentage:.1f}% of annual revenue "
                f"(Q4: {q4_revenue:,.0f}, Annual: {annual_revenue:,.0f}). "
            )

            # Add quarterly breakdown if available
            if all([q1_revenue, q2_revenue, q3_revenue]):
                evidence += (
                    f"Quarterly split: Q1={q1_revenue:,.0f}, Q2={q2_revenue:,.0f}, "
                    f"Q3={q3_revenue:,.0f}, Q4={q4_revenue:,.0f}. "
                )

            evidence += "High Q4 concentration may indicate channel stuffing or aggressive revenue recognition."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=75.0,
                extracted_data={
                    "q4_percentage": q4_percentage,
                    "q4_revenue": q4_revenue,
                    "annual_revenue": annual_revenue,
                    "q1_revenue": q1_revenue,
                    "q2_revenue": q2_revenue,
                    "q3_revenue": q3_revenue,
                },
            )

        return self.create_not_triggered_result("Revenue distribution across quarters is balanced")


class CustomerConcentrationFlag(RedFlagBase):
    """Flag #45: Top Customer Concentration > 25% (MEDIUM)."""

    def __init__(self):
        self.flag_number = 45
        self.flag_name = "Top Customer > 25%"
        self.category = FlagCategory.REVENUE
        self.severity = FlagSeverity.MEDIUM
        self.description = "Single customer accounts for >25% of revenue (dependency risk)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for customer concentration risk."""
        financial_data = data.get("financial_data", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")

        # Check structured data for customer concentration
        notes_data = financial_data.get("notes", {})
        top_customer_pct = self.extract_value(notes_data, "top_customer_percentage", default=0.0)

        # If no structured data, search notes text
        if top_customer_pct == 0 and notes_text:
            import re

            notes_lower = notes_text.lower()

            # Search for customer concentration disclosures
            concentration_keywords = [
                "top customer",
                "largest customer",
                "single customer",
                "customer concentration",
            ]

            has_concentration_mention = any(keyword in notes_lower for keyword in concentration_keywords)

            if has_concentration_mention:
                # Try to extract percentage
                pattern = r'(?:customer|single).*?(\d+(?:\.\d+)?)\s*%'
                matches = re.findall(pattern, notes_lower)
                if matches:
                    try:
                        percentages = [float(m) for m in matches if 0 < float(m) <= 100]
                        if percentages:
                            top_customer_pct = max(percentages)
                    except:
                        pass

        # Trigger if top customer > 25%
        if top_customer_pct > 25:
            evidence = (
                f"Top customer accounts for {top_customer_pct:.1f}% of revenue. "
                f"High customer concentration creates significant business risk if relationship is lost."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=80.0,
                extracted_data={
                    "top_customer_pct": top_customer_pct,
                },
            )

        return self.create_not_triggered_result("No significant customer concentration")


class RevenuePolicyChangeFlag(RedFlagBase):
    """Flag #46: Revenue Recognition Policy Changed (HIGH)."""

    def __init__(self):
        self.flag_number = 46
        self.flag_name = "Revenue Policy Change"
        self.category = FlagCategory.REVENUE
        self.severity = FlagSeverity.HIGH
        self.description = "Company changed revenue recognition policy during the year"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for revenue recognition policy changes."""
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        accounting_policies = data.get("sections", {}).get("accounting_policies", "")

        # Search for policy change keywords
        policy_change_keywords = [
            "change in revenue recognition",
            "revenue recognition policy changed",
            "revised revenue recognition",
            "adopted new revenue standard",
            "change in accounting policy",
            "ind as 115",  # Indian accounting standard for revenue
            "ifrs 15",  # International standard
            "revenue from contracts with customers",
        ]

        combined_text = (notes_text + " " + accounting_policies).lower()
        policy_change_mentions = []

        for keyword in policy_change_keywords:
            if keyword in combined_text:
                policy_change_mentions.append(keyword)

        # Look for "change" near "revenue" within 50 characters
        import re

        pattern = r'change.{0,50}revenue.{0,50}recogni|revenue.{0,50}recogni.{0,50}change'
        contextual_match = re.search(pattern, combined_text)

        # Trigger if policy change mentioned
        if policy_change_mentions or contextual_match:
            # Try to extract reason for change
            reason = "Not specified"
            if "ind as" in combined_text or "ifrs" in combined_text:
                reason = "Adoption of new accounting standard"

            evidence = (
                f"Revenue recognition policy change detected "
                f"({len(policy_change_mentions)} references). "
                f"Reason: {reason}. "
                f"Policy changes can distort year-over-year comparisons and may be used to manage earnings."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=90.0,
                extracted_data={
                    "policy_change_mentions": policy_change_mentions,
                    "reason": reason,
                },
            )

        return self.create_not_triggered_result("No revenue recognition policy changes")


class UnbilledRevenueGrowingFlag(RedFlagBase):
    """Flag #47: Unbilled Revenue Growing Faster (MEDIUM)."""

    def __init__(self):
        self.flag_number = 47
        self.flag_name = "Unbilled Revenue Growing"
        self.category = FlagCategory.REVENUE
        self.severity = FlagSeverity.MEDIUM
        self.description = "Unbilled revenue growing faster than billed revenue (quality concern)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if unbilled revenue is growing disproportionately."""
        financial_data = data.get("financial_data", {})
        balance_sheet = financial_data.get("balance_sheet", {})
        profit_loss = financial_data.get("profit_loss", {})

        # Extract unbilled revenue (contract assets)
        unbilled_current = self.extract_value(balance_sheet, "current_assets", "unbilled_revenue", "value", default=0.0)
        unbilled_previous = self.extract_value(balance_sheet, "current_assets", "unbilled_revenue", "previous_year", default=0.0)

        # Alternative: Check contract assets
        if unbilled_current == 0:
            unbilled_current = self.extract_value(balance_sheet, "current_assets", "contract_assets", "value", default=0.0)
            unbilled_previous = self.extract_value(balance_sheet, "current_assets", "contract_assets", "previous_year", default=0.0)

        # Get revenue for comparison
        revenue_current = self.extract_value(profit_loss, "revenue", "value", default=0.0)
        revenue_previous = self.extract_value(profit_loss, "revenue", "previous_year", default=0.0)

        if not all([unbilled_current, unbilled_previous, revenue_current, revenue_previous]):
            return self.create_not_triggered_result("Insufficient unbilled revenue data")

        # Calculate growth rates
        unbilled_growth = self.calculate_growth_rate(unbilled_current, unbilled_previous)
        revenue_growth = self.calculate_growth_rate(revenue_current, revenue_previous)

        # Calculate unbilled as % of revenue
        unbilled_pct_current = (unbilled_current / revenue_current) * 100
        unbilled_pct_previous = (unbilled_previous / revenue_previous) * 100

        # Trigger if unbilled growing > revenue + 15%
        growth_divergence = unbilled_growth > revenue_growth + 0.15
        increasing_pct = unbilled_pct_current > unbilled_pct_previous + 5  # Increased by 5 percentage points

        if growth_divergence or increasing_pct:
            evidence_parts = []

            if growth_divergence:
                evidence_parts.append(
                    f"Unbilled revenue grew {self.safe_percentage(unbilled_growth):.1f}% "
                    f"while billed revenue grew {self.safe_percentage(revenue_growth):.1f}% "
                    f"(divergence: {self.safe_percentage(unbilled_growth - revenue_growth):.1f}%)"
                )

            if increasing_pct:
                evidence_parts.append(
                    f"Unbilled revenue as % of total revenue increased from {unbilled_pct_previous:.1f}% to {unbilled_pct_current:.1f}%"
                )

            evidence = ". ".join(evidence_parts) + ". Growing unbilled revenue may indicate aggressive revenue recognition or collection issues."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=75.0,
                extracted_data={
                    "unbilled_growth": unbilled_growth,
                    "revenue_growth": revenue_growth,
                    "unbilled_pct_current": unbilled_pct_current,
                    "unbilled_pct_previous": unbilled_pct_previous,
                },
            )

        return self.create_not_triggered_result("Unbilled revenue growth is normal")


class UnusualExportGeographyFlag(RedFlagBase):
    """Flag #48: Unusual Export Geography (LOW)."""

    def __init__(self):
        self.flag_number = 48
        self.flag_name = "Unusual Export Geography"
        self.category = FlagCategory.REVENUE
        self.severity = FlagSeverity.LOW
        self.description = "Significant exports to tax havens or unusual jurisdictions"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for exports to suspicious jurisdictions."""
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        financial_data = data.get("financial_data", {})

        # List of tax havens and unusual jurisdictions
        suspicious_jurisdictions = [
            "cayman",
            "bermuda",
            "british virgin islands",
            "bvi",
            "mauritius",
            "seychelles",
            "bahamas",
            "panama",
            "luxembourg",
            "jersey",
            "guernsey",
            "isle of man",
            "monaco",
            "liechtenstein",
        ]

        notes_lower = notes_text.lower()

        # Check for geographic revenue breakdown
        has_geographic_section = any(
            keyword in notes_lower
            for keyword in ["geographic", "geographical", "segment", "export"]
        )

        if not has_geographic_section:
            return self.create_not_triggered_result("Geographic revenue breakdown not found")

        # Search for suspicious jurisdictions
        found_jurisdictions = []
        for jurisdiction in suspicious_jurisdictions:
            if jurisdiction in notes_lower:
                found_jurisdictions.append(jurisdiction)

        # Try to extract export percentage
        import re

        export_pct = 0
        pattern = r'export.*?(\d+(?:\.\d+)?)\s*%'
        matches = re.findall(pattern, notes_lower)
        if matches:
            try:
                percentages = [float(m) for m in matches if 0 < float(m) <= 100]
                if percentages:
                    export_pct = max(percentages)
            except:
                pass

        # Trigger if suspicious jurisdictions found
        if found_jurisdictions:
            evidence = (
                f"Exports to tax haven jurisdictions detected: {', '.join(set(found_jurisdictions))}. "
            )

            if export_pct > 0:
                evidence += f"Total export revenue: {export_pct:.1f}%. "

            evidence += "Trade with tax havens may indicate transfer pricing schemes or revenue manipulation."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=60.0,  # Lower confidence as not always problematic
                extracted_data={
                    "found_jurisdictions": found_jurisdictions,
                    "export_pct": export_pct,
                },
            )

        return self.create_not_triggered_result("No unusual export geographies detected")


# Register all revenue quality flags
flag_registry.register(Q4RevenueConcentrationFlag())
flag_registry.register(CustomerConcentrationFlag())
flag_registry.register(RevenuePolicyChangeFlag())
flag_registry.register(UnbilledRevenueGrowingFlag())
flag_registry.register(UnusualExportGeographyFlag())

logger.info("Registered 5 revenue quality flags (Category 7)")
