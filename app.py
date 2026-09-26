from models import (
    add_transfer,
    get_transfers,
    get_beneficiaries,
    
)

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
    get_all_transfers,
    admin_total_customers,
    admin_total_loans,
    approve_transfer_request,
    approve_loan_request,
    get_all_loans,
    admin_total_transactions,
    admin_total_fd
)


app = Flask(__name__)

app.secret_key = "onlinebank123"


# =====================================================
# HOME
# =====================================================

@app.route('/')
def home():
    return render_template('index.html')


# =====================================================
# REGISTER
# =====================================================

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

        bank_name = request.form['bank_name']
        account_number = request.form['account_number']
        ifsc = request.form['ifsc']
        balance = request.form['balance']

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

        return redirect(url_for('customer_login'))

    return render_template("register.html")


# =====================================================
# CUSTOMER LOGIN
# =====================================================

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


# =====================================================
# CUSTOMER DASHBOARD
# =====================================================

@app.route("/customer_dashboard")
def customer_dashboard():

    if "customer_id" not in session:
        return redirect(url_for("customer_login"))

    customer_id = session["customer_id"]

    customer = get_customer(customer_id)

    transactions = get_transactions(customer_id)
    loans = get_loans(customer_id)
    fixed_deposits = get_fixed_deposits(customer_id)

    return render_template(
        "customer_dashboard.html",
        customer=customer,
        transactions=transactions,
        loans=loans,
        fixed_deposits=fixed_deposits
    )


# =====================================================
# PROFILE
# =====================================================

@app.route('/profile', methods=['GET', 'POST'])
def profile():

    if 'customer_id' not in session:
        return redirect(url_for('customer_login'))

    customer_id = session['customer_id']

    if request.method == "POST":

        update_customer(
            customer_id,
            request.form['name'],
            request.form['email'],
            request.form['phone'],
            request.form['gender'],
            request.form['address']
        )

        return redirect(url_for('profile'))

    customer = get_customer(customer_id)

    return render_template(
        'profile.html',
        customer=customer
    )


# =====================================================
# CHANGE PASSWORD
# =====================================================

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():

    if 'customer_id' not in session:
        return redirect(url_for('customer_login'))

    customer = get_customer(session['customer_id'])

    if request.method == 'POST':

        new_password = request.form.get('password')

        if not new_password:

            return render_template(
                'change_password.html',
                customer=customer,
                error="Please enter a new password."
            )

        update_password(
            session['customer_id'],
            new_password
        )

        return redirect(url_for('customer_dashboard'))

    return render_template(
        'change_password.html',
        customer=customer
    )


# =====================================================
# ACCOUNT
# =====================================================

@app.route('/account')
def account():

    if 'customer_id' not in session:
        return redirect(url_for('customer_login'))

    customer = get_customer(session['customer_id'])

    return render_template(
        'account.html',
        customer=customer
    )


# =====================================================
# TRANSFER
# =====================================================

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():

    if 'customer_id' not in session:
        return redirect(url_for('customer_login'))

    customer_id = session['customer_id']

    customer = get_customer(customer_id)

    beneficiaries = get_beneficiaries(customer_id)

    if request.method == 'POST':

        beneficiary_id = request.form.get('beneficiary')
        transfer_type = request.form.get('transfer_type')
        amount = request.form.get('amount')
        remarks = request.form.get('remarks', '')

        success, message = add_transfer(
            customer_id,
            beneficiary_id,
            transfer_type,
            amount,
            remarks
        )

        if success:
            return redirect(url_for('transfer'))

        transfers = get_transfers(customer_id)

        return render_template(
            'transfer.html',
            customer=get_customer(customer_id),
            beneficiaries=get_beneficiaries(customer_id),
            transfers=transfers,
            error=message
        )

    transfers = get_transfers(customer_id)

    return render_template(
        'transfer.html',
        customer=customer,
        beneficiaries=beneficiaries,
        transfers=transfers
    )


# =====================================================
# BENEFICIARY
# =====================================================

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


