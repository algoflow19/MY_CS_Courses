# -*- coding: utf-8 -*-
# Problem Set 5: Experimental Analysis
# Name: 
# Collaborators (discussion):
# Time:

import pylab
import re

# cities in our weather data
CITIES = [
    'BOSTON',
    'SEATTLE',
    'SAN DIEGO',
    'PHILADELPHIA',
    'PHOENIX',
    'LAS VEGAS',
    'CHARLOTTE',
    'DALLAS',
    'BALTIMORE',
    'SAN JUAN',
    'LOS ANGELES',
    'MIAMI',
    'NEW ORLEANS',
    'ALBUQUERQUE',
    'PORTLAND',
    'SAN FRANCISCO',
    'TAMPA',
    'NEW YORK',
    'DETROIT',
    'ST LOUIS',
    'CHICAGO'
]

TRAINING_INTERVAL = range(1961, 2010)
TESTING_INTERVAL = range(2010, 2016)

"""
Begin helper code
"""
class Climate(object):
    """
    The collection of temperature records loaded from given csv file
    """
    def __init__(self, filename):
        """
        Initialize a Climate instance, which stores the temperature records
        loaded from a given csv file specified by filename.

        Args:
            filename: name of the csv file (str)
        """
        self.rawdata = {}

        f = open(filename, 'r')
        header = f.readline().strip().split(',')
        for line in f:
            items = line.strip().split(',')

            date = re.match('(\d\d\d\d)(\d\d)(\d\d)', items[header.index('DATE')])
            year = int(date.group(1))
            month = int(date.group(2))
            day = int(date.group(3))

            city = items[header.index('CITY')]
            temperature = float(items[header.index('TEMP')])
            if city not in self.rawdata:
                self.rawdata[city] = {}
            if year not in self.rawdata[city]:
                self.rawdata[city][year] = {}
            if month not in self.rawdata[city][year]:
                self.rawdata[city][year][month] = {}
            self.rawdata[city][year][month][day] = temperature
            
        f.close()

    def get_yearly_temp(self, city, year):
        """
        Get the daily temperatures for the given year and city.

        Args:
            city: city name (str)
            year: the year to get the data for (int)

        Returns:
            a 1-d pylab array of daily temperatures for the specified year and
            city
        """
        temperatures = []
        assert city in self.rawdata, "provided city is not available"
        assert year in self.rawdata[city], "provided year is not available"
        for month in range(1, 13):
            for day in range(1, 32):
                if day in self.rawdata[city][year][month]:
                    temperatures.append(self.rawdata[city][year][month][day])
        return pylab.array(temperatures)

    def get_daily_temp(self, city, month, day, year):
        """
        Get the daily temperature for the given city and time (year + date).

        Args:
            city: city name (str)
            month: the month to get the data for (int, where January = 1,
                December = 12)
            day: the day to get the data for (int, where 1st day of month = 1)
            year: the year to get the data for (int)

        Returns:
            a float of the daily temperature for the specified time (year +
            date) and city
        """
        assert city in self.rawdata, "provided city is not available"
        assert year in self.rawdata[city], "provided year is not available"
        assert month in self.rawdata[city][year], "provided month is not available"
        assert day in self.rawdata[city][year][month], "provided day is not available"
        return self.rawdata[city][year][month][day]

def se_over_slope(x, y, estimated, model):
    """
    For a linear regression model, calculate the ratio of the standard error of
    this fitted curve's slope to the slope. The larger the absolute value of
    this ratio is, the more likely we have the upward/downward trend in this
    fitted curve by chance.
    
    Args:
        x: an 1-d pylab array with length N, representing the x-coordinates of
            the N sample points
        y: an 1-d pylab array with length N, representing the y-coordinates of
            the N sample points
        estimated: an 1-d pylab array of values estimated by a linear
            regression model
        model: a pylab array storing the coefficients of a linear regression
            model

    Returns:
        a float for the ratio of standard error of slope to slope
    """
    assert len(y) == len(estimated)
    assert len(x) == len(estimated)
    EE = ((estimated - y)**2).sum()
    var_x = ((x - x.mean())**2).sum()
    SE = pylab.sqrt(EE/(len(x)-2)/var_x)
    return SE/model[0]

"""
End helper code
"""

