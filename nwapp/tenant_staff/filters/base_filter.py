# -*- coding: utf-8 -*-
import django_filters
from tenant_foundation.models import Staff
from django.db import models
from django.db.models import Q
from django.utils import timezone


class StaffFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('user__member__contact__first_name', 'first_name'),
            ('user__member__contact__last_name', 'last_name'),
            # ('telephone', 'telephone'),
            ('user__member__contact__email', 'email'),
            ('user__groups', 'role_id'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    def keyword_filtering(self, queryset, name, value):
        return Staff.objects.search(value).order_by('user__member__contact__last_name')

    search = django_filters.CharFilter(method='keyword_filtering')

    def first_name_filtering(self, queryset, name, value):
        return queryset.filter(
            Q(user__member__contact__first_name__icontains=value) |
            Q(user__member__contact__first_name__istartswith=value) |
            Q(user__member__contact__first_name__iendswith=value) |
            Q(user__member__contact__first_name__exact=value) |
            Q(user__member__contact__first_name__icontains=value)
        )

    first_name = django_filters.CharFilter(method='first_name_filtering')

    def last_name_filtering(self, queryset, name, value):
        return queryset.filter(
            Q(user__member__contact__last_name__icontains=value) |
            Q(user__member__contact__last_name__istartswith=value) |
            Q(user__member__contact__last_name__iendswith=value) |
            Q(user__member__contact__last_name__exact=value) |
            Q(user__member__contact__last_name__icontains=value)
        )

    last_name = django_filters.CharFilter(method='last_name_filtering')

    # def available_for_task_item_filtering(self, queryset, name, value):
    #     """
    #     Filter will find all the available staffs for the specific job
    #     for the task.
    #     """
    #     task_item = TaskItem.objects.filter(id=value).first()
    #
    #     # (a) Find all the unique staffs that match the job skill criteria
    #     #     for the job.
    #     # (b) Find all the unique staffs which do not have any activity
    #     #     sheet items created previously.
    #     # (c) FInd all unique staffs which have active accounts.
    #     # (d) If an Staff has an active Announcement attached to them,
    #     #     they should be uneligible for a job.
    #     skill_set_pks = None
    #     try:
    #         skill_set_pks = task_item.job.skill_sets.values_list('pk', flat=True)
    #         activity_sheet_staff_pks = ActivitySheetItem.objects.filter(
    #             job=task_item.job
    #         ).values_list('staff_id', flat=True)
    #         queryset = queryset.filter(
    #            Q(skill_sets__in=skill_set_pks) &
    #            ~Q(id__in=activity_sheet_staff_pks) &
    #            Q(owner__is_active=True) &
    #            Q(
    #                Q(away_log__isnull=True)|
    #                Q(away_log__start_date__gt=timezone.now()) # (*)
    #            )
    #         ).distinct()
    #
    #         # (*) - If tstaffs vacation did not start today then allow
    #         #       the staff to be listed as available in the list.
    #     except Exception as e:
    #         available_staffs = None
    #         print("available_for_task_item_filtering |", e)
    #     return queryset
    #
    # available_for_task_item = django_filters.CharFilter(method='available_for_task_item_filtering')
    #
    # def keyword_filtering(self, queryset, name, value):
    #     return Staff.objects.partial_text_search(value)
    #
    # search = django_filters.CharFilter(method='keyword_filtering')
    #
    # def state_filtering(self, queryset, name, value):
    #     return queryset.filter(owner__is_active=value)
    #
    # state = django_filters.NumberFilter(method='state_filtering')
    #
    # def skill_sets_filtering(self, queryset, name, value):
    #     pks_string = value
    #     pks_arr = pks_string.split(",")
    #     if pks_arr != ['']:
    #         queryset = queryset.filter(
    #             skill_sets__in=pks_arr,
    #             owner__is_active=True
    #         )
    #         queryset = queryset.order_by('last_name', 'given_name').distinct()
    #
    #     return queryset
    #
    # skill_sets = django_filters.CharFilter(method='skill_sets_filtering')
    #
    def email_filtering(self, queryset, name, value):
        # DEVELOPERS NOTE:
        # `Django REST Framework` appears to replace the plus character ("+")
        # with a whitespace, as a result, to fix this issue, we will replace
        # the whitespace with the plus character for the email.
        value = value.replace(" ", "+")

        # Search inside user account OR the customer account, then return
        # our filtered results.
        queryset = queryset.filter(
            Q(user__email=value)|
            Q(user__member__contact__email=value)
        )
        return queryset

    email = django_filters.CharFilter(method='email_filtering')

    def telephonel_filtering(self, queryset, name, value):
        return queryset.filter(
            Q(user__member__contact__primary_phone=value)|
            Q(user__member__contact__secondary_phone=value))

    telephone = django_filters.CharFilter(method='telephonel_filtering')

    def role_id_filtering(self, queryset, name, value):
        if value == 0 or value == "0":
            return queryset
        return queryset.filter(
            user__groups__id=value,
            user__is_active=True
        )

    role_id = django_filters.NumberFilter(method='role_id_filtering')

    def role_ids_filtering(self, queryset, name, value):
        pks_string = value
        pks_arr = pks_string.split(",")
        if pks_arr != ['']:
            queryset = queryset.filter(
                user__groups__in=pks_arr,
                user__is_active=True
            )
            queryset = queryset.order_by('user__last_name', 'user__first_name').distinct()

        return queryset

    role_ids = django_filters.CharFilter(method='role_ids_filtering')

    class Meta:
        model = Staff
        fields = [
            'search',
            'first_name',
            'last_name',
            'email',
            'telephone',
            'role_id',
            'role_ids',
        ]
