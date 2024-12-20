from django.core import serializers
from django.contrib import messages

from app.models import BusinessTypes, Business, BusinessCategories
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from . locations import locations


def index_page(request):
    try:
        """print((
            Business.objects
            .values('google_pid')  # Group by the 'google' field
            .annotate(count=Count('id'))  # Count occurrences
            .order_by('google_pid')  # Optional: order by the 'google' field
        ))"""
        context = {
            'types': BusinessTypes.objects.all(),
            'categories': BusinessCategories.objects.all(),
            'business': Business.objects.all()[0:20],
            'locations': locations,
            'featured': Business.objects.filter(featured=True).all()
        }

        return render(request, 'app/index.html', context)
    except Exception as e:
        print(e)
        return JsonResponse({'statusMsg': 'error'}, status=404)


def search_page(request):
    try:
        category = request.GET.get('category')
        location = request.GET.get('location')

        page_number = 1 if not request.GET.get('page')  else request.GET.get('page')
        paginator = Paginator(Business.objects.filter(type__category_id=category, type__address=location), 20)
        context = {
            'types': BusinessTypes.objects.all(),
            'categories': BusinessCategories.objects.all(),
            'business': paginator.get_page(page_number),
            'locations': locations,
            'location': location,
            'category': BusinessCategories.objects.filter(id=category).first(),
            'featured': Business.objects.filter(featured=True).all()
        }
        return render(request, 'app/index.html', context)

    except Exception as e:
        print(e)
        return JsonResponse({'statusMsg': 'error'}, status=404)


def business_list(request):
    try:
        page_number = 1 if not request.GET.get('page') else request.GET.get('page')
        paginator = Paginator(Business.objects.all(), 20)

        data = serializers.serialize('json', paginator.get_page(page_number))

        # Optionally return a JsonResponse in a view
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(e)

def featured_business(request):
    try:
        data = serializers.serialize('json', Business.objects.filter(featured=True).all())

        # Optionally return a JsonResponse in a view
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(e)


def business_list_search(request, category, location):
    try:
        page_number = 1 if not request.GET.get('page')  else request.GET.get('page')
        paginator = Paginator(Business.objects.filter(type__category__slug=category, type__slug=location), 20)
        data = serializers.serialize('json', paginator.get_page(page_number))
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(e)
        return JsonResponse({'statusMsg': 'error'}, status=404)


def categories_list(request):
    try:
        data = serializers.serialize('json', BusinessCategories.objects.all())
        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'statusMsg': 'error'}, status=404)


def types_list(request):
    try:
        data = serializers.serialize('json', BusinessTypes.objects.all())
        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'statusMsg': 'error'}, status=404)


def update_business_page(request, business_id):
    try:
        business = Business.objects.filter(id=business_id).first()
        if request.method == "POST" and business:
            business.name = request.POST.get('name')
            business.phone = request.POST.get('phone')
            business.email = request.POST.get('email')
            business.google_rating = request.POST.get('google_rating')
            business.google_reviews_count = request.POST.get('google_reviews_count')
            business.facebook_rating = request.POST.get('facebook_rating')
            business.facebook_reviews_count = request.POST.get('facebook_reviews_count')
            business.yelp_rating = request.POST.get('yelp_rating')
            business.yelp_reviews_count = request.POST.get('yelp_reviews_count')
            business.our_review = request.POST.get('our_review')
            business.our_rating = request.POST.get('our_rating')
            business.save()
            messages.success(request, f"{business.name} successfully updated.")

            if request.POST.get('category') and request.POST.get('location'):
                return redirect('app-search-page', category=request.POST.get('category'), location=request.POST.get('location'))

            return redirect('app-index-page')
        context = {
            'business': business
        }
        return render(request, 'app/update.html', context)
    except Exception as e:
        print(e)


def show_business_page(request, business_id):
    try:
        context = {
            'business': Business.objects.filter(id=business_id).first()
        }
        return render(request, 'app/show_business.html', context)

    except Exception as e:
        print(e)