# =====================================================
# BILL PAYMENT
# =====================================================

@app.route('/billpayment', methods=['GET', 'POST'])
def billpayment():

    if 'customer_id' not in session:
        return redirect(url_for('customer_login'))

    customer_id = session['customer_id']

    if request.method == "POST":

        bill_type = request.form['bill_type']
        consumer_number = request.form['consumer_number']
        provider = request.form['provider']
        amount = request.form['amount']

        success, message = add_bill_payment(
            customer_id,
            bill_type,
            consumer_number,
            provider,
            amount
        )

        if not success:

            customer = get_customer(customer_id)
            bills = get_bill_payments(customer_id)

            return render_template(
                "billpayment.html",
                customer=customer,
                bills=bills,
                error=message
            )

        return redirect(url_for('billpayment'))

    customer = get_customer(customer_id)
    bills = get_bill_payments(customer_id)

    return render_template(
        "billpayment.html",
        customer=customer,
        bills=bills
    )


# =====================================================
# FIXED DEPOSIT
# =====================================================

@app.route('/fixeddeposit', methods=['GET', 'POST'])
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

        return redirect(url_for('fixeddeposit'))

    fds = get_fixed_deposits(session['customer_id'])

    return render_template(
        "fixeddeposit.html",
        customer=customer,
        fds=fds
    )


# =====================================================
# LOAN
# =====================================================

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


# =====================================================
# TRANSACTION
# =====================================================

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


# =====================================================
# ADMIN LOGIN
# =====================================================

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        admin_id = request.form.get('admin_id')
        password = request.form.get('password')

        if admin_id == 'ADM1234' and password == '1234':

            session['admin_logged_in'] = True

            return redirect(url_for('admin_dashboard'))

        return render_template(
            'admin_login.html',
            error='Invalid Admin ID or Password'
        )

    return render_template('admin_login.html')


# =====================================================
# ADMIN DASHBOARD
# =====================================================

@app.route('/admin_dashboard')
def admin_dashboard():

    return render_template(
        'admin_dashboard.html'
    )

# =====================================================
# ADMIN - CUSTOMERS
# =====================================================

@app.route('/customers')
def customers():

    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    customers = get_all_customers()

    return render_template(
        'customers.html',
        customers=customers
    )


# =====================================================
# ADMIN - APPROVE TRANSFER
# =====================================================

@app.route('/approve_transfer')
def approve_transfer():

    transfers = get_all_transfers()

    return render_template(
        'approve_transfer.html',
        transfers=transfers
    )

# =====================================================
# ADMIN - APPROVE INDIVIDUAL TRANSFER
# =====================================================

@app.route('/approve_transfer/<int:transfer_id>')
def approve_transfer_action(transfer_id):

    approve_transfer_request(transfer_id)

    return redirect(url_for('approve_transfer'))


# =====================================================
# ADMIN - APPROVE LOAN
# =====================================================

@app.route('/approve_loan')
def approve_loan():

    loans = get_all_loans()

    return render_template(
        'approve_loan.html',
        loans=loans
    )
# =====================================================
# ADMIN - APPROVE INDIVIDUAL LOAN
# =====================================================

@app.route('/approve_loan/<int:loan_id>')
def approve_loan_action(loan_id):

    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    approve_loan_request(loan_id)

    return redirect(url_for('approve_loan'))


# =====================================================
# ADMIN - REPORTS
# =====================================================
@app.route('/reports')
def reports():

    customers = get_all_customers()

    report = {
        'customers': len(customers),
        'loans': 0,
        'transfers': 0,
        'fds': 0,
        'bills': 0,
        'balance': 0
    }
    return render_template(
        'reports.html',
        report=report
    )
# =====================================================
# ADMIN LOGOUT
# =====================================================

@app.route('/admin_logout')
def admin_logout():

    session.pop('admin_logged_in', None)

    return redirect(url_for('admin_login'))


# =====================================================
# CUSTOMER LOGOUT
# =====================================================

@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('customer_login'))


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)