import random

def generate_greeting (user):
    greetings = [
        f'¡Feliz cumpleaños, {user.mention}! 🎉🎂🎁 Que tengas un día lleno de alegría y diversión!',
        f'¡Felicidades, {user.mention}! 🥳🎉🎈 Espero que pases un día increíble rodeado de tus seres queridos.',
        f'¡Muchas felicidades, {user.mention}! 🎂🎁🎉 Te deseo un día lleno de risas y momentos inolvidables.',
        f'¡Feliz cumpleaños, {user.mention}! 🥳🎂🎈 Que todos tus deseos se hagan realidad y disfrutes al máximo de tu día.',
        f'¡Felicidades, {user.mention}! 🎉🎁🎂 Espero que la vida te siga llenando de alegrías y éxitos.'
    ]
    jokes = [
        '¿Sabías que el cumpleaños es bueno para la salud? Los estudios demuestran que las personas que tienen más cumpleaños viven más tiempo.',
        '¿Qué tipo de pastel prefieren los fantasmas para su cumpleaños? ¡Pastel de susto!',
        '¿Por qué los cumpleaños son buenos para ti? ¡Estadísticamente, las personas que tienen más cumpleaños viven más tiempo!',
        '¿Sabes por qué te queremos tanto? Porque hoy es tu cumpleaños. 😁🥳🎂',
        '¡Mira quién está un año más cerca de convertirse en un viejo cascarrabias! 🤣🎉'
    ]
    
    greeting = random.choice(greetings)
    joke = random.choice(jokes)
    
    message = f'{greeting} Espero que pases un gran día! {joke}'
    
    return message