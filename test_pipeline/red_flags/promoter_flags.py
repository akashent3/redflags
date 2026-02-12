"""Category 4: Promoter Red Flags (6 flags, 15% weight)."""

import re
import logging
from typing import Dict

from red_flags.models import FlagCategory, FlagSeverity
from red_flags.base import RedFlagBase
from red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class PromoterPledgeHighFlag(RedFlagBase):
    """Flag #24: Promoter Pledge > 50% (CRITICAL)."""
    def __init__(self):
        self.flag_number = 24
        self.flag_name = "Promoter Pledge > 50%"
        self.category = FlagCategory.PROMOTER
        self.severity = FlagSeverity.CRITICAL

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        sh = fd.get("shareholding_pattern", {})
        pledge_pct = self.extract_value(sh, "promoter_pledge_percentage", default=0.0)
        if pledge_pct == 0.0:
            governance_text = data.get("sections", {}).get("corporate_governance", "")
            notes_text = data.get("sections", {}).get("notes_to_accounts", "")
            combined = (governance_text + " " + notes_text).lower()
            for pattern in [r'pledged\s+(\d+(?:\.\d+)?)\s*%', r'pledge.*?(\d+(?:\.\d+)?)\s*%', r'(\d+(?:\.\d+)?)\s*%.*?pledged']:
                matches = re.findall(pattern, combined)
                if matches:
                    try:
                        pledge_pct = max(float(m) for m in matches)
                        break
                    except (ValueError, TypeError):
                        pass
        if pledge_pct > 50:
            return self.create_triggered_result(evidence=f"Promoter has pledged {pledge_pct:.1f}% of shareholding. High pledge indicates financial stress and margin call risk.", confidence=95.0, extracted_data={"promoter_pledge_pct": pledge_pct})
        return self.create_not_triggered_result("Promoter pledge within acceptable limits")


class PledgeIncreasingFlag(RedFlagBase):
    """Flag #25: Promoter Pledge Increasing (HIGH)."""
    def __init__(self):
        self.flag_number = 25
        self.flag_name = "Pledge Increasing QoQ"
        self.category = FlagCategory.PROMOTER
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        sh = fd.get("shareholding_pattern", {})
        curr = self.extract_value(sh, "promoter_pledge_percentage", default=0.0)
        prev = self.extract_value(sh, "promoter_pledge_percentage_previous", default=0.0)
        if curr == 0.0 and prev == 0.0:
            return self.create_not_triggered_result("Promoter pledge data not available")
        increase = curr - prev
        if increase > 5:
            return self.create_triggered_result(evidence=f"Promoter pledge increased from {prev:.1f}% to {curr:.1f}% (+{increase:.1f}pp). Worsening financial stress.", confidence=90.0, extracted_data={"pledge_current": curr, "pledge_previous": prev, "pledge_increase": increase})
        return self.create_not_triggered_result("Promoter pledge stable or decreasing")


class PromoterSellingSharesFlag(RedFlagBase):
    """Flag #26: Promoter Selling Shares (MEDIUM)."""
    def __init__(self):
        self.flag_number = 26
        self.flag_name = "Promoter Selling Shares"
        self.category = FlagCategory.PROMOTER
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        sh = fd.get("shareholding_pattern", {})
        curr = self.extract_value(sh, "promoter_holding_percentage", default=0.0)
        prev = self.extract_value(sh, "promoter_holding_percentage_previous", default=0.0)
        if curr == 0.0 and prev == 0.0:
            return self.create_not_triggered_result("Promoter holding data not available")
        decrease = prev - curr
        governance_text = data.get("sections", {}).get("corporate_governance", "").lower()
        selling_keywords = ["promoter sale", "promoter sold", "reduction in promoter holding", "divestment by promoter", "offloaded stake"]
        selling_mentions = sum(1 for kw in selling_keywords if kw in governance_text)
        if decrease > 2 or selling_mentions > 0:
            parts = []
            if decrease > 2:
                parts.append(f"Promoter holding decreased from {prev:.1f}% to {curr:.1f}% (-{decrease:.1f}pp)")
            if selling_mentions > 0:
                parts.append(f"Promoter stake reduction mentioned ({selling_mentions} references)")
            return self.create_triggered_result(evidence=". ".join(parts) + ". May indicate lack of confidence.", confidence=80.0, extracted_data={"holding_current": curr, "holding_previous": prev, "decrease": decrease})
        return self.create_not_triggered_result("Promoter holding stable or increasing")


