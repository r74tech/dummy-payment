# Mock Payment System with Automated Cart and Checkout Flow 🚀

This project provides a **complete payment flow simulation** using two FastAPI services:

1. **Cart Service**: Handles item additions and initiates the checkout process.  
   URL: `http://localhost:8001`
2. **Payment Server**: Processes payments and sends webhook notifications.  
   URL: `http://localhost:8000`

The flow mimics a real-world e-commerce payment process with these steps:
- Adding items to a cart.
- Initiating a checkout and sending a payment request.
- Capturing the payment.
- Sending and receiving a **webhook notification**.

---

## **Prerequisites**

1. **Python 3.9 or higher**
2. Install the following Python packages:
   ```bash
   pip install fastapi uvicorn requests
   ```
3. Install **jq** for JSON parsing:
   - **Ubuntu/Debian**:
     ```bash
     sudo apt-get install jq
     ```
   - **macOS**:
     ```bash
     brew install jq
     ```

---

## **Usage Instructions**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/r74tech/dummy-payment.git
   cd dummy-payment
   ```

2. **Start the Cart Service**:
   ```bash
   uvicorn cart_service:app --reload --port 8001
   ```

3. **Ensure the Payment Server is Running**:
   - If not already running, start it on port 8000:
     ```bash
     docker compose up -d --build
     ```

4. **Run the Payment Flow Script**:
   Make sure both services are running, then execute the script to test the complete flow:
   ```bash
   ./run_payment_flow.sh
   ```

---

## **Expected Output**

```bash
=== Step 1: Get Access Token ===
Access Token: YHPGUNHOXHO3
=== Step 2: Add Item to Cart ===
Cart Response: {"msg":"Item item001 added to cart","cart":{"item001":{"quantity":2,"price":100.0}}}
=== Step 3: Start Checkout ===
Order ID: 2HXG07P5EU7R
Payment Token: YHPGUNHOXHO3
=== Payment Flow Completed Successfully ===
```

Docker Compose Logs:
```bash
INFO:     Started server process [8]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started server process [7]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     192.168.65.1:38645 - "POST /auth/token HTTP/1.1" 200 OK
INFO:     192.168.65.1:27506 - "POST /cart/add HTTP/1.1" 200 OK
INFO:     127.0.0.1:53820 - "POST /payments/start HTTP/1.1" 200 OK
INFO:     127.0.0.1:53826 - "POST /payments/capture/YHPGUNHOXHO3 HTTP/1.1" 200 OK
INFO:     192.168.65.1:27507 - "POST /checkout HTTP/1.1" 200 OK
INFO:     127.0.0.1:52438 - "POST /callback HTTP/1.1" 200 OK
Received Webhook: {'token': 'YHPGUNHOXHO3', 'transaction': {'status': 'captured', 'order_id': '2HXG07P5EU7R', 'amount': 200.0}}
```

---

## **Troubleshooting**

1. **Verify Services**:
   - Ensure both services are running on the correct ports:
     - Cart Service: `http://localhost:8001`
     - Payment Server: `http://localhost:8000`

2. **Common Errors**:
   - **Connection Refused**: Verify that the services are running.
   - **jq not found**: Install `jq` using the instructions above.

3. **Check Logs**:
   - Use logs from the services to debug any issues:
     ```bash
     tail -f uvicorn.log
     ```

---

## **Project Overview**

This project offers a **full payment workflow** simulation, from cart management to payment capture and webhook notifications. It’s ideal for:
- **Testing e-commerce integrations**
- **Simulating payment flows for development and security exercises**
- **Mocking webhook handling scenarios**

Feel free to extend this project with additional features like security challenges, error simulations, or support for additional payment methods. 
