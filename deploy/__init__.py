import os
from subprocess import call

from fabric.contrib.files import exists, sed
from fabric.api import env, local, run, cd, prefix, put
from contextlib import contextmanager

REPO_URL = 'https://github.com/imhuwq/twiwei.git'

env.use_ssh_config = True
remote_path = '/home/%s/sites/twiwei' % env.user
env.active = '. %s/env/bin/activate' % remote_path
local_path = os.path.abspath(os.path.dirname(__file__) + '/../')


@contextmanager
def virtualenv():
    with cd(remote_path + '/env'):
        with prefix(env.active):
            yield


def deploy(server):
    env.host_string = server
    print('开始部署，请确保已经更新 requirements.txt, 并且本地代码已经提交到 git 代码仓库')
    source_folder = remote_path
    _create_directory_if_necessary(remote_path)
    _get_latest_source(source_folder)
    _update_configs(source_folder)
    _update_virtualenv(source_folder)
    _update_database(source_folder)
    _restart_server()


def _create_directory_if_necessary(site_folder):
    if not exists(site_folder):
        run("mkdir -p %s" % site_folder)


def _get_latest_source(source_folder):
    if exists('%s/.git' % source_folder):
        run("cd %s && git pull" % source_folder)
    else:
        run("git clone %s %s" % (REPO_URL, source_folder))
        current_commit = local("git log -n 1 --format=%H", capture=True)
        run("cd %s && git reset --hard %s" % (source_folder, current_commit))


def _update_configs(source_folder):
    local_config = local_path + '/config.py'
    remote_config = source_folder + '/config.py'
    call(['rsync', '-azP', local_config, remote_config])
    sed(remote_config, "USE_PROXY = True", "USE_PROXY = False")


def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/env'
    if not exists(virtualenv_folder + '/bin/pip'):
        run('virtualenv --python=python3 %s' % virtualenv_folder)
    run('%s/bin/pip install -r %s/requirements.txt'
        % (virtualenv_folder, source_folder))


def _update_database(source_folder):
    with virtualenv():
        if not exists(remote_path + '/migs'):
            run('cd %s && alembic init migs'
                % source_folder)
            put('%s/alembic.ini' % local_path, '%s/alembic.ini' % remote_path)
            put('%s/migs/env.py' % local_path, '%s/migs/env.py' % remote_path)

        run('cd %s && alembic revision --autogenerate && alembic upgrade head'
            % source_folder)


# TODO: 使用 supervisor 监控 tornado 后再实现该功能
def _restart_server():
    pass
