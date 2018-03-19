from json import dumps
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from django.contrib.staticfiles.templatetags.staticfiles import static

from .forms import CategoryForm, EventForm
from .models import Category, Event
from .helpers import is_admin, admin_route


class EventsListView(View):
    def get(self, request):
        events = Event.objects.filter(end__gte=datetime.now()).order_by('start')
        return render(request, 'events_list.html', {
            'events': events,
            'is_admin': is_admin(request)
        })

class EventsCalendarView(View):
    def get(self, request):
        events = Event.objects.all()
        calendar_event_objects = []

        for event in events:
            image = event.image.url if event.image else static('images/default-image.png')
            calendar_event_objects.append({
                'id': event.id,
                'title': event.name,
                'start': event.start.isoformat(),
                'end': event.end.isoformat(),
                'start_display': event.start.strftime("%b. %d, %Y, %I:%M %p"),
                'end_display': event.end.strftime("%b. %d, %Y, %I:%M %p"),
                'image': image,
                'description': event.description,
                'venue': event.venue,
                'category': event.category.name
            })

        return render(request, 'calendar.html', {
            'calendar_events': dumps(calendar_event_objects)
        })


class EventCreateView(View):
    def get(self, request):
        form = EventForm()
        title = "Create New Event"
        return render(request, 'event.html', {'form': form, 'title': title})

    def post(self, request):
        form = EventForm(request.POST, request.FILES)
        try:
            form.save()
        except ValueError as e:
            title = "Create New Event"
            return render(request, 'event.html', {'form': form, 'title': title})

        return redirect('events:events_list')


@method_decorator(admin_route, name='dispatch')
class EventApproveView(View):
    def get(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)    
            event.approved = True
            event.save()
            return redirect('events:events_list')
        except:
            return redirect('events:events_list')


@method_decorator(admin_route, name='dispatch')
class EventEditView(View):
    def get(self, request, event_id):

        try:
            event = Event.objects.get(pk=event_id)
        except:
            return redirect('events:events_list')

        form = EventForm(instance=event)
        title = "Edit Event"

        return render(request, 'event.html', {'form': form, 'title': title})

    def post(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
        except:
            return redirect('events:events_list')

        form = EventForm(request.POST, request.FILES, instance=event)
        try:
            form.save()
        except ValueError as e:
            title = "Edit Event"
            return render(request, 'event.html', {'form': form, 'title': title})

        return redirect('events:events_list')


@method_decorator(admin_route, name='dispatch')
class EventDeleteView(View):
    def get(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
            event.delete()
            return redirect('events:events_list')
        except:
            return redirect('events:events_list')

@method_decorator(admin_route, name='dispatch')
class CategoryCreateView(View):
    def get(self, request):
        form = CategoryForm()
        title = "Create New Category"
        return render(request, 'event.html', {'form': form, 'title': title})

    def post(self, request):
        form = CategoryForm(request.POST)
        try:
            form.save()
        except ValueError as e:
            title = "Create New Category"
            return render(request, 'event.html', {'form': form, 'title': title})

        return redirect('events:events_list')
        