def generate_models(x, y, degs):
    """
    Generate regression models by fitting a polynomial for each degree in degs
    to points (x, y).

    Args:
        x: an 1-d pylab array with length N, representing the x-coordinates of
            the N sample points
        y: an 1-d pylab array with length N, representing the y-coordinates of
            the N sample points
        degs: a list of degrees of the fitting polynomial

    Returns:
        a list of pylab arrays, where each array is a 1-d array of coefficients
        that minimizes the squared error of the fitting polynomial
    """
    fit_params=[]
    for deg in degs:
        z=pylab.polyfit(x,y,deg)
        fit_params.append(z)
    return fit_params   


def r_squared(y, estimated):
    """
    Calculate the R-squared error term.
    
    Args:
        y: 1-d pylab array with length N, representing the y-coordinates of the
            N sample points
        estimated: an 1-d pylab array of values estimated by the regression
            model

    Returns:
        a float for the R-squared error term
    """
    mean=sum(y)/len(y)
    return 1 - sum((estimated-y)**2)/sum((y-mean)**2)

def evaluate_models_on_training(x, y, models):
    """
    For each regression model, compute the R-squared value for this model with the
    standard error over slope of a linear regression line (only if the model is
    linear), and plot the data along with the best fit curve.

    For the plots, you should plot data points (x,y) as blue dots and your best
    fit curve (aka model) as a red solid line. You should also label the axes
    of this figure appropriately and have a title reporting the following
    information:
        degree of your regression model,
        R-square of your model evaluated on the given data points,
        and SE/slope (if degree of this model is 1 -- see se_over_slope). 
    
    Args:
        x: an 1-d pylab array with length N, representing the x-coordinates of
            the N sample points
        y: an 1-d pylab array with length N, representing the y-coordinates of
            the N sample points
        models: a list containing the regression models you want to apply to
            your data. Each model is a pylab array storing the coefficients of
            a polynomial.

    Returns:
        None
    """
    pylab.xlabel("years")
    pylab.ylabel("degrees Celsius")
    def createModelFingure(originXs,originYs,coefficantes):
        modelYs=pylab.polyval(coefficantes,originXs)
        R_2=r_squared(y,modelYs)
        if(len(coefficantes)!=2):
            pylab.title("Model deg="+str(len(coefficantes)-1)+" and its R^2 is "+str(R_2))
        else:
            pylab.title("Model deg="+str(len(coefficantes)-1)+" and its R^2="+str(R_2)+"\n its slop-to-slop standard error is "+str(se_over_slope(originXs,originYs,modelYs,coefficantes)))
        pylab.plot(originXs,originYs,"b.")
        pylab.plot(originXs,modelYs,"r")
    
    if(len(models)==0):
        raise ValueError("You don't input a model!")
    createModelFingure(x,y,models[0])
    for model in models[1:]:
        pylab.figure()
        createModelFingure(x,y,model)
    

def gen_cities_avg(climate, multi_cities, years):
    """
    Compute the average annual temperature over multiple cities.

    Args:
        climate: instance of Climate
        multi_cities: the names of cities we want to average over (list of str)
        years: the range of years of the yearly averaged temperature (list of
            int)

    Returns:
        a pylab 1-d array of floats with length = len(years). Each element in
        this array corresponds to the average annual temperature over the given
        cities for a given year.
    """
    years_avg=[]
    for year in years:
        current_year_data=[]
        for city in multi_cities:
            current_city_data=climate.get_yearly_temp(city,year)
            current_year_data.append(sum(current_city_data)/len(current_city_data))
        years_avg.append(sum(current_year_data)/len(current_year_data))
    return pylab.array(years_avg)
        

def moving_average(y, window_length):
    """
    Compute the moving average of y with specified window length.

    Args:
        y: an 1-d pylab array with length N, representing the y-coordinates of
            the N sample points
        window_length: an integer indicating the window length for computing
            moving average

    Returns:
        an 1-d pylab array with the same length as y storing moving average of
        y-coordinates of the N sample points
    """
    mv_avg=[]
    for i in range(len(y)):
        current_list=[]
        if(i-window_length+1<0):
            current_list=y[:i+1]
        else:
            current_list=y[i-window_length+1:i+1]
        mv_avg.append(sum(current_list)/len(current_list))
    return pylab.array(mv_avg)


