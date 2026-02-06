"""Category 6: Balance Sheet Red Flags (7 flags, 10% weight).

Balance sheet quality is fundamental to financial health. Red flags include
excessive debt, poor coverage ratios, contingent liabilities, and asset quality issues.
"""

import logging
from typing import Dict

from app.models.red_flag import FlagCategory, FlagSeverity
from app.red_flags.base import RedFlagBase, RedFlagResult
from app.red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class DebtGrowingFasterFlag(RedFlagBase):
    """Flag #37: Debt Growing Faster than Equity (HIGH)."""

    def __init__(self):
        self.flag_number = 37
        self.flag_name = "Debt Growing > Equity"
        self.category = FlagCategory.BALANCE_SHEET
        self.severity = FlagSeverity.HIGH
        self.description = "Debt growth significantly exceeds equity growth"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if debt is growing faster than equity."""
        financial_data = data.get("financial_data", {})
        balance_sheet = financial_data.get("balance_sheet", {})

        # Extract current and previous year values
        debt_current = self.extract_value(balance_sheet, "total_debt", "value", default=0.0)
        debt_previous = self.extract_value(balance_sheet, "total_debt", "previous_year", default=0.0)

        equity_current = self.extract_value(balance_sheet, "shareholders_equity", "value", default=0.0)
        equity_previous = self.extract_value(balance_sheet, "shareholders_equity", "previous_year", default=0.0)

        if not all([debt_current, debt_previous, equity_current, equity_previous]):
            return self.create_not_triggered_result("Insufficient debt/equity data")

        # Calculate growth rates
        debt_growth = self.calculate_growth_rate(debt_current, debt_previous)
        equity_growth = self.calculate_growth_rate(equity_current, equity_previous)

        # Calculate current D/E ratio
        debt_equity_ratio = self.calculate_ratio(debt_current, equity_current)

        # Trigger if debt growth > equity growth + 20%
        growth_divergence = debt_growth > equity_growth + 0.20

        if growth_divergence:
            evidence = (
                f"Debt grew {self.safe_percentage(debt_growth):.1f}% while equity grew only {self.safe_percentage(equity_growth):.1f}% "
                f"(divergence: {self.safe_percentage(debt_growth - equity_growth):.1f}%). "
                f"Current Debt/Equity ratio: {debt_equity_ratio:.2f}. "
                f"Excessive debt growth increases financial risk."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=85.0,
                extracted_data={
                    "debt_growth": debt_growth,
                    "equity_growth": equity_growth,
                    "debt_equity_ratio": debt_equity_ratio,
                    "debt_current": debt_current,
                    "equity_current": equity_current,
                },
            )

        return self.create_not_triggered_result("Debt growth aligned with equity")


class InterestCoverageLowFlag(RedFlagBase):
    """Flag #38: Interest Coverage Ratio < 2x (HIGH)."""

    def __init__(self):
        self.flag_number = 38
        self.flag_name = "Interest Coverage < 2x"
        self.category = FlagCategory.BALANCE_SHEET
        self.severity = FlagSeverity.HIGH
        self.description = "Company cannot comfortably service debt (interest coverage < 2x)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check interest coverage ratio."""
        financial_data = data.get("financial_data", {})
        profit_loss = financial_data.get("profit_loss", {})

        # Extract EBIT and interest expense
        ebit = self.extract_value(profit_loss, "ebit", "value", default=0.0)
        interest_expense = self.extract_value(profit_loss, "interest_expense", "value", default=0.0)

        # If EBIT not available, try calculating from PAT
        if ebit == 0:
            pat = self.extract_value(profit_loss, "net_profit", "value", default=0.0)
            tax = self.extract_value(profit_loss, "tax_expense", "value", default=0.0)
            ebit = pat + tax + interest_expense

        if not interest_expense or interest_expense == 0:
            return self.create_not_triggered_result("Interest expense data not available or company has no debt")

        if ebit <= 0:
            # Negative EBIT means cannot cover interest at all
            return self.create_triggered_result(
                evidence=f"EBIT is negative ({ebit:,.0f}) while interest expense is {interest_expense:,.0f}. Company cannot service debt from operations.",
                confidence=100.0,
                extracted_data={
                    "ebit": ebit,
                    "interest_expense": interest_expense,
                    "interest_coverage": 0.0,
                },
            )

        # Calculate interest coverage ratio
        interest_coverage = self.calculate_ratio(ebit, interest_expense)

        # Trigger if coverage < 2x
        if interest_coverage < 2.0:
            evidence = (
                f"Interest Coverage Ratio is {interest_coverage:.2f}x "
                f"(EBIT: {ebit:,.0f}, Interest: {interest_expense:,.0f}). "
                f"Coverage below 2x indicates difficulty servicing debt."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=90.0,
                extracted_data={
                    "interest_coverage": interest_coverage,
                    "ebit": ebit,
                    "interest_expense": interest_expense,
                },
            )

        return self.create_not_triggered_result("Interest coverage is adequate")