class DisproportionateSalaryFlag(RedFlagBase):
    """Flag #27: Disproportionate Managerial Remuneration (MEDIUM)."""
    def __init__(self):
        self.flag_number = 27
        self.flag_name = "Disproportionate Salary"
        self.category = FlagCategory.PROMOTER
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        notes = fd.get("notes", {})
        pl = fd.get("profit_loss", {})
        remuneration = self.extract_value(notes, "managerial_remuneration", "value", default=0.0)
        pat = self.extract_value(pl, "net_profit", "value", default=0.0)
        if not pat or pat <= 0:
            return self.create_not_triggered_result("PAT not available or company is loss-making")
        if remuneration == 0.0:
            notes_text = data.get("sections", {}).get("notes_to_accounts", "").lower()
            for pattern in [r'director.*?remuneration.*?(\d+(?:,\d+)*(?:\.\d+)?)', r'managerial remuneration.*?(\d+(?:,\d+)*(?:\.\d+)?)']:
                matches = re.findall(pattern, notes_text)
                if matches:
                    try:
                        remuneration = max(float(m.replace(',', '')) for m in matches)
                        break
                    except (ValueError, TypeError):
                        pass
        if remuneration == 0.0:
            return self.create_not_triggered_result("Managerial remuneration data not available")
        pct = (remuneration / pat) * 100
        if pct > 5:
            return self.create_triggered_result(evidence=f"Managerial remuneration is {pct:.1f}% of PAT (Remuneration: {remuneration:,.0f}, PAT: {pat:,.0f}). Excessive compensation may indicate profit extraction.", confidence=75.0, extracted_data={"remuneration": remuneration, "pat": pat, "pct": pct})
        return self.create_not_triggered_result("Remuneration within reasonable limits")


class PromoterEntityNameChangeFlag(RedFlagBase):
    """Flag #28: Promoter Entity Name Change (LOW)."""
    def __init__(self):
        self.flag_number = 28
        self.flag_name = "Promoter Entity Name Change"
        self.category = FlagCategory.PROMOTER
        self.severity = FlagSeverity.LOW

    def check(self, data: Dict):
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        governance_text = data.get("sections", {}).get("corporate_governance", "")
        combined = (notes_text + " " + governance_text).lower()
        keywords = ["name changed from", "formerly known as", "renamed to", "change of name", "name change", "erstwhile"]
        mentions = [kw for kw in keywords if kw in combined]
        if mentions:
            return self.create_triggered_result(evidence=f"Entity name change mentioned ({len(mentions)} references: {', '.join(set(mentions))}). May obscure past issues.", confidence=60.0, extracted_data={"mentions": mentions})
        return self.create_not_triggered_result("No entity name changes detected")


class ICDToPromoterGroupFlag(RedFlagBase):
    """Flag #29: ICDs to Promoter Group (HIGH)."""
    def __init__(self):
        self.flag_number = 29
        self.flag_name = "ICDs to Promoter Group"
        self.category = FlagCategory.PROMOTER
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        rpt = fd.get("related_party_transactions", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        icd_amount = abs(self.extract_value(rpt, "inter_corporate_deposits", "value", default=0.0))
        icd_keywords = ["inter-corporate deposit", "inter corporate deposit", "icd given", "icd to", "deposit given to", "short-term deposit to"]
        notes_lower = notes_text.lower()
        icd_mentions = [kw for kw in icd_keywords if kw in notes_lower]
        promoter_keywords = ["promoter", "group company", "related party"]
        promoter_icd_context = any(
            pk in notes_lower[max(0, notes_lower.find(ik) - 100):notes_lower.find(ik) + 100]
            for ik in icd_mentions for pk in promoter_keywords
        ) if icd_mentions else False
        if icd_amount > 0 or (icd_mentions and promoter_icd_context):
            parts = []
            if icd_amount > 0:
                parts.append(f"ICDs to related parties: {icd_amount:,.0f}")
            if icd_mentions:
                parts.append(f"ICD references ({len(icd_mentions)} mentions)")
            return self.create_triggered_result(evidence=". ".join(parts) + ". Fund diversion risk.", confidence=85.0, extracted_data={"icd_amount": icd_amount, "icd_mentions": icd_mentions})
        return self.create_not_triggered_result("No ICDs to promoter group detected")


flag_registry.register(PromoterPledgeHighFlag())
flag_registry.register(PledgeIncreasingFlag())
flag_registry.register(PromoterSellingSharesFlag())
flag_registry.register(DisproportionateSalaryFlag())
flag_registry.register(PromoterEntityNameChangeFlag())
flag_registry.register(ICDToPromoterGroupFlag())
