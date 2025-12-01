from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from users.decorators import role_required
from users.models import CustomUser
from django.contrib import messages
from .utils import send_deposit_receipt

from django.utils import timezone
from django.db.models import Sum
from .models import Wallet, Transaction, FundSettings

from datetime import timedelta



@login_required
@role_required(allowed_roles=['admin', 'store', 'subadmin'])
def user_balance_report(request):
    wallets = Wallet.objects.select_related('user').all()
    return render(request, 'funds/user_balance_report.html', {'wallets': wallets})


@login_required
def transaction_history(request):
    if request.user.role in ['admin', 'store', 'subadmin']:
        # Admin / privileged roles can see all transactions
        transactions = Transaction.objects.all().order_by('-timestamp')
    else:
        # Normal user sees only their own transactions
        wallet = Wallet.objects.get(user=request.user)
        transactions = wallet.transactions.all().order_by('-timestamp')

    return render(request, 'funds/transaction_history.html', {'transactions': transactions})



@login_required
@role_required(allowed_roles=['admin', 'store'])
def withdraw_funds(request, user_id):
    target_user = get_object_or_404(CustomUser, id=user_id)
    wallet, _ = Wallet.objects.get_or_create(user=target_user)

    if request.method == "POST":
        amount = request.POST.get("amount")
        reason = request.POST.get("reason", "Deduction")

        try:
            amount = float(amount)
            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
            elif amount > wallet.liquid:
                messages.error(request, f"Insufficient liquid balance. User has {wallet.liquid}.")
            else:
                # Deduct funds
                wallet.liquid -= amount
                wallet.save()

                # Record transaction
                Transaction.objects.create(
                    wallet=wallet,
                    amount=-amount,  # negative for deduction
                    transaction_type='withdraw',
                    performed_by=request.user
                )

                # Optional: send receipt for deduction
                # send_deposit_receipt(wallet, -amount, request.user)  # optional

                messages.success(request, f"Successfully deducted {amount} from {target_user.full_name}'s wallet. Reason: {reason}")
                return redirect('withdraw_funds', user_id=user_id)

        except ValueError:
            messages.error(request, "Invalid amount.")

    return render(request, 'funds/withdraw_funds.html', {'target_user': target_user, 'wallet': wallet})


@login_required
def reserve_to_liquid(request):
    wallet = Wallet.objects.get(user=request.user)

    if request.method == "POST":
        amount = request.POST.get("amount")
        try:
            amount = float(amount)
            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
            elif amount > wallet.reserve:
                messages.error(request, f"Insufficient reserve balance. You have {wallet.reserve}.")
            else:
                # Perform transfer
                wallet.reserve -= amount
                wallet.liquid += amount
                wallet.save()

                # Record transaction
                Transaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type='transfer',
                    performed_by=request.user
                )

                messages.success(request, f"Successfully transferred {amount} from Reserve to Liquid.")
                return redirect('reserve_to_liquid')

        except ValueError:
            messages.error(request, "Invalid amount.")

    return render(request, 'funds/reserve_to_liquid.html', {'wallet': wallet})



@login_required
@role_required(allowed_roles=['admin', 'store'])
def deposit_funds(request, user_id):
    target_user = get_object_or_404(CustomUser, id=user_id)
    wallet, _ = Wallet.objects.get_or_create(user=target_user)

    # Get fund settings (or defaults)
    settings_obj = FundSettings.objects.first()
    max_transaction = settings_obj.max_deposit_per_transaction if settings_obj else 10000
    daily_limit = settings_obj.daily_deposit_limit_per_user if settings_obj else 50000

    if request.method == "POST":
        amount = request.POST.get("amount")
        try:
            amount = float(amount)
            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
                return redirect('deposit_funds', user_id=user_id)

            if amount > float(max_transaction):
                messages.error(request, f"Deposit exceeds max per transaction limit ({max_transaction}).")
                return redirect('deposit_funds', user_id=user_id)

            # Calculate today's total deposits for the user
            today = timezone.now().date()
            total_today = Transaction.objects.filter(
                wallet=wallet,
                transaction_type='deposit',
                timestamp__date=today
            ).aggregate(total=Sum('amount'))['total'] or 0

            if total_today + amount > float(daily_limit):
                messages.error(request, f"Deposit exceeds daily limit ({daily_limit}). You have already deposited {total_today} today.")
                return redirect('deposit_funds', user_id=user_id)

            # Update wallet
            wallet.liquid += amount
            wallet.save()

            # Record transaction
            transaction = Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type='deposit',
                performed_by=request.user
            )

            # Send receipt email
            send_deposit_receipt(wallet, amount, request.user)

            messages.success(request, f"Deposited {amount} to {target_user.full_name} and receipt emailed.")
            return redirect('deposit_funds', user_id=user_id)

        except ValueError:
            messages.error(request, "Invalid amount.")

    return render(request, 'funds/deposit_funds.html', {'target_user': target_user, 'wallet': wallet})


@login_required
@role_required(allowed_roles=['admin', 'store', 'subadmin'])
def transaction_summary(request, period='daily'):
    now = timezone.now()

    if period == 'daily':
        start_date = now.replace(hour=0, minute=0, second=0)
    elif period == 'weekly':
        start_date = now - timedelta(days=now.weekday())  # start of week
    elif period == 'monthly':
        start_date = now.replace(day=1, hour=0, minute=0, second=0)
    else:
        start_date = None

    transactions = Transaction.objects.all()
    if start_date:
        transactions = transactions.filter(timestamp__gte=start_date)

    return render(request, 'funds/transaction_summary.html', {
        'transactions': transactions,
        'period': period.capitalize()
    })



@login_required
@role_required(allowed_roles=['admin', 'store'])
def deposit_funds(request, user_id):
    target_user = get_object_or_404(CustomUser, id=user_id)
    wallet, created = Wallet.objects.get_or_create(user=target_user)

    if request.method == "POST":
        amount = request.POST.get("amount")
        try:
            amount = float(amount)
            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
            else:
                # Update wallet
                wallet.liquid += amount
                wallet.save()

                # Record transaction
                Transaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type='deposit',
                    performed_by=request.user
                )

                messages.success(request, f"Deposited {amount} to {target_user.full_name}")
                return redirect('deposit_funds', user_id=user_id)
        except ValueError:
            messages.error(request, "Invalid amount.")

    return render(request, 'funds/deposit_funds.html', {'target_user': target_user, 'wallet': wallet})



@login_required
def view_wallet(request):
    user = request.user

    if user.role in ['admin']:
        # Admin can see all wallets
        wallets = Wallet.objects.all()
        return render(request, 'funds/wallet_list.html', {'wallets': wallets})
    else:
        # Regular user sees only their wallet
        wallet = Wallet.objects.get(user=user)
        return render(request, 'funds/wallet_detail.html', {'wallet': wallet})


