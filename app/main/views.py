#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author : liuyu
# date :    2017/10/4

from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response,send_from_directory,jsonify
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import main
from config import Config, SendmailUser
from .forms import EditProfileForm, EditProfileAdminForm, PostForm,\
    CommentForm
from .. import db
from ..models import Permission, Role, User, Post, Comment
from ..decorators import admin_required, permission_required
import baculautils
import baculaforms
import baculamodels
import apiutils
import getbnip
import base64
from werkzeug.utils import secure_filename
from app.db import  sqliteutil
import updownfileutils
import json,os,time,datetime

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from gevent import monkey

monkey.patch_all()


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items

    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp

@main.route('/bacula')
def getbacula():
        k=baculautils.start('haha')
        print type(k)
        return render_template('bacula.html',body=k)

@main.route('/runfailjob')
@login_required
def runfailbacula():
        k=baculautils.start('run')
        print type(k)
        return render_template('bacula.html',body=k)


@main.route('/restorebacula', methods=['GET', 'POST'])
@login_required
def restorebacula():
        form = baculaforms.chosehost()
        timeinfo=['999']
        if form.validate_on_submit():
            hostip=form.hostip.data,
            sitename=form.sitename.data
            timeinfo = baculamodels.rawinput(hostip, sitename).split("<br/>")
            print timeinfo
        return render_template('restorebacula.html',form=form,posts=timeinfo)

@main.route('/runrestorebacula/', methods=['POST','GET'])
@login_required
def runrestorebacula():
        data = request.args
        hostip =  data.get("hostip")
        sitename = data.get("sitename")
        id = data.get("id")
        body = baculamodels.runrestores(id, sitename, hostip)
        result={}
        result['code']=1
        result['infos']=body
        return render_template('baculastatus.html',body=body,data=result)

@main.route('/getrunrestorejobs', methods=['POST','GET'])
@login_required
def getrunrestorejobs():
        body=baculautils.getrestorejobs()
        data = request.args
        data = data.get("data")
        print data
        if data:
            if 'Restore' in data and 'uri' not in data:
                return render_template('baculastatus.html', posts=body, data=data)
            else:
                data = eval(base64.decodestring(data))
                return render_template('baculastatus.html', posts=body, data=data)
                #return render_template('baculastatus.html',posts=body,jobname=data['jobname'],action=data['action'],status=data['status'])
        else:
            return render_template('baculastatus.html',posts=body)

@main.route('/getjobdetails', methods=['GET'])
@login_required
def getjobdetails():
        data = request.args
        hostip = data.get("hostip")
        body=baculautils.run(hostip, 'yuge')
        print body
        return render_template('baculadetails.html',data=body)

@main.route('/bacularunfailjob', methods=['GET'])
@login_required
def bacularunfailjob():
        data = request.args
        hostip = data.get("hostip")
        body=baculautils.run(hostip, 'run')
        print body
        return render_template('baculadetails.html',data=body)

@main.route('/getjoblogs', methods=['GET'])
@login_required
def getjoblogs():
        data = request.args
        hostip = data.get("hostip")
        clientip = data.get("jobname").split("-Backup")[0]
        jobid = data.get("jobid")
        body=apiutils.getbaculalogs(hostip,clientip,jobid)
        if 'row' not in str(body):
            data=""
        else:
            body = json.loads(body)
            data = body["resultset"]['row']
        return render_template('joblogs.html',data=data,clientip=clientip+"-Backup",hostip=hostip)

@main.route('/getjobreport', methods=['GET'])
@login_required
def getjobreport():
        data = request.args
        hostip = data.get("hostip")
        clientip = data.get("jobname").split("-")[0]
        jobid = data.get("jobid")
        data=apiutils.getbaculareport(hostip,clientip)
        today = datetime.date.today()
        lastweekdat =str( today - datetime.timedelta(days=7))
        print data
        otherags={}
        otherags["today"]=today
        otherags["lastweekdat"] = lastweekdat
        otherags["hostip"] = hostip
        otherags["jobid"] = jobid
        otherags["clientip"] = clientip+"-Backup"
        return render_template('jobreport.html',data=data,otherags=otherags)




@main.route('/nagios')
@login_required
def getnagios():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))

