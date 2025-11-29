from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View  
from django.contrib import messages
from django.contrib.auth import logout
from .models import Customer, Product, Cart, Payment, OrderPlaced, Wishlist
from .forms import CustomerProfileForm, CustomerRegistrationForm
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

# Home, About, Contact
@login_required
def home(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, "app/home.html", locals())

@login_required
def about(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, "app/about.html", locals())

@login_required
def contact(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, "app/contact.html", locals())

@method_decorator(login_required, name='dispatch')
# Category views
class CategoryView(View): 
    def get(self, request, val):
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request, "app/category.html", locals())
    
@method_decorator(login_required, name='dispatch')
class CategoryTitle(View):
    def get(self, request, val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, "app/category.html", locals())


@method_decorator(login_required, name='dispatch')
# product detail
class ProductDetail(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        wishlist = Wishlist.objects.filter(Q(product=product) & Q(user=request.user))

        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, "app/productdetail.html", locals())


@method_decorator(login_required, name='dispatch')
class ProductsView(View):
    """Render a page listing all products with a sidebar of categories and an All Products link."""
    def get(self, request):
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        # Query param for selecting a category from the products page
        selected_category = request.GET.get('category', None)
        if selected_category:
            product = Product.objects.filter(category=selected_category)
        else:
            product = Product.objects.all()
        # Unique categories for sidebar (returns codes like 'AR', 'CD')
        categories = Product.objects.values_list('category', flat=True).distinct()
        # Convert category codes to readable names using CATEGORY_CHOICES
        # We import CATEGORY_CHOICES from models below these classes so it is available in template.
        from .models import CATEGORY_CHOICES
        cat_map = {code: name for code, name in CATEGORY_CHOICES}
        # Pass a list of dictionaries for ease in template
        categories = [{'code': c, 'name': cat_map.get(c, c)} for c in categories]
        return render(request, "app/products.html", {
            "product": product,
            "categories": categories,
            "selected_category": selected_category,
            "totalitem": totalitem,
            "wishitem": wishitem
        })


class CustomLoginView(LoginView):
    """Custom login view that redirects admin/staff users to the Django admin index page after a successful login.

    This class honors `next` if provided, otherwise checks if the user is staff/superuser and redirects to the admin.
    Otherwise it falls back to the site `home` view.
    """
    def get_success_url(self):
        # Respect 'next' redirect param if provided
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        user = self.request.user
        # If user is staff or superuser, send to admin dashboard
        if user and (user.is_staff or user.is_superuser):
            return reverse_lazy('admin:index')
        # Default redirect for ordinary users
        return reverse_lazy('home')

## Customer registration
class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, 'app/customerregistration.html', locals())

    def post(self, request):
        form = CustomerRegistrationForm(request.POST) 
        if form.is_valid():
            form.save()
            success = True
            messages.success(request, "Congratulations! User registered successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return render(request, 'app/customerregistration.html', locals())

@method_decorator(login_required, name='dispatch')
# Profile views
class ProfileViews(View):
    def get(self, request):
        form = CustomerProfileForm()
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, 'app/profile.html', locals())

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(
                user=user,
                name=name,
                locality=locality,
                mobile=mobile,
                city=city,
                state=state,
                zipcode=zipcode
            )
            reg.save()
            messages.success(request, "Congratulations! Profile saved successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return render(request, 'app/profile.html', locals())

@login_required
# Address views
def address(request):
    add = Customer.objects.filter(user=request.user)
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, 'app/address.html', {'add': add})


