## ACTIONS ##

### Outside site: ###
##### Login #####
Users can log into and out of their accounts.

##### Register/Create new user #####
New Users can sign up for an account, they are logged in upon registering.

---
######(All of the below actions are only available to logged in users)######

### Main Page: ###
##### Make game #####
Users can create a new tafl session. 
They may choose to play as white or black, or may choose “random” if they don’t care which. 
After clicking OK, they will sit on the game screen until a second player joins them. 
When someone tries to do so, this starting player will get a pop-up saying 
“[Name2] wants to join you. Is this okay? Y/N” and they may then accept or reject that player. 
If they accept, and the colors of the players haven’t been set yet, then they will be prompted to select. 

The chat feature will be active at this time so they may discuss. 
There will also be an option for random assignment by the computer. 
Once colors are set, the game begins. 
If the starting player rejects the newcomer, they resume sitting on the game screen waiting, 
and the other play will receive a notice they’ve been rejected and may continue perusing the main page.

##### Join game #####
Users may instead scroll through open games others have created and click “join” to play with someone.

##### Sort games #####
The list of open games is sortable by open color, initiating player rank, or time, 
with the default sorting being newest-to-oldest.

##### Search for user #####
Users may search for other users’ profiles by entering a username into the search bar. 
Results in the form of profile links are returned beneath this.


### Game: ###
##### Make Move #####
The player whose turn it is can move one of their pieces. 
When they attempt a move, the server checks if the move was valid 
(and if it wasn’t, resets the move and gives an error message and lets the player try again),
if it causes any pieces to be captured, or if it triggers either of the win conditions.
Once this is complete, the game switches to the other player for their turn.

##### Resign Game #####
A user may click this button at any time to resign the game. 
This will give them a loss to their record. Upon clicking,
they will first be prompted with a pop-up asking them to confirm that they want to end the game.

#####Request Rules Pop-up #####
A user may click this button at any time to get a pop-up window with a brief rules explanation.

##### Send Chat Message #####
Users may send each other brief text messages via a chat client next to the game.
 The chat display will be updated in real time as they do so.

##### Disable chat #####
Users may turn off chat for themselves. The client will not appear on the page while it is disabled.


### Leaderboard: ###
##### Load leaderboards #####
Because tafl is an asymmetric game (the goals of the black side and the white side are different), 
there will be three leaderboards - one listing players by overall rank (determined by their overall win/loss record),
one ranking them by specifically their win/loss record as white, and the last specifically as black.
Each player listing gives their username and their rank for that board.
The username will link to their profile.

### Player profiles: ###
##### Load rank/win-loss/etc info #####
Player profiles give the player name and various stats 
(overall/white/black ranks, games played/won/lost, games played/won/lost as white/black).