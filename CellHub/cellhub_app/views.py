from django.shortcuts import render  

def IndexView(request):  
    return render(request, 'cellhub_app/index.html', {'message': 'Hola Mundo'})