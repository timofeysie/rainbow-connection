# Emoji OS

## States for the learning sport

1. ready to sign up for game (blinking cursor)
2. joined game (check)
3. game ready (countdown?)
4. reading question (dots)
5. game on! (spinning wheel)
6. correct answer (green circle)
7. incorrect answer (red X)
8. second attempt correct (white circle)
9. game over result from server

These should all have small animations that can be interrupted if needed.

### Ready to sign up for game

This would be when the Pico is broadcasting on wifi.  The network connection is tested and the current data and time are called for.

This actually blocks the thread while it is happening, hence we need something like a blinking cursor to signal that something is happening.

When I pair with the Pico it starts its loop of counting how long it is connected for.  This is where whoever is using the app on the phone can start to prepare the game by collecting the details from each broadcasting Pico and send them the message that the game is about to start.

How does a user register their name as connected to the medallion device they will use?

One solution would be for them to have an NFC card with their username on it so this can be used to broadcast their availability.
