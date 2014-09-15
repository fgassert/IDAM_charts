#!/usr/bin/env python

#######################################
#IDAM amoeba chart builder
#
#Francis Gassert
#6-30-2011
#######################################

import os, string, math, sys, csv, svg, ConfigParser


#######################################
# Global Variables
#######################################

#configfile if found sets global variables based on file
### not yet implemented
configfile = "defaultconfig.cfg"

class c(object):
    """global variables"""
    
    #savename is the filename to save by .svg is autoappended
    savename = "test"

    #datafile is the filename of the data to be loaded
    #file should be in .csv format of 4 columns labeled magnitudebenefit, saliencebenefit, magnitudecost, saliencecost
    datafile = 'defaultdata.csv'

    #charttype determines chart type as follows:
    # 0 = amoeba
    # 1 = column
    # 2 = bar
    charttype = 2

    #swapsaliencemagnitude swaps the axes to be salience on radius and magnitude by width/color if true(1)
    swapsaliencemagnitude=0

    #saliencebywidth sets whether salience is visualized by wedge (column) width
    #   0 = no, 1 = linear, >1 = log 
    #   suggested values: 0, 1, math.e
    saliencebywidth=1

    #saliencebycolor sets whether salience is visualized by wedge color transparency
    #   0 = no, 1 = linear, >1 = polynomial
    #   suggested values: 0, 2
    saliencebycolor=1

    #xgrid draws dividers between the columns if True(1)
    xgrid = 1
    #ygrid draws gridlines at magnitude values if True(1)
    ygrid = 1
    # drawsaliencedividers draws minor dividers inside wedges (columns) if saliencebywidth is greater than one
    drawsaliencedividers=1
    # includezerosalience displays a value of 0 salience as nonwhite and width > 0 if true(1)
    includezerosalience=1
    # includezeromagnitude displays a value of 0 magnitude as height > 0 if true(1)
    includezeromagnitude=1

    #magnitudearea sets if magnitude rings are sized by radius (0) or by area of wedges (1) (amoeba only)
    magnitudearea=1
    #magnitudelog sets if magnitude rings (bar heights) sized linearly (0) or logarithmicly with base equal to magnitudelog
    #   suggested: 0, math.e
    magnitudelog=2

    #saliencelegend draws a legend for salience values if true
    saliencelegend=1
    #magnitudelegend draws a legend for magnitude values if true
    magnitudelegend=1

    #colorsbenefit and colorscost are lists of three RGB three-tuples for the colors of BP, SE, and GP wedges respectively
    #   suggested: [(0,0,192),(0,0,192),(0,0,192)]
    colorsbenefit = [(0,96,192),(0,96,192),(0,96,192)]
    colorscost = [(192,96,0),(192,96,0),(192,96,0)]

    #each amoeba chart is of size 1000x1000 thus a radius of 500 circle will circumscribe the chart
    #centerradius sets the size of the empty center hole (ameoba only)
    centerradius=155
    #edgeradius sets the radius (height) of the maximum magnitude
    edgeradius=300
    #textradius sets the radius (height) of the labels and dividers
    textradius=350

    #sets fontsize of text; this is proportional to the chartsize of 1000x1000
    #   suggested: 36
    font=36
    
    #centerlabel sets the labeltext that appears in the center of the ameobas (ameoba only)
    #   suggested: ['Positive','Negative'], None 
    centerlabel=['Positive','Negative']
    # title appears above charts if not empty
    title=""

    ##############################
    # bar/column only options
    #spacebars leaves an empty column between the three categories if True(1)
    spacebars = 1
    # ticksize draws ticks of size ticksize if no gridlines
    # 	suggested: 0, 15
    ticksize = 15
    # barline draws a border around bars of width barline if nonzero
    # 	suggested: 0, 3
    barline = 3
    # barlineshade determines how dark the border will be. 0 = black, 1 = color of bar
    # 	suggested: 0,.5
    barlineshade = .5
    
    maxvalue=3

    indicatornames = ['BP1','BP2','BP3','BP4','BP5','BP6','BP7','SE1','SE2','SE3','SE4','SE5','SE6','SE7','GP1','GP2','GP3','GP4','GP5','GP6','GP7',]
    indicatorfullnames = ['BP1','BP2','BP3','BP4','BP5','BP6','BP7','SE1','SE2','SE3','SE4','SE5','SE6','SE7','GP1','GP2','GP3','GP4','GP5','GP6','GP7',]
    
    #testvalues
    magnitudebenefit = [1,2,3,1,2,3,0,1,2,3,1,2,3,0,1,2,3,1,2,3,0,]
    saliencebenefit =  [0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,]
    magnitudecost = [1,2,3,1,2,3,0,1,2,3,1,2,3,0,1,2,3,1,2,3,0,]
    saliencecost =  [0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,]
    
    def __init__(self):
        pass
    

