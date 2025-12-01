

# funds/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('wallet/', views.view_wallet, name='view_wallet'),
    path('deposit/<int:user_id>/', views.deposit_funds, name='deposit_funds'),
    path('withdraw/<int:user_id>/', views.withdraw_funds, name='withdraw_funds'),
    path('transfer/reserve-to-liquid/', views.reserve_to_liquid, name='reserve_to_liquid'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('reports/user-balances/', views.user_balance_report, name='user_balance_report'),
    path('reports/transactions/<str:period>/', views.transaction_summary, name='transaction_summary'),
]
