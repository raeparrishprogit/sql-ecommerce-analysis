# Interview walkthrough

Use this as a study guide. Run the project and be comfortable explaining each decision in your own words.

1. Start with the operations question: prioritize delivery investigation while tracking sales.
2. Explain the difference between item grain and order grain. A raw join of multiple items and reviews can inflate sales.
3. Walk through a CTE that aggregates items per order, then the review aggregation and delivery-date denominator.
4. Explain why RJ is a priority based on both late count and rate, and why SP remains relevant by volume.
5. Show a failed/nonzero quality check: eight delivered orders lack dates. They stay in sales but leave the delivery denominator.
6. Explain why the review gap is association rather than causal impact.
7. Open the reconciliation query and independent pandas assertions to show how totals were verified.

## Honest presentation
Describe this as an independent portfolio analysis built with AI assistance, then explain what you reviewed, reproduced, and understand. Do not claim to have worked for the source company, launched the proposed intervention, or achieved a revenue lift.
