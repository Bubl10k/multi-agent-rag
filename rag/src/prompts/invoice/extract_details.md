Extract invoice details from this conversation and return a JSON object.

Conversation:
${conversation}

Return this exact JSON structure (null for missing optional fields, empty list for no items):
{
  "client_info": {"name": null, "address": null, "email": null, "tax_id": null},
  "line_items": [{"description": "string", "qty": 1, "unit_price": 0.0}],
  "invoice_meta": {"invoice_number": null, "issue_date": null, "due_date": null, "currency": "${default_currency}"},
  "tax_rate": ${default_tax_rate},
  "is_complete": false,
  "missing_fields": ["list required fields that are missing"]
}

is_complete is true only when: client_info.name is set, line_items has at least one item with description and unit_price > 0, and invoice_meta.issue_date is set.
Return ONLY the JSON, no explanation.${context_section}