import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response

target_x = 0
target_y = 0
behaviour = "food"

@bottle.route('/')
def index():
	return '''
	Battlesnake documentation can be found at
	   <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
	'''

@bottle.route('/static/<path:path>')
def static(path):
	"""
	Given a path, return the static file located relative
	to the static folder.

	This can be used to return the snake head URL in an API response.
	"""
	return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
	"""
	A keep-alive endpoint used to prevent cloud application platforms,
	such as Heroku, from sleeping the application instance.
	"""
	return ping_response()

@bottle.post('/start')
def start():
	data = bottle.request.json
	
	
	global target_x
	global target_y
	target_x = data["board"]["food"][0]["x"]
	target_y = data["board"]["food"][0]["y"]
	"""
	TODO: If you intend to have a stateful snake AI,
			initialize your snake state here using the
			request's data if necessary.
	"""
	#print(json.dumps(data))

	color = "#00FF00"

	return start_response(color)


@bottle.post('/move')
def move():

	global target_x
	global target_y
	global behaviour
	data = bottle.request.json
	
	
	body = data["you"]["body"]	# list of dictionaries
	our_name = data["you"]["name"] #string
	head = body[0] #dictionary
	head_x = head["x"] #int
	head_y = head["y"]
	health = data["you"]["health"] #int
	tail = body[-1] #dictionary
	length = len(body) #int
	
	other_snakes = data["board"]["snakes"] #list of dictionaries
	other_snakes.remove(data["you"])
	
	height = data["board"]["height"] #int
	width = data["board"]["width"] #int

	food = data["board"]["food"] #list of dictionaries

	directions = ['up', 'down', 'left', 'right']
	direction = 'none'
	
	if(head_x == target_x and head_y == target_y):
		target_x = food[0]["x"]
		target_y = food[0]["y"]
	
	if(head_x == 0):
		directions.remove("left")
	if(head_x == width-1):
		directions.remove("right")
	if(head_y == 0):
		directions.remove("up")
	if(head_y == height-1):
		directions.remove("down")	

	
	for i in range(1,length):
		part_x = body[i]["x"]
		part_y = body[i]["y"]
		if(head_x - part_x == 1 and head_y - part_y == 0 and "left" in directions):
			directions.remove("left")
		if(head_x - part_x == -1 and head_y - part_y == 0 and "right" in directions):
			directions.remove("right")
		if(head_y - part_y == 1 and head_x - part_x == 0 and "up" in directions):
			directions.remove("up")
		if(head_y - part_y == -1 and head_x - part_x == 0 and "down" in directions):
			directions.remove("down")	
	
	#directions is now only movements that won't kill the snake from walls or itself
	
	#seek food
	if(behaviour == "food"):
		if(head_x - target_x > 0 and "left" in directions):
			direction = 'left'
		elif(head_x - target_x < 0 and "right" in directions):
			direction = 'right'
		if(head_y - target_y > 0 and "up" in directions):
			direction = 'up'
		elif(head_y - target_y < 0 and "down" in directions):
			direction = 'down'
	elif(behavour == "chase tail"):
		pass

	if(direction == 'none'):
		if(len(directions) > 0):
			direction = random.choice(directions)
		else:
			direction = "up"	
		

	return move_response(direction)


@bottle.post('/end')
def end():
	data = bottle.request.json

	"""
	TODO: If your snake AI was stateful,
		clean up any stateful objects here.
	"""
	#print(json.dumps(data))

	return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
	bottle.run(
		application,
		host=os.getenv('IP', '0.0.0.0'),
		port=os.getenv('PORT', '8080'),
		debug=os.getenv('DEBUG', True)
	)
