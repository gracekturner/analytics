
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.db import models
from .forms import *
import openpyxl
import pandas
import xlrd
from .models import *
from .presentation import *
from decimal import *
from .choices import *
from django.utils.translation import gettext as _
from .lyticmethods import *
import re
import ast
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
# run homepage. The carousel was murder let me tell you.
def homepage(request):
    templates = {}
    templates['signup'] =  UserForm()
    templates['login'] = Login()
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            name = request.POST.get('username', '')
            psw = request.POST.get('password', '')
            if User.objects.filter(username=name).exists():
                return HttpResponse("This Username is already taken.")
            #create user profile
            user = User(username = name)
            user.set_password(psw)
            user.save()

            #create user settings
            create_settings(name)


        user_form = Login(request.POST)
        if user_form.is_valid():
            name = request.POST.get('username', '')
            psw = request.POST.get('password', '')
            user = authenticate(username = name, password = psw)
            if user is None:
                return HttpResponse("Your login or password is incorrect.")
        login(request, user)
        return redirect('main', netid=name)



    return render(request, 'analytics/homepage.html', templates)


# parse the excel sheet, pull the appropriate column, and create Text models for each row entry
# and associated to the ID.
def parse(excel, sheet, name, title, ID, id_object):
    data = pandas.read_excel(excel, sheetname = sheet)
    if data.empty:
        return title
    desc =  str(title) + "\n" + str(excel) + "\n" + str(sheet) + "\n" + str(name) + "\n"
    titl = "Dataset" + "_" + str(ID)

    new_data = Property(description = desc, title= titl )
    new_data.save()
    text = data[name]
    for each in text:
        new_text = Text(text = each)
        new_text.save()
        new_text.properties.add(new_data)
    id_object.properties.add(new_data)
    return title


def network(request, netid, dataid):
    if not request.user.is_authenticated():
        return HttpResponse("You are not logged in.")

    id_object, dataname, anlytmethod, presentmethod = pull_settings(netid)
    if dataname != "NULL":
        list_of_text_objects = id_object.properties.filter(description__contains = dataname)[0].text_set.all()
    return networkgraph2(id_object.properties.filter(title__contains = "Similarity_Score_" + dataname)[0], dataid = int(dataid))
# creates the image appropriately, associated with the netid.
def image(request, netid):
    if not request.user.is_authenticated():
        return HttpResponse("You are not logged in.")

    id_object, dataname, anlytmethod, presentmethod = pull_settings(netid)

    if anlytmethod == "":
        return blankimage()
    if  presentmethod == "":
        return blankimage()

    if dataname != "NULL":
        list_of_text_objects = id_object.properties.filter(description__contains = dataname)[0].text_set.all()
    if anlytmethod == "0":
        sentiment(list_of_text_objects, id_object, dataname)
        if presentmethod == "0":
            return piechart(id_object.properties.filter(title__contains = "Sentiment_Score_" + dataname)[0])
        if presentmethod == "1":
            return barchart(id_object.properties.filter(title__contains = "Sentiment_Score_" + dataname)[0])
    if anlytmethod == "1":
        print " i get here"
        keywords = ast.literal_eval(id_object.properties.filter(title__contains = "Keyword_Dict_")[0].description)
        cat_objects = categorizer(list_of_text_objects, keywords, id_object, dataname)
        print cat_objects.description
        if presentmethod == "0":

            return piechart(cat_objects)
        if presentmethod == "1":
            return barchart(cat_objects)
    if anlytmethod == "2":
        similarity_score2(list_of_text_objects, id_object, dataname)
        return networkgraph2(id_object.properties.filter(title__contains = "Similarity_Score_" + dataname)[0], dataid = "")
    if anlytmethod == "3":
        chart_object = topic_fingerprint_builder(list_of_text_objects, id_object, dataname)
        return bubblechart(chart_object)
        #return blankimage()
def create_settings(netid):
    text = netid + "***GA***\n\n\n"
    id_object = Text(text = text)
    id_object.save()

def pull_settings(netid):
    #get setting Text model for the netid.
    id_object = Text.objects.filter(text__contains = netid + "***GA***")[0]

    # get current dataset/analytic method/presentation settings
    portions = id_object.text.split('\n')
    dataname = portions[1]
    anlytmethod = portions[2]
    presentmethod = portions[3]

    #return {"settings": settings, "dataname": dataname, "anlytmethod": anlytmethod, "presentmethod": presentmethod}
    return id_object, dataname, anlytmethod, presentmethod

def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return redirect('homepage')

def push_settings(id_object, dataname, anlytmethod, presentmethod, netid):

    id_object.text = str(netid) + "***GA***\n" + dataname + "\n" + anlytmethod + "\n" + presentmethod
    id_object.save()
    return id_object, dataname, anlytmethod, presentmethod

def pull_datasets(id_object, netid):
    datasets = id_object.properties.filter(title = "Dataset_" + str(netid))
    titles = []

    for each in datasets:
        name = each.description.split("\n")[0]
        titles.append(name)

    return titles, datasets

def get_dataset_options(id_object, netid):
    titles,datasets = pull_datasets(id_object, netid)
    dataset_options = options_builder(titles)
    action = ("00", _("New Dataset"))
    dataset_options+= (action,)
    return dataset_options

