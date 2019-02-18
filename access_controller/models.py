from abc import ABCMeta, abstractmethod

from datetime import datetime


class Policy ():
    def __init__(self):
        pass

    @abstractmethod
    def evaluate(self, input):
        """Method documentation"""
        return


class PublicResourcePolicy(Policy):
    def evaluate(self, input):
        print("""Evaluating PublicResourcePolicy
        with input
        {0}
        """.format(input))

        # Try to get the required info
        try:
            resource_private = input['resource_private']
            request_user = input['request_user']

            # If the user is authenticated,
            if request_user.is_authenticated():
                print "user authenticated"
                # and is the resource is public,
                if resource_private is False:
                    print "resource is public"
                    return True
            print "Failed!"
            # Otherwise, deny
            return False

        # If info cannot be obtained, then deny
        except:
            print "Exception Failed!"
            return False


class OwnerPolicy(Policy):
    def evaluate(self, input):
        print("""Evaluating OwnerPolicy
                with input
                {0}
                """.format(input))

        # Try to get the required info
        try:
            resource_owner = input['resource_owner']
            resource_private = input['resource_private']
            request_user = input['request_user']

            # If the user is authenticated,
            if request_user.is_authenticated():
                print "user authenticated"
                # and is the resource is private,
                if resource_private is True:
                    print "resource is private"
                    # and is the owner,
                    if request_user.id == resource_owner.id:
                        print "user is the owner"
                        # then allow
                        return True
            print "Failed!"
            # Otherwise, deny
            return False

        # If info cannot be obtained, then deny
        except:
            print "Exception Failed!"
            return False


class AccessGrantedPolicy(Policy):
    def evaluate(self, input):
        print("""Evaluating AccessGrantedPolicy
                        with input
                        {0}
                        """.format(input))

        # Try to get the required info
        try:
            request_user = input['request_user']
            request_time = input['request_time']
            access_list = input['access_list']

            # If the user is authenticated,
            if request_user.is_authenticated():
                print "user authenticated"
                for accessInfo in access_list:
                    # and he is one of the users that have access,
                    print "testing access info"
                    print accessInfo
                    if request_user.id == accessInfo['user'].id:
                        print "user in access list"
                        # and the request is made during the access period,
                        s = accessInfo['start']
                        e = accessInfo['end']
                        if datetime(s.year, s.month, s.day) < request_time < datetime(e.year, e.month, e.day):
                            print "time in access period"
                            # and the access is valid,
                            if accessInfo['valid'] is True:
                                print "access is valid"
                                # then allow
                                return True
            print "Failed!"
            # Otherwise, deny
            return False

        # If info cannot be obtained, then deny
        except:
            print "Exception Failed!"
            return False


class EditGrantedPolicy(Policy):
    def evaluate(self, input):
        print("""Evaluating EditGrantedPolicy
                        with input
                        {0}
                        """.format(input))

        # Try to get the required info
        try:
            request_user = input['request_user']
            request_time = input['request_time']
            access_list = input['access_list']

            # If the user is authenticated,
            if request_user.is_authenticated():
                print "user authenticated"
                for accessInfo in access_list:
                    # and he is one of the users that have access,
                    print "testing access info"
                    print accessInfo
                    if request_user.id == accessInfo['user'].id:
                        print "user in access list"
                        # and the request is made during the access period,
                        s = accessInfo['start']
                        e = accessInfo['end']
                        if datetime(s.year, s.month, s.day) < request_time < datetime(e.year, e.month, e.day):
                            print "time in access period"
                            # and the access is valid,
                            if accessInfo['valid'] is True and accessInfo['can_edit'] is True:
                                print "access is valid"
                                # then allow
                                return True
            print "Failed!"
            # Otherwise, deny
            return False

        # If info cannot be obtained, then deny
        except:
            print "Exception Failed!"
            return False
