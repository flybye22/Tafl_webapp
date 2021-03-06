from django.conf.urls import include, url

urlpatterns = [
    url(r'^$', 'tafl.views.gamespage', name='games'),
    url(r'^mainpage', 'tafl.views.gamespage', name='games'),
    url(r'^game$', 'tafl.views.game', name='game'),
    url(r'^register$', 'tafl.views.register', name='register'),
    url(r'^login$', 'tafl.views.mylogin', name='login'),
    url(r'^logout$', 'tafl.views.mylogout', name='logout'),
    url(r'^makegame$', 'tafl.views.makegame', name='makegame'),
    url(r'^joingame$', 'tafl.views.joingame', name='joingame'),
    url(r'^usersearch', 'tafl.views.usersearch', name='usersearch'),
    url(r'^profile', 'tafl.views.profile', name='view'),
    url(r'^leaderboard', 'tafl.views.leaderboard', name='leaderboard'),
    url(r'^whatis$', 'tafl.views.about', name='about'),
    url(r'^resign$', 'tafl.views.resign', name='resign'),
    url(r'^sendMessage$', 'tafl.views.sendMessage', name='sendMessage')
]