def rmse(y, estimated):
    """
    Calculate the root mean square error term.

    Args:
        y: an 1-d pylab array with length N, representing the y-coordinates of
            the N sample points
        estimated: an 1-d pylab array of values estimated by the regression
            model

    Returns:
        a float for the root mean square error term
    """
    return (sum((y-estimated)**2)/len(y))**0.5

def gen_std_devs(climate, multi_cities, years):
    """
    For each year in years, compute the standard deviation over the averaged yearly
    temperatures for each city in multi_cities. 

    Args:
        climate: instance of Climate
        multi_cities: the names of cities we want to use in our std dev calculation (list of str)
        years: the range of years to calculate standard deviation for (list of int)

    Returns:
        a pylab 1-d array of floats with length = len(years). Each element in
        this array corresponds to the standard deviation of the average annual 
        city temperatures for the given cities in a given year.
    """
    total_data=[]
    for year in years:
        current_year_data=[]
        for city in multi_cities:
            current_year_data.append(climate.get_yearly_temp(city,year))
        current_year_data=pylab.array(current_year_data)
        pylab.plot(pylab.array(range(len(current_year_data[0]))),current_year_data[0])
        pylab.plot(pylab.array(range(len(current_year_data[1]))),current_year_data[1])
        current_year_data=sum(current_year_data)/len(multi_cities)
        pylab.figure()
        mean=sum(current_year_data)/len(current_year_data)
        total_data.append( ( sum((current_year_data-mean)**2)/len(current_year_data))**0.5 /mean)
    return pylab.array(total_data)

def evaluate_models_on_testing(x, y, models):
    """
    For each regression model, compute the RMSE for this model and plot the
    test data along with the model’s estimation.

    For the plots, you should plot data points (x,y) as blue dots and your best
    fit curve (aka model) as a red solid line. You should also label the axes
    of this figure appropriately and have a title reporting the following
    information:
        degree of your regression model,
        RMSE of your model evaluated on the given data points. 

    Args:
        x: an 1-d pylab array with length N, representing the x-coordinates of
            the N sample points
        y: an 1-d pylab array with length N, representing the y-coordinates of
            the N sample points
        models: a list containing the regression models you want to apply to
            your data. Each model is a pylab array storing the coefficients of
            a polynomial.

    Returns:
        None
    """
    pylab.xlabel("years")
    pylab.ylabel("degrees")
    def createModelFingure(originXs,originYs,coefficantes):
        modelYs=pylab.polyval(coefficantes,originXs)
        v_rmse=rmse(y,modelYs)
        pylab.title("Model deg="+str(len(coefficantes)-1)+" and its RMSE="+str(v_rmse))
        pylab.plot(originXs,originYs,"b.")
        pylab.plot(originXs,modelYs,"r")
    if(len(models)==0):
        raise ValueError("You don't input a model!")
    createModelFingure(x,y,models[0])
    for model in models[1:]:
        pylab.figure()
        createModelFingure(x,y,model)
    
    
    
    
if __name__ == '__main__':

    climate_data=Climate("/home/kk/CS_Courses/MY_MIT_CS_Courses/6.0002/PS5/data.csv")
    

    # Part A.4
    days_data=[]
    axisX_years=pylab.array(TRAINING_INTERVAL)
#    for year_num in TRAINING_INTERVAL:
#        days_data.append(climate_data.get_daily_temp('NEW YORK',1,10,year_num))
#    days_data=pylab.array(days_data)
#    models=generate_models(axisX_years,days_data,[1])
#    evaluate_models_on_training(axisX_years,days_data,models)
#    pylab.figure()
#    years_avg_data=[]
#    for year_num in TRAINING_INTERVAL:
#        current_year_data=climate_data.get_yearly_temp('NEW YORK',year_num)
#        years_avg_data.append(sum(current_year_data)/len(current_year_data))
#    years_avg_data=pylab.array(years_avg_data)
#    models=generate_models(axisX_years,years_avg_data,[1])
#    evaluate_models_on_training(axisX_years,years_avg_data,models)

#Write Up:
#        1. The second graph can describe the data better since its R is higher and 
#        the data points much closer to the curve than the first one.
#        
#        
#        2. The temputer of both graphs goes up and down very quickly, and only has a 
#        slow trend to go up. Besides, the frist graph is much more noise beacause it 
#        wave range is much bigger than the second and it can change very quickly from 
#        point to point.
#        
#        3.The second graph's standard error-to-slope ratio is less than 0.5, which 
#        show that the trend on the graph is significant.
    
    # Part B
