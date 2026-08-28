from django.shortcuts import render


def placeholder(request):
    return render(request, "home.html", {"page_title": "管理端预留页面"})
