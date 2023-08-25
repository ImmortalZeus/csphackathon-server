from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, time

from .forms import  AccountAuthenticationForm
from .models import Contestant, Problem, LeaderBoard
from django.db.models.query_utils import Q
from django.core import serializers
from django.template.loader import render_to_string
from django.forms.models import model_to_dict

from bs4 import BeautifulSoup
import math

import json, os
import subprocess

staticpath = 'mainpage/static'

tier = ["Unrated", "IGM", "GM", "IM", "CM", "Expert"]

def gettime(data):
    f = open(f"{staticpath}/json/config.json")
    data = json.load(f)
    
    start = datetime.combine(datetime(data["start"]["year"], data["start"]["month"], data["start"]["date"]).date(), time(data["start"]["hour"], data["start"]["minute"], data["start"]["second"]))
    freeze = datetime.combine(datetime(data["freeze"]["year"], data["freeze"]["month"], data["freeze"]["date"]).date(), time(data["freeze"]["hour"], data["freeze"]["minute"], data["freeze"]["second"]))
    end = datetime.combine(datetime(data["end"]["year"], data["end"]["month"], data["end"]["date"]).date(), time(data["end"]["hour"], data["end"]["minute"], data["end"]["second"]))
    now = datetime.now()

    return start, freeze, end, now

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        f = open(f"{staticpath}/json/config.json")
        data = json.load(f)

        start, freeze, end, now = gettime(data)


        submissions = []
        for submissions2 in request.user.submissions.values():
            submissions = submissions + submissions2

        # sort nhật kí nộp bài theo tgian, nộp gần xếp trước
        sort_on = "time"
        submissions = [(-dict_[sort_on], dict_) for dict_ in submissions]
        submissions.sort()
        submissions = [dict_ for (key, dict_) in submissions]

        submissions = submissions[0:10:] # chỉ hiện 10 lần nộp đầu tiên

        return render(request, "index.html", {
            "submissions": submissions,
            "contest": data["contest"],
            "username": request.user.get_username(),
            "folder": os.listdir(f"{staticpath}/resources"),
            "now": now.timestamp(),
            "start": start.timestamp(),
            "end": end.timestamp()
        })
    else:
        return redirect("signin")

def signin(request, *args, **kwargs):
    f = open(f"{staticpath}/json/config.json")
    data = json.load(f)

    start, freeze, end, now = gettime(data)

    user = request.user
    if(user.is_authenticated):
        return redirect('home')

    context = {
        "contest": data["contest"]
    }

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if(form.is_valid()):
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect("home")
            else:
                return render(request, "signin.html", {
                    "contest": data["contest"],
                    'error_message': "Đã xảy ra lỗi khi đăng nhập",
                })
        else:
            return render(request, "signin.html", {
                "contest": data["contest"],
                'error_message': "Thông tin đăng nhập không hợp lệ",
            })

    return render(request, "signin.html", context)

def signout(request):
    logout(request)
    return redirect("signin")

def updateleaderboard(leaderboard, problemset, contestants, data, tier, rankinglist):
    problemset2 = []
    for problem2 in problemset: # clone
        problem3 = {
            "id": problem2["id"],
            "name": problem2["name"],
            "testnum": problem2["testnum"],
            "mscore": problem2["mscore"],
            "submissions": problem2["submissions"],
            "ordered": problem2["ordered"],
            "unsolved": problem2["unsolved"],
        }
        problemset2.append(problem3)
    contestants2 = []
    for contestant2 in contestants: # clone
        contestant3 = {
            "id": contestant2["id"],
            "password": contestant2["password"],
            "username": contestant2["username"],
            "is_active": contestant2["is_active"],
            "is_admin": contestant2["is_admin"],
            "is_staff": contestant2["is_staff"],
            "is_superuser": contestant2["is_superuser"],
            "members": contestant2["members"],
            "firstac": contestant2["firstac"],
            "score": contestant2["score"],
            "penalty": contestant2["penalty"],
            "submissions": contestant2["submissions"],
            "submitted": contestant2["submitted"],
            "tscore": contestant2["tscore"],
            "tpenalty": contestant2["tpenalty"],
        }
        contestants2.append(contestant3)
    leaderboard.value = {
        "contest": data["contest"],
        "problemset": problemset2,
        "contestants": contestants2,
        "tier" : tier,
        "ranking": rankinglist,
    }
    leaderboard.save()

