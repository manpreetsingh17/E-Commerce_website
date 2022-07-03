from django.db import models


class Product(models.Model):
    product_id = models.AutoField  # auto field is an integer field that automatically increments acc to available ids
    product_name = models.CharField(max_length=50)#same as auto field but for characters and max length is the parameter
    category = models.CharField(max_length=50,default="")
    subcategory = models.CharField(max_length=50,default="")
    price = models.IntegerField(default=0)#default islie dal rhe hai kyuki jo products hamne add kiye hai database me(ghadi) unme jo abhi add kiye vo nhi hai eg(category,image etc)islie admin confused that is why adding default
    desc = models.CharField(max_length=300)
    pub_date = models.DateField()
    image = models.ImageField(upload_to="shop/images",default="")

    def __str__(self):
        return self.product_name


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True) # auto field is an integer field that automatically increments acc to available ids
    name = models.CharField(max_length=50)#same as auto field but for characters and max length is the parameter
    email = models.CharField(max_length=70,default="")
    phone = models.CharField(max_length=70,default="")
    desc = models.CharField(max_length=300,default="")


    def __str__(self):
        return self.name


class Orders(models.Model):
    order_id = models.AutoField(primary_key = True)
    items_json = models.CharField(max_length=5000)
    amount = models.IntegerField(default=0)
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=111)
    address = models.CharField(max_length=111)
    city = models.CharField(max_length=111)
    state = models.CharField(max_length=111)
    zip_code = models.CharField(max_length=111)
    phone = models.CharField(max_length=111,default="")


class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key = True)
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:7] + "..."