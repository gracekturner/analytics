from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.db import models
from .models import *
from decimal import *
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from pylab import figure, axes, pie, title
import numpy as np
import networkx as nx

def labels_and_values (chart_object):

    # pull out frequency labels and values (space separated file)
    bits = chart_object.description.split("\n")
    labels = []
    values = []
    for i in range(0, len(bits)-1, 2):
        labels.append(bits[i] + " " + bits[i+1])
        values.append(int(bits[i+1]))
    return labels, values

# takes a specifically formatted Property data object, creates a pie chart,
#returns image as a HttpResponse rendering.
def piechart(chart_object):
    hfont = {'fontname':'Roboto'}
    title = chart_object.title.split("_")[-1] + " "+ chart_object.title.split("_")[0] +" Analysis"
    labels, values = labels_and_values(chart_object)

    #build pie chart using matplotlib.
    f = figure(figsize=(6,6))
    ax = axes([0.1, 0.1, 0.8, 0.8])
    f.patch.set_facecolor('white')
    f.suptitle(title, fontsize = 25, fontname ='Roboto')

    patches, texts = plt.pie(values, startangle = 90)
    plt.legend(patches, labels, loc="best")

    #send to HttpResponse. To be honest, don't know exactly how this works.
    canvas = FigureCanvasAgg(f)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    plt.close(f)

    #return response
    return response

def networkgraph2(chart_object, dataid = ""):

    settings = chart_object.description.split("\n")


    graph = eval(chart_object.description.split("\n")[0])

    r = int(chart_object.description.split("\n")[1])
    newdict = eval(chart_object.description.split("\n")[2])
    pos = {}
    labels = {}
    G=nx.Graph()

    G.add_nodes_from(range(r))
    G.add_edges_from(graph)
    for each in newdict:
        splits = newdict[each].split(",")
        pos[each] = np.array([splits[0], splits[1]], dtype = 'float64')
    if dataid != "":
        nodes = set()
        nodes.add(dataid)
        prevlen = 0
        value = True
        while value:
            prevlen = len(nodes)
            newset = set()
            for each in nodes:
                val = G.neighbors(each)
                for v in val:
                    newset.add(v)
                    if len(nodes.union(newset)) >= 20: break
                if len(nodes.union(newset)) >= 20: break
            nodes = nodes.union(newset)
            if len(nodes) > 20:
                value = False
            if prevlen == len(nodes):
                value = False

        G = G.subgraph(list(nodes))

        pos = nx.fruchterman_reingold_layout(G)
        for each in G.nodes():
            labels[each] = str(each)


    #print graph

    f = figure(figsize= (6,6))
    #nx.draw(G, nx.get_node_attributes(G, 'pos'), with_labels=True, node_size=200)
    #nx.draw(G, pos)
    #sub_graphs = list(nx.connected_component_subgraphs(G))

    #send to http response
    col_list = plt.cm.get_cmap("Pastel1", 1)
    print col_list(0)

    #for i in range(0, len(sub_graphs)):
    #    nx.draw(sub_graphs[i], nx.get_node_attributes(sub_graphs[i], 'pos'), node_color =col_list(i), node_size = 200 )
    nx.draw(G, pos, node_size=400, node_color = 'aliceblue')
    if labels:
        nx.draw(G, pos, node_size=1000, node_color = 'aliceblue')
        nx.draw_networkx_labels(G,pos,labels,font_size=15)
    else:
        nx.draw(G, pos, node_size=400, node_color = 'aliceblue')
    canvas = FigureCanvasAgg(f)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response


def networkgraph(chart_object):
    graph = chart_object.description.strip("\n").split("\n")
    title = chart_object.title.replace("Similarity_Score_", "")
    uncon = eval(graph[-1:][0])
    graph = [eval(each) for each in graph][:-1]


    f = figure(figsize= (7,7))
    nodies = set([n1 for n1, n2 in graph] + [n2 for n1, n2 in graph])
    #nodies = nodies.union(uncon)
    labels = {}
    # create networkx graph
    G=nx.Graph()

     #add nodes
    for node in nodies:
        G.add_node(node)
        labels[node] = str(node)

    G.add_nodes_from(range(e))
    G.add_edges_from(graph)

    #titles
    plt.title("Network Graph of " + title)

    sub_graphs = list(nx.connected_component_subgraphs(G))
    number_sub_graphs = nx.number_connected_components(G)
    col_list = plt.cm.get_cmap("Pastel1", number_sub_graphs)

    pos = nx.fruchterman_reingold_layout(G)
    for i in range(0, number_sub_graphs):
            nx.draw(sub_graphs[i], pos, node_color =col_list(i), node_size = 200 )
    nx.draw_networkx_labels(G, pos, labels)




    #send to http response
    canvas = FigureCanvasAgg(f)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    plt.close(f)

    return response

def blankimage():
    f = figure(figsize=(6,6))
    f.patch.set_facecolor('white')
    canvas = FigureCanvasAgg(f)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    plt.close(f)

    #return response
    return response


def barchart(chart_object):

    labels, values = labels_and_values(chart_object)
    labels = [""] + labels
    values = [0] + values

    fig, (ax0) = plt.subplots(nrows=1, figsize=(6,6))
    fig.patch.set_facecolor('white')
    y_pos = np.arange(len(tuple(labels)))
    ax0.bar(y_pos, tuple(values), align='edge')
    ax0.spines['top'].set_visible(False)
    ax0.spines['right'].set_visible(False)
    ax0.yaxis.set_ticks_position('left')
    ax0.xaxis.set_ticks_position('bottom')
    plt.xticks(y_pos, tuple(labels), rotation = 30)
    plt.tight_layout()


    #send to HttpResponse. To be honest, don't know exactly how this works.
    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    plt.close(fig)

    return response