def getrankinglist(contestants):
    currank = 0
    curscore = curpenalty = -1
    rankinglist = list()
    for team in contestants:
        if team["submitted"] == True and (team["tscore"] != curscore or team["tpenalty"] != curpenalty):
            currank += 1
        curscore = team["tscore"]
        curpenalty = team["tpenalty"]
        rankinglist.append(currank)
    
    return rankinglist

def contest(request):
    f = open(f"{staticpath}/json/config.json")
    data = json.load(f)

    start, freeze, end, now = gettime(data)
    
    problemset = Problem.objects.all().values()
    #problemset2 = [x.fields.testnum for x in serializers.serialize("json", Problem.objects.all())]
    problemset3 = []
    problemset2 = Problem.objects.all()
    for problem in problemset2:
        problemset3.append({"name": problem.name, "testnum": problem.testnum})
    if request.user.is_authenticated:
        return render(request, "contest.html", {
            "contest": data["contest"],
            "username": request.user.get_username(),
            "problemset": problemset,
            "problemset2": problemset3
        })
    else:
        return redirect("signin")

def ranking(request):
    f = open(f"{staticpath}/json/config.json")
    data = json.load(f)

    start, freeze, end, now = gettime(data)


    if request.user.is_authenticated:
        if now.timestamp() < freeze.timestamp() or now.timestamp() > end.timestamp(): # nếu chưa đến giờ freeze hoặc đã hết giờ
            problemset = Problem.objects.all().values()
            contestants = Contestant.objects.all().order_by('-tscore', 'tpenalty', 'id').values()
            rankinglist = getrankinglist(contestants)
            leaderboard = LeaderBoard.objects.filter(name="rankingsave").exists()
            if not leaderboard:
                leaderboard = LeaderBoard.objects.create(name="rankingsave")
            else:
                leaderboard = LeaderBoard.objects.get(name="rankingsave")
            updateleaderboard(leaderboard, problemset, contestants, data, tier, rankinglist)

            return render(request, "ranking.html", {
                "contest": data["contest"],
                "problemset": problemset,
                "contestants": contestants,
                "tier" : tier,
                "ranking": rankinglist,
            })
        else: # đã freeze
            problemset = Problem.objects.all().values()
            contestants = Contestant.objects.all().order_by('-tscore', 'tpenalty', 'id').values()
            rankinglist = getrankinglist(contestants)
            leaderboard = LeaderBoard.objects.filter(name="rankingsave").exists()
            if not leaderboard:
                leaderboard = LeaderBoard.objects.create(name="rankingsave")
            else:
                leaderboard = LeaderBoard.objects.get(name="rankingsave")
            if not leaderboard.value:
                updateleaderboard(leaderboard, problemset, contestants, data, tier, rankinglist)
            return render(request, "ranking.html", leaderboard.value)
    else:
        return redirect("signin")


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


import socketio
sio = socketio.Server(async_mode='eventlet')

# cái lý do t dùng socket.io vì nó khá là tiện và code nhìn sạch sẽ đơn giản hơn cái trc kia t làm

"""
@sio.event
def connect(sid, data):
    print(bcolors.OKGREEN + bcolors.BOLD + "A user connected : " + sid + bcolors.BOLD + bcolors.ENDC)

@sio.event
def disconnect(sid):
    print(bcolors.OKGREEN + bcolors.BOLD + "A user disconnected : " + sid + bcolors.BOLD + bcolors.ENDC)
"""

