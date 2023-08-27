import json
import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db.models import ImageField

from PIL import Image


class AbstractSingleton:
    """
    Singleton class to store one instance per each child class

    EX:
        class Foo(AbstractSingleton):
            pass

        Foo()

        Then the mapper would be like this:
            {
                "Foo": <object blah blah>
            }
    """

    __CLS_OBJ_MAPPER = {}

    def __new__(cls, *args, **kwargs):
        if cls is AbstractSingleton:
            raise ValueError("create instances from abstract class is not allowed!")
        _mapper = AbstractSingleton.__CLS_OBJ_MAPPER
        if _mapper.get(cls.__name__) is None:
            _mapper[cls.__name__] = object.__new__(cls)
        return _mapper[cls.__name__]


class AbstractPropertySingleton:
    """
    This class can be used to create single instance from
    child class according to the first element sent to __init__
    method

    NOTICE: This class uses only the first parameter.
            You must ignore **kwargs when creating instances from child classes
            otherwise it wont work!!!

            EX :
                class Foo(AbstractPropertySingleton):
                    def __init__(self, name):
                        self.name = name

                correct ---- >     Foo("Python")
                wrong   ---- >     Foo(name="Python")

    EX:
        class Boo(AbstractPropertySingleton):
            def __init__(self, name):
                self.name = name
        class Blah(AbstractPropertySingleton):
            def __init__(self, last):
                self.last = last

        Boo("Python")
        Boo("Django")
        Blah("Developer")

        Then the class mapper would be like this:
        {
            "Boo": {
                "Python": < instance_1 >
                "Django": < instance_2 >
            },
            "Blah": {
                "Developer": < instance_1 >
            }
        }
    """

    __CLS_OBJ_PROPERTY_MAPPER = {}

    def __new__(cls, *args, **kwargs):
        if cls is AbstractPropertySingleton:
            raise ValueError("create instances from abstract class is not allowed!")
        _mapper = AbstractPropertySingleton.__CLS_OBJ_PROPERTY_MAPPER
        if _mapper.get(cls.__name__) is None:
            _mapper[cls.__name__] = {}
        try:
            return _mapper[cls.__name__][args[0]]
        except KeyError:
            _mapper[cls.__name__][args[0]] = object.__new__(cls)
            return _mapper[cls.__name__][args[0]]


class CustomImageField(ImageField):
    def __init__(self, *args, **kwargs):
        self.max_size = kwargs.pop("max_size", None)
        self.valid_dimensions = kwargs.pop("valid_dimensions", None)
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super().clean(*args, **kwargs)
        try:
            in_memory_file = data.file
            if self.max_size and in_memory_file.size > self.max_size:
                raise ValidationError(
                    _("Please keep file size under %s. Current file size is %s")
                    % (self.max_size, in_memory_file.size)
                )
            if self.valid_dimensions is not None:
                try:
                    tmp_img = Image.open(in_memory_file)
                    width, height = tmp_img.size
                except Exception:
                    raise ValidationError(_("Not a valid image file"))
                valid_height, valid_width = self.valid_dimensions
                if not (valid_height == height and valid_width == width):
                    raise ValidationError(
                        _("valid dimension is %s but got %s")
                        % (self.valid_dimensions, tmp_img.size)
                    )
        except FileNotFoundError:
            pass
        return data

