"""AI-powered PDF extraction using Claude API.

Sends developer price list PDFs to Claude Sonnet and returns structured
estate / lot / guideline data.
"""

from __future__ import annotations

import base64
import json
import logging

import anthropic

from hlp.config import get_settings

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """\
You are a data extraction assistant for a house and land packaging system.

Analyse the attached PDF which is a developer price list for a residential estate.
Extract ALL data you can find and return it as a single JSON object with this exact schema:

{
  "estates": [
    {
      "estate_name": "string — name of the estate/development",
      "stage_name": "string — stage number or name (e.g. '1', 'Stage 1', '2A')",
      "suburb": "string or null",
      "postcode": "string or null",
      "developer_name": "string — the developer/builder company",
      "contact_name": "string or null",
      "contact_email": "string or null",
      "contact_mobile": "string or null",
      "lots": [
        {
          "lot_number": "string — the lot number",
          "street_name": "string or null",
          "frontage": "number or null — lot frontage in metres",
          "depth": "number or null — lot depth in metres",
          "size_sqm": "number or null — lot area in square metres",
          "land_price": "number or null — price in dollars (no $ sign, no commas)",
          "orientation": "string or null — N, S, E, W, NE, NW, SE, SW",
          "corner_block": "boolean — true if the lot is a corner block"
        }
      ],
      "guidelines": [
        {
          "guideline_type": "string — e.g. 'Recycled Water', 'Eaves', 'Roof Pitch'",
          "cost": "number or null — additional cost in dollars if applicable",
          "notes": "string — description or requirement details"
        }
      ]
    }
  ],
  "confidence": "high | medium | low",
  "notes": "any issues, ambiguities, or missing data you noticed"
}

Rules:
- If the PDF covers multiple stages of the same estate, create a separate entry in the estates array for each stage.
- Extract ALL lots listed in the price list.
- For land_price, convert to a plain number (e.g. 350000 not "$350,000").
- For frontage, depth, size_sqm, convert to plain numbers.
- Set corner_block to true only if explicitly indicated.
- For guidelines/design requirements, extract each type with its cost and any notes.
- If data is unclear or possibly incorrect, note it in the top-level "notes" field and set confidence accordingly.
- Return ONLY the JSON object, no markdown code fences, no explanation text.
"""


def extract_from_pdf(pdf_bytes: bytes) -> dict:
    """Send PDF to Claude Sonnet and return the extracted structured data.

    Args:
        pdf_bytes: Raw PDF file content.

    Returns:
        A dict matching the extraction schema above.

    Raises:
        ValueError: If the API response cannot be parsed as JSON.
        anthropic.APIError: On API communication failures.
    """
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")

    logger.info("Sending PDF (%d bytes) to Claude for extraction", len(pdf_bytes))

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": EXTRACTION_PROMPT,
                    },
                ],
            }
        ],
    )

    raw_text = message.content[0].text  # type: ignore[union-attr]
    logger.info("Received extraction response (%d chars)", len(raw_text))

    # Handle potential markdown code blocks in response
    text = raw_text.strip()
    if text.startswith("```"):
        # Remove ```json or ``` prefix and trailing ```
        lines = text.split("\n")
        # Drop first line (```json) and last line (```)
        if lines[-1].strip() == "```":
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        text = "\n".join(lines)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse extraction JSON: %s", exc)
        raise ValueError(f"Could not parse AI extraction response as JSON: {exc}") from exc

    return data
