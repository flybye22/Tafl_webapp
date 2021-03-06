from django.shortcuts import render, redirect, get_object_or_404
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage

from django.http import Http404, HttpResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
import json

import random

from tafl.redis import *
from tafl.models import *
from tafl.forms import *
import tafl.game

@login_required
def gamespage(request):
    context = {}

    currUser = request.user
    context['user'] = currUser

    sortby = request.GET.get('sortby')
    #citation for __isnull
    #stackoverflow.com/questions/14831327/in-a-django-queryset-how-to-
       # filter-for-not-exists-in-a-many-to-one-relationsh
    if sortby == 'timeOtN' or not sortby:
        # by timeOtN is default
        games = Game.objects.filter(waiting_player__isnull=False).order_by('timestamp')
    if sortby == "timeNtO":
        games = Game.objects.filter(waiting_player__isnull=False).order_by('-timestamp')
    if sortby == 'rankLtH':
        games = Game.objects.filter(waiting_player__isnull=False).order_by('waiting_player__rank')
    if sortby == 'rankHtL':
        games = Game.objects.filter(waiting_player__isnull=False).order_by('-waiting_player__rank')

    fbC = request.GET.get('filterbyC')
    if fbC == 'BL':
        games = games.filter(black_player__isnull=True)
    elif fbC == 'WH':
        games = games.filter(white_player__isnull=True)

    fbV = request.GET.get('filterbyV')
    if fbV == 'tablut':
        games = games.filter(ruleset__name="Tablut")
    elif fbV == 'brandubh':
        games = games.filter(ruleset__name="Brandubh")
        
    context['games'] = games
    usform = SearchForm()
    context['usform'] = usform
    return render(request, "tafl/mainpage.html", context)

@login_required
@transaction.atomic
def game(request):
    # Get player
    p = Player.objects.get(user=request.user)
    # Post requests to game are move requests
    if(request.method == 'POST' and "move" in request.POST and request.POST["move"] != ""):
        # Get game and move
        move = json.loads(request.POST["move"])
        g = request.user.player_set.all()[0].cur_game

        # Check if move is valid
        if(not g.is_valid_move(move[0], move[1])):
            return HttpResponse("invalid move")

        # Move was valid, check for other player and send the move update
        if(g.other_player(p) != None):
            send_move_update(g.other_player(p), move)

        # Commit move to database
        g.make_move(move[0], move[1])

        # Check for capture and make capture
        toRemove = g.check_capture(move[1])
        for sq in toRemove:
            send_capture(p, g.other_player(p), [sq.x_coord, sq.y_coord])

        # Check for win and do win things if appropriate
        winner = g.check_win()
        if(winner != None):
            g.end_game(winner)

        return HttpResponse("valid")

    if(p.cur_game == None):
        return redirect('/tafl/')
    messages = ChatMessage.objects.filter(game = p.cur_game)
    context = {'game':p.cur_game, 'player': p, 'messages': messages}
    return render(request, "tafl/gamepage.html", context)

@login_required
def makegame(request):
    if(request.method == 'POST'):
        #check if user already has a game going - if so, error
        if Player.objects.get(user=request.user).cur_game != None:
            HttpResponse("error: already have a game in progress")
            return gamespage(request)
            
        form = GameForm(request.POST)
        if form.is_valid():
            ruleset = Ruleset.objects.get(name=form.cleaned_data['ruleset'])
            player = Player.objects.get(user=request.user)
            if(form.cleaned_data['optradio'] == "black"):
                g = tafl.game.make_game(ruleset, player, None, player)
            elif(form.cleaned_data['optradio'] == "white"):
                g = tafl.game.make_game(ruleset, None, player, player)
            else:
                coinflip = random.randint(0,1)
                if coinflip:
                    g = tafl.game.make_game(ruleset, None, player, player)
                else:
                    g = tafl.game.make_game(ruleset, player, None, player)
            
            if(form.cleaned_data['is_priv']): #private game
                g.is_priv = True
                g.priv_pw = form.cleaned_data['priv_pw']
                g.save()

            player.cur_game = g;
            player.save()

    return redirect('/tafl/game')

@login_required
def joingame(request):
    context = {}

    usr = request.user
    player = Player.objects.get(user=usr)
    
    #if player already has a cur_game, error
    if player.cur_game != None:
        HttpResponse("error: have game already in progress")
        return gamespage(request)

    gameid = request.POST['gameid']
    g = Game.objects.get(pk=gameid)

    #if private game, check inputted pw against stored one
    if g.is_priv:
        pwAttempt = request.POST['gamepw']
        if pwAttempt != g.priv_pw:
            HttpResponse("wrong pw")
            context['user'] = request.user
            context['games'] = Game.objects.filter(waiting_player__isnull=False).order_by('timestamp')
            context['usform'] = SearchForm()
            context['wrongpw'] = True
            context['wronggame'] = g.id
            return render(request, "tafl/mainpage.html", context)

    #set player 2
    if g.black_player != None:
        g.white_player = player
    elif g.white_player != None:
        g.black_player = player
    else: #shouldn't happen now, return error.
        return HttpResponse("error")

    send_join(g.waiting_player, player)
    g.waiting_player = None #cleanup
    player.cur_game = g

    g.save()
    player.save()

    return redirect('/tafl/game') 

