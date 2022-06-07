import base64
import datetime

import numpy as np
from django.shortcuts import render
import pickle as pk
# Create your views here.
from matplotlib import pyplot as plt
from rest_framework import generics, filters, status
from rest_framework.response import Response

from DashboardService.models import CovidNews, FAQ
from DashboardService.serializers import NewsSerializer, FAQSerializer
from VaccinationService.validators import ValidateUserRole
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import random
import math
import time
from sklearn.linear_model import LinearRegression, BayesianRidge
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error
import datetime
import operator

class CovidNewsDashboardView(generics.ListCreateAPIView):
    """
    View for the Covid News Dashboard
    """
    serializer_class = NewsSerializer
    queryset = CovidNews.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        """
        This view should return a list of all the news
        for the covid19 news dashboard
        """
        return CovidNews.objects.all()

    def create(self, request, *args, **kwargs):
        """
        This view should create a new news item
        """
        validate_user = ValidateUserRole()
        if not validate_user.has_permission(request):
            return Response(data={'message': 'You do not have permission to create a news item'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CovidNewsDashboardUpdate(generics.UpdateAPIView):
    """
    View for updating a news item
    """
    serializer_class = NewsSerializer
    queryset = CovidNews.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        """
        This view should update a news item
        """
        validate_user = ValidateUserRole()
        if not validate_user.has_permission(request):
            return Response(data={'message': 'You do not have permission to update a news item'},
                            status=status.HTTP_403_FORBIDDEN)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class MLpredictionViews(generics.ListAPIView):
    """
    View for the ML prediction
    """

    def list(self, request, *args, **kwargs):
        """
        This view should return a list of all the news
        for the covid19 news dashboard
        """

        confirmed = pk.load(open('ML/dates.pickle', 'rb'))
        deaths = pk.load(open('ML/deaths_pickle', 'rb'))
        dates = confirmed.keys()
        world_cases = []
        total_deaths = []
        mortality_rate = []
        days_in_future = 10
        future_forcast = np.array([i for i in range(len(dates) + days_in_future)]).reshape(-1, 1)
        adjusted_dates = future_forcast[:-10]
        for i in dates:
            confirmed_sum = confirmed[i].sum()
            death_sum = deaths[i].sum()

            # confirmed, deaths, recovered, and active
            world_cases.append(confirmed_sum)
            total_deaths.append(death_sum)
            # calculate rates
            mortality_rate.append(death_sum / confirmed_sum)
        world_cases = np.array(world_cases).reshape(-1, 1)
        total_deaths = np.array(total_deaths).reshape(-1, 1)
        # Convert integer into datetime for better visualization
        start = '1/22/2020'
        start_date = datetime.datetime.strptime(start, '%m/%d/%Y')
        future_forcast_dates = []
        for i in range(len(future_forcast)):
            future_forcast_dates.append((start_date + datetime.timedelta(days=i)).strftime('%m/%d/%Y'))

        response_dict = {
            "svm_prediction": [],
            "bayesian_prediction": [],
            "ploynomial_prediction": [],
        }

        svm = pk.load(open('ML/SVM_ML.pickle', 'rb'))
        bayesian_confirmed = pk.load(open('ML/bayesian.pickle', 'rb'))
        linear = pk.load(open('ML/linear_pred.pickle', 'rb'))

        svm_prediction = svm.predict(future_forcast)
        response_dict['svm_prediction'] = {
            'Date': future_forcast_dates[-10:],
            'SVM Predicted # of Confirmed Cases Worldwide': np.round(svm_prediction[-10:])
        }

        #poly_future_forcast = pk.load(open('ML/poly_future_forcast_transform.pickle', 'rb'))
        poly = PolynomialFeatures(degree=2)
        poly_future_forecast = poly.fit_transform(future_forcast)
        # poly_future_forecast = poly_future_forcast.fit_transform(future_forcast)
        linear_prediction = linear.predict(poly_future_forecast)
        linear_prediction = linear_prediction.reshape(1, -1)[0]
        response_dict['ploynomial_prediction'] = {
            'Date': future_forcast_dates[-10:],
            'Polynomial Predicted # of Confirmed Cases Worldwide': np.round(linear_prediction[-10:])
        }

        bayesian_poly = PolynomialFeatures(degree=2)
        bayesian_poly_future_forcast = bayesian_poly.fit_transform(future_forcast)
        bayesian_pred = bayesian_confirmed.predict(bayesian_poly_future_forcast)
        response_dict['bayesian_prediction'] = {
            'Date': future_forcast_dates[-10:],
            'Bayesian Predicted # of Confirmed Cases Worldwide': np.round(bayesian_pred[-10:])
        }

        plot_predictions(adjusted_dates, world_cases, svm_prediction, 'SVM Predictions', 'purple', future_forcast)
        plot_predictions(adjusted_dates, world_cases, linear_prediction, 'Polynomial Regression Predictions', 'orange',
                         future_forcast)
        plot_predictions(adjusted_dates, world_cases, bayesian_pred, 'Bayesian Ridge Regression Predictions', 'green',
                         future_forcast)

        file = open('ML/SVM Predictions.png', 'rb')
        image_data = base64.b64encode(file.read()).decode('utf-8')
        response_dict['svm_prediction']['image'] = image_data

        file = open('ML/Polynomial Regression Predictions.png', 'rb')
        image_data = base64.b64encode(file.read()).decode('utf-8')
        response_dict['ploynomial_prediction']['image'] = image_data

        file = open('ML/Bayesian Ridge Regression Predictions.png', 'rb')
        image_data = base64.b64encode(file.read()).decode('utf-8')
        response_dict['bayesian_prediction']['image'] = image_data

        return Response(data={'predictions': response_dict,'message': 'Predictions successfully generated'})


def plot_predictions(x, y, pred, algo_name, color, future_forcast):
    plt.figure(figsize=(16, 10))
    plt.plot(x, y)
    plt.plot(future_forcast, pred, linestyle='dashed', color=color)
    plt.title('Worldwide Coronavirus Cases Over Time', size=30)
    plt.xlabel('Days Since 1/22/2020', size=30)
    plt.ylabel('# of Cases', size=30)
    plt.legend(['Confirmed Cases', algo_name], prop={'size': 20})
    plt.xticks(size=20)
    plt.yticks(size=20)
    return plt.savefig('ML/' + algo_name + '.png')


class FAQViews(generics.ListCreateAPIView):
    """
    View for the FAQ
    """
    model = FAQ
    serializer_class = FAQSerializer

    def list(self, request, *args, **kwargs):
        """
        This view should return a list of all the FAQs
        for the covid19 news dashboard
        """
        faqs = FAQ.objects.all()
        serializer = FAQSerializer(faqs, many=True)
        return Response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        """
        This view should create a new FAQ
        for the covid19 news dashboard
        """
        validate_user = ValidateUserRole()
        if not validate_user.has_permission(request):
            return Response(data={'message': 'You do not have permission to create a FAQ'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = FAQSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
