# 🤖Comandos de Chatbot de YouTube
Ejecuta comandos para obtener información del stream, minijuegos, etc. Alguien llamado **lord_shit** te responderá...

## Comandos disponibles
- **!comandos**: Lista de comandos disponibles
- **!calva**: Me das un beso en la calva y suena algo!!
- **!led [color]**: (Solo en Navidad). Usa este comando para cambiar el color de los leds de mi gorro de navidad. Tiene un cooldown de uso de 5 minutos.
	- Colores disponibles: azul, rojo, verde, morado, amarillo, furcia, rainbow, apagado
	- Ejemplo de uso: **!led azul**, **!led morado**
- **!redes**: Lista de mis redes sociales
- **!pc**: Especificaciones de mis PCs
- **!discord**: Mi server de Discord
- **!donar**: Enlaces para hacer una aportación al stream
- **!gamble [cantidad]**: Apuesta tus **Monedas Calvas** en una tragaperras.
	El juego depende solo de **azar** y no hay ningún porcentaje de suerte/mala suerte.
	Tienes un** cooldown de 5 minutos** por usuario. Más abajo verás cómo conseguir **monedas gratis**
	- Recompensas:
		- 3 estrellas [⭐⭐⭐]: **x2.5**
		- 3 emojis iguales (Ejemplo [👽👽👽]): **x2**
		- 2 emojis iguales (Ejemplo [⭐❤️⭐]): **x1.5**
- **!monedas**: Consulta cuántas **Monedas Calvas** tienes. Abajo verás el funcionamiento de estas monedas.
- **!canjear [recompensa]**: Canjea una recompensa por **Monedas Calvas**
	- Recompensas disponibles:
		- **susto**: me das un susto :D. (Ejemplo: **!canjear susto**)
			- **Coste**: 200 Monedas Calvas
		- **destacar [mensaje]**: Destaca un mensaje en la pantalla. El mensaje se verá en los demás servicios y se quedará guardado en el vídeo, no solo en el chat. (Ejemplo: **!canjear destacar Hola, quiero salir en el stream**)
			- **Coste**: 500 Monedas Calvas

## Sistema de Monedas (Monedas Calvas)
Cada usuario tiene sus propias Monedas Calvas, que se consiguen automáticamente cada 5 minutos solo **si has interactuado en el chat en esos 5 minutos**. Con solo escribir 1 vez en esos 5 minutos, **conseguirás 20 Monedas Calvas**. 
‼️Estas monedas solo se usarán dentro del stream y se podrán canjear por **acciones en el propio stream**, pero **nunca se podrán canjear por bienes** (dinero, skins de juego, claves de juegos, etc). En resumen, **no puedes comprar ni vender estas monedas**, solo son monedas de minijuegos‼️
Puedes navegar por este repositorio para comprobar cómo está hecho el sistema de monedas. 
En app.py se reparten 20 monedas cada 5 minutos a los usuarios que han escrito en el chat en esos 5 minutos
Dentro de scripts/gambler/gambler.py, podrás ver cómo funciona la apuesta
