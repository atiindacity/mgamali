# funds/utils.py
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from xhtml2pdf import pisa
from io import BytesIO

def send_deposit_receipt(wallet, amount, performed_by):
    # Render HTML template
    context = {
        'user': wallet.user,
        'amount': amount,
        'performed_by': performed_by,
        'timestamp': wallet.transactions.last().timestamp,  # latest transaction
        'liquid_balance': wallet.liquid
    }
    html = render_to_string('funds/deposit_receipt.html', context)

    # Generate PDF
    pdf_file = BytesIO()
    pisa.CreatePDF(html, dest=pdf_file)
    pdf_file.seek(0)

    # Send email
    email = EmailMessage(
        subject='Deposit Receipt',
        body='Please find attached your deposit receipt.',
        from_email=None,  # uses DEFAULT_FROM_EMAIL
        to=[wallet.user.email],
    )
    email.attach('deposit_receipt.pdf', pdf_file.read(), 'application/pdf')
    email.send()
