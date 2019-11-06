import os
import stripe
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

stripe_keys = {
  'secret_key': os.environ.get('STRIPE_SECRET_KEY'),
  'publishable_key': os.environ.get('STRIPE_PUBLISHABLE_KEY')
}

stripe.api_key = stripe_keys['secret_key']

@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/charges/new', methods=['GET'])
def new_charge():
    return render_template('charges/new.html', key=stripe_keys['publishable_key'])

@app.route('/charge', methods=['POST'])
def charge():
    try:
        amount = 500   # amount in cents
        customer = stripe.Customer.create(
            email='sample@customer.com',
            source=request.form['stripeToken']
        )
        result = stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='usd',
            description='Test Charge'
        )
        return redirect(url_for('show_charge',charge_id=result.id))
    except stripe.error.StripeError:
        return render_template('charges/error.html')

@app.route('/charges/<charge_id>')
def show_charge(charge_id):
    result = stripe.Charge.retrieve(charge_id)
    return render_template('charges/charge.html', result=result)

if __name__ == '__main__':
    app.run()
