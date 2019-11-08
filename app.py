import os
import stripe
from flask import Flask, render_template, request, redirect, url_for, abort, jsonify

app = Flask(__name__)

stripe_keys = {
  'secret_key': os.environ.get('STRIPE_SECRET_KEY'),
  'publishable_key': os.environ.get('STRIPE_PUBLISHABLE_KEY')
}

stripe.api_key = stripe_keys['secret_key']

@app.route('/')
def index():
    return render_template("index.html")

products_list = [
    {
        'id': 1,
        'name': 'Apple',
        'description': 'Something really, really special',
        'amount': 600
    },
    {
        'id': 2,
        'name': 'Banana',
        'description': 'Something even more special',
        'amount': 700
    },
]


@app.route('/products')
def list_products():
    return render_template("products.html", products=products_list)

def get_product(product_id):
    for product in products_list:
        if product['id'] == product_id:
            return product
    return False


@app.route('/products/<int:product_id>')
def product(product_id):
    product = get_product(product_id)
    if product:
        product['amount_in_dollars'] = product['amount'] / 100
        return render_template(
            'charges/new.html',
            key=stripe_keys['publishable_key'],
            product=product
        )
    return abort(404)


@app.route('/charge', methods=['POST'])
def charge():
    response = jsonify('error')
    response.status_code = 500

    product = get_product(int(request.json['product']))
    if product:
        try:
            product = get_product(int(request.json['product']))
            customer = stripe.Customer.create(
                email='sample@customer.com',
                source=request.json['token']
            )
            result = stripe.Charge.create(
                customer=customer.id,
                amount=product['amount'],
                currency='usd',
                description=product['description']
            )
            response = jsonify('success')
            response.status_code = 202
        except stripe.error.StripeError:
            return response

    return response

@app.route('/charges/<charge_id>')
def show_charge(charge_id):
    result = stripe.Charge.retrieve(charge_id)
    return render_template('charges/charge.html', result=result)

if __name__ == '__main__':
    app.run()
