from django import template

register = template.Library()


@register.simple_tag
def str_to_int(data):
    if data:
        r1 = float(data.google_rating) if data and data.google_rating != '' else 0.0
        r2 = float(data.facebook_rating) if data and data.facebook_rating != '' else 0.0
        r3 = float(data.yelp_rating) if data and data.yelp_rating != '' else 0.0

        return {
            'avg_int': int((int(r1) + int(r2) + int(r3)) / 3),
            'avg_float': (r1 + r2 + r3) / 3
        }
    return 0