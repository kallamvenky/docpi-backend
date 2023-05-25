import pandas as pd
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
import os
import shutil
from django.conf import settings
import sys
import numpy as np
from pathlib import Path
import json
from django.core.paginator import Paginator
from docpi_app.api.serializer.user import UserSerializer
from docpi_app.api.serializer.document import DocumentSerializer
from rest_framework import status
from django.contrib.auth.hashers import make_password
from docpi_app.models import User, Documents
from django.contrib.auth.hashers import check_password
import random
from docpi_app.connection import file_path, bucket_name, upload_bucket
sys.setrecursionlimit(10000)
import uuid
import json
from docpi_app.api.aws import upload_file_to_s3, read_csv_from_s3

class PandasEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.datetime64):
            return obj.item().isoformat()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        else:
            return super().default(obj)




class get_dataframe(APIView):
    def get(self, request, *args, **kwargs):
        filename = kwargs['filename']
        file = f"{file_path}/{filename}"
        df = read_csv_from_s3(bucket_name, file)
        response_data = df.head(1).to_json(orient='records')
        return Response(response_data)
    
class upload_file(APIView):
    def post(self, request, *args, **kwargs):
        if request.FILES.get("file"):
            user = kwargs['user']
            uploaded_file = request.FILES["file"]
            random_number = random.randint(0, 10000)
            filename = f"{uuid.uuid4()}_{random_number}.csv"
            file = f"{file_path}/{filename}"
            # print(folder_name)
            upload_file_to_s3(uploaded_file, bucket_name, file)
            print("file uploaded")
            file_size = read_csv_from_s3(bucket_name, file).shape
            print("file size")
            print(file_size)
            # return JsonResponse({"message": "File uploaded"})
            
            userInstance = User.objects.get(id=user)
            userData = UserSerializer(userInstance)  
            print(userInstance)
            document = {
                'userDetails': userData.data['id'],
                'name': filename,
                'shape': f'{file_size}'
            }
            serializer = DocumentSerializer(data = document)
            if serializer.is_valid():
                try:
                    serializer.save()
                    documentInstance = Documents.objects.get(name=filename,userDetails__id=userData.data['id'])
                    print('docu')
                    print(documentInstance)
                    documentData = DocumentSerializer(documentInstance)  
                    print(documentData.data)
                    Response({
                                 'status': 201,
                                'user': user,
                                'shape': f'{file_size}',
                                'document': filename
                                 }, status=status.HTTP_201_CREATED)
                except Exception as e:
                    print(e)
                    return Response({
                                     'status': 409,
                                    'data': 'Filename already exists',
                                     }, status=status.HTTP_409_CONFLICT)
            if not serializer.is_valid():
                print("not a valid")
                print(serializer.errors)

        return JsonResponse({"error": "Invalid request."})
    
class sort_dataframe(APIView):
    def get(self, request, *args, **kwargs):
        filename = kwargs['filename']
        file = f"{file_path}/{filename}"
        df = read_csv_from_s3(bucket_name, file)
        column = kwargs['column']
        order = kwargs['order']
        o = []
        for i in range(len(order)):
            minimum = min(range(len(order)))
            maximum = max(range(len(order)))
            if i > minimum and i < maximum:
                o.append((order[i]))
        o = ''.join(map(str, o))
        o = [bool(x.strip()) for x in o.split(',')]
        
        c = []
        for i in range(len(column)):
            minimum = min(range(len(column)))
            maximum = max(range(len(column)))
            if i > minimum and i < maximum:
                c.append((column[i]))
        c = ''.join(map(str, c))
        c = [x.strip() for x in c.split(',')]
        
        df = df.sort_values(by=c,
               ascending=o)
        response_data = df.head(100).to_json(orient='records')
        return Response(response_data) 
    
    
