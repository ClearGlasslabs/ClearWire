Write a short follow-up message for an overdue invoice.

Tone: {tier}.
Constraints:
- 4 sentences maximum
- No "I hope this email finds you well"
- No emojis, no exclamation marks
- Mention the invoice ID and amount specifically
- If the prior message is friendly, stay friendly; if it's distant, stay direct
- End with a clear next step (a date, a confirmation request, or an offer to talk)

Context:
- Client: {client}
- Invoice: {invoice_id}
- Amount: {amount}
- Days overdue: {days}
- Last message we exchanged with this client:

{last_message}

Write the message body only. No subject line, no signature.