#    years_data=gen_cities_avg(climate_data,CITIES,axisX_years)
#    models=generate_models(axisX_years,years_data,[1])
#    evaluate_models_on_training(axisX_years,years_data,models)

#    Write Up:
#	1. The curve in this graph fit the data points much better than it in part A.(R^2 0.74 vs 0.18), and it also show the grow trend on temputer much clear than part A, since its slop-to-slop standard error is merely not above 0.086.
#	2. I think that since we count more data, we could elimate the no-rules randomnees in the change of temputer much better.
#	3. ....
#	4. May get a simmiar result of the second graph of part A. 
#	
    # Part C
#    years_data=gen_cities_avg(climate_data,CITIES,axisX_years)
#    mv_avg_years_data=moving_average(years_data,5)
#    models=generate_models(axisX_years,mv_avg_years_data,[1])
#    evaluate_models_on_training(axisX_years,mv_avg_years_data,models)
    
    # Part D.2
    years_data=gen_cities_avg(climate_data,CITIES,axisX_years)
    mv_avg_years_data=moving_average(years_data,5)
    models=generate_models(axisX_years,mv_avg_years_data,[1,2,20])
#    evaluate_models_on_training(axisX_years,mv_avg_years_data,models)
#Write Up:
#	1. One degree-polynomial curver fit its graph pretty good, but two degree-polynomial curver fit tis graph even better, and 20 degree-polynomial curver fit its graph almost perfect.
#	2. The 20 degree-polynomial graph. It just go up and down like the points go.
#	3. The 20 degree-polynomial graph. With so many degrees, the curver become very flexible, and just follow the change trend of the points.
#	 
    futher_years=pylab.array(TESTING_INTERVAL)
#    futher_years_data=gen_cities_avg(climate_data,CITIES,futher_years)
#    futher_years_avg=moving_average(futher_years_data,5)
#    evaluate_models_on_testing(futher_years,futher_years_avg,models)
    
    
    # Part E
#    std_devs=gen_std_devs(climate_data,['BOSTON','SEATTLE'],pylab.array(range(1961,2016)))
#    std_devs_avg=moving_average(std_devs,1)
#    print(std_devs_avg)
#    modles=generate_models(pylab.array(range(1961,2016)),std_devs_avg,[1])
#    evaluate_models_on_training(pylab.array(range(1961,2016)),std_devs_avg,modles)
    
#Write Up:
#   1. No, the graph show that the temperature variation is getting
#   smaller over these years.
#   2. I think the most important thing is that how we measuring the temperatures more extreme.
#   In my opinion, more extreme weather may not lead to the growth of the standard deviation 
#   in our data, but we can surely conut if there is more extreme temperature days.
#   

#years=pylab.array(TRAINING_INTERVAL)
#jan_std_devs=[]
#for year in years:
#    current_year_data=[]
#    for city in CITIES:
#        current_city_data=[]
#        for i in range(1,31):
#            current_city_data.append(climate_data.get_daily_temp(city,3,i,year))
#        current_year_data.append(pylab.std(current_city_data))
#    jan_std_devs.append(pylab.mean(current_year_data))
#    
##pylab.plot(years,jan_std_devs)
#modles=generate_models(years,jan_std_devs,[1])
#evaluate_models_on_training(years,jan_std_devs,modles)

years=pylab.array(TRAINING_INTERVAL)
extrme_days=[]
for year in years:
    current_year_data=[]
    for city in CITIES:
        current_city_data=climate_data.get_yearly_temp(city,year)
        mx=max(current_city_data)
        mn=min(current_city_data)
        city_mean=pylab.mean(current_city_data)
        current_num=0
        for temputer in current_city_data:
            if(temputer>city_mean and temputer > (mx-city_mean)*0.5+city_mean ):
                current_num+=1
            elif(temputer < city_mean-(city_mean-mn)*0.5):
                current_num+=1
        current_year_data.append(current_num)
    extrme_days.append(pylab.mean(current_year_data))


pylab.plot(years,extrme_days)
modles=generate_models(years,extrme_days,[1])
evaluate_models_on_training(years,extrme_days,modles)