def chambaicpp(testid, useranscpp):
    # Command to compile the C++ program 
    compile_command = ["g++", os.path.abspath(f"./mainpage/checkercpp/{testid}.cpp"), "-o", os.path.abspath(f"./mainpage/checkercpp/{testid}")] 
    
    # Command to execute the compiled program 
    run_command = [os.path.abspath(f"./mainpage/checkercpp/{testid}")]
    
    # Compile the C++ program 
    compile_process = subprocess.run(compile_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
    
    # Check if the compilation was successful 
    if compile_process.returncode == 0: 
        # Run the compiled program 
        run_process = subprocess.Popen(run_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = run_process.communicate(bytes(str(useranscpp), 'utf-8'))[0].decode("utf-8") # output là điểm bài làm
        out = out.strip()
        return int(out)
        
    else:
        # Print the compilation error messages
        print("Compilation failed.")
        print(compile_process.stderr.decode())
        return 0

def chambaipy(testid, useranspy):
    import imp
    checker = imp.load_source('checker', os.path.abspath(f"./mainpage/checkerpy/{testid}.py"))
    return checker.check(useranspy)

def calscore(problem, user, useranscpp, useranspy, time, start, freeze, end):
    # tscore = chambaicpp(problem.name, useranscpp)
    tscore = chambaipy(problem.id, useranspy)
    penalty = math.floor(((time.timestamp() - start.timestamp())/60)) + 20 * len(user.submissions[str(problem.id)])
    # print(problem.name, tscore, penalty, user.username, userans)

    return {
        "useranscpp": useranscpp,
        "useranspy": useranspy,
        "problem": problem.name,
        "tscore": tscore,
        "penalty": penalty,
        "time": time.timestamp(),
        "user": user.username
    }

@sio.event
def submit(sid, message):
    f = open(f"{staticpath}/json/config.json")
    data = json.load(f)

    start, freeze, end, now = gettime(data)

    # event khi có người nộp bài
    if now.timestamp() < start.timestamp():
        return sio.emit('returnscore', {"error": "Contest chưa bắt đầu !"})
    if now.timestamp() > end.timestamp():
        return sio.emit('returnscore', {"error": "Contest đã kết thúc !"})
    
    if message['sessionid'] == 'None':
        return sio.emit('returnscore', {"error": "Nộp bài thất bại !"})
    
    try:
        session = Session.objects.get(session_key=message['sessionid'])
    except Session.DoesNotExist:
        return sio.emit('returnscore', {"error": "Nộp bài thất bại !"})

    uid = session.get_decoded().get('_auth_user_id')

    try:
        user = Contestant.objects.get(pk=uid)
    except Contestant.DoesNotExist:
        return sio.emit('returnscore', {"error": "Nộp bài thất bại !"})
    
    try:
        problem = Problem.objects.get(name=message["problem"])
    except Problem.DoesNotExist:
        return sio.emit('returnscore', {"error": "Nộp bài thất bại !"})

    useranscpp = message["anscpp"]
    useranspy = message["anspy"]

    if str(problem.id) not in user.submissions:
        user.submissions[str(problem.id)] = []

    scoreinfo = calscore(problem, user, useranscpp, useranspy, now, start, freeze, end)

    problemset = Problem.objects.all().values()
    contestants = Contestant.objects.all().order_by('-tscore', 'tpenalty', 'id').values()
    rankinglist = getrankinglist(contestants)
    leaderboard = LeaderBoard.objects.filter(name="rankingsave").exists()
    if not leaderboard:
        leaderboard = LeaderBoard.objects.create(name="rankingsave")
    else:
        leaderboard = LeaderBoard.objects.get(name="rankingsave")
    if not leaderboard.value:
        updateleaderboard(leaderboard, problemset, contestants, data, tier, rankinglist)

    # nếu max điểm , tức là nếu AC
    if scoreinfo["tscore"] == problem.mscore:
        filtered = filter(lambda submission: submission["tscore"] == problem.mscore, problem.submissions) # check có thằng nào AC trước hay không
        if len(list(filtered)) == 0: # chưa có thằng nào AC
            user.firstac[str(problem.id)] = True
            problem.unsolved = False


    user.score[str(problem.id)] = scoreinfo["tscore"]
    user.penalty[str(problem.id)] = scoreinfo["penalty"]
    user.submissions[str(problem.id)].append(scoreinfo)
    user.submitted = True
    problemset = Problem.objects.all().values()
    user.tscore = 0
    user.tpenalty = 0
    for problem2 in problemset: # tính tổng điểm và tổng penalty
        if str(problem2["id"] - 1) in user.score:
            user.tscore += user.score[str(problem2["id"] - 1)]
        if str(problem2["id"] - 1) in user.penalty:
            user.tpenalty += user.penalty[str(problem2["id"] - 1)]
    user.save() # cập nhật user

    problem.submissions.append(scoreinfo)
    problem.save() # cập nhật problem

    sio.emit('returnscore', scoreinfo, to=sid)
    
    if now.timestamp() < freeze.timestamp() or now.timestamp() > end.timestamp():
        problemset = Problem.objects.all().values()
        contestants = Contestant.objects.all().order_by('-tscore', 'tpenalty', 'id').values()
        rankinglist = getrankinglist(contestants)
        leaderboard = LeaderBoard.objects.filter(name="rankingsave").exists()
        if not leaderboard:
            leaderboard = LeaderBoard.objects.create(name="rankingsave")
        else:
            leaderboard = LeaderBoard.objects.get(name="rankingsave")
        updateleaderboard(leaderboard, problemset, contestants, data, tier, rankinglist)

        htmlranking = render_to_string("ranking.html", {
            "contest": data["contest"],
            "problemset": problemset,
            "contestants": contestants,
            "tier" : tier,
            "ranking": rankinglist,
        })
        parsed_html = BeautifulSoup(htmlranking, "html.parser")
        sio.emit('update_ranking', {"bodyhtml": str(parsed_html.body)})
    else:
        htmlranking = render_to_string("ranking.html", leaderboard.value)
        parsed_html = BeautifulSoup(htmlranking, "html.parser")
        sio.emit('update_ranking', {"bodyhtml": str(parsed_html.body)})
    # print(bcolors.OKGREEN + bcolors.BOLD + "A user submitted : " + sid + bcolors.BOLD + bcolors.ENDC)


from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Contestant)
def deleting_model(sender, instance, **kwargs):
    # print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    username = instance
    # print(kwargs['origin'].submissions)
    problemset = Problem.objects.all().values()
    # print(username)
    for problem in problemset: # tính tổng điểm và tổng penalty
        # print(problem['submissions'])
        problem2 = Problem.objects.get(name=problem["name"])
        # print(problem2.submissions)
        # print('\n\n\n\n')
        filtered = []
        unsolved = True
        for submission in problem2.submissions:
            if str(submission.get('user')) != str(username):
                filtered.append(submission)
                if submission.get('tscore') == problem.mscore:
                    unsolved = False
        problem2.submissions = filtered
        problem2.unsolved = unsolved
        # print(problem2.submissions)
        problem2.save()
        
    f = open(f"{staticpath}/json/config.json")
    data = json.load(f)

    start, freeze, end, now = gettime(data)
    
    if now.timestamp() < freeze.timestamp() or now.timestamp() > end.timestamp():
        problemset = Problem.objects.all().values()
        contestants = Contestant.objects.all().order_by('-tscore', 'tpenalty', 'id').values()
        rankinglist = getrankinglist(contestants)
        leaderboard = LeaderBoard.objects.filter(name="rankingsave").exists()
        if not leaderboard:
            leaderboard = LeaderBoard.objects.create(name="rankingsave")
        else:
            leaderboard = LeaderBoard.objects.get(name="rankingsave")
        updateleaderboard(leaderboard, problemset, contestants, data, tier, rankinglist)

        htmlranking = render_to_string("ranking.html", {
            "contest": data["contest"],
            "problemset": problemset,
            "contestants": contestants,
            "tier" : tier,
            "ranking": rankinglist,
        })
        parsed_html = BeautifulSoup(htmlranking, "html.parser")
        sio.emit('update_ranking', {"bodyhtml": str(parsed_html.body)})
    else:
        htmlranking = render_to_string("ranking.html", leaderboard.value)
        parsed_html = BeautifulSoup(htmlranking, "html.parser")
        sio.emit('update_ranking', {"bodyhtml": str(parsed_html.body)})