@login_required
def usersearch(request):
    context = {}
    form = SearchForm(request.POST)
    if form.is_valid():
        results = User.objects.filter(username__icontains=form.cleaned_data['search']).filter(is_staff=False)
        if not results.exists():
            context['nores'] = True
        context['usres'] = results
    context['user'] = request.user
    context['games'] = Game.objects.filter(waiting_player__isnull=False).order_by('timestamp')
    context['usform'] = SearchForm()
    return render(request, "tafl/mainpage.html", context)

@login_required
def profile(request):
    context = {}

    # user making the request so their profile link in navbar works
    currUser = request.user
    context['user'] = currUser

    # user whose profile we want to load
    profUser = get_object_or_404(User, username=request.GET.get('un'))
    context['puser'] = profUser
    player = Player.objects.get(user=profUser)
    context['rank'] = player.rank

    #get white finished total, get black finished total
    whitecompleteall = Game.objects.filter(white_player=player).filter(winner__isnull=False)
    blackcompleteall = Game.objects.filter(black_player=player).filter(winner__isnull=False)

    #get wins for each of those
    whitewins = whitecompleteall.filter(winner=player)
    blackwins = blackcompleteall.filter(winner=player)

    #do variant filtering if necessary
    variant = request.GET.get('variant')
    if variant == None:
        variant = "Overall"

    context['curvar'] = variant

    if variant == "Tablut" or variant == "Brandubh":
        whitetotal = whitecompleteall.filter(ruleset__name=variant).count()
        blacktotal = blackcompleteall.filter(ruleset__name=variant).count()
        whitewin = whitewins.filter(ruleset__name=variant).count()
        blackwin = blackwins.filter(ruleset__name=variant).count()
    else:
        whitetotal = whitecompleteall.count()
        blacktotal = blackcompleteall.count()
        whitewin = whitewins.count()
        blackwin = blackwins.count()

    #compute remaining stats
    whitelose = whitetotal - whitewin
    blacklose = blacktotal - blackwin
    overalltotal = whitetotal + blacktotal
    overallwin = whitewin + blackwin
    overalllose = whitelose + blacklose

    #send'em
    context['whitetotal'] = whitetotal
    context['whitewin'] = whitewin
    context['whitelose'] = whitelose
    context['blacktotal'] = blacktotal
    context['blackwin'] = blackwin
    context['blacklose'] = blacklose
    context['overalltotal'] = overalltotal
    context['overallwin'] = overallwin
    context['overalllose'] = overalllose
    return render(request, "tafl/profile.html", context)

@login_required
def about(request):
    return render(request, "tafl/about.html")

@login_required
def leaderboard(request):
    context = {}
    context['players'] = []
    for p in Player.objects.all():
        player_dict = {}
        player_dict['name'] = p.user.username
        player_dict['rank'] = p.rank
        player_dict['whwin'] = Game.objects.filter(white_player=p, winner=p).count()
        player_dict['blwin'] = Game.objects.filter(black_player=p, winner=p).count()
        player_dict['whgames'] = Game.objects.filter(white_player=p, waiting_player=None).exclude(winner=None).count()
        player_dict['blgames'] = Game.objects.filter(black_player=p, waiting_player=None).exclude(winner=None).count()
        context['players'].append(player_dict)
    return render(request, "tafl/leaderboard.html", context)

def mylogin(request):
    context = {}
    if request.method == "GET":
        context['lform'] = LoginForm()
        context['rform'] = RegistrationForm()
        return render(request, "tafl/login.html", context)
    
    form = LoginForm(request.POST)
    context['lform'] = form
    
    if not form.is_valid():
        context['rform'] = RegistrationForm()
        return render(request, "tafl/login.html", context)

    user = authenticate(username=form.cleaned_data['username'], 
                        password=form.cleaned_data['password'])
    if user is not None and user.is_active:
        login(request, user)
        return redirect('/tafl/')
    
    context['rform'] = RegistrationForm()
    return render(request, "tafl/login.html", context)

def mylogout(request):
    logout(request)
    context = {}
    context['lform'] = LoginForm()
    context['rform'] = RegistrationForm()
    return render(request, "tafl/login.html", context)

@transaction.atomic
def register(request):
    context = {}
    form = RegistrationForm(request.POST)
    context['rform'] = form

    if not form.is_valid():
        context['lform'] = LoginForm()
        return render(request, "tafl/login.html", context)

    #create user
    newUser = User.objects.create_user(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    email=form.cleaned_data['email'])
    newUser.save()

    #create player
    newPlayer = Player(user=newUser, cur_game=None, rank=400)
    newPlayer.save()
    
    #log them in
    newUser = authenticate(username=form.cleaned_data['username'],
                           password=form.cleaned_data['password1'])
    login(request, newUser)
    return redirect('/tafl/')

@login_required
@transaction.atomic
def resign(request):
    p = Player.objects.get(user=request.user)
    p.cur_game.end_game(p.cur_game.other_player(p))
    return redirect('/tafl/') 

@login_required
@transaction.atomic
def sendMessage(request):
    form = MessageForm(request.POST)
    if form.is_valid():
        p = Player.objects.get(user=request.user)
        msg = ChatMessage.objects.create(text=form.cleaned_data['text'],
                            user=request.user, time=timezone.now(), 
                            game=p.cur_game)
        send_message(p, p.cur_game.other_player(p), msg)
        return HttpResponse("valid")
    return HttpResponse("invalid")