class sortAndFilter(APIView):
    
    def get(self, request, *args, **kwargs):
        print('request hitted')
        page_size = 1000
        lazyevent = request.query_params.get('lazyEvent')
        data = json.loads(lazyevent)
        print(data)
        filename = data['fileName']
        file = f"{file_path}/{filename}"
        df = read_csv_from_s3(bucket_name, file)
        filter = []
        if(data['filters']!=None):
            print('fintering is initiated')
            for col in data['filters']:
                value = data['filters'][col]['value']
                # value = col['value']
                if value != '':
                    filter.append({col:value})
            for cols in filter:
                for col in cols:
                    filterValue = cols[col]
                    if df[col].dtypes == 'float64':
                        filterValue = np.float64(cols[col])
                    if df[col].dtypes == 'float32':
                        filterValue = np.float32(cols[col])
                    if df[col].dtypes == 'int32':
                        filterValue = np.int32(cols[col])
                    if df[col].dtypes == 'int64':
                        filterValue = np.int32(cols[col])
                    
                    df = df[(df[col]== filterValue)]
                    print(df.shape)
        if(data['sortField'] == None):
            paginator = Paginator(df, page_size)
            
            try:
                page_number = data['page']
            except:
                page_number = 1
            
            print(page_number)
            page_obj = paginator.page(page_number)
            page_data = page_obj.object_list.to_json(orient='records')
            data = {
                'results': page_data,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
                'total_pages': paginator.num_pages,
                'current_page_number': page_obj.number,
                'totalRecords': df.shape[0],

            }
        else:
            if(data['sortOrder'] == 1):
                df = df.sort_values(by=data['sortField'],
                   ascending=True)
            else:
                df = df.sort_values(by=data['sortField'],
                   ascending=False)
            paginator = Paginator(df, page_size)
            page_obj = paginator.page(1)
            page_data = page_obj.object_list.to_json(orient='records')
            data = {
                'results': page_data,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
                'total_pages': paginator.num_pages,
                'current_page_number': page_obj.number,
                'totalRecords': df.shape[0],

            }
            
        
        
         
        
        response = JsonResponse(data)
        return response



    
class filter_dataframe(APIView):
    def get(self, request, *args, **kwargs):
        filename = kwargs['filename']
        file = f"{file_path}/{filename}"
        df = read_csv_from_s3(bucket_name, file)
        print(df.shape)
        column = kwargs['column']
        value = kwargs['value']
        print('filename')
        print(filename)
        print('column details')
        print(column, value)
        c = []
        for i in range(len(column)):
            minimum = min(range(len(column)))
            maximum = max(range(len(column)))
            if i > minimum and i < maximum:
                c.append((column[i]))
        c = ''.join(map(str, c))
        c = [x.strip() for x in c.split(',')]
        print(c)
        value = kwargs['value']
        v = []
        for i in range(len(value)):
            minimum = min(range(len(value)))
            maximum = max(range(len(value)))
            if i > minimum and i < maximum:
                v.append((value[i]))
        v = ''.join(map(str, v))
        v = [x.strip() for x in v.split(',')]
        print(v)
        filter = []
        # filter.append(df['FFIRST'] == 'Michael')
        # for i in range(len(c)):
        #     filter.append(df[c[i]] == v[i])
        # print(tuple(filter))
        # df = df[(1,0,0,0,0,0,0,0,0,0,0)]
        print(c)
        print(v)
        print(df.shape)
        df = df[(df[c[0]]== v[0])]
        df = df[(df[c[0]]== v[0])]
        response_data = df.head(5).to_json(orient='records')
        print(response_data)
        return Response(response_data)
    
    
class Signup(APIView):
    def post(self, request, *args, **kwargs):
        user = request.data
        if user["password"] != user["confirmPassword"]:
            return Response({'message': 'Password mismatch'})
        user.pop('confirmPassword', None)
        user["password"] = make_password(user["password"])
        serializer = UserSerializer(data = user)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                                 'status': 201,
                                'user': serializer.data['user'],
                                'id': serializer.data['id'],
                                 }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                                 'status': 409,
                                'data': 'Email already exists',
                                 }, status=status.HTTP_409_CONFLICT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class Signin(APIView):
    def post(self, request, *args, **kwargs):
        user = request.data
        result = User.objects.get(email = user["user"])
        serializer = UserSerializer(result)        
        password_matches = check_password(user["password"], serializer.data["password"])
        if password_matches:
            return Response({
                'status': 200,
                'user': serializer.data['user'],
                'id': serializer.data['id'],
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 401,
                'data': 'Authentication failed',
            }, status=status.HTTP_401_UNAUTHORIZED)

class GetTableName(APIView):
    def post(self, request, *args, **kwargs):
        details = request.data
        if details['file'] == 'latest':
            documentInstance = Documents.objects.filter(userDetails=int(details['user'])).order_by('-id')[:1]
            documentData = DocumentSerializer(documentInstance, many=True)  
            name = documentData.data[0]["name"]
            print(name)
        return Response({
                'status': 200,
                'name': name
            }, status=status.HTTP_200_OK)
        