@main.route('/addbnserver', methods=['POST'])
def addbacula():
        infos={
            'baculacode': 'None',
            'baculainfo': 'None',
            'nagioscode': 'None',
            'nagiosinfo': 'None',
        }
        data = request.get_data()
        j_data = json.loads(data)
        clientip = j_data["hostip"]
        if clientip.startswith("10.112.0"):
            return "this is a test"
        key = j_data['key']
        if key == "ImJmM2EyNGU5MWRkMTA1Yzc2YTNhOTEyMWYxOTFjY2FkZjU4ZDQyMTIi.DLeDsQ.1yuURBM3Y_wUF7d49CrxMh18l4s":
            systype = j_data["systype"]  # linux windows
            locate = j_data["locate"]  #HA HK
            bnip = getbnip.getnagiosip(locate)
            print clientip ,systype ,locate,bnip["nip"],bnip["bip"]
            ninfo = eval(str(apiutils.addnagios(bnip["nip"],clientip,systype)))
            binfo = eval(str(apiutils.addbaculajob(bnip["nip"], clientip, systype)))
            infos['baculacode'] = str(binfo["exit_code"])
            print type(infos)
            infos['baculainfo'] = str(binfo["return_info"])
            infos['nagioscode'] = str(ninfo["exit_code"])
            infos['nagiosinfo'] = str(ninfo["return_info"])
            return json.dumps(infos)
        else:
            return "error!!!"

@main.route('/deletebajobs', methods=['GET'])
@login_required
def deletebajobs():
        data = request.args
        hostip = data.get("hostip")
        clientip = data.get("clientip").split("-Backup")[0]
        body=apiutils.delbaculajob(hostip,clientip)
        body=json.loads(body)
        print 'deletebajobs',body
        return redirect(url_for('.getjobdetails',hostip=hostip))

@main.route('/runbaculajob', methods=['GET'])
@login_required
def runbaculajob():
        data = request.args
        hostip = data.get("hostip")
        clientip = data.get("clientip")
        body=apiutils.runbaculajob(hostip,clientip)
        body=json.loads(body)
        print body
        return redirect(url_for('.getjobreport',hostip=hostip,jobname=clientip,jobid='now'))


@main.route('/runnewbaculajob', methods=['GET'])
@login_required
def runnewbaculajob():
        data = request.args
        hostip = data.get("hostip")
        clientips = list(eval(data.get("clientips")))
        print clientips
        for clientip in clientips:
            body=apiutils.runbaculajob(hostip,clientip)
            body=json.loads(body)
            print clientip
        return redirect(url_for('.getjobdetails',hostip=hostip))

@main.route('/runcheckjobs', methods=['GET'])
@login_required
def runcheckjobs():
        data = request.args
        hostip = data.get("hostip")
        print 'hostip',hostip

        apiutils.checkbacula(hostip)
        return redirect(url_for('.getjobdetails',hostip=hostip))

@main.route('/runclientrestores', methods=['GET'])
@login_required
def runclientrestores():
        data = request.args
        hostip = data.get("hostip")
        clientip = data.get("clientip").split("-Backup")[0]
        body=baculamodels.runclientrestores(clientip, hostip.split(" "))
        #body=json.loads(body)
        print body
        return redirect(url_for('.getrunrestorejobs',data=base64.encodestring(body)))


@main.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    basedir = os.path.abspath(os.path.dirname(__file__))
    file_dir = os.path.join(Config.UPLOADFILE,'upload')
    print file_dir
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['myfile']

    if f and updownfileutils.allowed_file(f.filename):
        fname = secure_filename(f.filename)
        print fname
        ext = fname.rsplit('.', 1)[1]
        nowtimes = time.time()
        unix_time = updownfileutils.forsafes(str(nowtimes),32)
        new_filename = str(unix_time) + '.tar.' + ext
        f.save(os.path.join(file_dir, new_filename))
        size = os.path.getsize(os.path.join(file_dir, new_filename))
        print '文件大小是 %s 字节' % size
        print new_filename
        token = base64.b64encode(new_filename)
        token=base64.b64encode(updownfileutils.forsafes(base64.b64encode(str(time.time()))+'@'+token,64))
        print token
        uri=str(url_for('main.api_upload', _external=True)).replace('api/upload','files/download/'+token)
        return jsonify({"code": '0', "infos": "SUCCESS", "uri": uri,"size":size})
    else:
        return jsonify({"code": '1001', "infos": "FAILED"})


@main.route('/files/download/<string:filename>', methods=['GET'],)
def download(filename):
    try:
        filename = base64.b64decode(filename)
    except :
        return "your request has expired"
    else:
        if updownfileutils.checktime(filename,12):
            filename = updownfileutils.checktime(filename,0)
            filename = base64.b64decode(filename)
            print os.path.join(Config.UPLOADFILE,'upload',filename)
            if os.path.isfile(os.path.join(Config.UPLOADFILE,'upload',filename)):
                return send_from_directory(os.path.join(Config.UPLOADFILE,'upload'), filename, as_attachment=True)
            return 'not found your files'
        else:
            return 'your request has expired'

@main.route('/downloads/files', methods=['GET'],)
def getdownfiles():
    data = baculamodels.getdownuri()
    return render_template('downuri.html',data=data )

@main.route('/baculajob/lists', methods=['GET'],)
def getbaculaquee():
    data = baculamodels.getbacuajobquee()
    return render_template('baculaquee.html',data=data )


