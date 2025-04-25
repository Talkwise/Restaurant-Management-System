from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import * 
import datetime
from django import forms 
from django.contrib.auth.decorators import user_passes_test
# Create your views here.


    

def configure(request):
    if request.method == "POST":
        if Configuration.objects.first():
            restaurant = Configuration.objects.first()
            restaurant.title =  request.POST['restaurant_name'] 
            restaurant.logo = request.FILES.get('logo')
        else:
            restaurant = Configuration(title = request.POST['restaurant_name'],logo=request.FILES.get('logo'))
        restaurant.save()
        
        
    return render(request,"restaurant/configure.html")

def is_admin(user):
    return user.is_authenticated and user.is_admin

def index(request):
    

    
    return render(request,"restaurant/index.html",{
        'user':request.user,
        'menu_items' : Menu.objects.all(),
       
        
        
        })
    


def login_view(request):
    if request.method == "POST":

        
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
       
        if user is not None: 
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "restaurant/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "restaurant/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone_number = request.POST['phone_number']
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "restaurant/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = CustomUser.objects.create_user(username, email, password,first_name=first_name,last_name=last_name,phone_number=phone_number)
            user.save()
        except IntegrityError:
            return render(request, "restaurant/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "restaurant/register.html")


def add_to_cart(request, item_id):
    if request.method == 'POST':
        menu_item = Menu.objects.get(pk=item_id)
        placing_orders_exist = Order.objects.filter(made_by=request.user, status='placing').exists()
        if placing_orders_exist:
            order = Order.objects.filter(made_by=request.user, status='placing').last()
        else:
            order = Order(made_by=request.user)
            order.save()
        
    if order:
        try:
            order_item = OrderItem.objects.get(order=order.id, menu_item=menu_item)
            order_item.quantity += 1
            order_item.save()
        except OrderItem.DoesNotExist:
            order_item = OrderItem.objects.create(order=order, menu_item=menu_item, quantity=1)
 
    order.grand_total = order.calculate_grand_total()
    order.save()
    return render(request,"restaurant/index.html",{
        'user':request.user,
        'menu_items' : Menu.objects.all(),
        'order':order,
        'order_items' :OrderItem.objects.filter(order=order),
        
        })
def remove_item(request,item_id):
    order_item = OrderItem.objects.get(pk=item_id)
    order = order_item.order
    order_item.delete()
    return render(request,"restaurant/index.html",{
        'user':request.user,
        'menu_items' : Menu.objects.all(),
        'order':order,
        'order_items' :OrderItem.objects.filter(order=order),
        
        })
def confirm_order(request):
    
    if request.method == "POST":
        order = Order.objects.get(pk=request.POST['order_id'])

        order.save()
        return render(request,"restaurant/index.html",{
        'user':request.user,
        'menu_items' : Menu.objects.all(),
        'order':order,
        'order_items' :OrderItem.objects.filter(order=order),
        'confirm' : True
        
        })

def place_order(request):
    
    if request.method == "POST":
        order = Order.objects.get(pk=request.POST['order_id'])
        order.status = "placed"
        order.created_at = datetime.datetime.now()
        payment_method = request.POST['paymentMethod']
        order.payment_method = payment_method
        order.save()

        houseNo = request.POST.get('houseNo',False)
        flatNo = request.POST.get('flatNo',False)
        street = request.POST.get('streetAddress',False)
        additional = request.POST.get('additional',False)

        address = ShippingDetails(order=order,houseNo = houseNo,flatNo = flatNo,street=street,additional=additional)
        address.save()

        return render(request, "restaurant/index.html",{
        'user':request.user,
        'menu_items' : Menu.objects.all(),
        'order':order,
        'order_items' :OrderItem.objects.filter(order=order),
        'confirm' : True,
        'placed' : True,
        
        })

def user_orders(request):
    return render(request,"restaurant/user_orders.html" , {
                      "orders":Order.objects.filter(made_by=request.user)}
                  )
@user_passes_test(is_admin)
def admin_home(request):
    return render(request,"restaurant/admin_home.html",{"orders":Order.objects.filter(status__in=['placed','Preparing','Dispatched'])})
@user_passes_test(is_admin)
def change_status(request):
    if request.method == "POST":
        status = request.POST['change_status'] 
        order = Order.objects.get(pk=request.POST['order_id'])
        order.status = status
        order.save()
        return render(request,"restaurant/admin_home.html",{"orders":Order.objects.filter(status__in=['placed','Preparing','Dispatched'])})
@user_passes_test(is_admin)
def manage_menu(request):
    menu_items = Menu.objects.all()
    

    return render(request, 'restaurant/manage_menu.html', {'menu_items': menu_items})


@user_passes_test(is_admin)
def update_item(request):
    if request.method == "POST":
        item = Menu.objects.get(pk=request.POST['item_id'])
        item.item_name = request.POST['item_name']
        item.price = request.POST['item_price']
        item.description = request.POST['item_description']

        if request.FILES.get('item_img'):
            item.image = request.FILES.get('item_img')
        
        item.save()

        return render(request, 'restaurant/manage_menu.html', {'menu_items': Menu.objects.all()})
    
    
@user_passes_test(is_admin)
def add_item(request):
    if request.method == "POST":
        item_name= request.POST['item_name']
        item_price=request.POST['item_price']
        description=request.POST['description']
        item_img = request.FILES.get('item_img')

        new_item = Menu(item_name=item_name,price=item_price,description=description,image=item_img)
        new_item.save()
   
    return render(request,'restaurant/add_item.html')

@user_passes_test(is_admin)
def sales_history(request):
    return render(request,"restaurant/sales_history.html",{
        "orders":Order.objects.filter(status= "Delivered")
    })


def remove_item(request,item_id):
    order_item = OrderItem.objects.get(pk=item_id)
    order = order_item.order
    order_item.delete()
    return render(request,"restaurant/index.html",{
        'user':request.user,
        'menu_items' : Menu.objects.all(),
        'order':order,
        'order_items' :OrderItem.objects.filter(order=order),
        
        })

@user_passes_test(is_admin)
def remove_menu_item(request,item_id):
    menu_item = Menu.objects.get(pk=item_id)
    menu_item.delete()
 
    return render(request,"restaurant/manage_menu.html",
            {'menu_items':  Menu.objects.all()})
                  
