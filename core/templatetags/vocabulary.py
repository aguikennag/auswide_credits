from django import template


register = template.Library()

@register.filter()
def startswith_vowel(word) :
    if not isinstance(word,str) :
        return False
    return word.lower()[0] in ['a','e','i','o','u']    


@register.filter()
def capitalize(word) :
    try : return word.capitalize()
    except : pass