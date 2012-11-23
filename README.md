    from mseparse.parse.mse2 import unzip_mse, set_data
    from zipfile import BadZipfile
    from yourproject import Set, Card  # Django Models of Sets and Cards
    from django.core.files.base import ContentFile

    try    
        zipfile = unzip_mse(mse_file_obj)
        set_spec, card_specs = set_data(_zipfile)
    except BadZipFile    
        raise ValueError("Couldn't parse")

    instance = Set()  # Django Model, but any object with attributes will do
    instance = update_setmodel_from_spec(instance, set_info)
    instance.save()
    previous_card_map = dict((i.name, i) for i in instance.card_set.all())
    for spec in card_specs:
        card = previous_card_map.get(spec.get('name').strip()) or\
                                            Card(user=request.user)
        card = update_cardmodel_from_spec(card, spec)
        card.set = instance
        if spec.get('image'):
            image = image_data(form._zipfile, spec['image'])
            if image:
                card.image.save('%s-%s.jpg' % (instance.slug, spec['image']),
                                                ContentFile(image.read()))
        card.save()
    instance.mse_file.save(request.FILES['mse_file'].name,
                                    mse_file_obj)
    messages.success(request, "MSE File imported")


