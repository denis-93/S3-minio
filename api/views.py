from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
import fs.errors
from fs_s3fs import S3FS
from fs import open_fs
from drf_spectacular.utils import extend_schema, OpenApiParameter


def get_s3_fs():
    """Создание файловой системы Amazon S3"""
    s3_fs = S3FS(
        settings.AWS_NAME_BUCKET,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_ENDPOINT_URL
    )
    return s3_fs


def downloader(home_dir, file_name):
    """Загрузчик файлов, возвращает True, если успешно"""
    if file_name != 'all':
        s3_fs = get_s3_fs()
        if file_name in s3_fs.listdir('/'):
            with home_dir.opendir('Downloads') as downloads:
                with s3_fs.open(file_name, 'rb') as f:
                    downloads.upload(file_name, f)
                    s3_fs.close()
                    return True
        else:
            return False
    else:
        with home_dir.opendir('Downloads') as downloads:
            s3_fs = get_s3_fs()
            files = s3_fs.listdir('/')
            for file in files:
                if s3_fs.isfile(file):
                    with s3_fs.open(file, 'rb') as f:
                        downloads.upload(file, f)
            s3_fs.close()
            return True


def download(request, file_name):
    """Представление для загрузки файлов"""
    if file_name != 'all':
        with open_fs('.') as home_dir:
            if home_dir.exists('Downloads'):
                is_download = downloader(home_dir, file_name)
                if is_download:
                    return HttpResponse('Успешная загрузка')
                else:
                    return HttpResponse('Ошибка при загрузке')
            else:
                home_dir.makedir('Downloads')
                is_download = downloader(home_dir, file_name)
                if is_download:
                    return HttpResponse('Успешная загрузка')
                else:
                    return HttpResponse('Ошибка при загрузке')
    else:
        with open_fs('.') as home_dir:
            if home_dir.exists('Downloads'):
                is_download = downloader(home_dir, file_name)
                if is_download:
                    return HttpResponse('Успешная загрузка')
                else:
                    return HttpResponse('Ошибка при загрузке')
            else:
                home_dir.makedir('Downloads')
                is_download = downloader(home_dir, file_name)
                if is_download:
                    return HttpResponse('Успешная загрузка')
                else:
                    return HttpResponse('Ошибка при загрузке')


def get_download_link(file_name='all'):
    """Получение ссылки для загрузки файлов"""
    return reverse('api:download-link', args=(file_name,))


class S3APIView(APIView):

    @extend_schema(parameters=[OpenApiParameter(name='file', description='Имя файла', required=False, type=str)])
    def get(self, request, *args, **kwargs):
        """Получение файлов и ссылок на их загрузку.
        В качестве параметра можно указать конкретный file,
        если параметров нет, вернет список всех файлов и ссылку на их загрузку"""
        if request.GET.get('file'):
            file = request.GET.get('file')
            s3_fs = get_s3_fs()
            files = s3_fs.listdir('/')
            if file in files:
                info = s3_fs.getinfo(file, namespaces=["details"])
                response = {
                    'file': file,
                    'size': info.size,
                    'download_link': request.get_host() + get_download_link(file)
                }
                s3_fs.close()
                return Response(response, status=200)
            else:
                return Response({'error': 'Файла не существует'})
        else:
            s3_fs = get_s3_fs()
            response = {
                'list_files': s3_fs.listdir('/'),
                'download_link': request.get_host() + get_download_link()
            }
            s3_fs.close()
            return Response(response, status=200)

    def post(self, request, *args, **kwargs):
        """Отправляет файлы на S3. В body в качестве обязательного аргумента path(директория),
        необязательный file_name. Если file_name не указан, отправит в облако все файлы в директории"""
        if {'path'}.issubset(request.data):
            try:
                uploads = open_fs(request.data['path'])
            except fs.errors.CreateFailed:
                return Response({'error': 'Несуществующий путь'})
            files = uploads.listdir('/')
            if {'file_name'}.issubset(request.data):
                if request.data['file_name'] in files:
                    with uploads.open(request.data['file_name'], 'rb') as f:
                        s3_fs = get_s3_fs()
                        s3_fs.upload(request.data['file_name'], f)
                        response = {'status': 201, 'list_files': s3_fs.listdir('/')}
                        s3_fs.close()
                        uploads.close()
                        return Response(response, status=201)
                else:
                    return Response({'error': 'Файл не найден'})
            else:
                for file in files:
                    if uploads.isfile(file):
                        with uploads.open(file, 'rb') as f:
                            s3_fs = get_s3_fs()
                            s3_fs.upload(file, f)
                response = {'status': 201, 'list_files': s3_fs.listdir('/')}
                s3_fs.close()
                uploads.close()
                return Response(response, status=201)
        else:
            return Response({'error': 'Нет необходимых аргументов'})
