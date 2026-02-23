## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool, read_financial_document

## Task 1: Verify the document is a legitimate financial report
verification = Task(
    description="Read the uploaded financial document at '{file_path}' and verify that it is a legitimate financial report.\n"
    "Check for the presence of standard financial elements such as balance sheets, income statements, "
    "cash flow statements, revenue figures, and regulatory disclosures.\n"
    "If the document is not a valid financial report, clearly state why and stop further analysis.\n"
    "If it is valid, provide a brief summary of the document type and key sections identified.",

    expected_output="""A structured verification report containing:
- Document type classification (e.g., quarterly report, annual filing, earnings update)
- Key financial sections identified (balance sheet, income statement, cash flow, etc.)
- Confirmation of legitimacy (PASS/FAIL) with reasoning
- Brief summary of the document's scope and reporting period""",

    agent=verifier,
    tools=[read_financial_document],
    async_execution=False,
)

## Task 2: Analyze the financial document in depth
analyze_financial_document = Task(
    description="Thoroughly analyze the financial document at '{file_path}' to answer the user's query: {query}.\n"
    "Extract and interpret key financial metrics including revenue, net income, margins, EPS, "
    "debt levels, cash flow, and any other relevant data points.\n"
    "Identify trends, compare with prior periods where available, and highlight notable items.\n"
    "Search the internet for current market context to enrich your analysis.",

    expected_output="""A comprehensive financial analysis report containing:
- Executive summary of key findings
- Detailed breakdown of financial metrics (revenue, income, margins, EPS, etc.)
- Trend analysis and period-over-period comparisons
- Notable items and red flags identified
- Market context from current news and industry data
- Direct answers to the user's specific query""",

    agent=financial_analyst,
    tools=[read_financial_document, search_tool],
    async_execution=False,
)

## Task 3: Provide investment analysis and recommendations
investment_analysis = Task(
    description="Based on the financial analysis of the document at '{file_path}', provide well-reasoned investment recommendations.\n"
    "Consider the financial health, growth prospects, valuation metrics, and competitive position "
    "revealed by the document. Address the user's query: {query}.\n"
    "Ensure all recommendations are data-driven, diversified, and include appropriate disclaimers.\n"
    "Search the internet for current analyst ratings, price targets, and market sentiment.",

    expected_output="""A professional investment analysis containing:
- Investment thesis summary (bull case and bear case)
- Key valuation metrics and how they compare to industry benchmarks
- Specific, data-driven investment recommendations with rationale
- Portfolio allocation suggestions appropriate for different risk profiles
- Relevant disclaimers about investment risks
- References to current analyst consensus and market data""",

    agent=investment_advisor,
    tools=[read_financial_document, search_tool],
    async_execution=False,
)

## Task 4: Perform risk assessment
risk_assessment = Task(
    description="Perform a comprehensive risk assessment based on the financial document at '{file_path}'.\n"
    "Evaluate market risk, credit risk, liquidity risk, and operational risk factors.\n"
    "Assess the company's financial resilience and identify potential vulnerabilities.\n"
    "Address the user's query: {query} from a risk management perspective.\n"
    "Search for any recent news or regulatory developments that could impact risk profile.",

    expected_output="""A structured risk assessment report containing:
- Overall risk rating (Low / Medium / High) with justification
- Market risk factors and their potential impact
- Credit and liquidity risk evaluation
- Operational risk considerations
- Stress test scenarios (best case, base case, worst case)
- Risk mitigation recommendations
- Regulatory and compliance risk factors""",

    agent=risk_assessor,
    tools=[read_financial_document, search_tool],
    async_execution=False,
)