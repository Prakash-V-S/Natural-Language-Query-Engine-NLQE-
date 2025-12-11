from openai import OpenAI
from dotenv import load_dotenv
import os
import re

# Load .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

async def parse_natural_query(query: str):
    """
    Convert natural language query to SQL.
    """

    # Prompt sent to LLM
    prompt = f"""
You are an expert PostgreSQL SQL generator.

Use ONLY PostgreSQL syntax.

Use the following schema:
TABLE customers(customer_id, name, email, city, region_id, created_at)
TABLE regions(region_id, name)
TABLE products(product_id, sku, name, category, price)
TABLE sales(sale_id, sale_date, customer_id, product_id, quantity, unit_price, revenue)
TABLE invoices(invoice_id, invoice_date, sale_id, invoiced, amount)
TABLE returns(return_id, sale_id, return_date, qty_returned, refund_amount)

Strict rules:
- Use DATE_TRUNC for time grouping.
- Use correct JOINs.
- For revenue use sales.revenue.
- Return ONLY SQL inside ```sql ... ```
- NEVER add explanation.

User request:
{query}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert PostgreSQL SQL generator. "
                    "Use ONLY PostgreSQL syntax. "
                    "Use the following schema:\n"
                    "TABLE customers(customer_id, name, email, city, region_id, created_at)\n"
                    "TABLE regions(region_id, name)\n"
                    "TABLE products(product_id, sku, name, category, price)\n"
                    "TABLE sales(sale_id, sale_date, customer_id, product_id, quantity, unit_price, revenue)\n"
                    "TABLE invoices(invoice_id, invoice_date, sale_id, invoiced, amount)\n"
                    "TABLE returns(return_id, sale_id, return_date, qty_returned, refund_amount)\n\n"
                    "Rules:\n"
                    "- Use DATE_TRUNC for time grouping.\n"
                    "- Use correct JOINs.\n"
                    "- For revenue use sales.revenue.\n"
                    "- Return ONLY SQL inside ```sql ... ```\n"
                    "- NEVER explain.\n"
                )
            },
            {"role": "user", "content": prompt}
        ]
    )

    raw_sql = response.choices[0].message.content.strip()

    # Extract SQL block
    match = re.search(r"```sql\s*(.*?)```", raw_sql, re.DOTALL | re.IGNORECASE)
    if match:
        sql_only = match.group(1).strip()
    else:
        sql_only = raw_sql

    return {"sql": sql_only}
