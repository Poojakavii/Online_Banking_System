from flask import Flask, render_template, request, redirect, url_for, session
from models import *
from models import (
    register_customer,
    get_customer,
    check_login,
    add_beneficiary,
    get_beneficiaries,
    add_transfer,
    get_transfers,
    add_bill_payment,
    get_bill_payments,
    add_fixed_deposit,
    get_fixed_deposits,
    add_loan,
    get_loans,
    get_transactions,
    update_customer,
    get_transaction_count,
    get_loan_count,
    get_fd_count,
    get_recent_transactions,
    get_all_customers,
    admin_total_customers,
    admin_total_loans,
    admin_total_transactions,
    admin_total_fd
)


app = Flask(__name__)
app.secret_key = "onlinebank123"

# ---------------- HOME ----------------

@app.route('/')
def home():
    return render_template('index.html')


# ---------------- REGISTER ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == "POST":

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        address = request.form['address']
        dob = request.form['dob']
        gender = request.form['gender']
        account_type = request.form['account_type']

    try:

       register_customer(
        name,
        email,
        phone,
        password,
        address,
        dob,
        gender,
        account_type,
        bank_name,
        account_number,
        ifsc,
        balance
    )

    except Exception as e:

        if "Duplicate entry" in str(e):

          return render_template(
            "register.html",
            error="Email already registered. Please use another email."
        )

    else:
        raise
# ---------------- LOGIN ----------------

@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():

    if request.method == "POST":

        email = request.form['email']
        password = request.form['password']

        customer = check_login(email, password)

        if customer:

            session['customer_id'] = customer['customer_id']

            return redirect(url_for('customer_dashboard'))

        else:
            return "Invalid Email or Password"

    return render_template('customer_login.html')
# ---------------- DASHBOARD ----------------
@app.route('/customer_dashboard')
def customer_dashboard():

    customer_id = session['customer_id']

    customer = get_customer(customer_id)

    transaction_count = get_transaction_count(customer_id)

    loan_count = get_loan_count(customer_id)

    fd_count = get_fd_count(customer_id)

    transactions = get_recent_transactions(customer_id)


    return render_template(
        'customer_dashboard.html',
        customer=customer,
        transaction_count=transaction_count,
        loan_count=loan_count,
        fd_count=fd_count,
        transactions=transactions
    )

# ---------------- PROFILE ----------------

# ---------------- PROFILE ----------------
from models import update_customer
@app.route('/profile')
def profile():

    if 'customer_id' not in session:
        return redirect(url_for('customer_login'))

    customer = get_customer(session['customer_id'])

    return render_template(
        'profile.html',
        customer=customer
    )

# ---------------- ACCOUNT ----------------

@app.route('/account')
def account():

    if 'customer_id' not in session:
        return redirect(url_for('customer_login'))

    customer = get_customer(session['customer_id'])

    return render_template(
        'account.html',
        customer=customer
    )

# ---------------- TRANSFER ----------------

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():

    if 'customer_id' not in session:
        return redirect(url_for('customer_login'))

    customer = get_customer(session['customer_id'])

    beneficiaries = get_beneficiaries(session['customer_id'])

    if request.method == "POST":

        beneficiary_id = request.form['beneficiary']
        transfer_type = request.form['transfer_type']
        amount = request.form['amount']
        remarks = request.form['remarks']

        add_transfer(
            session['customer_id'],
            beneficiary_id,
            transfer_type,
            amount,
            remarks
        )
        
        add_transaction(
            session['customer_id'],
            "Fund Transfer",
            amount,
            "Pending"
        )
        
        return redirect(url_for('transfer'))

    transfers = get_transfers(session['customer_id'])

    return render_template(
        'transfer.html',
        customer=customer,
        beneficiaries=beneficiaries,
        transfers=transfers
    )

# ---------------- BENEFICIARY ----------------

from models import add_beneficiary, get_beneficiaries


