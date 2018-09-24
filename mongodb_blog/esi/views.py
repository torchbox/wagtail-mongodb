from django.shortcuts import render_to_response

from mongodb_blog.esi import ESI_REGISTRY


def esi(request, name):
    template = ESI_REGISTRY[name]['template']
    context = ESI_REGISTRY[name]['get_context']()
    return render_to_response(template, context)