#######################################
def ringradii(i):
    rings=c.maxvalue+c.includezeromagnitude
    if(i==0):
        return c.centerradius
    if(c.magnitudelog):
        if(c.magnitudearea):
            return (math.sqrt((c.edgeradius**2-c.centerradius**2)/(c.magnitudelog**(rings-1))*(c.magnitudelog**(i-1))+c.centerradius**2))
        else:
            return (c.centerradius + (c.edgeradius-c.centerradius)/(c.magnitudelog**(rings-1))*(c.magnitudelog**(i-1)))
    else:
        if(c.magnitudearea):
            return (math.sqrt((c.edgeradius**2-c.centerradius**2)/rings*i+c.centerradius**2))
        else:
            return (c.centerradius + (c.edgeradius-c.centerradius)/rings*i)

#######################################
def barheight(i):
    rings=c.maxvalue+c.includezeromagnitude
    if(i==0):
        return 0
    if(c.magnitudelog):
        return (c.edgeradius/(c.magnitudelog**(rings-1))*(c.magnitudelog**(i-1)))
    else:
        return (c.edgeradius/rings*i)


#######################################
def makecircle(magnitude, salience, benefit=1):
    if c.swapsaliencemagnitude:
        tm = salience[:]
        salience = magnitude[:]
        magnitude = tm
    
    #general variables
    indicatorseparatorangles = [-math.pi*2/21*i + math.pi/21 for i in range(0,22)]
    indicatorcenterangles = [-math.pi*2/21*i for i in range(0,21)]
    wedgeangle = math.pi*2/21
    
    
    out = svg.svg(width=1000, height=1000+100*c.saliencelegend, viewbox='0 0 1000 1%d00' % (1*c.saliencelegend==True))
    
    if(benefit):
        colors=c.colorsbenefit
    else:
        colors=c.colorscost
    if c.centerlabel is not None:
        out.add(svg.text(c.centerlabel[1-benefit], 500, 500, fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))
    
    #draw wedges
    for i in range(0,21):
        r = ringradii(magnitude[i]+c.includezeromagnitude)
        if(c.saliencebywidth==1):
            wedgewidth = wedgeangle/2/(3+c.includezerosalience)*(salience[i]+c.includezerosalience)
        elif(c.saliencebywidth>1):
            wedgewidth = wedgeangle/2/(saliencebywidth**3)*(c.saliencebywidth**salience[i])
        else:
            wedgewidth = wedgeangle/2
        x1 = (500 + math.cos(indicatorcenterangles[i]+wedgewidth)*c.centerradius)
        y1 = (500 + math.sin(indicatorcenterangles[i]+wedgewidth)*c.centerradius)
        x2 = (500 + math.cos(indicatorcenterangles[i]+wedgewidth)*r)
        y2 = (500 + math.sin(indicatorcenterangles[i]+wedgewidth)*r)
        x3 = (500 + math.cos(indicatorcenterangles[i]-wedgewidth)*r)
        y3 = (500 + math.sin(indicatorcenterangles[i]-wedgewidth)*r)
        x4 = (500 + math.cos(indicatorcenterangles[i]-wedgewidth)*c.centerradius)
        y4 = (500 + math.sin(indicatorcenterangles[i]-wedgewidth)*c.centerradius)
        if(c.saliencebycolor):
            s = ((salience[i]+c.includezerosalience)**c.saliencebycolor)/((3.0+c.includezerosalience)**c.saliencebycolor)
        else:
            s = 1
        red,green,blue = colors[i//7]
        d = 'M %s,%s L %s,%s A %s,%s 0 0,0 %s,%s L %s,%s A %s,%s 0 0,1 %s,%s' % (x1,y1,x2,y2,r,r,x3,y3,x4,y4,c.centerradius,c.centerradius,x1,y1)
        if(salience[i]>0 or c.includezerosalience):
            out.add(svg.path(d, fill='rgb(%s,%s,%s)' % (red,green,blue), p='fill-opacity="%s"' % s))
        
            
            
    #draw dividers and text
    for i in range(0,21):
        
        if(c.saliencebywidth and c.drawsaliencedividers):
            x1 = (500 + math.cos(indicatorcenterangles[i])*c.centerradius)
            y1 = (500 + math.sin(indicatorcenterangles[i])*c.centerradius)
            x2 = (500 + math.cos(indicatorcenterangles[i])*c.edgeradius)
            y2 = (500 + math.sin(indicatorcenterangles[i])*c.edgeradius)
            out.add(svg.line(x1, y1, x2, y2, 'black', .5))
            for j in range(1-c.includezerosalience,3):
                if(c.saliencebywidth>1):
                    wedgewidth = wedgeangle/2/(c.saliencebywidth**3)*(c.saliencebywidth**j)
                else:
                    wedgewidth = wedgeangle/2/(3+c.includezerosalience)*(j+c.includezerosalience)
                for k in [1,-1]:
                    x1 = (500 + math.cos(indicatorcenterangles[i]+wedgewidth*k)*c.centerradius)
                    y1 = (500 + math.sin(indicatorcenterangles[i]+wedgewidth*k)*c.centerradius)
                    x2 = (500 + math.cos(indicatorcenterangles[i]+wedgewidth*k)*c.edgeradius)
                    y2 = (500 + math.sin(indicatorcenterangles[i]+wedgewidth*k)*c.edgeradius)
                    out.add(svg.line(x1, y1, x2, y2, 'black', .5))
        
        #invisible link and tooltip box
        x1 = (500 + math.cos(indicatorcenterangles[i]+wedgeangle/2)*c.centerradius)
        y1 = (500 + math.sin(indicatorcenterangles[i]+wedgeangle/2)*c.centerradius)
        x2 = (500 + math.cos(indicatorcenterangles[i]+wedgeangle/2)*c.textradius+25)
        y2 = (500 + math.sin(indicatorcenterangles[i]+wedgeangle/2)*c.textradius+25)
        x3 = (500 + math.cos(indicatorcenterangles[i]-wedgeangle/2)*c.textradius+25)
        y3 = (500 + math.sin(indicatorcenterangles[i]-wedgeangle/2)*c.textradius+25)
        x4 = (500 + math.cos(indicatorcenterangles[i]-wedgeangle/2)*c.centerradius)
        y4 = (500 + math.sin(indicatorcenterangles[i]-wedgeangle/2)*c.centerradius)
        d = 'M %s,%s L %s,%s L %s,%s L %s,%s z' % (x1,y1,x2,y2,x3,y3,x4,y4)
        newpath = svg.path(d, fill='white', p='fill-opacity="0.0"')
        newpath.add(svg.title(' %s: %s\n Magnitude %s\tSalience %s' % (c.indicatornames[i], c.indicatorfullnames[i], magnitude[i], salience[i])))
        out.add(newpath)

        x = (500 + math.cos(indicatorcenterangles[i])*c.textradius)
        y = (500 + math.sin(indicatorcenterangles[i])*c.textradius)
        out.add(svg.text(c.indicatornames[i], x, y, fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))
        
        # draw dividers
        x1 = 500 + math.cos(indicatorseparatorangles[i])*c.centerradius
        y1 = 500 + math.sin(indicatorseparatorangles[i])*c.centerradius
        if(i % 7 == 0):
            x2 = 500 + math.cos(indicatorseparatorangles[i])*(c.textradius+25)
            y2 = 500 + math.sin(indicatorseparatorangles[i])*(c.textradius+25)
            out.add(svg.line(x1, y1, x2, y2, 'black', 10))
        elif (c.xgrid or (c.saliencebywidth and c.drawsaliencedividers)):
                x2 = 500 + math.cos(indicatorseparatorangles[i])*(c.textradius)
                y2 = 500 + math.sin(indicatorseparatorangles[i])*(c.textradius)
                out.add(svg.line(x1, y1, x2, y2, 'black', 2))
    
    #draw rings
    for i in range(0,c.maxvalue+c.includezeromagnitude+1):
        if(i==c.includezeromagnitude):
            w=5
            out.add(svg.circle('500','500',ringradii(i),'black',w,'none'))
        elif (c.ygrid or i==0):
            w=1
            out.add(svg.circle('500','500',ringradii(i),'black',w,'none'))

    return out

#######################################
def makemagnitudelegend():
    angles = [-math.pi/2,math.pi/2]
    wedgeangle = math.pi*2/21
    
    out = svg.svg(width=250, height=1000, viewbox='0 0 250 1000')
    
    
    x = (500 + math.cos(angles[0])*c.textradius)
    y = (500 + math.sin(angles[0])*c.textradius)
    if c.swapsaliencemagnitude:
        te = 'Salience:'
    else: 
        te = 'Magnitude:'
    out.add(svg.text(te, 125, 25, fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))
    
    for angle in angles:
    
        x1 = (125 + math.cos(angle+wedgeangle/2)*c.centerradius)
        y1 = (500 + math.sin(angle+wedgeangle/2)*c.centerradius)
        x2 = (125 + math.cos(angle+wedgeangle/2)*c.textradius)
        y2 = (500 + math.sin(angle+wedgeangle/2)*c.textradius)
        x3 = (125 + math.cos(angle-wedgeangle/2)*c.textradius)
        y3 = (500 + math.sin(angle-wedgeangle/2)*c.textradius)
        x4 = (125 + math.cos(angle-wedgeangle/2)*c.centerradius)
        y4 = (500 + math.sin(angle-wedgeangle/2)*c.centerradius)
    
        out.add(svg.line(x1, y1, x2, y2, 'black', 2))
        out.add(svg.line(x3, y3, x4, y4, 'black', 2))
    
        
    
        if(c.drawsaliencedividers):
            x1 = (125 + math.cos(angle)*c.centerradius)
            y1 = (500 + math.sin(angle)*c.centerradius)
            x2 = (125 + math.cos(angle)*c.edgeradius)
            y2 = (500 + math.sin(angle)*c.edgeradius)
            out.add(svg.line(x1, y1, x2, y2, 'black', .5))
            for j in range(1-c.includezerosalience,3):
                if(c.saliencebywidth>1):
                    wedgewidth = wedgeangle/2/(c.saliencebywidth**3)*(c.saliencebywidth**j)
                else:
                    wedgewidth = wedgeangle/2/(3+c.includezerosalience)*(j+c.includezerosalience)
                x1 = (125 + math.cos(angle-wedgewidth)*c.centerradius)
                y1 = (500 + math.sin(angle-wedgewidth)*c.centerradius)
                x2 = (125 + math.cos(angle-wedgewidth)*c.edgeradius)
                y2 = (500 + math.sin(angle-wedgewidth)*c.edgeradius)
                out.add(svg.line(x1, y1, x2, y2, 'black', .5))
                x1 = (125 + math.cos(angle+wedgewidth)*c.centerradius)
                y1 = (500 + math.sin(angle+wedgewidth)*c.centerradius)
                x2 = (125 + math.cos(angle+wedgewidth)*c.edgeradius)
                y2 = (500 + math.sin(angle+wedgewidth)*c.edgeradius)
                out.add(svg.line(x1, y1, x2, y2, 'black', .5))
                
        for i in range(0,c.maxvalue+c.includezeromagnitude+1):
            if(i==c.includezeromagnitude):
                w=5
            else:
                w=1
            r=ringradii(i)
            x1 = (125 + math.cos(angle+wedgeangle/1.5)*r)
            y1 = (500 + math.sin(angle+wedgeangle/1.5)*r)
            x2 = (125 + math.cos(angle-wedgeangle/1.5)*r)
            y2 = (500 + math.sin(angle-wedgeangle/1.5)*r)
            d = 'M %s,%s A %s,%s 0 0,0 %s,%s' % (x1,y1,r,r,x2,y2)
            out.add(svg.path(d, stroke='black', strokewidth=w))

            y = y1
            if(i%2==0):
                x = x2 + 10*angle
            else:
                x = x1 - 10*angle
            if(i-c.includezeromagnitude>=0):
                out.add(svg.text(i-c.includezeromagnitude, x, y, fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))
    
    return out

###############################
def makebars(magnitudebenefit,saliencebenefit,magnitudecost,saliencecost):

    if c.swapsaliencemagnitude:
        tm = saliencebenefit[:]
        saliencebenefit = magnitudebenefit[:]
        magnitudebenefit = tm
        tm = saliencecost[:]
        saliencecost = magnitudecost[:]
        magnitudecost = tm

    #general variables
    out = svg.svg(width = 2250, height = 1000, viewbox='0 0 2250 1000')
    barwidth = 2050/(21+c.spacebars*2)

    for cb in range(0,2):
        if(cb==0):
            colors=c.colorsbenefit
            magnitude=magnitudebenefit
            salience=saliencebenefit
        else:    
            magnitude=magnitudecost
            salience=saliencecost
            colors=c.colorscost    

        #draw bars
        for i in range(0,21):
            h = barheight(magnitude[i]+c.includezeromagnitude)
            if(c.saliencebywidth==1):
                w = barwidth/(3+c.includezerosalience)*(salience[i]+c.includezerosalience)
            elif(c.saliencebywidth>1):
                w = barwidth/(c.saliencebywidth**3)*(c.saliencebywidth**salience[i])
            else:
                w = barwidth
            if(c.saliencebycolor):
                s = ((salience[i]+c.includezerosalience)**c.saliencebycolor)/((3.0+c.includezerosalience)**c.saliencebycolor)
            else:
                s = 1
            red,green,blue = colors[i//7]
            if(salience[i]>0 or c.includezerosalience):
                barlinecolor=(int(red*c.barlineshade),int(green*c.barlineshade),int(blue*c.barlineshade))
                out.add(svg.rect(200+(i+(i//7)*c.spacebars)*barwidth+(barwidth-w)/2,500+(cb-1)*h,w,h, fill='rgb(%s,%s,%s)' % (red,green,blue), stroke='rgb(%s,%s,%s)' % (barlinecolor[0],barlinecolor[1],barlinecolor[2]), strokewidth=c.barline, p='fill-opacity="%s"' % s))

            #invisible link and tooltip box
            newrect = svg.rect(200+(i+(i//7)*c.spacebars)*barwidth,500+(cb-1)*c.textradius,barwidth,c.textradius, fill='white', p='fill-opacity="0.0"')
            newrect.add(svg.title(' %s: %s\n Magnitude %s\tSalience %s' % (c.indicatornames[i], c.indicatorfullnames[i], magnitude[i], salience[i])))
            out.add(newrect)


        #draw ygrid
        for i in range(0,c.maxvalue+c.includezeromagnitude+1):
            if(i==c.includezeromagnitude):
                w=5
            else:
                w=1
            if (c.ygrid or i==0):
                x2 = 2250
            else:
                x2 = 200+c.ticksize
            out.add(svg.line(200-c.ticksize,500+barheight(i)*(cb-.5)*2,x2,500+barheight(i)*(cb-.5)*2,'black',w))


    #draw xgrid dividers
    out.add(svg.line(200,500-c.edgeradius,200,500+c.edgeradius,'black',5))
    for i in range(1,22+c.spacebars*2):
        if (c.xgrid or (c.saliencebywidth and c.drawsaliencedividers)):
            out.add(svg.line(200+barwidth*i,500-c.edgeradius,200+barwidth*i,500+c.edgeradius, 'black', 1))
        elif(ticksize):
            out.add(svg.line(200+barwidth*i,500-c.ticksize,200+barwidth*i,500+c.ticksize, 'black', 1))

    #draw salience dividers and column headings
    for i in range(0,21):
        if(c.saliencebywidth and c.drawsaliencedividers):
            for j in range(1-c.includezerosalience,3):
                if(c.saliencebywidth>1):
                    w = barwidth/2/(c.saliencebywidth**3)*(c.saliencebywidth**j)
                else:
                    w = barwidth/2/(3+c.includezerosalience)*(j+c.includezerosalience)
                for k in [1,-1]:
                    out.add(svg.line(200+barwidth*(i+(i//7)+.5)+k*w,500-c.edgeradius,200+barwidth*(i+(i//7)+.5)+k*w,500+c.edgeradius, 'black', .5))

        x = (200+(i+(i//7)*c.spacebars+.5)*barwidth)
        y = (500 - c.textradius)
        out.add(svg.text(c.indicatornames[i], x, y, fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))

    #draw magnitude legend
    if c.magnitudelegend:
        if c.swapsaliencemagnitude:
            te = 'Salience'
        else: 
            te = 'Magnitude'
        mag=svg.g(p='transform="rotate(-90 100 500)"')
        mag.add(svg.text(te, 100, 500, fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))
        out.add(mag)
        lastnumber=1
        for i in range(0,c.maxvalue+c.includezeromagnitude+1):
            if (i-c.includezeromagnitude==0):
                out.add(svg.text(i-c.includezeromagnitude, 160,502-barheight(i), fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))
                if (barheight(i)*2>c.font):
                    out.add(svg.text(i-c.includezeromagnitude, 160,502+barheight(i), fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))
            elif (i-c.includezeromagnitude>0):
                # alternate top and bottom if axis lables too close
                out.add(svg.text(i-c.includezeromagnitude, 160,502+barheight(i)*lastnumber, fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))
                if (barheight(i)-barheight(i-1)>c.font):
                    out.add(svg.text(i-c.includezeromagnitude, 160,502-barheight(i)*lastnumber, fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))
                else:
                    lastnumber = lastnumber * -1



    return out

###############################
def makebarsvert(magnitudebenefit,saliencebenefit,magnitudecost,saliencecost):

    if c.swapsaliencemagnitude:
        tm = saliencebenefit[:]
        saliencebenefit = magnitudebenefit[:]
        magnitudebenefit = tm
        tm = saliencecost[:]
        saliencecost = magnitudecost[:]
        magnitudecost = tm

    #general variables
    t = 0
    if c.centerlabel is not None:
        t = 50
    out = svg.svg(width = 1000, height = 2250+t, viewbox='0 0 1000 2150')
    barwidth = 2050/(21+c.spacebars*2)
    
    chart = svg.g('transform="translate(0 %s)"' % t)
    out.add(chart)
    
    for cb in range(0,2):
        if c.centerlabel is not None:
            out.add(svg.text(c.centerlabel[1-cb], 250+(cb)*500, 25, fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))
        
        if(cb==1):
            colors=c.colorsbenefit
            magnitude=magnitudebenefit
            salience=saliencebenefit
        else:    
            magnitude=magnitudecost
            salience=saliencecost
            colors=c.colorscost    

        #draw bars
        for i in range(0,21):
            h = barheight(magnitude[i]+c.includezeromagnitude)
            if(c.saliencebywidth==1):
                w = barwidth/(3+c.includezerosalience)*(salience[i]+c.includezerosalience)
            elif(c.saliencebywidth>1):
                w = barwidth/(c.saliencebywidth**3)*(c.saliencebywidth**salience[i])
            else:
                w = barwidth
            if(c.saliencebycolor):
                s = ((salience[i]+c.includezerosalience)**c.saliencebycolor)/((3.0+c.includezerosalience)**c.saliencebycolor)
            else:
                s = 1
            red,green,blue = colors[i//7]
            if(salience[i]>0 or c.includezerosalience):
                barlinecolor=(int(red*c.barlineshade),int(green*c.barlineshade),int(blue*c.barlineshade))
                chart.add(svg.rect(500+(cb-1)*h,(i+(i//7)*c.spacebars)*barwidth+(barwidth-w)/2,h,w, fill='rgb(%s,%s,%s)' % (red,green,blue), stroke='rgb(%s,%s,%s)' % (barlinecolor[0],barlinecolor[1],barlinecolor[2]), strokewidth=c.barline, p='fill-opacity="%s"' % s))

            #invisible link and tooltip box
            newrect = svg.rect(500+(cb-1)*c.textradius,(i+(i//7)*c.spacebars)*barwidth,c.textradius,barwidth, fill='white', p='fill-opacity="0.0"')
            newrect.add(svg.title(' %s: %s\n Magnitude %s\tSalience %s' % (c.indicatornames[i], c.indicatorfullnames[i], magnitude[i], salience[i])))
            chart.add(newrect)


        #draw ygrid
        for i in range(0,c.maxvalue+c.includezeromagnitude+1):
            if(i==c.includezeromagnitude):
                w=5
            else:
                w=1
            if (c.ygrid or i==0):
                x2 = 0
            else:
                x2 = 2050-c.ticksize
            chart.add(svg.line(500+barheight(i)*(cb-.5)*2,2050+c.ticksize,500+barheight(i)*(cb-.5)*2,x2,'black',w))   


    #draw xgrid dividers
    chart.add(svg.line(500-c.edgeradius,2050,500+c.edgeradius,2050,'black',5))
    for i in range(0,21+c.spacebars*2):
        if (c.xgrid or (c.saliencebywidth and c.drawsaliencedividers)):
            chart.add(svg.line(500-c.edgeradius,barwidth*i,500+c.edgeradius,barwidth*i, 'black', 1))
        elif(ticksize):
            chart.add(svg.line(500-c.ticksize,barwidth*i,500+c.ticksize,barwidth*i, 'black', 1))

    #draw salience dividers and column headings
    for i in range(0,21):
        if(c.saliencebywidth and c.drawsaliencedividers):
            for j in range(1-c.includezerosalience,3):
                if(c.saliencebywidth>1):
                    w = barwidth/2/(c.saliencebywidth**3)*(c.saliencebywidth**j)
                else:
                    w = barwidth/2/(3+c.includezerosalience)*(j+c.includezerosalience)
                for k in [1,-1]:
                    chart.add(svg.line(500-c.edgeradius,barwidth*(i+(i//7)+.5)+k*w,500+c.edgeradius,barwidth*(i+(i//7)+.5)+k*w, 'black', .5))

        x = (500 - c.textradius)
        y = ((i+(i//7)*c.spacebars+.5)*barwidth)
        chart.add(svg.text(c.indicatornames[i], x, y, fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))

    #draw magnitude legend
    if c.magnitudelegend:
        if c.swapsaliencemagnitude:
            te = 'Salience'
        else: 
            te = 'Magnitude'
        mag=svg.g(p='transform="translate(0 2050)"')
        mag.add(svg.text(te, 500, 100, fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))

        lastnumber=1
        for i in range(0,c.maxvalue+c.includezeromagnitude+1):
            if (i-c.includezeromagnitude==0):
                mag.add(svg.text(i-c.includezeromagnitude,502-barheight(i),40, fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))
                if (barheight(i)*2>c.font):
                    mag.add(svg.text(i-c.includezeromagnitude,502+barheight(i), 40, fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))
            elif (i-c.includezeromagnitude>0):
                # alternate top and bottom if axis lables too close
                mag.add(svg.text(i-c.includezeromagnitude, 502+barheight(i)*lastnumber,40, fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))
                if (barheight(i)-barheight(i-1)>c.font):
                    mag.add(svg.text(i-c.includezeromagnitude, 502-barheight(i)*lastnumber,40, fontsize=c.font, p='style="text-anchor: middle; dominant-baseline: middle"'))
                else:
                    lastnumber = lastnumber * -1
        chart.add(mag)


    return out


##############################
def makesaliencelegend():
    out = svg.svg(width=2000, height=100, viewbox='0 0 2000 100')
    if c.swapsaliencemagnitude:
        te = 'Magnitude:'
    else: 
        te = 'Salience:'
        
    out.add(svg.text(te, 70, 50, fontsize=c.font))
    for i in range(0,2):
        if i==0:
            red,green,blue = c.colorsbenefit[0]
        elif c.colorsbenefit[0]==c.colorscost[0]:
            return out
        else:
            red,green,blue = c.colorscost[0]
        
        for j in range(0,3+c.includezerosalience):
            out.add(svg.text(j + (1-c.includezerosalience), (i*950+290+j*(200-60*c.includezerosalience)), 50, fontsize=c.font))
            if(c.saliencebycolor):
                s = ((j+1)**c.saliencebycolor)/((3.0+c.includezerosalience)**c.saliencebycolor)
            else:
                s = 1
            if(c.saliencebywidth):
                out.add(svg.rect((i*950+320+j*(200-60*c.includezerosalience)),11,80,50, stroke='black', fill='none'))
                if(c.saliencebywidth>1):
                    w = 80.0/(c.saliencebywidth**3)*(c.saliencebywidth**(j+1-c.includezerosalience))
                else:
                    w = 80.0/(3+c.includezerosalience)*(j+1)
                out.add(svg.rect((i*950+360+j*(200-60*c.includezerosalience)-(w/2)),11,w,50, stroke='none', fill='rgb(%s,%s,%s)' % (red,green,blue), p='fill-opacity="%s"' % s))
            else:
                out.add(svg.rect((i*950+320+j*(200-60*c.includezerosalience)),11,80,50, stroke='none', fill='rgb(%s,%s,%s)' % (red,green,blue), p='fill-opacity="%s"' % s))
    return out


#######################################
def loaddata(data):
    """attempts to open a datafile"""
    
    mbcolumn = None
    sbcolumn = None
    mccolumn = None
    sccolumn = None
    
    # test values
    
    if(data!=None):
        try:
            csvfile = open(data, 'rU')
            dialect = csv.Sniffer().sniff(csvfile.read(1024),',;\t\n')
            csvfile.seek(0)
            reader = [row for row in csv.reader(csvfile, dialect)]
            print "loaded"
            for i in range(len(reader[0])):
                if(reader[0][i][:10]=='magnitudeb'):
                    mbcolumn = i
                if(reader[0][i][:9]=='salienceb'):
                    sbcolumn = i
                if(reader[0][i][:10]=='magnitudec'):
                    mccolumn = i
                if(reader[0][i][:9]=='saliencec'):
                    sccolumn = i
            if(mbcolumn is None or sbcolumn is None or mccolumn is None or sccolumn is None):
                mbcolumn=0
                sbcolumn=1
                mccolumn=2
                sccolumn=3
                if(reader[0][0]=="" and len(reader[0])==5):
                    mbcolumn=1
                    sbcolumn=2
                    mccolumn=3
                    sccolumn=4
                    
                    
            mbenefit=[float(reader[i][mbcolumn]) for i in range(1,22)]
            sbenefit=[float(reader[i][sbcolumn]) for i in range(1,22)]
            mcost=[float(reader[i][mccolumn]) for i in range(1,22)]
            scost=[float(reader[i][sccolumn]) for i in range(1,22)]
        
            if any([i>c.maxvalue or i<0 for i in mbenefit]):
                print 'Bad data'
                return 0
            if any([i>c.maxvalue or i<0 for i in sbenefit]):
                print 'Bad data'
                return 0
            if any([i>c.maxvalue or i<0 for i in mcost]):
                print 'Bad data'
                return 0
            if any([i>c.maxvalue or i<0 for i in scost]):    
                print 'Bad data'
                return 0
        except Exception as e:
            print "failed to load data", e
            return 0
    c.magnitudebenefit=mbenefit
    c.saliencebenefit=sbenefit
    c.magnitudecost=mcost
    c.saliencecost=scost     
    return 1


#######################################
def loadconfig(cfg):
    if cfg is not None:
        con = ConfigParser.ConfigParser()
        con.read(cfg)
        if con.has_section("config"):
            if con.has_option("config","savename"):
                c.savename=con.get("config","savename")
            if con.has_option("config","datafile"):
                c.datafile=con.get("config","datafile")
            if con.has_option("config","charttype"):
                c.charttype=con.getint("config","charttype")
            if con.has_option("config","swapsaliencemagnitude"):
                c.swapsaliencemagnitude=con.getboolean("config","swapsaliencemagnitude")
            if con.has_option("config","saliencebywidth"):
                c.saliencebywidth=con.getboolean("config","saliencebywidth")
            if con.has_option("config","saliencebycolor"):
                c.saliencebycolor=con.getboolean("config","saliencebycolor")
            if con.has_option("config","xgrid"):
                c.xgrid=con.getboolean("config","xgrid")
            if con.has_option("config","ygrid"):
                c.ygrid=con.getboolean("config","ygrid")
            if con.has_option("config","drawsaliencedividers"):
                c.drawsaliencedividers=con.getboolean("config","drawsaliencedividers")
            if con.has_option("config","includezerosalience"):
                c.includezerosalience=con.getboolean("config","includezerosalience")
            if con.has_option("config","includezeromagnitude"):
                c.includezeromagnitude=con.getboolean("config","includezeromagnitude")
            if con.has_option("config","magnitudearea"):
                c.magnitudearea=con.getboolean("config","magnitudearea")
            if con.has_option("config","magnitudelog"):
                c.magnitudelog=eval(con.get("config","magnitudelog"))
            if con.has_option("config","saliencelegend"):
                c.saliencelegend=con.getboolean("config","saliencelegend")
            if con.has_option("config","magnitudelegend"):
                c.magnitudelegend=con.getboolean("config","magnitudelegend")
            if con.has_option("config","colorsbenefit"):
                c.colorsbenefit=eval(con.get("config","colorsbenefit"))
            if con.has_option("config","colorscost"):
                c.colorscost=eval(con.get("config","colorscost"))
            if con.has_option("config","centerradius"):
                c.centerradius=con.getint("config","centerradius")
            if con.has_option("config","edgeradius"):
                c.edgeradius=con.getint("config","edgeradius")
            if con.has_option("config","textradius"):
                c.textradius=con.getint("config","textradius")
            if con.has_option("config","font"):
                c.font=con.getint("config","font")
            if con.has_option("config","centerlabel"):
                c.centerlabel=eval(con.get("config","centerlabel"))
            if con.has_option("config","title"):
                c.centerlabel=con.get("config","title")
            if con.has_option("config","spacebars"):
                c.spacebars=con.getboolean("config","spacebars")
            if con.has_option("config","ticksize"):
                c.ticksize=con.getint("config","ticksize")
            if con.has_option("config","barline"):
                c.barline=con.getint("config","barline")
            if con.has_option("config","barlineshade"):
                c.barlineshade=con.getfloat("config","barlineshade")
            if con.has_option("config","maxvalue"):
                c.maxvalue=con.getint("config","maxvalue")
            if con.has_option("config","indicatornames"):
                c.indicatornames=eval(con.get("config","indicatornames"))
            if con.has_option("config","indicatorfullnames"):
                c.indicatorfullnames=eval(con.get("config","indicatorfullnames"))
        
    

#######################################
def main():
    
    # bar chart
    if(c.charttype==2):
        svgport = svg.svg(viewbox='0 0 1000 2%d50' % 3*(c.magnitudelegend==True))
        if c.magnitudelegend:
            chart1 = svg.g()
        else:
            chart1 = svg.g()
        chart1.add(makebarsvert(c.magnitudebenefit,c.saliencebenefit,c.magnitudecost,c.saliencecost))
        svgport.add(chart1)
        
        # salience legend for bar
        if(c.saliencelegend):
            sal = svg.g(p='transform="rotate(90 1000 50) translate(%s 0)"' % (550+c.textradius))
            sal.add(makesaliencelegend())
            svgport.add(sal)
        
    else:
        # amoeba chart
        if(c.charttype==0):
            svgport = svg.svg(viewbox='0 0 2%d50 1%d00' % (3*(c.magnitudelegend==True), 1*(c.saliencelegend==True)))
            chart1 = svg.g()
            chart1.add(makecircle(c.magnitudebenefit,c.saliencebenefit,benefit=1))
            chart2 = svg.g(p='transform="translate(1050)"')
            chart2.add(makecircle(c.magnitudecost,c.saliencecost,benefit=0))
    
            svgport.add(chart1)
            svgport.add(chart2)
        
            if (c.magnitudelegend):
                mag = svg.g(p='transform="translate(2050)"')
                mag.add(makemagnitudelegend())
                svgport.add(mag)
        
        # column chart (default)
        else:
            svgport = svg.svg(viewbox='0 0 2%d50 1%d00' % (3*(c.magnitudelegend==True), 1*(c.saliencelegend==True)))
            if c.magnitudelegend:
                chart1 = svg.g()
            else:
                chart1 = svg.g(p='transform="translate(-200)"')
            chart1.add(makebars(c.magnitudebenefit,c.saliencebenefit,c.magnitudecost,c.saliencecost))
            svgport.add(chart1)

        # salience legend for amoeba and column
        if(c.saliencelegend):
            sal = svg.g(p='transform="translate(0 %s)"' % (550+c.textradius))
            sal.add(makesaliencelegend())
            svgport.add(sal)
    
    svg.gen(svgport, c.savename)

if __name__ == '__main__':
    argdict = {}
    loadconfig(configfile)
    if (len(sys.argv)>2):
        for i in range((len(sys.argv)-1)//2):
            argdict[sys.argv[2*i+1]]=string.strip(sys.argv[2*i+2])

        if "-c" in argdict:
            loadconfig(argdict["-c"])
        if "-d" in argdict:
            c.datafile=argdict["-d"]
        if "-s" in argdict:
            c.savename=argdict["-s"]
    
    loaddata(c.datafile)
    main()
