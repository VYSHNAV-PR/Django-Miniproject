from django.shortcuts import render,redirect,get_object_or_404
from .models import Product,Cart,Order
from .forms import UserRegisterForm,UserLoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import stripe
from django.conf import settings
from django.urls import reverse
stripe.api_key=settings.STRIPE_SECRET_KEY

# Create your views here.
def home(request):
   return render(request,'home.html')
def view_products(request):
   products=Product.objects.all()
   return render(request,'view_products.html',{'products': products}) 
def register(request):
   form=UserRegisterForm(request.POST or None)
   if request.method =='POST' and form.is_valid():
      form.save()
      return redirect('viewproduct')
   return render(request,'register.html',{"form":form})
def login_form(request):
   forms=UserLoginForm(request,data=request.POST or None)
   if request.method == 'POST' and forms.is_valid():
      user=forms.get_user()
      login(request,user)
      return redirect('home')
   return render(request,'login.html',{'form':forms})
def logout_form(request):
   logout(request)
   return redirect('home')

@login_required
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # messages.success(request, "Item added to cart ✅")
    return redirect('cart')

@login_required
def cart(request):
    items = Cart.objects.filter(user=request.user)

    if request.method == "POST":

        # ❌ DELETE ITEM
        if 'delete_item' in request.POST:
            item_id = request.POST.get('delete_item')
            Cart.objects.filter(id=item_id, user=request.user).delete()
            return redirect('cart')

        # ➕ INCREASE QTY
        if 'increase_qty' in request.POST:
            item_id = request.POST.get('increase_qty')
            item = Cart.objects.get(id=item_id, user=request.user)
            item.quantity += 1
            item.save()
            return redirect('cart')

        # ➖ DECREASE QTY
        if 'decrease_qty' in request.POST:
            item_id = request.POST.get('decrease_qty')
            item = Cart.objects.get(id=item_id, user=request.user)

            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()

            return redirect('cart')

        # ✅ PLACE ORDER (SELECTED ITEMS ONLY)
        if 'place_order' in request.POST:
            selected_ids = request.POST.getlist('selected_items')

            if selected_ids:
                request.session['selected_cart_items'] = selected_ids
                return redirect('checkout')
            else:
                return redirect('cart')

    # 💰 CALCULATE TOTAL
    for item in items:
        item.total = item.product.price * item.quantity

    total_price = sum(item.total for item in items)

    return render(request, 'cart.html', {
        'items': items,
        'total_price': total_price
    })

def search(request):
    query = request.GET.get('q', '').strip()
    products  = Product.objects.all()

    if query:
        products  = Product.objects.filter(name__icontains=query)

    return render(request, 'view_products.html', {
        'products': products,
        'query': query
    })
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_details.html', {'product': product})

@login_required
def place_order(request):
    return redirect('address')


@login_required
def checkout(request):

    selected_ids = request.session.get('selected_cart_items', [])

    # ⚠️ If no items selected → go back
    if not selected_ids:
        return redirect('cart')

    cart_items = Cart.objects.filter(id__in=selected_ids, user=request.user)

    if request.method == "POST":

        # 📦 ADDRESS DETAILS
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        request.session['name'] = name
        request.session['email'] = email
        request.session['phone'] = phone
        request.session['address'] = address

        # 💳 PAYMENT METHOD
        method = request.POST.get('payment_method')

        # ✅ CASH ON DELIVERY
        if method == "cod":
            for item in cart_items:
                Order.objects.create(
                    user=request.user,
                    product=item.product,
                    quantity=item.quantity
                )

            cart_items.delete()
            request.session['selected_cart_items'] = []

            return redirect('success')

        # 💳 STRIPE PAYMENT
        elif method == "stripe":
            line_items = []

            for item in cart_items:
                line_items.append({
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': item.product.name,
                        },
                        'unit_amount': int(float(item.product.price) * 100),
                    },
                    'quantity': item.quantity,
                })

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url='http://127.0.0.1:8000/success/?items=' + ",".join(selected_ids),
                cancel_url='http://127.0.0.1:8000/checkout/',
            )

            return redirect(session.url)

    return render(request, 'checkout.html', {
        'cart_items': cart_items
    })


@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    return render(request, 'order.html', {'orders': orders})


@login_required
def success(request):

    selected_ids = request.GET.get('items', '')

    if selected_ids:
        selected_ids = selected_ids.split(',')
    else:
        selected_ids = request.session.get('selected_cart_items', [])

    cart_items = Cart.objects.filter(id__in=selected_ids, user=request.user)

    for item in cart_items:
        Order.objects.create(
            user=request.user,
            product=item.product,
            quantity=item.quantity
        )

    cart_items.delete()

    # 🧹 CLEAR SESSION
    request.session['selected_cart_items'] = []

    return render(request, 'success.html')

