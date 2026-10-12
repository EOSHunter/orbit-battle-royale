class_name MouseLock
extends Node
## Owns pointer lock for the whole game. State is static so any script can call
## MouseLock.capture() etc.; the autoload "MouseLockTicker" runs _process.
##
## Browsers refuse a new pointer lock for about a second after Esc releases it,
## so a click that comes too soon is retried for a few seconds (the click's user
## activation is still valid) instead of giving up. Losing the lock any other way
## (Esc, alt-tab, a refused request) leaves the cursor visible until the next
## click; the game never turns the camera from a free cursor.

## How often a refused request is repeated, and for how long after the click.
const RETRY_EVERY := 0.3
const RETRY_FOR := 4.0
## Mouse movement ignored right after the lock is granted, when browsers can
## report one large jump.
const SETTLE_TIME := 0.05
## A single motion event larger than this (pixels) is a browser glitch, not a flick.
const MAX_MOTION := 500.0

static var _wanted := false
static var _retry_left := 0.0
static var _retry_wait := 0.0
static var _captured := false
static var _settle := 0.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_captured = is_captured()


## Ask for pointer lock. Call from a click or key press.
static func capture() -> void:
	_wanted = true
	_retry_left = RETRY_FOR
	_retry_wait = RETRY_EVERY
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


## Show the cursor and stop any pending request.
static func release() -> void:
	_wanted = false
	_retry_left = 0.0
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


static func is_captured() -> bool:
	return Input.mouse_mode == Input.MOUSE_MODE_CAPTURED


## True while a capture request is still being retried.
static func is_pending() -> bool:
	return _wanted and _retry_left > 0.0 and not _captured


## Camera movement for a motion event, or zero when it should be ignored.
static func look_delta(motion: InputEventMouseMotion) -> Vector2:
	if not _captured or _settle > 0.0 or motion.relative.length() > MAX_MOTION:
		return Vector2.ZERO
	return motion.relative


func _process(delta: float) -> void:
	_settle = maxf(0.0, _settle - delta)
	var now := is_captured()
	if now != _captured:
		_captured = now
		if now:
			_settle = SETTLE_TIME
			_retry_left = 0.0
		else:
			# Lost the lock (Esc, alt-tab): wait for the next click.
			_wanted = false
			_retry_left = 0.0
	if _wanted and not now and _retry_left > 0.0:
		_retry_left -= delta
		_retry_wait -= delta
		if _retry_wait <= 0.0:
			_retry_wait = RETRY_EVERY
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
