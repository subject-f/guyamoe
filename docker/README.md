# Getting Started

This Docker configuration does the absolute bare minimum for you to get started. 

Otherwise:
```bash
docker-compose up
``` 
in this directory and you're done. 

## nginx

If you want to run with Nginx (which you really shouldn't unless you change a bunch of the configurations), use: 
```bash
docker-compose -f docker-compose.yml -f nginx/docker-compose.yml up
```

## Superuser

Use this to create a superuser with the username `root` and password as `password`:
```bash
docker run -it --rm --network="guyamoe-intercontinental-highway" \
    -v $PWD/..:/guya -w="/guya" \
    -v $PWD/settings.py:/guya/guyamoe/settings.py \
    $(docker build -q -f Dockerfile ..) \
    sh -c "echo \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('root', 'root@example.com', 'password')\" | python manage.py shell"
```

Or you can just shell into the web container and create one that way. Either way works.

## docker-compose

If you can't be assed to install docker-compose, use this:
```bash
echo alias docker-compose="'"'sudo docker run --rm -it \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v "$PWD/../:$PWD/../" \
    -w="$PWD" \
    docker/compose:1.25.4'"'" >> ~/.bashrc

source ~/.bashrc
```
Note that this snippet isn't portable since the bind mount is specific for this purpose, so it may be a good idea to alias it differently.