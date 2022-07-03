from django.shortcuts import render
from .models import Product, Contact, Orders, OrderUpdate  # importing the products from database
from math import ceil  # import the ceil function from math
import json
from django.http import HttpResponse
from . import Checksum

MERCHANT_KEY = 'VMLsKh7413179871'


def index(request):
    # products = Product.objects.all()
    # print(products)
    # n = len(products)
    # nSlides = n // 4 + ceil((n / 4) - (n // 4))

    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    # params = {'no_of_slides': nSlides, 'range': range(1,nSlides), 'product': products}
    # allProds = [[products, range(1, nSlides), nSlides],
    # [products, range(1, nSlides), nSlides]]
    params = {'allProds': allProds}
    return render(request, 'shop/index.html', params)


def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query.lower() in item.desc.lower() or query.lower() in item.product_name.lower() or query.lower() in item.category.lower():
        return True
    else:
        return False


def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds}
    if len(allProds) == 0 or len(query)<3:
        params = {'msg':"Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    submitted = False
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone,
                          desc=desc)  # jp pehla wala argument hai vo database ka hai aur second vala uper se lia hai is se hum form me values ko database se connect kar sakte hai
        contact.save()
        submitted = True
    return render(request, 'shop/contact.html', {'submitted': submitted})


def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order) > 0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success","updates":updates, "itemsJson":order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"no item"}')
        except Exception as e:
            return HttpResponse('{status":"error"}')

    return render(request, 'shop/tracker.html')



def productView(request, myid):
    # fetch the product using id
    product = Product.objects.filter(id=myid)

    return render(request, 'shop/prodview.html', {'product': product[0]})


def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        order = Orders(items_json=items_json, name=name, amount=amount, email=email, phone=phone,
                       address=address, city=city, state=state,
                       zip_code=zip_code)  # jp pehla wala argument hai vo database ka hai aur second vala uper se lia hai is se hum form me values ko database se connect kar sakte hai
        order.save()
        update = OrderUpdate(order_id=order.order_id,
                             update_desc="The order has been placed")  # all these values are updated on the database django-admin
        update.save()
        thank = True
        id = order.order_id
        # return render(request, 'shop/checkout.html',{'thank':thank, 'id':id})
        # request paytm to transfer the amount to your account after payment by user
        param_dict = {
            'MID': 'VMLsKh3337469871',
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlepayment/',
        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'shop/paytm.html', {'param_dict': param_dict})
    return render(request, 'shop/checkout.html')


def productname(request):
    products = Product.objects.all()
    return render(request, 'shop/productname.html', {
        'all_products': products})  # third parameter here gives the html file the required dictionary(prodcuts) to retreive the data(name of product)


def handlerequest(request):
    # paytm will send you post request here hence exempt it from csrf token
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not sucessful becouse' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})
