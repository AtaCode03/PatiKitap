import pytest
from io import BytesIO
from PIL import Image
from fastapi import HTTPException
from main import normalize_image,image_check
from auth import Identity

def test_image_is_reencoded_resized_and_invalid_data_is_rejected():
    image=Image.new('RGB',(1900,1200),'orange');source=BytesIO();image.save(source,'PNG')
    result=normalize_image(source.getvalue())
    with Image.open(BytesIO(result)) as output:
        assert output.format=='JPEG' and max(output.size)<=1600
        assert not output.getexif()
    with pytest.raises(HTTPException):normalize_image(b'not an image')

def test_image_reference_requires_own_canonical_object_path():
    user=Identity('11111111-1111-4111-8111-111111111111')
    image_check('book-media/'+user.id+'/'+'a'*32+'.jpg',user)
    with pytest.raises(HTTPException):image_check('book-media/'+user.id+'/../someone/image.jpg',user)