class ShortTermDebtHighFlag(RedFlagBase):
    """Flag #39: Short-term Debt Funding Long-term Assets (HIGH)."""

    def __init__(self):
        self.flag_number = 39
        self.flag_name = "ST Debt Funding LT Assets"
        self.category = FlagCategory.BALANCE_SHEET
        self.severity = FlagSeverity.HIGH
        self.description = "Short-term debt comprises >60% of total debt (maturity mismatch risk)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if excessive reliance on short-term debt."""
        financial_data = data.get("financial_data", {})
        balance_sheet = financial_data.get("balance_sheet", {})

        # Extract short-term and total debt
        short_term_debt = self.extract_value(balance_sheet, "current_liabilities", "short_term_borrowings", "value", default=0.0)
        long_term_debt = self.extract_value(balance_sheet, "non_current_liabilities", "long_term_borrowings", "value", default=0.0)

        total_debt = short_term_debt + long_term_debt

        if total_debt == 0:
            return self.create_not_triggered_result("Company has minimal debt")

        # Calculate short-term debt percentage
        st_debt_percentage = (short_term_debt / total_debt) * 100

        # Trigger if ST debt > 60% of total debt
        if st_debt_percentage > 60:
            evidence = (
                f"Short-term debt is {st_debt_percentage:.1f}% of total debt "
                f"(ST Debt: {short_term_debt:,.0f}, Total Debt: {total_debt:,.0f}). "
                f"High reliance on short-term debt creates refinancing risk and maturity mismatch."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=85.0,
                extracted_data={
                    "st_debt_percentage": st_debt_percentage,
                    "short_term_debt": short_term_debt,
                    "long_term_debt": long_term_debt,
                    "total_debt": total_debt,
                },
            )

        return self.create_not_triggered_result("Debt maturity profile is balanced")


