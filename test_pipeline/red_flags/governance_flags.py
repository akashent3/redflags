"""Category 5: Corporate Governance Red Flags (7 flags, 12% weight)."""

import re
import logging
from typing import Dict

from red_flags.models import FlagCategory, FlagSeverity
from red_flags.base import RedFlagBase
from red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class IndependentDirectorExitFlag(RedFlagBase):
    """Flag #30: Independent Director Resignation (HIGH)."""
    def __init__(self):
        self.flag_number = 30
        self.flag_name = "Independent Director Exit"
        self.category = FlagCategory.GOVERNANCE
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        gov = data.get("sections", {}).get("corporate_governance", "")
        dr = data.get("sections", {}).get("directors_report", "")
        combined = (gov + " " + dr).lower()
        # Check structured governance data
        governance = data.get("financial_data", {}).get("governance", {})
        if governance.get("independent_director_resignation"):
            return self.create_triggered_result(evidence="Independent director resignation confirmed. ID exits often signal governance concerns.", confidence=90.0)
        keywords = ["independent director resigned", "independent director resignation", "resignation of independent director", "independent director ceased", "independent director stepped down"]
        mentions = [kw for kw in keywords if kw in combined]
        if not mentions and "independent" in combined and "resign" in combined:
            if re.search(r'independent.{0,50}resign|resign.{0,50}independent', combined):
                mentions.append("independent director resignation (contextual)")
        if mentions:
            return self.create_triggered_result(evidence=f"ID resignation detected ({len(mentions)} references). ID exits often signal governance concerns.", confidence=85.0)
        return self.create_not_triggered_result("No independent director resignations detected")


class CFOCSChangeFlag(RedFlagBase):
    """Flag #31: CFO or Company Secretary Changed (HIGH)."""
    def __init__(self):
        self.flag_number = 31
        self.flag_name = "CFO/CS Change in Year"
        self.category = FlagCategory.GOVERNANCE
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        gov = data.get("sections", {}).get("corporate_governance", "")
        dr = data.get("sections", {}).get("directors_report", "")
        combined = (gov + " " + dr).lower()
        governance = data.get("financial_data", {}).get("governance", {})
        cfo_change = governance.get("cfo_change", False)
        cs_change = governance.get("cs_change", False)
        keywords = ["cfo resigned", "cfo appointed", "chief financial officer resigned", "chief financial officer appointed", "company secretary resigned", "company secretary appointed", "cs resigned", "cs appointed", "change of cfo", "change of company secretary", "new cfo", "new company secretary"]
        mentions = [kw for kw in keywords if kw in combined]
        if not cfo_change:
            cfo_change = any("cfo" in m or "chief financial officer" in m for m in mentions)
        if not cs_change:
            cs_change = any("company secretary" in m or "cs " in m for m in mentions)
        if cfo_change or cs_change or mentions:
            parts = []
            if cfo_change:
                parts.append("CFO changed during the year")
            if cs_change:
                parts.append("Company Secretary changed during the year")
            return self.create_triggered_result(evidence=". ".join(parts) + f". {len(mentions)} references found. Key management changes may indicate underlying issues.", confidence=90.0, extracted_data={"cfo_change": cfo_change, "cs_change": cs_change})
        return self.create_not_triggered_result("No CFO or CS changes detected")


