from django import template

from main.models import ContactMessage

register = template.Library()


@register.simple_tag(takes_context=True)
def unread_messages(context):
    """Jumlah pesan Contact yang belum dibaca. Hanya untuk pemilik
    (superuser); pengunjung lain selalu mendapat 0, dan tidak ada query."""
    request = context.get("request")
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated or not user.is_superuser:
        return 0
    return ContactMessage.objects.filter(is_read=False).count()