class ContingentLiabilitiesHighFlag(RedFlagBase):
    """Flag #40: Contingent Liabilities > 20% of Net Worth (HIGH)."""

    def __init__(self):
        self.flag_number = 40
        self.flag_name = "Contingent Liabilities > 20% NW"
        self.category = FlagCategory.BALANCE_SHEET
        self.severity = FlagSeverity.HIGH
        self.description = "Contingent liabilities are high relative to net worth (hidden risk)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for excessive contingent liabilities."""
        financial_data = data.get("financial_data", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")

        # Extract from structured data
        notes_data = financial_data.get("notes", {})
        contingent_liabilities = self.extract_value(notes_data, "contingent_liabilities", "value", default=0.0)

        # Extract net worth (shareholders equity)
        balance_sheet = financial_data.get("balance_sheet", {})
        net_worth = self.extract_value(balance_sheet, "shareholders_equity", "value", default=0.0)

        # If no structured data, try to extract from notes text
        if contingent_liabilities == 0 and notes_text:
            import re

            # Look for contingent liabilities section
            notes_lower = notes_text.lower()
            if "contingent liabilit" in notes_lower:
                # Try to extract amount
                pattern = r'contingent.*?(?:rs|inr|₹)\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)'
                matches = re.findall(pattern, notes_lower)
                if matches:
                    try:
                        amounts = [float(m.replace(',', '')) for m in matches]
                        contingent_liabilities = max(amounts)
                    except:
                        pass

        if not net_worth or net_worth == 0:
            return self.create_not_triggered_result("Net worth data not available")

        if contingent_liabilities == 0:
            return self.create_not_triggered_result("No significant contingent liabilities")

        # Calculate as percentage of net worth
        contingent_pct = (contingent_liabilities / abs(net_worth)) * 100

        # Trigger if > 20% of net worth
        if contingent_pct > 20:
            evidence = (
                f"Contingent liabilities are {contingent_pct:.1f}% of net worth "
                f"(Contingent: {contingent_liabilities:,.0f}, Net Worth: {net_worth:,.0f}). "
                f"High contingent liabilities represent significant off-balance-sheet risk."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=80.0,
                extracted_data={
                    "contingent_liabilities": contingent_liabilities,
                    "net_worth": net_worth,
                    "contingent_pct": contingent_pct,
                },
            )

        return self.create_not_triggered_result("Contingent liabilities within acceptable range")


class FrequentDebtRestructuringFlag(RedFlagBase):
    """Flag #41: Frequent Debt Restructuring (MEDIUM)."""

    def __init__(self):
        self.flag_number = 41
        self.flag_name = "Frequent Debt Restructuring"
        self.category = FlagCategory.BALANCE_SHEET
        self.severity = FlagSeverity.MEDIUM
        self.description = "Company has undergone debt restructuring (financial stress indicator)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for debt restructuring mentions."""
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        directors_report = data.get("sections", {}).get("directors_report", "")

        # Search for restructuring keywords
        restructuring_keywords = [
            "debt restructur",
            "loan restructur",
            "restructuring of debt",
            "restructuring of loan",
            "debt renegotiat",
            "loan renegotiat",
            "refinanc",
            "debt repayment rescheduled",
            "restructuring scheme",
            "corporate debt restructuring",
            "cdr",
        ]

        combined_text = (notes_text + " " + directors_report).lower()
        restructuring_mentions = []

        for keyword in restructuring_keywords:
            if keyword in combined_text:
                restructuring_mentions.append(keyword)

        # Trigger if restructuring mentioned
        if restructuring_mentions:
            evidence = (
                f"Debt restructuring detected in disclosures "
                f"({len(restructuring_mentions)} references: {', '.join(set(restructuring_mentions[:3]))}). "
                f"Debt restructuring indicates financial stress and inability to service original terms."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=85.0,
                extracted_data={
                    "restructuring_mentions": restructuring_mentions,
                },
            )

        return self.create_not_triggered_result("No debt restructuring detected")


class HeavyAssetPledgingFlag(RedFlagBase):
    """Flag #42: Heavy Asset Pledging (MEDIUM)."""

    def __init__(self):
        self.flag_number = 42
        self.flag_name = "Heavy Asset Pledging"
        self.category = FlagCategory.BALANCE_SHEET
        self.severity = FlagSeverity.MEDIUM
        self.description = "More than 50% of assets are pledged to lenders"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for heavy asset pledging."""
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        financial_data = data.get("financial_data", {})

        # Check structured data
        notes_data = financial_data.get("notes", {})
        pledged_assets = self.extract_value(notes_data, "assets_pledged", "value", default=0.0)

        # Get total assets
        balance_sheet = financial_data.get("balance_sheet", {})
        total_assets = self.extract_value(balance_sheet, "total_assets", "value", default=0.0)

        # Text search for pledging mentions
        pledge_keywords = [
            "asset pledged",
            "assets pledged",
            "charge created",
            "hypothecated",
            "mortgaged",
            "security for borrowing",
            "secured by",
        ]

        notes_lower = notes_text.lower()
        pledge_mentions = sum(1 for keyword in pledge_keywords if keyword in notes_lower)

        # Try to extract pledged percentage from text
        import re

        pledge_pct = 0
        if pledged_assets > 0 and total_assets > 0:
            pledge_pct = (pledged_assets / total_assets) * 100
        else:
            # Try to extract percentage from text
            pattern = r'(\d+(?:\.\d+)?)\s*%.*?(?:asset|charge|pledged)'
            matches = re.findall(pattern, notes_lower)
            if matches:
                try:
                    percentages = [float(m) for m in matches if 0 < float(m) <= 100]
                    if percentages:
                        pledge_pct = max(percentages)
                except:
                    pass

        # Trigger if pledge > 50% or multiple pledge mentions
        significant_pledging = pledge_pct > 50
        extensive_mentions = pledge_mentions >= 5

        if significant_pledging or extensive_mentions:
            evidence_parts = []

            if significant_pledging:
                evidence_parts.append(
                    f"Assets pledged: {pledge_pct:.1f}% of total assets"
                )

            if extensive_mentions:
                evidence_parts.append(
                    f"Extensive asset pledging disclosures ({pledge_mentions} references)"
                )

            evidence = ". ".join(evidence_parts) + ". Heavy asset pledging reduces financial flexibility and increases default risk."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=75.0,
                extracted_data={
                    "pledged_assets": pledged_assets,
                    "total_assets": total_assets,
                    "pledge_pct": pledge_pct,
                    "pledge_mentions": pledge_mentions,
                },
            )

        return self.create_not_triggered_result("Asset pledging within normal range")


class IntangiblesGrowingFastFlag(RedFlagBase):
    """Flag #43: Intangible Assets Growing Fast (MEDIUM)."""

    def __init__(self):
        self.flag_number = 43
        self.flag_name = "Intangibles Growing Fast"
        self.category = FlagCategory.BALANCE_SHEET
        self.severity = FlagSeverity.MEDIUM
        self.description = "Intangible assets growing >30% YoY (potential asset inflation)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for rapid growth in intangible assets."""
        financial_data = data.get("financial_data", {})
        balance_sheet = financial_data.get("balance_sheet", {})

        # Extract intangible assets
        intangibles_current = self.extract_value(balance_sheet, "non_current_assets", "intangible_assets", "value", default=0.0)
        intangibles_previous = self.extract_value(balance_sheet, "non_current_assets", "intangible_assets", "previous_year", default=0.0)

        if not intangibles_current or intangibles_current == 0:
            return self.create_not_triggered_result("No significant intangible assets")

        if not intangibles_previous or intangibles_previous == 0:
            return self.create_not_triggered_result("Cannot calculate growth (previous year data missing)")

        # Calculate growth rate
        intangibles_growth = self.calculate_growth_rate(intangibles_current, intangibles_previous)

        # Also check intangibles as % of total assets
        total_assets = self.extract_value(balance_sheet, "total_assets", "value", default=0.0)
        intangibles_pct = (intangibles_current / total_assets) * 100 if total_assets else 0

        # Trigger if growth > 30% YoY
        rapid_growth = intangibles_growth > 0.30
        high_percentage = intangibles_pct > 20  # Also flag if > 20% of total assets

        if rapid_growth or high_percentage:
            evidence_parts = []

            if rapid_growth:
                evidence_parts.append(
                    f"Intangible assets grew {self.safe_percentage(intangibles_growth):.1f}% "
                    f"(from {intangibles_previous:,.0f} to {intangibles_current:,.0f})"
                )

            if high_percentage:
                evidence_parts.append(
                    f"Intangibles are {intangibles_pct:.1f}% of total assets"
                )

            evidence = ". ".join(evidence_parts) + ". Rapid intangible asset growth may indicate aggressive capitalization or goodwill from acquisitions."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=70.0,
                extracted_data={
                    "intangibles_growth": intangibles_growth,
                    "intangibles_current": intangibles_current,
                    "intangibles_previous": intangibles_previous,
                    "intangibles_pct": intangibles_pct,
                },
            )

        return self.create_not_triggered_result("Intangible asset growth is normal")


# Register all balance sheet flags
flag_registry.register(DebtGrowingFasterFlag())
flag_registry.register(InterestCoverageLowFlag())
flag_registry.register(ShortTermDebtHighFlag())
flag_registry.register(ContingentLiabilitiesHighFlag())
flag_registry.register(FrequentDebtRestructuringFlag())
flag_registry.register(HeavyAssetPledgingFlag())
flag_registry.register(IntangiblesGrowingFastFlag())

logger.info("Registered 7 balance sheet flags (Category 6)")