@main.route('/api/download/getdownuri', methods=['GET'],)
def getdownuri():
    data = request.args
    serverip = data.get("hostip")
    sitename = data.get("sitename")
    clientip = data.get("clientip")
    addtime = data.get("addtime")
    ispost = data.get("ispost")
    ischeck = data.get("checkdata")
    if ispost != "ok" and ischeck != "yes" :
        Downloaduri = sqliteutil.Downuri
        sqlitein = sqliteutil.Modify()
        infos = sqlitein.get(Downloaduri,hostip=serverip,sitename=sitename,clientip=clientip,addtime=addtime)
        for i in infos:
            print 'post',i.ispost
            if i.ispost != "ok":
                i.checkdata = 'yes'
                i.description = u'数据压缩传输中'
                i.ispost = 'compressing'
        sqlitein.commit()
        urinfos=eval(apiutils.getdownuris(serverip, sitename, clientip))
        print urinfos
        checkdata = 'no'
        datasize = u"未知"
        print 'code',urinfos["code"]
        if str(urinfos["code"]) == '99':
            uri = 'http://127.0.0.1/files/download/hello'
            description = u"数据正在还原中"
            state = 'running'
        elif str(urinfos["code"]) == '33':
            uri = 'http://127.0.0.1/files/download/hello'
            description = u"通信异常"
            state = 'connect failed'
            checkdata = 'no'
        else:
            if str(urinfos["code"]) != '0':
                uri='http://127.0.0.1/files/download/hello'
                description=u"文件找不到"
                state = 'no'
                checkdata = 'yes'
            else:
                uri = urinfos["uri"]
                datasize = urinfos["size"]
                description = u"还原成功"
                state='ok'
                checkdata = 'yes'
        Downloaduri = sqliteutil.Downuri
        sqlitein = sqliteutil.Modify()
        infos = sqlitein.get(Downloaduri,hostip=serverip,sitename=sitename,clientip=clientip,addtime=addtime)
        for i in infos:
            print 'post',i.ispost
            if i.ispost != "ok":
                i.uri = uri
                i.ispost = state
                i.description = description
                i.checkdata = checkdata
                i.datasize = datasize
        sqlitein.commit()
    data = baculamodels.getdownuri()
    print data
    return render_template('downuri.html',data=data)


@main.route('/api/download/delgetdownuri', methods=['GET'],)
def delgetdownuri():
    data = request.args
    print data
    datas=[]
    serverip = data.get("hostip")
    sitename = data.get("sitename")
    clientip = data.get("clientip")
    addtime = data.get("addtime")
    Downloaduri = sqliteutil.Downuri
    sqlitein = sqliteutil.Quary()
    info=sqlitein.first(Downloaduri,hostip=serverip,sitename=sitename,clientip=clientip,addtime=addtime)
    print apiutils.delflagfile(serverip, sitename, clientip)
    if info != None:
        try:
            uri=base64.b64decode(str(info.uri).split('/files/download/')[1])
            print uri
            urifilename = updownfileutils.checktime(uri, 0)
            print urifilename
            filename = base64.b64decode(urifilename)
            filepath = os.path.join(Config.UPLOADFILE, 'upload', filename)
            print filepath
            if os.path.exists(filepath):
                os.unlink(filepath)
            sqlitein = sqliteutil.Delete()
            sqlitein.delete(Downloaduri, hostip=serverip, sitename=sitename, clientip=clientip, addtime=addtime)
            sqlitein.commit()
            datas = baculamodels.getdownuri()
        except :
            sqlitein = sqliteutil.Delete()
            sqlitein.delete(Downloaduri, hostip=serverip, sitename=sitename, clientip=clientip, addtime=addtime)
            sqlitein.commit()
            datas = baculamodels.getdownuri()
            print 'error'

    return render_template('downuri.html', data=datas)

from ..email import send_email
@main.route('/api/report/bacula/mail', methods=['GET'],)
def sendbaculareport():
    data = baculautils.start('haha')
    try:
        send_email(SendmailUser.mailto_list[0], u'备份任务报告',
                'mail/report_bacula', body=data)
    except:
        return 'error'
    return redirect(url_for('.getbacula'))


@main.route('/api/download/delbaculajob', methods=['GET'],)
def delbaculajob():
    data = request.args
    hostip = data.get("hostip")
    sitename = data.get("sitename")
    clientip = data.get("clientip")
    addtime = data.get("addtime")

    Restorejobs = sqliteutil.Restorejob
    sqlitein = sqliteutil.Delete()
    sqlitein.delete(Restorejobs, hostip=hostip, sitename=sitename, clientip=clientip, addtime=addtime)
    sqlitein.commit()

    return redirect(url_for('.getbaculaquee'))


