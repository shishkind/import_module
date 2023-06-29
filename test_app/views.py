# views.py
from django.http import HttpResponse
from django.template import loader

def show_phones(request):
    template = loader.get_template('index.html')
    context = {}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)

from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm

# Imaginary function to handle an uploaded file.
from Parser import main
from django.utils.safestring import mark_safe

import fileinput

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            print(f)
            with open(request.FILES['file'].name, 'wb+') as destination:
               for chunk in request.FILES['file'].chunks():
                    destination.write(chunk)
            result = [0,0,0,0,0,0]
            result = main(f)
            template = loader.get_template('index.html')
            context = {'form' : form, 'try': mark_safe('<div class="alert alert-success" role="alert"> В систему успешно добавлено %s публикаций.<ul><li>Статьи в научных журналах: %s</li><li>Материалы конференций: %s</li><li>Главы в книгах: %s</li></li><li>Прочие: %s</li></ul>Источник данных - %s</div>'%(result[1], result[3], result[2], result[4], result[5], result[0]))}
            return render(request, 'index.html', context)

    else:
        form = UploadFileForm() 
        return render(request, 'index.html', {'form': form, })