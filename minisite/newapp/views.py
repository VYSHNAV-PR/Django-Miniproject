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
     
    for item in items:
        item.total=item.product.price*item.quantity
    # ✅ Calculate total price
    total_price = sum(item.product.price * item.quantity for item in items)

    if request.method == "POST":

        # ✅ DELETE ITEM
        if 'delete_item' in request.POST:
            item_id = request.POST.get('delete_item')
            Cart.objects.filter(id=item_id, user=request.user).delete()
            return redirect('cart')

        # ✅ PLACE ORDER
        selected_ids = request.POST.getlist('selected_items')

        if selected_ids:
            selected_items = Cart.objects.filter(id__in=selected_ids, user=request.user)

            for item in selected_items:
                Order.objects.create(
                    user=request.user,
                    product=item.product,
                    quantity=item.quantity
                )

            selected_items.delete()
            return redirect('success')

    # ✅ Pass total_price to template
    return render(request, 'cart.html', {'items': items, 'total_price': total_price})

def search(request):
    query = request.GET.get('q')
    items = Product.objects.all()

    if query:
        items = items.filter(name__icontains=query)

    return render(request, 'view_products.html', {
        'items': items,
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
    cart_items = Cart.objects.filter(user=request.user)

    if request.method == "POST":
        # ✅ Get address details
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # ✅ Store in session (optional)
        request.session['name'] = name
        request.session['email'] = email
        request.session['phone'] = phone
        request.session['address'] = address

        # ✅ Get payment method
        method = request.POST.get('payment_method')

        # ✅ COD
        if method == "cod":
            for item in cart_items:
                Order.objects.create(
                    user=request.user,
                    product=item.product,
                    quantity=item.quantity
                )

            cart_items.delete()
            return redirect('success')

        # ✅ STRIPE
        elif method == "stripe":
            return redirect('stripe_checkout')

    return render(request, 'checkout.html')


@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'order.html', {'orders': orders})


def success(request):
    return render(request, 'success.html')
# @login_required
# def cart(request):
#     items = Cart.objects.filter(user=request.user)

#     if request.method == "POST":

#         # ✅ DELETE ITEM
#         if 'delete_item' in request.POST:
#             item_id = request.POST.get('delete_item')
#             Cart.objects.filter(id=item_id, user=request.user).delete()
#             return redirect('viewcart')

#         # ✅ PLACE ORDER
#         selected_ids = request.POST.getlist('selected_items')

#         if selected_ids:
#             selected_items = Cart.objects.filter(id__in=selected_ids, user=request.user)

#             for item in selected_items:
#                 Order.objects.create(
#                     user=request.user,
#                     product=item.product,
#                     quantity=item.quantity
#                 )

#             selected_items.delete()
#             return redirect('vieworders')

#     return render(request, 'cart.html', {'items': items})
