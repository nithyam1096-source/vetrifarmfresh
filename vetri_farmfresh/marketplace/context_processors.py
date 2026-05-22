from .models import Cart

def cart_count(request):
    if request.user.is_authenticated:
        count = Cart.objects.filter(customer__user=request.user).count()
        return {'cart_count': count}
    return {'cart_count': 0}
