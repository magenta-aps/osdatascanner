# chat/views.py
from django.shortcuts import render


def socketindex(request):
    return render(request, 'socket_template/socketindex.html')
    


def socketroom(request, room_name):
    return render(request, 'socket_template/socketroom.html', {
        'room_name': room_name
    })
