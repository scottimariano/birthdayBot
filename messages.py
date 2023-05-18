import random

def generate_greeting (user):
    greetings = [
        f'¡Feliz cumpleaños, {user.mention}! 🎉🎂🎁 Que la pases bomba hoy y que se te cumplan todos los deseos.',
        f'¡Felicidades, {user.mention}! 🥳🎉🎈 Que tengas un día lleno de mate, asado y buena compañía.',
        f'¡Muchas felicidades, {user.mention}! 🎂🎁🎉 Que este día sea una fiesta inolvidable y te deje muchos recuerdos.',
        f'¡Feliz cumpleaños, {user.mention}! 🥳🎂🎈 Espero que la rompas en tu día y que siempre tengas razones para brindar.',
        f'¡Felicidades, {user.mention}! 🎉🎁🎂 Que los años que vienen estén llenos de metas cumplidas y pura felicidad.'
    ]
    jokes = [
        '¿Sabías que el cumpleaños es el día oficial para comer todas las empanadas que quieras? ¡Aprovechá, amigo!',
        '¿Por qué los cumpleaños son tan geniales? Porque son la excusa perfecta para comer medialunas sin culpa, loco.',
        '¿Sabés por qué te bancamos tanto? Porque hoy es tu cumpleaños y los amigos se bancan en las buenas y en las malas. Y por que traes torta!!.',
        '¡Mirá quién está un año más sabio y con más facha! Que sigas llenando de alegría nuestras vidas, ¡salud!'
    ]
    
    greeting = random.choice(greetings)
    joke = random.choice(jokes)
    
    message = f'{greeting} {joke}'
    
    return message