class LowBoardAttendanceFlag(RedFlagBase):
    """Flag #32: Low Board Meeting Attendance (MEDIUM)."""
    def __init__(self):
        self.flag_number = 32
        self.flag_name = "Low Board Attendance"
        self.category = FlagCategory.GOVERNANCE
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        gov = data.get("sections", {}).get("corporate_governance", "")
        if not gov:
            return self.create_not_triggered_result("Corporate governance report not found")
        governance = data.get("financial_data", {}).get("governance", {})
        if governance.get("board_attendance_issues"):
            return self.create_triggered_result(evidence="Board attendance issues identified. Poor attendance suggests lack of board engagement.", confidence=80.0)
        gov_lower = gov.lower()
        percentages = []
        for pattern in [r'attendance.*?(\d+)%', r'(\d+)%.*?attendance']:
            matches = re.findall(pattern, gov_lower)
            if matches:
                percentages.extend(int(m) for m in matches if 0 <= int(m) <= 100)
        if not percentages:
            return self.create_not_triggered_result("Board attendance data not found")
        avg = sum(percentages) / len(percentages)
        minimum = min(percentages)
        if avg < 75 or minimum < 50:
            evidence = f"Board attendance concerns (Average: {avg:.1f}%, Lowest: {minimum}%). "
            if minimum < 50:
                evidence += "At least one director attended less than 50% of meetings. "
            return self.create_triggered_result(evidence=evidence + "Poor attendance suggests lack of engagement.", confidence=80.0, extracted_data={"avg_attendance": avg, "min_attendance": minimum})
        return self.create_not_triggered_result("Board attendance is satisfactory")


class RelatedOnAuditCommitteeFlag(RedFlagBase):
    """Flag #33: Related Party on Audit Committee (MEDIUM)."""
    def __init__(self):
        self.flag_number = 33
        self.flag_name = "Related on Audit Committee"
        self.category = FlagCategory.GOVERNANCE
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        gov = data.get("sections", {}).get("corporate_governance", "")
        if not gov:
            return self.create_not_triggered_result("Corporate governance report not found")
        governance = data.get("financial_data", {}).get("governance", {})
        if governance.get("audit_committee_concerns"):
            return self.create_triggered_result(evidence="Audit committee independence concerns identified.", confidence=75.0)
        gov_lower = gov.lower()
        if "audit committee" not in gov_lower:
            return self.create_not_triggered_result("Audit committee details not found")
        ac_start = gov_lower.find("audit committee")
        ac_section = gov_lower[ac_start:ac_start + 500]
        concern_keywords = ["executive director", "non-independent", "promoter", "related party", "not independent"]
        concerns = [kw for kw in concern_keywords if kw in ac_section]
        if concerns:
            return self.create_triggered_result(evidence=f"Audit committee independence concerns: {', '.join(set(concerns))}. Should be majority independent.", confidence=70.0, extracted_data={"concerns": concerns})
        return self.create_not_triggered_result("Audit committee composition appears independent")


class DelayedAGMResultsFlag(RedFlagBase):
    """Flag #34: Delayed AGM or Results Filing (MEDIUM)."""
    def __init__(self):
        self.flag_number = 34
        self.flag_name = "Delayed AGM/Results"
        self.category = FlagCategory.GOVERNANCE
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        dr = data.get("sections", {}).get("directors_report", "")
        notes = data.get("sections", {}).get("notes_to_accounts", "")
        combined = (dr + " " + notes).lower()
        governance = data.get("financial_data", {}).get("governance", {})
        if governance.get("filing_delays"):
            return self.create_triggered_result(evidence="Filing delays confirmed. May indicate operational or compliance issues.", confidence=80.0)
        delay_keywords = ["delayed", "extension", "extended time", "beyond due date", "filing delay", "postponed", "rescheduled", "late filing", "penalty for delay"]
        mentions = [kw for kw in delay_keywords if kw in combined]
        agm_delay = "agm" in combined and any(d in combined[max(0, combined.find("agm") - 50):combined.find("agm") + 100] for d in ["delay", "postpone", "extended"])
        if mentions or agm_delay:
            parts = []
            if agm_delay:
                parts.append("AGM delay mentioned")
            if mentions:
                parts.append(f"Delay references ({len(mentions)} mentions)")
            return self.create_triggered_result(evidence=". ".join(parts) + ". May indicate compliance issues.", confidence=75.0, extracted_data={"delay_mentions": mentions[:5], "agm_delay": agm_delay})
        return self.create_not_triggered_result("No filing delays detected")