def parse_post(request, netid):

    #get past id_object, dataname, anlytmethod, presentmethod
    id_object, dataname, anlytmethod, presentmethod = pull_settings(netid)

    # if dataset is a new File
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():

        excel = request.FILES['new_data']
        dataname = request.POST.get('dataset_title', '')
        sheet = request.POST.get('sheet_name', '')
        col = request.POST.get('text_name', '')
        title = request.POST.get('dataset_title', '')
        dataname = parse(excel,sheet, col, title, netid, id_object)


    # if dataset is an old file
    dataset_options = get_dataset_options(id_object, netid)
    form = CurrentFiles(request.POST, choice = dataset_options)
    if form.is_valid():
        dataname = dataset_options[int(request.POST.get('optionfile', ''))][1]

    # if presentation method changes
    form = PresentMethod(request.POST, choice = PRESENTATION_SENTIMENT_OPTIONS)
    if form.is_valid():
        presentmethod = request.POST.get('optionpresent', '')

    # if analysis method changes
    form = AnalyticMethod_S(request.POST)
    if form.is_valid():
        anlytmethod = request.POST.get('optionlytic', '')
        if anlytmethod == "2":
            if dataname != "NULL":
                list_of_text_objects = id_object.properties.filter(description__contains = dataname)[0].text_set.all()
                similarity_score2(list_of_text_objects, id_object, dataname)
        if anlytmethod == "3":
            if dataname != "NULL":
                list_of_text_objects = id_object.properties.filter(description__contains = dataname)[0].text_set.all()
                topic_fingerprint_builder(list_of_text_objects, id_object, dataname)

    # if categorizer changes
    form = CurrentCategoryModel(request.POST)
    if form.is_valid():
        anlytmethod = "1"
        mtitle = request.POST.get('model_title', '')
        count = 0
        extra = {}
        while request.POST.get('extra_key_' + str(count), '') :
            key = request.POST.get('extra_key_' + str(count), '')
            cat = request.POST.get('extra_cat_' + str(count), '')
            delete = request.POST.get('extra_delete_' + str(count), '')
            if not delete:
                extra[key] = cat
            count+=1
        if id_object.properties.filter(title__contains = "Keyword_Dict_"):
            p = id_object.properties.filter(title__contains = "Keyword_Dict_")[0]
        else:
            p = Property()
        p.title = "Keyword_Dict_" + mtitle
        p.description = str(extra)
        p.save()
        if not id_object.properties.filter(title__contains = "Keyword_Dict_"):
            id_object.properties.add(p)


    push_settings(id_object, dataname, anlytmethod, presentmethod, netid)
    return

def get_text(id_object, dataname):
    list_of_text_objects = id_object.properties.filter(description__contains = dataname)[0].text_set.all()
    text = []
    count = 0
    for each in list_of_text_objects:
        if "***GA***" in each.text:
            continue
        text.append({"id": count, "text": each.text})
        count+=1
    return text
def main(request, netid):
    if not request.user.is_authenticated():
        return HttpResponse("You are not logged in.")
    if request.user.username != netid:
        return HttpResponse("You do not have access to this")

    if request.method == "POST":
        parse_post(request, netid)

    ## get the new settings ##
    id_object, dataname, anlytmethod, presentmethod = pull_settings(netid)

    if id_object.properties.filter(title__contains = "Keyword_Dict"):
        keydict = id_object.properties.filter(title__contains = "Keyword_Dict")[0]
        extra = ast.literal_eval(keydict.description)
        title = keydict.title.replace("Keyword_Dict_", "")
        keydict = [{'key': x, 'dict': extra[x]}
                       for x in extra]


    else:
        keydict = []
        title = ""
    ## build forms##
    form = {}
    form['form_data'] = UploadFileForm()
    form['form_anlyt'] = AnalyticMethod_S()
    form['form_present'] = PresentMethod( choice = PRESENTATION_SENTIMENT_OPTIONS)
    form['form_options'] = CurrentFiles( choice =  get_dataset_options(id_object, netid))
    #form['form_anlyt_cat'] = CurrentCategoryModel(initial={'model_title': title},extra = extra)
    form['form_anlyt_cat'] = CurrentCategoryModel(initial={'model_title': title})
    form['form_anlyt_cat_extras'] = keydict
    ## build dataset settings ##
    form['dataset'] = dataname
    if anlytmethod == "":
        form['anlyt'] = ""
    else: form['anlyt'] = int(anlytmethod)
    if anlytmethod == "2":
        list_of_text_objects = id_object.properties.filter(description__contains = dataname)[0].text_set.all()
        similarity_score2(list_of_text_objects, id_object, dataname)

        data = id_object.properties.filter(title = "Similarity_Score_" + dataname)[0].description
        pos = eval(data.split("\n")[2])
        form['pos'] = [{'id': each, 'x': str(Decimal(pos[each].split(",")[0])*442 + 20) , 'y': str((1- Decimal(pos[each].split(",")[1]))*442 + 15)} for each in pos]
        form['dataid'] = get_text(id_object, dataname)
    form['present'] = presentmethod
    form['netid'] = netid
    return render(request, 'analytics/maintwo.html', form)
