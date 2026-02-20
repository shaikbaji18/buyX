# TODO: Email Confirmation Implementation

## Task Summary
Implement confirmation emails for:
1. User/Distributor signup - "Thanks for choosing buyX. Let's start our journey together"
2. Order confirmation - "Your order has been successfully confirmed. Track your order with the given order id."

## Plan:

### 1. Update `user/models.py`
- [ ] Update `send_welcome_email()` function with new message:
  - Subject: "Welcome to buyX - Let's Start Our Journey Together!"
  - Message: "Thanks for choosing buyX. Let's start our journey together"
- [ ] Create new `send_order_confirmation_email()` function:
  - Subject: "Order Confirmed - Your buyX Order"
  - Message: "Your order has been successfully confirmed. Track your order with the given order id."

### 2. Update `user/views.py`
- [ ] Import `send_order_confirmation_email` in views
- [ ] Call `send_order_confirmation_email()` in `process_payment()` function after order is confirmed

### 3. Testing
- [ ] Test user signup email
- [ ] Test distributor signup email
- [ ] Test order confirmation email