@app.route('/beneficiary', methods=['GET', 'POST'])
def beneficiary():

    if 'customer_id' not in session:
        return redirect(url_for('customer_login'))

    customer = get_customer(session['customer_id'])

    if request.method == "POST":

        add_beneficiary(
            session['customer_id'],
            request.form['beneficiary_name'],
            request.form['bank_name'],
            request.form['receiver_account'],
            request.form['ifsc']
        )

        return redirect(url_for('beneficiary'))

    beneficiaries = get_beneficiaries(session['customer_id'])

    return render_template(
        'beneficiary.html',
        customer=customer,
        beneficiaries=beneficiaries
    )
# ---------------- BILL PAYMENT ----------------



# ---------------- BILL PAYMENT ----------------

    # ---------------- BILL PAYMENT ----------------

@app.route('/billpayment', methods=['GET','POST'])
def billpayment():

    if 'customer_id' not in session:
        return redirect(url_for('customer_login'))

    customer_id = session['customer_id']


    if request.method == "POST":

        bill_type = request.form['bill_type']
        consumer_number = request.form['consumer_number']
        provider = request.form['provider']
        amount = request.form['amount']


        from models import add_bill_payment

        add_bill_payment(
            customer_id,
            bill_type,
            consumer_number,
            provider,
            amount
        )


        return redirect(url_for('billpayment'))



    from models import get_bill_payments

    bills = get_bill_payments(customer_id)


    return render_template(
        'billpayment.html',
        bills=bills
    )
# ---------------- FIXED DEPOSIT ----------------

@app.route('/fixeddeposit', methods=['GET','POST'])
def fixeddeposit():

    if 'customer_id' not in session:
        return redirect(url_for('customer_login'))

    customer = get_customer(session['customer_id'])

    if request.method == "POST":

        amount = request.form['amount']
        tenure = request.form['tenure']

        interest = 7.25

        add_fixed_deposit(
            session['customer_id'],
            amount,
            tenure,
            interest
        )
        
        add_transaction(
            session['customer_id'],
            "Fixed Deposit",
            amount,
            "Completed"
        )
        
        return redirect(url_for('fixeddeposit'))

    fds = get_fixed_deposits(session['customer_id'])

    return render_template(
        "fixeddeposit.html",
        customer=customer,
        fds=fds
    )

# ---------------- LOAN ----------------

@app.route('/loan', methods=['GET', 'POST'])
def loan():

    if 'customer_id' not in session:
        return redirect(url_for('customer_login'))

    customer = get_customer(session['customer_id'])

    if request.method == "POST":

        loan_type = request.form['loan_type']
        amount = request.form['amount']
        tenure = request.form['tenure']
        income = request.form['income']
        purpose = request.form['purpose']

        add_loan(
            session['customer_id'],
            loan_type,
            amount,
            tenure,
            income,
            purpose
        )
        
        add_transaction(
            session['customer_id'],
            "Loan Application",
            amount,
            "Pending"
        )
        
        return redirect(url_for('loan'))

    loans = get_loans(session['customer_id'])

    return render_template(
        "loan.html",
        customer=customer,
        loans=loans
    )
# ---------------- TRANSACTION ----------------

@app.route('/transaction')
def transaction():

    if 'customer_id' not in session:
        return redirect(url_for('customer_login'))

    customer = get_customer(session['customer_id'])

    transactions = get_transactions(session['customer_id'])

    return render_template(
        "transaction.html",
        customer=customer,
        transactions=transactions
    )
# ---------------- ADMIN ----------------

@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')


@app.route('/customers')
def customers():
    return render_template('customers.html')


@app.route('/approve_transfer')
def approve_transfer():
    return render_template('approve_transfer.html')


@app.route('/approve_loan')
def approve_loan():
    return render_template('approve_loan.html')


@app.route('/reports')
def reports():
    return render_template('reports.html')


# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('customer_login'))


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)