from flask import Blueprint

db_manage_cmd_bp = Blueprint('db_manage_cmd_blue', __name__, cli_group=None)# cli_group wskazuje do jakiej grupy należy przyporządkować utworzone komendy,
# my już mamy utworzoną grupę cli-group

from api.commands import db_manage_commands