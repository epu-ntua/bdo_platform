# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from query_designer.models import *
from django.http import JsonResponse

from aggregator.models import *
from query_designer.query_processors.utils import ResultEncoder
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from access_controller.policy_enforcement_point import PEP
from website_analytics.views import *
from datetime import datetime
import traceback

def execute_query(request, pk=None):
    user = request.user
    if user.is_authenticated:
        doc_str = request.POST.get('query', '')

        # get or fake query object
        if not pk:
            q = AbstractQuery(document=json.loads(doc_str))
        else:
            q = AbstractQuery.objects.get(pk=pk)
            # try:
            #     q.document = json.loads(doc_str)
            # except ValueError:
            #     pass
            q.document['limit'] = 1000000
        # print q.document
        # print q.raw_query
        # get POST params
        dimension_values = request.POST.get('dimension_values', '')
        variable = request.POST.get('variable', '')
        only_headers = request.POST.get('only_headers', '').lower() == 'true'

        # check for the access
        try:
            dataset_list = []
            doc = q.document
            print q.document
            for el in doc['from']:
                dataset = Variable.objects.get(id=int(el['type'])).dataset
                if dataset.id not in dataset_list:
                    dataset_list.append(dataset.id)
            print dataset_list
            for dataset_id in dataset_list:
                access_decision = PEP.access_to_dataset_for_query(request, dataset_id)
                if access_decision is False:
                    raise PermissionDenied
        except:
            return HttpResponseForbidden()

        try:
            check_api_calls(user)
        except Exception as e:
            print 'API call failed because user exceeded the number of allowed API calls or does not have a plan'
            traceback.print_exc()
            # return render(request, 'error_page.html', {'message': e.message})
            return JsonResponse({"error_message": e.message})
        try:
            # execute
            result = q.execute(dimension_values=dimension_values,
                               variable=variable,
                               only_headers=only_headers,
                               with_encoder=True)
        except ValueError as ve:
            return JsonResponse({"error_message": str(ve.message)})
        except Exception as e:
            if e.args[0] == 'max_memory_exceeded':
                return JsonResponse({"error_message": 'Your query execution exceeded the available memory. Please limit your selection on space and time and try again.'})
            else:
                return JsonResponse({"error_message": str(e.message)})
        response, encoder = result
        # import pdb
        # pdb.set_trace()
        # send results
        for dataset_list_el_id in dataset_list:
            try:
                dataset_obj = Dataset.objects.get(id=dataset_list_el_id)
                dataset_exploration(dataset_obj)
                if len(dataset_list) > 1:
                    dataset_join(dataset_obj)
            except:
                pass

        return JsonResponse(response, encoder=encoder)
    else:
        return HttpResponseForbidden()


def check_api_calls(user):
    user_plans = UserPlans.objects.filter(user=user, date_end__gte=datetime.now()).order_by('-date_end')
    if len(user_plans) > 0:
        user_plan = user_plans[0]
        plan = user_plan.plan
        plan_limit = plan.query_limit
        if plan_limit is not None:
            apicalls_count = user_plan.query_count
            if apicalls_count < plan_limit:
                check_flag = True
                user_plan.query_count = user_plan.query_count + 1
                user_plan.save()
                print 'API calls increased'
            else:
                print 'API calls exceeded plan limit'
                check_flag = False
        else:
            check_flag = True
            user_plan.query_count = user_plan.query_count + 1
            user_plan.save()
            print 'Unlimited plan'
    else:
        new_plan = UserPlans(user=user, plan=BDO_Plan.objects.get(plan_name='free'))
        new_plan.save()
        new_plan.query_count = new_plan.query_count + 1
        new_plan.save()
        check_flag = True
    if not check_flag:
        raise Exception('Permission Denied! You have exceeded your monthly request quota for the Big Data Ocean API!<br>Current Plan: ' + str(user_plan.plan.plan_title) + '<br>API Calls: ' + str(user_plan.query_count) + '/' + str(user_plan.plan.query_limit) + '<br>Please, upgrade to a higher tier!')