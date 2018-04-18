# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login, logout
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views import generic
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import UserForm, UserLoginForm, RequestForm, MessageForm
from .models import UserRequests, Messages
from .serializers import UserRequestsSerializer, MessagesSerializer, MessageNotifySerializer


# Create your views here.

#requests/
class IndexList(APIView):
    template_name = "requestservice/index.html"
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        user = self.request.user
        if user.is_authenticated:
            open = UserRequests.objects.filter(closed=False).order_by('-deadline')
            openser = UserRequestsSerializer(open, many=True)
            closed = UserRequests.objects.filter(closed=True).order_by('-deadline')
            closedser = UserRequestsSerializer(closed, many=True)
            all_requests = open.count() + closed.count()
            return Response({'all_requests': all_requests, 'open': openser.data, 'closed': closedser.data},
                            template_name="index.html")
            #return render(request, self.template_name, {'all_requests': serializer.data, 'open': openser.data, 'closed': closedser.data})
        else:
            return Response(None, template_name="index.html")
            #return render(request, self.template_name, {'all_requests': None})


    def post(self, request):
        serializer = UserRequestsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def ajaxcall(request):
    if request.method == 'GET':
        mode = request.GET['mode']
        if mode == 'user':
            user = request.user
            open = UserRequests.objects.filter(user=user.username, closed=False)
            openser = UserRequestsSerializer(open, many=True)
            closed = UserRequests.objects.filter(user=user.username, closed=True)
            closedser = UserRequestsSerializer(closed, many=True)
            sum = open.count() + closed.count()
            return JsonResponse({'open': openser.data, 'closed': closedser.data, 'sum': sum},
                                content_type="application/json")
        elif mode == 'all':
            open = UserRequests.objects.filter(closed=False)
            openser = UserRequestsSerializer(open, many=True)
            closed = UserRequests.objects.filter(closed=True)
            closedser = UserRequestsSerializer(closed, many=True)
            sum = open.count() + closed.count()
            return JsonResponse({'open': openser.data, 'closed': closedser.data, 'sum': sum},
                                content_type="application/json")
        elif mode == 'search':
            title = request.GET['title']
            try:
                open = UserRequests.objects.filter(title=title, closed=False)
            except UserRequests.DoesNotExist:
                open = ""
            openser = UserRequestsSerializer(open, many=True)
            try:
                closed = UserRequests.objects.filter(title=title, closed=True)
            except UserRequests.DoesNotExist:
                closed = ""
            closedser = UserRequestsSerializer(closed, many=True)
            sum = open.count() + closed.count()
            return JsonResponse({'open': openser.data, 'closed': closedser.data, 'sum': sum},
                                content_type="application/json")
        else:
            return HttpResponse("Invalid Mode Selection")
    else:
        return HttpResponse("Request method is not a GET")


class Detail(APIView):
    template_name = "requestservice/detail.html"
    renderer_classes = (TemplateHTMLRenderer,)
    entry = UserRequests

    def get_object(self, pk):
        try:
            return UserRequests.objects.get(pk=pk)
        except UserRequests.DoesNotExist:
            raise Http404

    def get_keywords(self, keywords):
        keys_list = []
        try:
            keys_list = keywords.split(',')
            return keys_list
        except UserRequests.DoesNotExist:
            raise Http404

    def clear_duplicates(self, list):
        clear_list = []
        for entry in list:
            if entry not in clear_list:
                clear_list.append(entry)
        return clear_list


    def get(self, request, pk):
        entry = self.get_object(pk)
        user = self.request.user
        serializer = UserRequestsSerializer(entry)
        prev = UserRequests.objects.filter(user=user.username)
        prevser = UserRequestsSerializer(prev, many=True)
        list = self.get_keywords(entry.keywords)
        related = []
        for key in list:
            current_results = UserRequests.objects.filter(keywords__icontains=key).exclude(pk=entry.pk)
            relatedser = UserRequestsSerializer(current_results, many=True)
            related += relatedser.data
        related = self.clear_duplicates(related)
        #related = UserRequests.objects.filter(keywords__icontains=entry.keywords).exclude(pk=entry.pk)

        return Response({'index': serializer.data, 'prev': prevser.data, 'related': related},
                        template_name="detail.html")
        #return render(request, self.template_name,
         #             {'index': serializer.data, 'prev': prevser.data, 'related': relatedser.data})

    def put(self, request, pk):
        snippet = self.get_object(pk)
        serializer = UserRequestsSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SearchView(APIView):
    template_name = "requestservice/searchres.html"
    renderer_classes = (TemplateHTMLRenderer,)

    def get_object(self, title):
        try:
            return UserRequests.objects.filter(title=title)
        except UserRequests.DoesNotExist:
            return None

    def get(self, request):
        title = request.GET['title']
        results = self.get_object(title)
        resser = UserRequestsSerializer(results, many=True)

        return Response({'results': resser.data}, template_name="searchres.html")