class RegulatoryPenaltiesFlag(RedFlagBase):
    """Flag #35: SEBI/Stock Exchange Penalties (HIGH)."""
    def __init__(self):
        self.flag_number = 35
        self.flag_name = "SEBI/Exchange Penalties"
        self.category = FlagCategory.GOVERNANCE
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        gov = data.get("sections", {}).get("corporate_governance", "")
        dr = data.get("sections", {}).get("directors_report", "")
        notes = data.get("sections", {}).get("notes_to_accounts", "")
        combined = (gov + " " + dr + " " + notes).lower()
        governance = data.get("financial_data", {}).get("governance", {})
        if governance.get("sebi_penalties"):
            amt = governance.get("penalty_amount", 0)
            return self.create_triggered_result(evidence=f"Regulatory penalties confirmed. Amount: {amt:,.0f}. Indicates compliance failures.", confidence=95.0)
        keywords = ["sebi penalty", "sebi fine", "stock exchange penalty", "regulatory penalty", "non-compliance penalty", "penalty imposed", "fine imposed", "penalty paid", "adjudication", "show cause notice", "regulatory action"]
        mentions = [kw for kw in keywords if kw in combined]
        if mentions:
            amounts = re.findall(r'penalty.*?(?:rs|inr|₹)\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)', combined)
            total_penalty = sum(float(a.replace(',', '')) for a in amounts) if amounts else 0
            evidence = f"Regulatory penalties detected ({len(mentions)} references: {', '.join(set(mentions[:3]))}). "
            if total_penalty > 0:
                evidence += f"Total penalties: {total_penalty:,.0f}. "
            return self.create_triggered_result(evidence=evidence + "Indicates compliance failures.", confidence=95.0, extracted_data={"mentions": mentions, "total_penalty": total_penalty})
        return self.create_not_triggered_result("No regulatory penalties detected")


class WhistleblowerComplaintsFlag(RedFlagBase):
    """Flag #36: Whistle-blower Complaints Received (MEDIUM)."""
    def __init__(self):
        self.flag_number = 36
        self.flag_name = "Whistle-blower Complaints"
        self.category = FlagCategory.GOVERNANCE
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        gov = data.get("sections", {}).get("corporate_governance", "")
        dr = data.get("sections", {}).get("directors_report", "")
        combined = (gov + " " + dr).lower()
        governance = data.get("financial_data", {}).get("governance", {})
        wb_count = governance.get("whistleblower_complaints", 0)
        if wb_count and wb_count > 0:
            return self.create_triggered_result(evidence=f"Whistle-blower complaints: {wb_count}. Suggests internal control concerns.", confidence=75.0, extracted_data={"complaint_count": wb_count})
        keywords = ["whistle blower complaint", "whistleblower complaint", "vigil mechanism complaint", "complaints received under"]
        mentions = [kw for kw in keywords if kw in combined]
        if mentions and "nil" not in combined[max(0, combined.find("whistle") - 20):combined.find("whistle") + 100]:
            count_matches = re.findall(r'(\d+)\s+complaint', combined)
            count = max((int(m) for m in count_matches if 0 < int(m) < 100), default=0) if count_matches else 0
            if count > 0 or mentions:
                return self.create_triggered_result(evidence=f"Whistle-blower complaints present ({count if count else 'details in report'}). Internal control concerns.", confidence=70.0, extracted_data={"complaint_count": count})
        return self.create_not_triggered_result("No whistle-blower complaints or reported as nil")


flag_registry.register(IndependentDirectorExitFlag())
flag_registry.register(CFOCSChangeFlag())
flag_registry.register(LowBoardAttendanceFlag())
flag_registry.register(RelatedOnAuditCommitteeFlag())
flag_registry.register(DelayedAGMResultsFlag())
flag_registry.register(RegulatoryPenaltiesFlag())
flag_registry.register(WhistleblowerComplaintsFlag())
