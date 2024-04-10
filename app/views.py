from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pandas as pd

data=pd.read_excel('./files/Sales Info.xlsx',index_col='Date')
cat=['Home Appliances', 'Accessories', 'Kitchen', 'Mobiles', 'Desktops']
sales_data=dict()
for c in cat:
    sales_data[c]=data[data['Category']==c][['Sales']]

from keras.models import load_model
model=dict()
for c in cat:
    fname='./files/'+c+'.h5'
    model[c]=load_model(fname)

import pickle
f=open('./files/scaler.dat','rb')
scaler=pickle.load(f)
f=open('./files/Xin.dat','rb')
Xin=pickle.load(f)
timestep = 30
future=30

def insert_end(Xin,new_input):
    #print ('Before: \n', Xin , new_input )
    for i in range(timestep-1):
        Xin[:,i,:] = Xin[:,i+1,:]
    Xin[:,timestep-1,:] = new_input
    #print ('After :\n', Xin)
    return Xin


def homePage(request):
    return render(request,'home.html')

def registerPage(request):
    form=UserCreationForm()
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    return render(request,'register.html',{'form':form})

def loginPage(request):
    if request.method=='POST':
        uname=request.POST['uname']
        pwd=request.POST['pwd']
        user=authenticate(request,username=uname,password=pwd)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"Invalid User Name / Password")
    return render(request,'login.html')

def logoutPage(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def forecastPage(request):
    if request.method=='POST':
        product=request.POST['product']
        duration=request.POST['duration']
        imgpath={'week':'next_week.png','month':'next_month.png','quarter':'next_quarter.png','year':'next_year.png'}
        filepath={'week':'./files/all_products_next_week.pkl',
                  'month':'./files/all_products_next_month.pkl',
                  'quarter':'./files/all_products_next_quarter.pkl',
                  'year':'./files/all_products_next_year.pkl'}
        if product=='All Products':
            f=open(filepath[duration],'rb')
            data=pickle.load(f)
            sales=0
            for key in data:
                sales=round(sales+sum(data[key]['Forecasted']),0)
            path=imgpath[duration]
        else:
            f=open(filepath[duration],'rb')
            sales=round(sales+sum(data[product]['Forecasted']),0)
            path=imgpath[duration]
        return render(request,'forecast.html',{'path':path,'duration':duration,'product':product,'sales':sales})
    return render(request,'forecast.html')