class Create(APIView):
    template_name = "requestservice/userrequests_form.html"
    renderer_classes = (TemplateHTMLRenderer,)
    parser_classes = (FormParser, MultiPartParser)
    form_class = RequestForm

    def get_object(self, pk):
        try:
            return UserRequests.objects.get(pk=pk)
        except UserRequests.DoesNotExist:
            raise Http404

    def get(self, request):
        form = self.form_class(None)
        return Response({'form': form, 'entry': None}, template_name="userrequests_form.html")
        #return render(request, self.template_name, {'form': form})

    def post(self, request, format=None):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            data = request.data
            serializer = UserRequestsSerializer(data=data, context={'request': request})
            serializer.user = self.request.user.username  # use your own profile here
            serializer.file = self.request.FILES
            if serializer.is_valid():
                entry = serializer.save(user=request.user.username)
                return redirect('requestservice:detail', entry.id)
            error_message = serializer.errors
            #return render(request, self.template_name, {'form': form, 'error_message': error_message, 'entry': request.data})
            return Response({'form': form, 'error_message': error_message, 'entry': None},
                                          template_name="userrequests_form.html")
        error_message = "Form Not Valid. Please Retry"
        return Response({'form': form, 'error_message': error_message, 'entry': None},
                        template_name="userrequests_form.html")
        #return render(request, self.template_name, {'form': form, 'error_message': error_message, 'entry': request.data})

class Update(APIView):

    template_name = "requestservice/userrequests_form.html"
    renderer_classes = (TemplateHTMLRenderer,)
    parser_classes = (FormParser, MultiPartParser)
    form_class = RequestForm

    def get_object(self, pk):
        try:
            return UserRequests.objects.get(pk=pk)
        except UserRequests.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        entry = self.get_object(pk)
        form = self.form_class(instance=entry)
        return Response({'form': form, 'entry': entry}, template_name="userrequests_form.html")

    def post(self, request, pk, format=None):
        entry = self.get_object(pk=pk)
        form = self.form_class(request.POST, request.FILES, instance=entry)

        if form.is_valid():
            serializer = UserRequestsSerializer(entry, data=request.data, context={'request': request})
            serializer.user = self.request.user.username  # use your own profile here
            serializer.file = entry.file

            if serializer.is_valid():
                entry = serializer.save(user=request.user.username)
                return redirect('requestservice:detail', entry.id)
            error_message = serializer.errors
            #return render(request, self.template_name, {'form': form, 'error_message': error_message, 'entry': request.data})
            return Response({'form': form, 'error_message': error_message, 'entry': request.data},
                                          template_name="userrequests_form.html")
        error_message = "Form Not Valid. Please Retry"
        return Response({'form': form, 'error_message': error_message, 'entry': request.data},
                        template_name="userrequests_form.html")
        #return render(request, self.template_name, {'form': form, 'error_message': error_message, 'entry': request.data})

def closeRequest(request,pk):
    if request.method == 'GET':
        req = UserRequests.objects.get(pk=pk)
        data = {'closed': True}
        serializer = UserRequestsSerializer(req, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return redirect('requestservice:reqdiscusion', req.pk)

class Discussion(APIView):

    template_name = 'requestservice/reqdiscussion.html'
    renderer_classes = (TemplateHTMLRenderer,)
    parser_classes = (FormParser, MultiPartParser)
    form_class = MessageForm

    def get_messages(self,pk):
        try:
            return Messages.objects.filter(requestid=pk).order_by('date')
        except Messages.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        results = self.get_messages(pk)
        req = UserRequests.objects.get(pk=pk)
        reqser = UserRequestsSerializer(req)
        resser = MessagesSerializer(results, many=True)
        return Response({'entry': reqser.data, 'messages': resser.data}, template_name="reqdiscussion.html")

    def post(self, request, pk):
        message = self.form_class(request.POST)
        req = UserRequests.objects.get(pk=pk)

        if message.is_valid():
            data = {'message': request.POST['message'], 'requestid': req.pk, 'userreq': req.user,
                    'userpost': self.request.user.username}
            notify = {'user': req.user, 'messageid': req.id}
            serializer = MessagesSerializer(data=data, context={'request': request})
            serializer.userreq = req.user
            if serializer.is_valid():
                serializer.save(userreq=req.user)
                if req.user != request.user.username:
                    notifyserializer = MessageNotifySerializer(data=notify)
                    if notifyserializer.is_valid():
                        notifyserializer.save()

                return redirect('requestservice:reqdiscusion', req.id)
            error_message = serializer.errors

            #return redirect('templates:reqdiscusion', entry.id)
            return Response({'error_message': error_message, 'messages': request.data},
                                          template_name="reqdiscussion.html")
        error_message = "Form Not Valid. Please Retry"

        #return redirect('userrequests:reqdiscusion', entry.id)
        return Response({'error_message': error_message, 'messages': request.data},
                        template_name="reqdiscussion.html")


class UserLogin(generic.View):
    form_class = UserLoginForm
    template_name = 'requestservice/login_form.html'

    # display blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('requestservice:index')
            error_message = 'Wrong Username or Password! Try Again!'

        return render(request, self.template_name, {'form': form, 'error_message': error_message})



class UserFormView(generic.View):
    form_class = UserForm
    template_name = 'requestservice/registration_form.html'

    # display blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # register user to DB
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            # return user object if credentials are correct
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('requestservice:index')

        return render(request, self.template_name, {'form': form})

def UserLogout(request):
    logout(request)
    return redirect('requestservice:index')