@method_decorator(login_required, name='dispatch')
class updateAddress(View):
    def get(self, request, pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, 'app/updateAddress.html', locals())

    def post(self, request, pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request, "Congratulations! Profile updated successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return redirect("address")

@login_required
#Custom logout function
def logout_user(request):
    logout(request)
    messages.success(request, "You have logged out successfully")
    return redirect('login')

@login_required
# Cart stuff
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    if not product_id:
        return redirect('home')
    product = Product.objects.get(id=product_id)
    Cart.objects.create(user=user, product=product, quantity=1)
    return redirect('show_cart')

@login_required
def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = sum(p.quantity * p.product.discounted_price for p in cart)
    shipping = 30
    totalamount = amount + shipping
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, 'app/addtocart.html', {
        'cart': cart,
        'amount': amount,
        'shipping': shipping,
        'totalamount': totalamount
    })

@method_decorator(login_required, name='dispatch')
# Checkout
class checkout(View):
    def get(self, request):
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        famount = 0
        for p in cart_items:
            famount += p.quantity * p.product.discounted_price
        totalamount = famount + 40 
        return render(request, "app/checkout.html", {
            "add": add,
            "cart_items": cart_items,
            "totalamount": totalamount,
            "totalitem": totalitem
        })
    
    def post(self, request):
        user = request.user
        cust_id = request.POST.get("custid")
        customer = Customer.objects.get(id=cust_id)

        cart_items = Cart.objects.filter(user=user)

        # Workflow statuses
        STATUS_CHOICES = ["To Ship", "To Deliver", "To Receive", "Completed"]

        # Create orders with initial status "To Ship"
        for item in cart_items:
            OrderPlaced(
                user=user,
                customer=customer,
                product=item.product,
                quantity=item.quantity,
                payment=None,   # no payment record
                status=STATUS_CHOICES[0]  # start at "To Ship"
            ).save()
            item.delete()

        messages.success(request, f"Order placed successfully! Status: {STATUS_CHOICES[0]}")
        return redirect("orders")

@login_required
# Orders
def orders(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    user = request.user
    order_placed = OrderPlaced.objects.filter(user=user)
    return render(request, "app/orders.html", {
        "order_placed": order_placed,
        "totalitem": totalitem
    })

@login_required
# Cart Function
def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()

        cart = Cart.objects.filter(user=request.user)
        amount = sum(p.quantity * p.product.discounted_price for p in cart)
        shipping = 30
        totalamount = amount + shipping

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'shipping': shipping,
            'totalamount': totalamount
        }
        return JsonResponse(data)

@login_required
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        if c.quantity > 1:
            c.quantity -= 1
            c.save()

        cart = Cart.objects.filter(user=request.user)
        amount = sum(p.quantity * p.product.discounted_price for p in cart)
        shipping = 30
        totalamount = amount + shipping

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'shipping': shipping,
            'totalamount': totalamount
        }
        return JsonResponse(data)

@login_required
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()

        cart = Cart.objects.filter(user=request.user)
        amount = sum(p.quantity * p.product.discounted_price for p in cart)
        shipping = 30
        totalamount = amount + shipping

        data = {
            'amount': amount,
            'shipping': shipping,
            'totalamount': totalamount
        }
        return JsonResponse(data)

@login_required
def plus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id'] 
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist(user=user, product=product).save()
        data = {'message': "Added To Wishlist"}
        return JsonResponse(data)

@login_required
def minus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id'] 
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist.objects.filter(user=user, product=product).delete()
        data = {'message': "Removed From Wishlist"}
        return JsonResponse(data)

@login_required
def search(request):
    query = request.GET.get('search', '').upper()

    if query:
        product = Product.objects.filter(
            Q(title__icontains=query) | Q(category__icontains=query)
        )
    else:
        product = Product.objects.none()

    totalitem = wishitem = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()

    return render(request, "app/search.html", {
        "product": product,
        "totalitem": totalitem,
        "wishitem": wishitem,
        "query": query
    })

@login_required
def wishlist(request):
    if not request.user.is_authenticated:
        return redirect("login")

    product = [item.product for item in Wishlist.objects.filter(user=request.user)]

    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()

    return render(request, "app/wishlist.html", {
        "product": product,
        "totalitem": totalitem,
        "wishitem": wishitem,
    })
