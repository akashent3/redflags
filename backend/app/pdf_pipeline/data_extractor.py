"""Extract structured financial data from annual report sections."""

import json
import logging
from typing import Dict, Optional

from app.llm.gemini_client import gemini_client
from app.llm.prompts import (
    AUDITOR_REPORT_ANALYSIS_PROMPT,
    CASHFLOW_QUALITY_PROMPT,
    FINANCIAL_DATA_EXTRACTION_PROMPT,
    RPT_ANALYSIS_PROMPT,
)

logger = logging.getLogger(__name__)


class FinancialDataExtractor:
    """Extract key financial metrics from annual report sections."""

    def extract_key_metrics(
        self, sections: Dict[str, str], fiscal_year: str
    ) -> Dict[str, any]:
        """
        Extract all key financial metrics from detected sections.

        Args:
            sections: Dict mapping section names to extracted text
            fiscal_year: Fiscal year of the report (e.g., "2023")

        Returns:
            Dict containing all extracted financial data
        """
        extracted_data = {
            "fiscal_year": fiscal_year,
            "extraction_status": {},
        }

        # Extract from Balance Sheet
        if "balance_sheet" in sections:
            logger.info("Extracting data from Balance Sheet")
            bs_data = self._extract_from_section(
                section_text=sections["balance_sheet"],
                section_name="Balance Sheet",
                fiscal_year=fiscal_year,
            )
            extracted_data["balance_sheet"] = bs_data
            extracted_data["extraction_status"]["balance_sheet"] = "success"
        else:
            extracted_data["extraction_status"]["balance_sheet"] = "not_found"

        # Extract from Profit & Loss Statement
        if "profit_loss_statement" in sections:
            logger.info("Extracting data from P&L Statement")
            pl_data = self._extract_from_section(
                section_text=sections["profit_loss_statement"],
                section_name="Profit & Loss Statement",
                fiscal_year=fiscal_year,
            )
            extracted_data["profit_loss"] = pl_data
            extracted_data["extraction_status"]["profit_loss"] = "success"
        else:
            extracted_data["extraction_status"]["profit_loss"] = "not_found"

        # Extract from Cash Flow Statement
        if "cash_flow_statement" in sections:
            logger.info("Extracting data from Cash Flow Statement")
            cf_data = self._extract_cashflow_data(
                cashflow_text=sections["cash_flow_statement"],
                net_profit=extracted_data.get("profit_loss", {}).get("net_profit"),
            )
            extracted_data["cash_flow"] = cf_data
            extracted_data["extraction_status"]["cash_flow"] = "success"
        else:
            extracted_data["extraction_status"]["cash_flow"] = "not_found"

        # Extract from Notes to Accounts (audit fees, related parties)
        if "notes_to_accounts" in sections:
            logger.info("Extracting data from Notes to Accounts")
            notes_data = self._extract_from_section(
                section_text=sections["notes_to_accounts"],
                section_name="Notes to Accounts",
                fiscal_year=fiscal_year,
            )
            extracted_data["notes"] = notes_data
            extracted_data["extraction_status"]["notes"] = "success"
        else:
            extracted_data["extraction_status"]["notes"] = "not_found"

        # Analyze Related Party Transactions
        if "related_party_transactions" in sections:
            logger.info("Analyzing Related Party Transactions")
            rpt_data = self._extract_rpt_data(sections["related_party_transactions"])
            extracted_data["related_party_transactions"] = rpt_data
            extracted_data["extraction_status"]["related_party_transactions"] = "success"
        else:
            extracted_data["extraction_status"]["related_party_transactions"] = "not_found"

        # Analyze Auditor Report
        if "auditor_report" in sections:
            logger.info("Analyzing Auditor Report")
            auditor_data = self._analyze_auditor_report(sections["auditor_report"])
            extracted_data["auditor_analysis"] = auditor_data
            extracted_data["extraction_status"]["auditor_report"] = "success"
        else:
            extracted_data["extraction_status"]["auditor_report"] = "not_found"

        return extracted_data

    def _extract_from_section(
        self, section_text: str, section_name: str, fiscal_year: str
    ) -> Dict[str, any]:
        """
        Extract financial data from a specific section using LLM.

        Args:
            section_text: Text content of the section
            section_name: Name of the section
            fiscal_year: Fiscal year

        Returns:
            Dict of extracted financial metrics
        """
        try:
            # Limit text length to avoid token limits (first 10,000 chars)
            truncated_text = section_text[:10000]

            # Build prompt
            prompt = FINANCIAL_DATA_EXTRACTION_PROMPT.format(
                section_name=section_name,
                fiscal_year=fiscal_year,
                section_text=truncated_text,
            )

            # Call Gemini
            response_text = gemini_client.generate_structured_output(
                prompt=prompt, output_format="json"
            )

            # Parse JSON
            data = self._parse_json_response(response_text)
            return data

        except Exception as e:
            logger.error(f"Failed to extract data from {section_name}: {e}")
            return {"error": str(e)}

    def _extract_cashflow_data(
        self, cashflow_text: str, net_profit: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Extract and analyze cash flow data.

        Args:
            cashflow_text: Cash flow statement text
            net_profit: Net profit data for CFO/PAT ratio calculation

        Returns:
            Cash flow analysis data
        """
        try:
            truncated_text = cashflow_text[:10000]

            net_profit_str = json.dumps(net_profit) if net_profit else "Not available"

            prompt = CASHFLOW_QUALITY_PROMPT.format(
                cashflow_text=truncated_text, net_profit=net_profit_str
            )

            response_text = gemini_client.generate_structured_output(
                prompt=prompt, output_format="json"
            )

            data = self._parse_json_response(response_text)
            return data

        except Exception as e:
            logger.error(f"Failed to extract cash flow data: {e}")
            return {"error": str(e)}

    def _extract_rpt_data(self, rpt_text: str) -> Dict[str, any]:
        """
        Extract related party transaction data.

        Args:
            rpt_text: Related party transactions section text

        Returns:
            RPT analysis data
        """
        try:
            truncated_text = rpt_text[:15000]  # RPT sections can be longer

            prompt = RPT_ANALYSIS_PROMPT.format(rpt_text=truncated_text)

            response_text = gemini_client.generate_structured_output(
                prompt=prompt, output_format="json"
            )

            data = self._parse_json_response(response_text)
            return data

        except Exception as e:
            logger.error(f"Failed to extract RPT data: {e}")
            return {"error": str(e)}

    def _analyze_auditor_report(self, auditor_text: str) -> Dict[str, any]:
        """
        Analyze auditor report for red flags.

        Args:
            auditor_text: Auditor report text

        Returns:
            Auditor analysis data
        """
        try:
            truncated_text = auditor_text[:8000]

            prompt = AUDITOR_REPORT_ANALYSIS_PROMPT.format(
                auditor_report_text=truncated_text
            )

            response_text = gemini_client.generate_structured_output(
                prompt=prompt, output_format="json"
            )

            data = self._parse_json_response(response_text)
            return data

        except Exception as e:
            logger.error(f"Failed to analyze auditor report: {e}")
            return {"error": str(e)}

    def _parse_json_response(self, response_text: str) -> Dict[str, any]:
        """
        Parse JSON from LLM response.

        Handles markdown code blocks and malformed JSON.
        """
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text.strip()

            # Parse JSON
            data = json.loads(json_text)
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            return {"error": "JSON parsing failed", "raw_response": response_text[:500]}


# Singleton instance
financial_data_extractor = FinancialDataExtractor()
